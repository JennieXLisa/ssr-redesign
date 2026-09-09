#!/usr/bin/env python3
"""Validate design/reference contracts only. Never import SSR, run targets, or call providers."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
outputs=['contracts/schemas/hardening-v1.schema.json','contracts/schemas/sdk-abi.json',
         'contracts/schemas/state-transitions.json','contracts/reference/public-api.pyi',
         'contracts/schemas/tool-inputs.schema.json']
before={p:(ROOT/p).read_bytes() for p in outputs}
p=subprocess.run([sys.executable,str(ROOT/'tools/build_hardening_schemas.py')],capture_output=True,text=True)
errors=[]
if p.returncode:errors.append('Schema generator failed: '+p.stderr[-2048:])
for name,raw in before.items():
 if (ROOT/name).read_bytes()!=raw:errors.append('Generated contract out of date: '+name)
import test_contract_hardening
suite=unittest.defaultTestLoader.loadTestsFromModule(test_contract_hardening)
result=unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():errors.append('Executable specification/reference tests failed')
# Every feature has its actual dedicated plan; trace is not merely a list of summaries.
trace=json.loads((ROOT/'TRACEABILITY.json').read_text())
for feature in trace['features']:
 path=feature.get('implementation_plan')
 if not path or not (ROOT/path).is_file():errors.append('Missing exact feature implementation plan: '+feature['id'])
manifest_path=ROOT/'MANIFEST.json'
if manifest_path.exists():
 manifest=json.loads(manifest_path.read_text())
 if manifest.get('format')=='ssr-document-manifest-v3':
  for path,item in manifest['files'].items():
   file=ROOT/path
   if not file.is_file() or file.stat().st_size!=item['bytes'] or hashlib.sha256(file.read_bytes()).hexdigest()!=item['sha256']:
    errors.append('Manifest content mismatch: '+path)
  from refresh_manifest import source_files
  actual={str(x.relative_to(ROOT)) for x in source_files()}
  if actual!=set(manifest['files']):errors.append('Manifest file membership mismatch')
 else:errors.append('Current manifest has not been regenerated')
# Protected earlier user approvals must stay byte-identical; validate_docs supplies that check.
report={'status':'PASS' if not errors else 'FAIL','kind':'DOCUMENT_AND_REFERENCE_CONTRACT_VALIDATION',
 'tests_run':result.testsRun,'failures':len(result.failures),'errors':errors,'generated_files_checked':len(outputs),
 'closed_definitions':len(json.loads((ROOT/outputs[0]).read_text())['$defs']),
 'sdk_methods':len(json.loads((ROOT/outputs[1]).read_text())['methods']),
 'feature_plans_checked':len(trace['features']),'application_tests_run':False,
 'migration_tests_against_harness_run':False,'provider_calls':0,'target_execution':False,
 'publication_verified_by_this_script':False,
 'manifest_content_set':manifest.get('content_set_sha256') if manifest_path.exists() else None}
(ROOT/'hardening-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
sys.exit(bool(errors))
