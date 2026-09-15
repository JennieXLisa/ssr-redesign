"""Run all delivered specification/reference checks, not runtime release gates."""
from __future__ import annotations

import ast
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import unittest

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def main() -> int:
    sys.dont_write_bytecode = True
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    for script in ['export_schemas.py', 'check_contracts.py']:
        completed = subprocess.run([sys.executable, '-B', str(HERE / script)], check=False)
        if completed.returncode:
            return completed.returncode
    parsed_files = []
    for path in sorted(ROOT.rglob('*.py')):
        if '__pycache__' not in path.parts:
            ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
            parsed_files.append(path.relative_to(ROOT).as_posix())
    schemas = []
    for path in sorted((ROOT / 'contracts/v1').glob('*.schema.json')):
        Draft202012Validator.check_schema(json.loads(path.read_text()))
        schemas.append(path.name)
    suite = unittest.defaultTestLoader.discover(str(HERE / 'regressions'), pattern='test_*.py')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {
        'scope': 'specification contracts, authored fixture integrity, pure decision/sanitizer/manifest models; no runtime SQL/parser/scanner/transport or performance gates',
        'environment': {'python': platform.python_version(), 'platform': platform.platform(),
                        **{name: importlib.metadata.version(name) for name in ['pydantic', 'jsonschema', 'PyYAML']}},
        'tests_run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
        'skipped': len(result.skipped), 'successful': result.wasSuccessful(),
        'failure_tests': [test.id() for test, _ in result.failures],
        'error_tests': [test.id() for test, _ in result.errors],
        'python_files_parsed': parsed_files, 'generated_schemas_validated': schemas,
    }
    (HERE / 'regression-results.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'python_files_parsed'}, indent=2))
    return 0 if result.wasSuccessful() and not result.skipped else 1


if __name__ == '__main__':
    raise SystemExit(main())
