"""Policy construction is not proof of native enforcement; see native probe."""
import dataclasses
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reference_isolation import (IsolationInputs, NativeLaunch, expected_ready, launch_envelope,
    linux_policy, policy_digest, replacement_environment, seatbelt_policy, validate_ready)


def inputs(platform='macos', purpose='compiler'):
    return IsolationInputs(platform, purpose, '/owned/source', ('/owned/sdk',),
                           '/owned/runtime', '/owned/control', '/owned/scratch',
                           ('/owned/runtime/bin/worker', '/owned/runtime/bin/semgrep-core'))


class NativePolicyTests(unittest.TestCase):
    def test_macos_default_deny_and_data_not_executable(self):
        policy = seatbelt_policy(inputs())
        self.assertIn('(deny default)', policy)
        self.assertNotIn('(allow network', policy)
        self.assertNotIn('(allow mach-lookup', policy)
        self.assertNotIn('(allow file-write*', policy)
        self.assertNotIn('file-map-executable (subpath "/owned/source")', policy)
        self.assertIn('(allow process-exec (literal "/owned/runtime/bin/worker")', policy)

    def test_scanner_scratch_only_writable_tree(self):
        policy = seatbelt_policy(inputs(purpose='scanner'))
        self.assertEqual(policy.count('(allow file-write*'), 1)
        self.assertIn('(allow file-write* (subpath "/owned/scratch"))', policy)

    def test_overlapping_or_noncanonical_roots_rejected(self):
        for field, value in [('snapshot', '/'), ('snapshot', '/owned/runtime/src'),
                             ('runtime', '/owned'), ('control', '/owned/sdk'),
                             ('scratch', '/owned/../tmp'), ('snapshot', '/usr/lib/target'),
                             ('snapshot', '/owned/line\nbreak')]:
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                dataclasses.replace(inputs(), **{field: value})

    def test_untrusted_executables_rejected(self):
        for files in [(), ('/owned/source/tool',), ('/bin/sh',), ('/owned/runtime',),
                      ('/owned/runtime/bin/worker', '/owned/runtime/bin/worker')]:
            with self.subTest(files=files), self.assertRaises(ValueError):
                dataclasses.replace(inputs(), executables=files)

    def test_policy_quotes_cannot_inject_allow_rule(self):
        value = dataclasses.replace(inputs(), snapshot='/owned/x") (allow network*) ("')
        policy = seatbelt_policy(value)
        self.assertIn('x\\") (allow network*) (\\"', policy)
        self.assertEqual(policy.count('\n(allow network'), 0)

    def test_linux_is_mandatory_namespaces_and_not_host_bind(self):
        policy = linux_policy(inputs('linux'))
        args = policy['argv']
        self.assertIn('--unshare-user', args)
        self.assertIn('--unshare-net', args)
        self.assertTrue(policy['deny_clone_namespace_flags'])
        self.assertIn('unshare', policy['seccomp_denied_syscalls'])
        self.assertNotIn('--unshare-user-try', args)
        self.assertNotIn('--not-a-security-boundary', args)
        self.assertNotIn('--share-net', args)
        self.assertEqual(policy['bubblewrap_minimum'], '0.12.0')
        self.assertEqual(args[-4:], ['--', '/runtime/bin/ssr-isolate', '--policy', '/control/launcher.json'])

    def test_linux_landlock_and_seccomp_are_required(self):
        policy = linux_policy(inputs('linux'))
        self.assertEqual(policy['landlock_minimum_abi'], 3)
        self.assertIn('TRUNCATE', policy['landlock_handled_fs'])
        self.assertTrue(policy['compiler_second_seal'])
        self.assertTrue(policy['no_new_privs'])
        self.assertIn('socket', policy['seccomp_denied_syscalls'])
        for rule in policy['landlock_rules']:
            if rule['path'] in ['/snapshot', '/control', '/resources/0']:
                self.assertEqual(rule['rights'], ['READ_FILE', 'READ_DIR'])
        self.assertFalse(any(r['path'] == '/scratch' for r in policy['landlock_rules']))

    def test_scanner_can_write_but_not_execute_scratch(self):
        policy = linux_policy(inputs('linux', 'scanner'))
        scratch = next(r for r in policy['landlock_rules'] if r['path'] == '/scratch')
        self.assertIn('WRITE_FILE', scratch['rights'])
        self.assertNotIn('EXECUTE', scratch['rights'])
        self.assertNotIn('MAKE_SOCK', scratch['rights'])
        self.assertFalse(policy['compiler_second_seal'])

    def test_environment_has_no_ambient_path_or_credentials(self):
        env = replacement_environment(inputs('linux'))
        self.assertEqual(env['HOME'], '/scratch')
        self.assertNotIn('PATH', env)
        self.assertNotIn('PYTHONPATH', env)
        self.assertNotIn('SSR_DATABASE_URL', env)
        self.assertNotIn('SSH_AUTH_SOCK', env)
        self.assertNotIn('DYLD_LIBRARY_PATH', env)

    def test_platform_mismatch_and_digest(self):
        with self.assertRaises(ValueError):
            seatbelt_policy(inputs('linux'))
        with self.assertRaises(ValueError):
            linux_policy(inputs())
        self.assertEqual(policy_digest(seatbelt_policy(inputs())), policy_digest(seatbelt_policy(inputs())))
        self.assertNotEqual(policy_digest(seatbelt_policy(inputs())), policy_digest(seatbelt_policy(inputs(purpose='scanner'))))

    def test_noexec_precedes_capability_drop_and_worker_execution(self):
        for purpose in ('compiler', 'scanner'):
            policy = linux_policy(inputs('linux', purpose))
            self.assertEqual(policy['noexec_mounts'], ['/snapshot', '/control', '/scratch', '/resources/0'])
            self.assertEqual(policy['mount_attributes'], ['NOEXEC', 'NOSUID', 'NODEV'])
            self.assertTrue(policy['mount_setattr_recursive'])
            self.assertEqual(policy['worker_capabilities'], [])
            self.assertEqual(policy['seal_order'][:3], ['verify_namespaces', 'noexec_mounts', 'drop_all_capabilities'])
            self.assertLess(policy['seal_order'].index('seccomp'), policy['seal_order'].index('worker_exec'))
            self.assertIn('mount_setattr', policy['seccomp_denied_syscalls'])

    def test_linux_fixed_loader_is_not_a_host_directory_grant(self):
        policy = linux_policy(inputs('linux'))
        args = policy['argv']
        self.assertIn('/lib64/ld-linux-x86-64.so.2', args)
        self.assertIn('/owned/runtime/lib/ld-linux-x86-64.so.2', args)
        self.assertEqual(replacement_environment(inputs('linux'))['LD_LIBRARY_PATH'], '/runtime/lib')

    def launch(self, platform='linux', purpose='compiler'):
        selected = dataclasses.replace(inputs(platform, purpose),
            executables=(f'/owned/runtime/bin/ssr-{purpose}-worker',))
        return NativeLaunch(selected, 'a' * 64, 'b' * 64,
                            101 if platform == 'linux' else None,
                            102 if platform == 'linux' else None)

    def test_complete_launch_envelope_and_ready_binding(self):
        for platform in ('linux', 'macos'):
            request = self.launch(platform)
            envelope = launch_envelope(request)
            self.assertEqual(envelope['purpose'], 'compiler')
            self.assertEqual(envelope['installation_digest'], 'a' * 64)
            self.assertEqual(envelope['worker_argv'][0],
                ('/runtime' if platform == 'linux' else '/owned/runtime') + '/bin/ssr-compiler-worker')
            self.assertEqual(envelope['launch_digest'], policy_digest({k: v for k, v in envelope.items() if k != 'launch_digest'}))
            ready = json.dumps(expected_ready(envelope), sort_keys=True, separators=(',', ':')).encode() + b'\n'
            validate_ready(envelope, ready)
            with self.assertRaises(ValueError):
                validate_ready(envelope, ready.replace(b'"compiler"', b'"scanner"'))
            with self.assertRaises(ValueError):
                validate_ready(envelope, ready + b'tool output')

    def test_incomplete_or_untrusted_launch_rejected(self):
        for change in ({'installation_digest': 'x'}, {'job_digest': ''},
                       {'host_user_namespace': True}, {'host_mount_namespace': None},
                       {'inputs': inputs('linux')}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                dataclasses.replace(self.launch(), **change)
        with self.assertRaises(ValueError):
            dataclasses.replace(self.launch('macos'), host_user_namespace=101)

    def test_changed_job_or_installation_cannot_reuse_ready(self):
        first = launch_envelope(self.launch())
        second = launch_envelope(dataclasses.replace(self.launch(), job_digest='c' * 64))
        self.assertNotEqual(first['launch_digest'], second['launch_digest'])
        with self.assertRaises(ValueError):
            validate_ready(second, json.dumps(expected_ready(first), sort_keys=True, separators=(',', ':')).encode() + b'\n')


if __name__ == '__main__':
    unittest.main()
