"""Native isolation policy compiler; pure data, not the production process runner.

The caller must verify roots/executable inventories with no-follow traversal.
Linux output additionally requires the specified Landlock/seccomp launcher. A
bubblewrap argv alone is NOT an isolation acceptance result.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import posixpath
import re


POLICY_VERSION = 'native-isolation-v1'
MAC_SYSTEM_ROOTS = ('/usr/lib', '/System/Library/dyld', '/System/Library/Frameworks')
READ = ('READ_FILE', 'READ_DIR')
SCRATCH = (*READ, 'WRITE_FILE', 'TRUNCATE', 'REMOVE_DIR', 'REMOVE_FILE',
           'MAKE_DIR', 'MAKE_REG', 'MAKE_FIFO', 'MAKE_SYM', 'REFER')
HANDLED_FS = ('EXECUTE', 'WRITE_FILE', 'READ_FILE', 'READ_DIR', 'REMOVE_DIR',
              'REMOVE_FILE', 'MAKE_CHAR', 'MAKE_DIR', 'MAKE_REG', 'MAKE_SOCK',
              'MAKE_FIFO', 'MAKE_BLOCK', 'MAKE_SYM', 'REFER', 'TRUNCATE')
# These are extra restrictions, not a purported complete syscall allowlist.
DENY_SYSCALLS = ('socket', 'connect', 'bind', 'listen', 'accept', 'accept4',
                 'sendto', 'sendmsg', 'sendmmsg', 'recvfrom', 'recvmsg', 'recvmmsg',
                 'ptrace', 'process_vm_readv', 'process_vm_writev', 'mount',
                 'umount2', 'pivot_root', 'mount_setattr', 'fsopen', 'fsconfig',
                 'fsmount', 'move_mount', 'open_tree', 'setns', 'unshare', 'bpf',
                 'userfaultfd', 'io_uring_setup', 'open_by_handle_at',
                 'name_to_handle_at', 'kexec_load', 'init_module', 'finit_module',
                 'delete_module', 'keyctl', 'add_key', 'request_key', 'perf_event_open')


def canonical_path(value: str) -> str:
    if (not isinstance(value, str) or not value.startswith('/') or value == '/'
            or value.startswith('//') or any(p in ('', '.', '..') for p in value.split('/')[1:])
            or any(ord(c) < 32 or ord(c) == 127 for c in value)):
        raise ValueError('expected a non-root canonical absolute path')
    value.encode('utf-8', errors='strict')
    return value


def within(path: str, root: str) -> bool:
    return path == root or path.startswith(root + '/')


@dataclass(frozen=True)
class IsolationInputs:
    platform: str
    purpose: str
    snapshot: str
    resources: tuple[str, ...]
    runtime: str
    control: str
    scratch: str
    executables: tuple[str, ...]

    def __post_init__(self):
        if self.platform not in ('macos', 'linux') or self.purpose not in ('compiler', 'scanner'):
            raise ValueError('unsupported native platform or purpose')
        if not isinstance(self.resources, tuple) or not isinstance(self.executables, tuple):
            raise ValueError('policy inventories must be immutable tuples')
        roots = (self.snapshot, *self.resources, self.runtime, self.control, self.scratch)
        for root in roots:
            canonical_path(root)
        for i, root in enumerate(roots):
            if any(within(root, other) or within(other, root) for other in roots[i + 1:]):
                raise ValueError('input/runtime/control/scratch roots must be disjoint')
            if self.platform == 'macos' and any(within(root, x) or within(x, root) for x in MAC_SYSTEM_ROOTS):
                raise ValueError('job roots must not overlap the fixed OS runtime roots')
        if not self.executables or len(set(self.executables)) != len(self.executables):
            raise ValueError('a nonempty unique trusted executable census is required')
        for executable in self.executables:
            canonical_path(executable)
            if executable == self.runtime or not within(executable, self.runtime):
                raise ValueError('executables must be exact files beneath the trusted runtime')


def seatbelt_policy(inputs: IsolationInputs) -> str:
    """Return explicit SBPL; do not splice reviewed input into policy syntax."""
    if inputs.platform != 'macos':
        raise ValueError('Seatbelt requires macos')
    quote = lambda value: json.dumps(value, ensure_ascii=False)
    readable = (inputs.snapshot, *inputs.resources, inputs.runtime, inputs.control, *MAC_SYSTEM_ROOTS)
    if inputs.purpose == 'scanner':
        readable += (inputs.scratch,)
    lines = ['(version 1)', '(deny default)', '(allow process-fork)',
             # dyld opens the root directory and checks these boot properties
             # before main on the probed OS. Literal / is NOT subpath /.
             '(allow file-read-data (literal "/"))',
             '(allow sysctl-read (sysctl-name "security.mac.lockdown_mode_state") (sysctl-name "kern.bootargs"))']
    # Only ancestry metadata is global enough to reach an approved leaf.
    ancestors = set()
    for root in (*readable, inputs.scratch):
        while root != '/':
            root = posixpath.dirname(root)
            ancestors.add(root)
    lines.append('(allow file-read-metadata ' + ' '.join(f'(literal {quote(p)})' for p in sorted(ancestors)) + ')')
    for root in readable:
        lines.append(f'(allow file-read* (subpath {quote(root)}))')
    for root in (inputs.runtime, *MAC_SYSTEM_ROOTS):
        lines.append(f'(allow file-map-executable (subpath {quote(root)}))')
    lines.append('(allow process-exec ' + ' '.join(f'(literal {quote(p)})' for p in inputs.executables) + ')')
    lines.append('(allow file-read* file-write-data (literal "/dev/null"))')
    lines.append('(allow file-read* (literal "/dev/urandom") (literal "/dev/random"))')
    if inputs.purpose == 'scanner':
        lines.append(f'(allow file-write* (subpath {quote(inputs.scratch)}))')
    # No network*, mach-lookup, ipc-posix*, process-exec wildcard, or home grant.
    return '\n'.join(lines) + '\n'


def replacement_environment(inputs: IsolationInputs) -> dict[str, str]:
    scratch = '/scratch' if inputs.platform == 'linux' else inputs.scratch
    env = {'LANG': 'C', 'LC_ALL': 'C', 'HOME': scratch, 'TMPDIR': scratch,
            'XDG_CACHE_HOME': scratch, 'PYTHONNOUSERSITE': '1',
            'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONHASHSEED': '0',
            'SEMGREP_SEND_METRICS': 'off', 'SEMGREP_ENABLE_VERSION_CHECK': '0'}
    if inputs.platform == 'linux':
        env['LD_LIBRARY_PATH'] = '/runtime/lib'  # Fixed packaged closure, never inherited.
    return env


def linux_policy(inputs: IsolationInputs) -> dict:
    """Exact bwrap mounts plus mandatory launcher policy, never an allow verdict."""
    if inputs.platform != 'linux':
        raise ValueError('bubblewrap requires linux')
    mounts = [(inputs.runtime, '/runtime'), (inputs.snapshot, '/snapshot'),
              (inputs.control, '/control')]
    mounts += [(path, f'/resources/{i}') for i, path in enumerate(inputs.resources)]
    argv = ['/usr/bin/bwrap', '--unshare-user', '--uid', '0', '--gid', '0',
            '--unshare-pid', '--unshare-net', '--unshare-ipc', '--unshare-uts', '--die-with-parent',
            '--new-session', '--cap-drop', 'ALL', '--cap-add', 'CAP_SYS_ADMIN',
            '--cap-add', 'CAP_SETPCAP', '--clearenv', '--tmpfs', '/',
            '--dir', '/resources', '--proc', '/proc', '--dev', '/dev']
    for source, destination in mounts:
        argv.extend(('--ro-bind', source, destination))
    # Linux x86-64 glibc capsule: one fixed interpreter alias, not host /lib.
    argv.extend(('--dir', '/lib64', '--ro-bind', inputs.runtime + '/lib/ld-linux-x86-64.so.2',
                 '/lib64/ld-linux-x86-64.so.2'))
    argv.extend(('--tmpfs', '/scratch', '--chdir', '/snapshot'))
    for key, value in sorted(replacement_environment(inputs).items()):
        argv.extend(('--setenv', key, value))
    argv.extend(('--remount-ro', '/', '--', '/runtime/bin/ssr-isolate',
                 '--policy', '/control/launcher.json'))
    rules = [{'path': dest, 'rights': list(READ)} for _, dest in mounts]
    mapped_executables = ['/runtime' + p[len(inputs.runtime):] for p in inputs.executables]
    for executable in mapped_executables:
        rules.append({'path': executable, 'rights': ['EXECUTE', 'READ_FILE']})
    rules.append({'path': '/lib64/ld-linux-x86-64.so.2', 'rights': ['EXECUTE', 'READ_FILE']})
    rules += [{'path': '/dev/null', 'rights': ['READ_FILE', 'WRITE_FILE', 'TRUNCATE']},
              {'path': '/dev/urandom', 'rights': ['READ_FILE']},
              {'path': '/dev/random', 'rights': ['READ_FILE']},
              {'path': '/proc', 'rights': list(READ)}]
    if inputs.purpose == 'scanner':
        rules.append({'path': '/scratch', 'rights': list(SCRATCH)})
    return {'version': POLICY_VERSION, 'bubblewrap_minimum': '0.12.0', 'argv': argv,
            'noexec_mounts': ['/snapshot', '/control', '/scratch',
                              *[f'/resources/{i}' for i in range(len(inputs.resources))]],
            'mount_attributes': ['NOEXEC', 'NOSUID', 'NODEV'],
            'mount_setattr_recursive': True,
            'bootstrap_capabilities': ['CAP_SYS_ADMIN', 'CAP_SETPCAP'],
            'worker_capabilities': [],
            'seal_order': ['verify_namespaces', 'noexec_mounts', 'drop_all_capabilities',
                           'no_new_privs', 'landlock', 'seccomp', 'worker_exec', 'worker_ready'],
            'landlock_minimum_abi': 3, 'landlock_handled_fs': list(HANDLED_FS),
            'landlock_rules': rules, 'seccomp_default': 'ALLOW',
            'seccomp_denied_errno': 'EPERM', 'seccomp_denied_syscalls': list(DENY_SYSCALLS),
            'seccomp_clone3_errno': 'ENOSYS', 'deny_clone_namespace_flags': True,
            'seccomp_bad_arch': 'KILL_PROCESS', 'no_new_privs': True,
            'compiler_second_seal': inputs.purpose == 'compiler'}


def policy_digest(value: str | dict) -> str:
    raw = value.encode('utf-8') if isinstance(value, str) else json.dumps(
        value, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class NativeLaunch:
    """Typed trusted-launch envelope, never a target-controlled command surface.

    Host executable names are fixed by purpose. A fixed worker reads job data
    only after its readiness handshake; there are no free-form argv selectors.
    """
    inputs: IsolationInputs
    installation_digest: str
    job_digest: str
    host_user_namespace: int | None = None
    host_mount_namespace: int | None = None

    def __post_init__(self):
        if not isinstance(self.inputs, IsolationInputs):
            raise ValueError('typed isolation inputs required')
        for value in (self.installation_digest, self.job_digest):
            if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
                raise ValueError('actual installation and canonical job SHA-256 required')
        worker = f'{self.inputs.runtime}/bin/ssr-{self.inputs.purpose}-worker'
        if worker not in self.inputs.executables:
            raise ValueError('selected fixed worker is absent from trusted executable census')
        namespaces = (self.host_user_namespace, self.host_mount_namespace)
        if self.inputs.platform == 'linux':
            if any(type(value) is not int or value <= 0 for value in namespaces):
                raise ValueError('Linux requires actual parent namespace inode identities')
        elif any(value is not None for value in namespaces):
            raise ValueError('macOS has no Linux namespace identities')


def launch_envelope(request: NativeLaunch) -> dict:
    """Exact /control/launcher.json shape, shared by launcher and fixed worker."""
    inputs = request.inputs
    linux = inputs.platform == 'linux'
    runtime = '/runtime' if linux else inputs.runtime
    control = '/control' if linux else inputs.control
    policy = linux_policy(inputs) if linux else seatbelt_policy(inputs)
    body = {'schema_version': 1, 'policy_version': POLICY_VERSION,
            'platform': inputs.platform, 'purpose': inputs.purpose,
            'installation_digest': request.installation_digest, 'job_digest': request.job_digest,
            'worker_argv': [runtime + '/bin/ssr-' + inputs.purpose + '-worker',
                            '--launch', control + '/launcher.json'],
            'parent_namespaces': {'user': request.host_user_namespace, 'mount': request.host_mount_namespace},
            'environment': replacement_environment(inputs), 'policy': policy,
            'policy_digest': policy_digest(policy)}
    # Digest excludes itself; this is a launch receipt, not a semantic dataset fingerprint.
    envelope = {**body, 'launch_digest': policy_digest(body)}
    if len(json.dumps(envelope, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':')).encode('utf-8')) > 1048576:
        raise ValueError('launcher policy exceeds the 1 MiB control-file limit')
    return envelope


def expected_ready(envelope: dict) -> dict:
    return {'type': 'READY', 'version': 1, 'launch_digest': envelope['launch_digest'],
            'policy_digest': envelope['policy_digest'], 'job_digest': envelope['job_digest'],
            'installation_digest': envelope['installation_digest'], 'purpose': envelope['purpose']}


def validate_ready(envelope: dict, line: bytes) -> None:
    """Read exactly one bounded canonical JSON line, before tool stdout begins."""
    if not isinstance(line, bytes) or len(line) > 2048 or not line.endswith(b'\n'):
        raise ValueError('missing or oversized readiness record')
    expected = json.dumps(expected_ready(envelope), sort_keys=True, ensure_ascii=False,
                          allow_nan=False, separators=(',', ':')).encode('utf-8') + b'\n'
    if line != expected:
        raise ValueError('readiness identity, fields, framing or policy mismatch')
