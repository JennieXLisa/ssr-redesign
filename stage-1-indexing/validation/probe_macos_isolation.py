"""Opt-in Seatbelt boundary probe using only owned fixtures and trusted C code.

This is not Semgrep/libclang or a production-runner acceptance test. It compiles
only validation/native/isolation_probe.c into a disposable private directory.
"""
from __future__ import annotations

import argparse
import errno
import hashlib
import json
from pathlib import Path
import platform
import shutil
import socket
import subprocess
import tempfile

from reference_isolation import IsolationInputs, policy_digest, replacement_environment, seatbelt_policy


HERE = Path(__file__).resolve().parent


def run_probe() -> dict:
    if platform.system() != 'Darwin':
        raise RuntimeError('NOT RUN: native macOS is required')
    sandbox = Path('/usr/bin/sandbox-exec')
    compiler = Path('/usr/bin/clang')
    if not sandbox.is_file() or not compiler.is_file():
        raise RuntimeError('NOT RUN: sandbox-exec and installed Apple clang are required')
    source = HERE / 'native/isolation_probe.c'
    records = []
    digests = {}
    with tempfile.TemporaryDirectory(prefix='ssr-native-probe-') as directory:
        root = Path(directory).resolve()  # Resolves our own temporary root, not target paths.
        for name in ['runtime', 'source', 'resources', 'control', 'scratch', 'outside']:
            (root / name).mkdir()
        executable = root / 'runtime/probe'
        built = subprocess.run([str(compiler), '-Wall', '-Wextra', '-Werror', str(source), '-o', str(executable)],
                               env={'PATH': '/usr/bin:/bin', 'LANG': 'C', 'HOME': str(root)},
                               capture_output=True, timeout=60, check=False, start_new_session=True)
        if built.returncode:
            raise RuntimeError('trusted probe compilation failed: ' + built.stderr.decode('utf-8', 'replace')[:1000])
        for location in ['source/allowed', 'resources/allowed', 'control/allowed', 'outside/secret']:
            (root / location).write_bytes(b'harness fixture only\n')
        (root / 'source/escape').symlink_to(root / 'outside/secret')
        shutil.copyfile(executable, root / 'source/not-executable')
        (root / 'source/not-executable').chmod(0o700)
        with socket.socket() as tcp, socket.socket(socket.AF_UNIX) as unix:
            tcp.bind(('127.0.0.1', 0)); tcp.listen(8)
            unix_path = str(root / 'outside/sock')
            unix.bind(unix_path); unix.listen(8)
            port = str(tcp.getsockname()[1])
            for purpose in ['compiler', 'scanner']:
                inputs = IsolationInputs('macos', purpose, str(root / 'source'), (str(root / 'resources'),),
                                         str(root / 'runtime'), str(root / 'control'), str(root / 'scratch'),
                                         (str(executable),))
                policy = seatbelt_policy(inputs)
                path = root / 'control/policy.sb'; path.write_text(policy)
                digests[purpose] = policy_digest(policy)
                cases = [('read', 'source/allowed', True), ('read', 'resources/allowed', True),
                         ('read', 'control/allowed', True), ('read', 'outside/secret', False),
                         ('directory', 'outside', False), ('read', 'source/escape', False),
                         ('write', 'source/must-not-exist', False), ('write', 'runtime/must-not-exist', False),
                         ('write', 'outside/must-not-exist', False), ('write', 'scratch/output', purpose == 'scanner'),
                         ('exec', 'source/not-executable', False), ('map_exec', 'source/not-executable', False),
                         ('child_read', 'outside/secret', False), ('tcp4', port, False),
                         ('udp4', port, False), ('tcp6', port, False), ('unix', 'outside/sock', False)]
                for mode, value, allowed in cases:
                    operand = value if mode in ('tcp4', 'udp4', 'tcp6') else str(root / value)
                    command = [str(sandbox), '-f', str(path), str(executable), mode, operand]
                    completed = subprocess.run(command, cwd=root / 'source',
                                               env=replacement_environment(inputs), capture_output=True,
                                               timeout=10, check=False, start_new_session=True, close_fds=True)
                    try:
                        observed = json.loads(completed.stdout)
                        passed = completed.returncode == 0 and observed['allowed'] is allowed
                        if not allowed:
                            passed = passed and observed['errno'] in (errno.EACCES, errno.EPERM)
                    except (ValueError, KeyError):
                        observed = {'returncode': completed.returncode,
                                    'stderr': completed.stderr.decode('utf-8', 'replace')[:600]}
                        passed = False
                    records.append({'purpose': purpose, 'operation': mode, 'fixture': value if not value.isdigit() else 'owned-loopback-port',
                                    'expected_allowed': allowed, 'result': 'PASS' if passed else 'FAIL', 'observed': observed})
    return {'scope': 'native Seatbelt policy with trusted harness probe only; no installed tool/production runner evidence',
            'platform': platform.platform(), 'policy_version': 'native-isolation-v1',
            'sandbox_executable_sha256': hashlib.sha256(sandbox.read_bytes()).hexdigest(),
            'probe_source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'physical_policy_digests': digests, 'checks': records,
            'passed': sum(x['result'] == 'PASS' for x in records),
            'failed': sum(x['result'] == 'FAIL' for x in records), 'linux': 'NOT RUN'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true', help='Compile and execute the owned native probe')
    args = parser.parse_args()
    if not args.run:
        parser.error('explicit --run is required; core checks do not invoke this probe')
    try:
        report = run_probe()
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        parser.exit(2, f'{exc}\n')
    print(json.dumps(report, indent=2))
    raise SystemExit(1 if report['failed'] else 0)
