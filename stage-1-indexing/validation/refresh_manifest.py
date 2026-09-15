"""Regenerate/check the specification overlay manifest without tracking caches."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
MANIFEST = ROOT / 'MANIFEST.json'
SUFFIXES = {'.md', '.json', '.py', '.sql', '.toml', '.yaml', '.yml', '.txt', '.c'}


def expected_manifest() -> dict:
    current = json.loads(MANIFEST.read_text())
    paths = [ROOT / name for name in ('IMPLEMENTATION.md', 'TRACEABILITY.json', 'VALIDATION.md')]
    for directory in ('contracts/v1', 'implementation', 'specification', 'validation'):
        paths += [path for path in (ROOT / directory).rglob('*')
                  if path.is_file() and path.suffix in SUFFIXES
                  and '__pycache__' not in path.parts
                  and not any(part.startswith('.') for part in path.relative_to(ROOT).parts)]
    entries = []
    for path in sorted(set(paths)):
        raw = path.read_bytes()
        entries.append({'path': path.relative_to(REPO).as_posix(), 'bytes': len(raw),
                        'sha256': hashlib.sha256(raw).hexdigest(),
                        'git_blob_sha1': hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()})
    return {**current, 'edition': '1.2', 'date': '2026-09-16',
            'delivery': 'Stage 1 specification/reference correction overlay; approved requirements retained',
            'self_excluded': True, 'files': entries}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    expected = expected_manifest()
    if args.check:
        actual = json.loads(MANIFEST.read_text())
        if actual != expected:
            before = {item['path']: item for item in actual.get('files', [])}
            after = {item['path']: item for item in expected['files']}
            changed = sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p))
            print(json.dumps({'valid': False, 'changed_or_missing': changed}, indent=2))
            return 1
        print(json.dumps({'valid': True, 'entries_verified': len(expected['files'])}))
    else:
        MANIFEST.write_text(json.dumps(expected, separators=(',', ':')) + '\n')
        print(json.dumps({'entries_written': len(expected['files'])}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
