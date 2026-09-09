#!/usr/bin/env python3
"""One-use, hash-checked documentation publisher; no application execution."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import lzma
import os
import shutil
import subprocess
import sys

ROOT = Path.cwd()
REPORT = Path('/tmp/ssr-hardening-publication')
REPO = 'JennieXLisa/ssr-redesign'
BASE = '6460d32856e9c0afa26b3561a72f0b5b30b26ee2'
RAW_SHA = '66694b31f4d5e4e5dcf9eefc34697c34d315f8988eae0ef2039cf7d45cb6ef58'
SET_SHA = 'ab60d56be5cdd331d8bf197d183b8ab639b52f54b499d9f9b4fe9ce085f12092'
GENERATED = ['contracts/schemas/hardening-v1.schema.json', 'contracts/schemas/sdk-abi.json',
             'contracts/schemas/state-transitions.json', 'contracts/reference/public-api.pyi',
             'contracts/schemas/tool-inputs.schema.json']
report = {'published': False, 'repository': REPO, 'base_commit': BASE, 'commits': [],
          'application_tests_run': False, 'provider_calls': 0, 'target_execution': False}

def require(condition, detail):
    if not condition:
        raise RuntimeError(detail)

def command(*args, capture=True):
    process = subprocess.run(list(args), cwd=ROOT, text=True, capture_output=capture)
    if process.returncode:
        raise RuntimeError('Command failed: ' + ' '.join(args[:3]))
    return process.stdout.strip() if capture else ''

def safe_path(value):
    require(isinstance(value, str) and value, 'Invalid path')
    p = PurePosixPath(value)
    require(not p.is_absolute() and p.as_posix() == value and '..' not in p.parts
            and not any(ord(c) < 32 for c in value) and '\\' not in value, 'Unsafe path')
    allowed = value == '.gitignore' or (
        len(p.parts) == 1 and (value.endswith('.md') or value.endswith('.json'))) or (
        p.parts[0] in {'contracts', 'tools', 'history'} or
        p.parts[0] in {'01-operating-model-autonomy-tools','02-security-discovery',
                      '03-contextual-collaboration','04-knowledge-evidence-coverage',
                      '05-investigation-falsification-findings','06-worker-pool-runtime',
                      '07-contracts-persistence-integration','08-validation-delivery'})
    require(allowed, 'Write outside documentation scope: ' + value)
    target = ROOT.joinpath(*p.parts)
    for parent in (target, *target.parents):
        if parent == ROOT.parent:
            break
        require(not parent.is_symlink(), 'Symlink in target path')
    return target

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def prepare():
    meta = json.loads((ROOT/'.maintenance/manifest.json').read_text())
    require(len(meta['parts']) == 10, 'Unexpected part count')
    chunks = []
    for i, item in enumerate(meta['parts']):
        require(item['path'] == f'.maintenance/part-{i:02}.xz', 'Part path mismatch')
        raw = (ROOT/item['path']).read_bytes()
        require(len(raw) == item['bytes'] and digest(raw) == item['sha256'], 'Part hash mismatch')
        chunks.append(raw)
    raw = lzma.decompress(b''.join(chunks), memlimit=256*1024*1024)
    require(len(raw) == 333393 and digest(raw) == RAW_SHA, 'Package hash mismatch')
    data = json.loads(raw)
    require(data['format'] == 'ssr-design-update-v1' and data['expected_source_commit'] == BASE,
            'Package identity mismatch')
    require(data['expected_content_set'] == SET_SHA and len(data['groups']) == 36,
            'Package target mismatch')
    prepared = []
    paths = set()
    for group in data['groups']:
        require(isinstance(group['message'], str) and group['message'].startswith('docs'), 'Bad message')
        result = []
        for item in group['files']:
            name = item['path']
            require(name not in paths, 'Duplicate file mutation')
            paths.add(name)
            path = safe_path(name)
            old = path.read_bytes() if path.exists() else None
            require((digest(old) if old is not None else None) == item['old_sha256'],
                    'Remote base content changed: ' + name)
            if 'copy_from_base' in item:
                # All files are prepared before the first mutation; this is the baseline copy.
                new = safe_path(item['copy_from_base']).read_bytes()
            else:
                lines = (old or b'').decode('utf-8').splitlines(keepends=True)
                previous = -1
                for start, end, text in item['edits']:
                    require(type(start) is int and type(end) is int and previous <= start <= end <= len(lines)
                            and isinstance(text, str), 'Invalid edit coordinates')
                    previous = end
                for start, end, text in reversed(item['edits']):
                    lines[start:end] = [text]
                new = ''.join(lines).encode('utf-8')
            require(len(new) <= 2*1024*1024 and digest(new) == item['new_sha256'],
                    'Reconstructed content mismatch: ' + name)
            result.append((name, new))
        prepared.append((group['message'], result))
    return prepared

def record():
    REPORT.mkdir(parents=True, exist_ok=True)
    (REPORT/'publication.json').write_text(json.dumps(report, indent=2)+'\n')

def commit_push(message, paths):
    if paths:
        command('git', 'add', '--', *paths)
    staged = command('git', 'diff', '--cached', '--name-only')
    if not staged:
        return
    require(command('git','ls-remote','origin','refs/heads/main').split()[0] ==
            command('git','rev-parse','HEAD'), 'Concurrent main update; no force push')
    command('git','commit','-m',message,'-m','Documentation/contract reference only. Source bundle SHA-256: '+RAW_SHA)
    command('git','push','origin','HEAD:refs/heads/main')
    sha = command('git','rev-parse','HEAD')
    require(command('git','ls-remote','origin','refs/heads/main').split()[0] == sha,
            'Remote publication not confirmed')
    report['commits'].append({'sha':sha,'message':message,'paths':staged.splitlines()})
    record()
    print('Published', sha, message, flush=True)

def validate(name, *args):
    with (REPORT/name).open('w') as out:
        p = subprocess.run(list(args), cwd=ROOT, stdout=out, stderr=subprocess.STDOUT)
    require(p.returncode == 0, 'Validation failed: ' + name)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    prepared = prepare()
    if args.validate_only:
        print('Verified', len(prepared), 'groups and', sum(len(x[1]) for x in prepared), 'file reconstructions')
        return
    require(os.environ.get('GITHUB_REPOSITORY') == REPO and
            os.environ.get('GITHUB_REF') == 'refs/heads/main', 'Unexpected repository/branch')
    command('git','merge-base','--is-ancestor',BASE,'HEAD')
    require(not command('git','status','--porcelain'), 'Dirty initial checkout')
    record()
    command('git','config','user.name','github-actions[bot]')
    command('git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com')
    for index, (message, files) in enumerate(prepared):
        for name, raw in files:
            path = safe_path(name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        names = [name for name, raw in files]
        if index == 0:
            command(sys.executable, 'tools/build_hardening_schemas.py')
            names.extend(GENERATED)
        commit_push(message, names)
    # This file is already in memory. The ephemeral workflow itself is removed by
    # the connector after this run, so GITHUB_TOKEN need not mutate workflow files.
    command('git','rm','-r','--','.maintenance')
    validate('structure.log',sys.executable,'tools/validate_docs.py')
    validate('manifest-build.log',sys.executable,'tools/refresh_manifest.py')
    validate('hardening.log',sys.executable,'tools/validate_hardening.py')
    validate('manifest-check.log',sys.executable,'tools/refresh_manifest.py','--check')
    validate('diff-check.log','git','diff','--check')
    manifest = json.loads((ROOT/'MANIFEST.json').read_text())
    require(manifest['content_set_sha256'] == SET_SHA, 'Final content-set mismatch')
    for message, files in prepared:
        for name, raw in files:
            require(safe_path(name).read_bytes() == raw, 'Final content mismatch: '+name)
    commit_push('docs: verify hardening package and remove temporary transfer data',
                ['MANIFEST.json','validation-results.json','hardening-validation.json'])
    require(not command('git','status','--porcelain'), 'Uncommitted final changes')
    report.update(published=True, verified_commit=command('git','rev-parse','HEAD'),
                  tree_sha=command('git','rev-parse','HEAD^{tree}'),
                  content_set_sha256=SET_SHA, source_files=len(manifest['files']),
                  reference_tests=json.loads((ROOT/'hardening-validation.json').read_text())['tests_run'],
                  temporary_workflow_cleanup_pending=True)
    for name in ('MANIFEST.json','validation-results.json','hardening-validation.json'):
        shutil.copy2(ROOT/name, REPORT/name)
    command('git','archive','--format=zip','--output='+str(REPORT/'design-source.zip'),'HEAD')
    record()

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        report['error'] = str(exc)[:2048]
        record()
        raise
