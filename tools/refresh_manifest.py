#!/usr/bin/env python3
"""Generate/check a non-self-referential manifest of tracked design source files."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
EXCLUDED={'MANIFEST.json','validation-results.json','hardening-validation.json'}
def source_files():
 # Tracked files plus deliberately prepared new source before its first commit.
 # All known generated runtime caches and temporary publication machinery excluded.
 paths=subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard'],cwd=ROOT).decode().split('\0')
 return sorted({ROOT/p for p in paths if p and p not in EXCLUDED and not p.startswith('.maintenance/') and not p.startswith('.github/workflows/apply-hardening') and '__pycache__' not in Path(p).parts and (ROOT/p).is_file()},key=lambda p:p.relative_to(ROOT).as_posix())
def build():
 files={str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in source_files()}
 raw=json.dumps(files,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
 return {'format':'ssr-document-manifest-v3','hash_algorithm':'SHA-256','excluded':sorted(EXCLUDED),
 'temporary_publication_paths_excluded':['.maintenance/','.github/workflows/apply-hardening*'],
 'content_set_sha256':hashlib.sha256(raw).hexdigest(),'files':files}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args();target=ROOT/'MANIFEST.json';new=build()
 if args.check:
  if not target.exists() or json.loads(target.read_text())!=new:raise SystemExit('Manifest mismatch; regenerate from the actual final tree')
  print(f"Manifest matches {len(new['files'])} source files")
 else:
  target.write_text(json.dumps(new,indent=2,ensure_ascii=False)+'\n');print(f"Manifest generated for {len(new['files'])} source files")
