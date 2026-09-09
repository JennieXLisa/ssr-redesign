#!/usr/bin/env python3
"""Validate this documentation package only; never import or execute SSR/targets."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []
active = [p for p in ROOT.rglob('*.md') if 'history' not in p.relative_to(ROOT).parts]
links_checked = 0
for path in active:
    text = path.read_text(encoding='utf-8')
    # Remove fenced code before interpreting links.
    in_fence = False
    plain = []
    for line in text.splitlines():
        if line.startswith('```'):
            in_fence = not in_fence
            continue
        if not in_fence:
            plain.append(line)
    if in_fence:
        errors.append(f'{path.relative_to(ROOT)}: unclosed code fence')
    for raw in re.findall(r'\]\(([^)]+)\)', '\n'.join(plain)):
        raw = raw.split(' "', 1)[0].strip('<>')
        if not raw or raw.startswith(('https:', 'http:', 'mailto:', '#')):
            continue
        rel = unquote(raw.split('#', 1)[0])
        target = (path.parent / rel).resolve()
        links_checked += 1
        if not target.exists():
            errors.append(f'{path.relative_to(ROOT)}: missing link {rel}')

trace = json.loads((ROOT / 'TRACEABILITY.json').read_text())
features = trace['features']
expected_sections = ['## Purpose and concrete outcome', '## Existing implementation and ownership',
                     '## Detailed requirements', '## Inputs, outputs, and state',
                     '## Ordered implementation', '## Failure, concurrency, and recovery',
                     '## Acceptance tests', '## Do not overengineer or expand scope',
                     '## Definition of done']
ids = {f['id'] for f in features}
if len(features) != 34 or len(ids) != 34:
    errors.append('Expected 34 unique feature guides')
requirements = 0
scenarios = 0
for f in features:
    p = ROOT / f['path']
    if not p.exists():
        errors.append(f"Missing feature {f['id']}")
        continue
    s = p.read_text()
    for h in expected_sections:
        if h not in s:
            errors.append(f"{f['id']}: missing section {h}")
    for dep in f['dependencies']:
        if dep not in ids:
            errors.append(f"{f['id']}: unknown dependency {dep}")
    req_prefix = '-C' if f['id'] in {'P1-F01', 'P1-F02'} else '-R'
    test_prefix = '-CT' if f['id'] in {'P1-F01', 'P1-F02'} else '-T'
    rq = re.findall(r'\*\*(' + re.escape(f['id'] + req_prefix) + r'\d+)\.\*\*', s)
    ts = re.findall(r'^\| (' + re.escape(f['id'] + test_prefix) + r'\d+) \|', s, re.M)
    if len(rq) != f['requirements'] or len(set(rq)) != len(rq):
        errors.append(f"{f['id']}: requirement count/identity mismatch")
    if len(ts) != f['tests'] or len(set(ts)) != len(ts):
        errors.append(f"{f['id']}: test count/identity mismatch")
    requirements += len(rq)
    scenarios += len(ts)
for phase in range(1, 9):
    dirs = [p for p in ROOT.iterdir() if p.is_dir() and p.name.startswith(f'{phase:02d}-')]
    if len(dirs) != 1:
        errors.append(f'Phase {phase}: missing/duplicate directory')
        continue
    for name in ['SPECIFICATION.md', 'IMPLEMENTATION_PLAN.md']:
        p = dirs[0] / name
        if not p.exists() or 'DRAFT COMPLETE' not in p.read_text():
            errors.append(f'Phase {phase}: missing completed-draft {name}')

history = ROOT / 'history' / 'before-delegated-completion'
manifest = json.loads((history / 'manifest.json').read_text())
for rel, meta in manifest.items():
    p = history / rel
    if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != meta['sha256']:
        errors.append(f'Historical checkpoint changed: {rel}')

# Check table structure outside fenced examples (escaped pipes are cell content).
tables_checked = 0
for path in active:
    block = []
    fenced = False
    blocks = []
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if line.startswith('```'):
            fenced = not fenced
        if not fenced and line.startswith('|'):
            block.append((number, line))
        elif block:
            blocks.append(block)
            block = []
    if block:
        blocks.append(block)
    for block in blocks:
        tables_checked += 1
        if len(block) < 2 or re.fullmatch(r'\|[ :|\-]+\|', block[1][1]) is None:
            errors.append(f'{path.relative_to(ROOT)}:{block[0][0]}: table lacks header separator')
            continue
        columns = len(re.findall(r'(?<!\\)\|', block[0][1]))
        for number, row in block[2:]:
            if len(re.findall(r'(?<!\\)\|', row)) != columns:
                errors.append(f'{path.relative_to(ROOT)}:{number}: table column mismatch')

# Preserve original approved text, not just a count of newly written requirements.
preserved_requirements = 0
preserved_scenarios = 0
base_feature = Path('01-operating-model-autonomy-tools/features')
for code, slug in [('P1-F01', 'research-access-and-ownership'),
                   ('P1-F02', 'indexed-navigation-and-retrieval')]:
    original = (history / base_feature / f'{code}-{slug}.md').read_text()
    ledger = (ROOT / base_feature / code / 'APPROVED_REQUIREMENTS.md').read_text()
    testledger = (ROOT / base_feature / code / 'APPROVED_TESTS.md').read_text()
    if code == 'P1-F01':
        requirements_to_check = re.findall(r'^\| P1-F01-R\d+ \|.*$', original, re.M)
        tests_to_check = re.findall(r'^\| F01-T\d+[^\n]*$', original, re.M)
    else:
        requirements_to_check = [m.group(0).strip() for m in re.finditer(
            r'^### P1-F02-R\d+[^\n]*\n.*?(?=^#{1,3} |\Z)', original, re.M | re.S)]
        tests_to_check = re.findall(r'^\| P1-F02-T\d+ \|.*$', original, re.M)
    for value in requirements_to_check:
        if value not in ledger:
            errors.append(f'{code}: previously approved requirement text changed')
    for value in tests_to_check:
        if value not in testledger:
            errors.append(f'{code}: previously approved test text changed')
    preserved_requirements += len(requirements_to_check)
    preserved_scenarios += len(tests_to_check)
if (preserved_requirements, preserved_scenarios) != (113, 156):
    errors.append('Previous approval ledger count mismatch')

schema_cases = 0
try:
    from jsonschema import Draft202012Validator
    schema = json.loads((ROOT / 'contracts/schemas/tool-inputs.schema.json').read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    for case in json.loads((ROOT / 'contracts/examples/validation-cases.json').read_text()):
        is_valid = validator.is_valid(case['value'])
        schema_cases += 1
        if is_valid != case['valid']:
            errors.append(f"Schema fixture {case['name']}: expected valid={case['valid']}, actual {is_valid}")
except ImportError:
    errors.append('jsonschema is unavailable; schema checks were not run')

result = {'status': 'PASS' if not errors else 'FAIL', 'active_markdown_files': len(active),
          'features': len(features), 'phase_specifications': 8, 'phase_implementation_plans': 8,
          'completion_requirements': requirements, 'new_acceptance_scenarios': scenarios,
          'local_links_checked': links_checked, 'markdown_tables_checked': tables_checked,
          'historical_files_verified': len(manifest), 'preserved_requirements': preserved_requirements,
          'preserved_acceptance_scenarios': preserved_scenarios,
          'schema_fixtures': schema_cases, 'errors': errors,
          'application_tests_run': False, 'github_published': False}
print(json.dumps(result, indent=2))
sys.exit(1 if errors else 0)
