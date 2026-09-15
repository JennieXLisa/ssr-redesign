"""Fixture/profile compatibility and hash reference checks, not adapter execution."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

from pydantic import ValidationError

VALIDATION = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(VALIDATION))
from reference_language_fixtures import load_fixtures
from reference_profiles import (FingerprintInputs, PROFILE_KEYS, default_file_options,
    extraction_projection, fixture_to_profile, profile_fingerprints,
    resolution_projection, validate_profile_inventory)
from settings import SemanticProfile, Settings, merge_settings

FIXTURE_SHA = 'f0ce4df0e3eb3ce0d8f841cab0104789518ad9660d7367d1f0eec87280e500f9'
# Deterministic reference-test identities, not claims about installed tool digests.
INPUTS = FingerprintInputs(snapshot_id='00000000-0000-4000-8000-000000000001',
    parser_resources_digest='1' * 64, resolver_digest='2' * 64, compiler_inputs_digest='3' * 64)


class FixtureProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = load_fixtures()
        cls.by_id = {case['id']: case for case in cls.cases}

    def mapped(self, name):
        return fixture_to_profile(self.by_id[name])

    def test_all_32_profiles_map_and_json_roundtrip_without_changing_corpus(self):
        self.assertEqual(len(self.cases), 32)
        before = deepcopy(self.cases)
        fields = set()
        for case in self.cases:
            with self.subTest(fixture=case['id']):
                profile = fixture_to_profile(case)
                fields.update(case['profile'])
                self.assertEqual(SemanticProfile.model_validate_json(profile.model_dump_json()), profile)
                self.assertEqual({p.path: p.language for p in profile.file_options},
                                 {s['path']: s['language'] for s in case['sources']})
        self.assertEqual(fields, PROFILE_KEYS)
        self.assertEqual(self.cases, before)
        source = VALIDATION.parent / 'contracts/v1/language-fixtures.json'
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), FIXTURE_SHA)

    def test_explicit_field_mapping_has_no_ignored_values(self):
        for case in self.cases:
            p = fixture_to_profile(case)
            shorthand = case['profile']
            for key, value in shorthand.items():
                with self.subTest(case=case['id'], field=key):
                    if key == 'mode':
                        self.assertTrue(all(o.mode == value and o.strict for o in p.file_options))
                    elif key == 'php_input':
                        self.assertTrue(all(o.input == value for o in p.file_options))
                    elif key == 'package_root':
                        self.assertEqual(p.package_roots, ['' if value == '.' else value])
                    elif key == 'compiler':
                        self.assertEqual(p.compiler_options[0].standard, value)
                    elif key == 'include_root':
                        self.assertEqual(p.compiler_options[0].include_roots, ('' if value == '.' else value,))
                    elif key == 'translation_units':
                        self.assertEqual(list(p.compiler_options[0].translation_units), value)
                    elif key == 'shell_mode':
                        self.assertTrue(all(o.language == value for o in p.file_options))
                    elif key == 'cwd_snapshot':
                        self.assertTrue(all(o.cwd_snapshot == ('' if value == '.' else value) for o in p.file_options))
                    else:
                        self.fail('unaccounted fixture field')

    def test_root_mount_rebases_all_source_and_context_paths(self):
        mount = 'replica-0001/cpp-test-member'
        cpp = fixture_to_profile(self.by_id['cpp-test-member'], root=mount)
        self.assertEqual(cpp.compiler_options[0].include_roots, (mount,))
        self.assertEqual(cpp.compiler_options[0].translation_units,
                         (mount + '/Test.cpp', mount + '/main.cpp'))
        python = fixture_to_profile(self.by_id['python-captured-import'], root='examples/python')
        self.assertEqual(python.package_roots, ['examples/python'])
        shell = fixture_to_profile(self.by_id['bash-captured-source'], root='examples/bash')
        self.assertTrue(all(o.cwd_snapshot == 'examples/bash' for o in shell.file_options))

    def test_default_dialects_modes_and_translation_units_are_explicit(self):
        self.assertEqual(self.mapped('c-prototype-pointer').compiler_options[0].translation_units, ('unit.c',))
        self.assertEqual(self.mapped('cpp-test-member').compiler_options[0].translation_units, ('Test.cpp', 'main.cpp'))
        for suffix, language, mode in [('.mjs', 'javascript', 'module'), ('.cjs', 'javascript', 'commonjs'),
                ('.mts', 'typescript', 'module'), ('.cts', 'typescript', 'commonjs'),
                ('.js', 'javascript', 'script'), ('.tsx', 'tsx', 'script')]:
            option = default_file_options('file' + suffix, language)
            self.assertEqual(option['mode'], mode)
            self.assertEqual(option['strict'], mode == 'module')
        for lang in ('bash', 'zsh'):
            option = self.mapped(lang + '-parse-error').file_options[0]
            self.assertEqual(option.language, lang)
            self.assertIsNone(option.cwd_snapshot)
        self.assertEqual(self.mapped('php-parse-error').file_options[0].input, 'mixed')

    def test_unknown_wrong_dialect_and_wrong_type_fixture_fields_rejected(self):
        mutations = [
            ('javascript-tdz', {'mode': 'module', 'typo': True}),
            ('javascript-tdz', {'mode': None}),
            ('javascript-tdz', {'mode': 'auto'}),
            ('javascript-tdz', {'php_input': 'mixed'}),
            ('python-captured-import', {'package_root': 1}),
            ('php-only-namespace-alias', {'php_input': 'auto'}),
            ('bash-substitutions', {'shell_mode': 'zsh', 'cwd_snapshot': '.'}),
            ('cpp-test-member', {'compiler': 'c17', 'translation_units': ['main.cpp']}),
            ('cpp-test-member', {'translation_units': ['main.cpp']}),
            ('cpp-test-member', {'compiler': 'c++20', 'translation_units': 'main.cpp'}),
            ('cpp-test-member', {'compiler': 'c++20', 'translation_units': []}),
            ('cpp-test-member', {'compiler': 'c++20', 'translation_units': ['not-captured.cpp']}),
        ]
        for name, values in mutations:
            case = deepcopy(self.by_id[name])
            case['profile'] = values
            with self.subTest(name=name, values=values), self.assertRaises(ValueError):
                fixture_to_profile(case)

    def test_production_options_reject_unknown_or_conflicting_combinations(self):
        cpp = self.mapped('cpp-test-member').model_dump(mode='json')
        js = {'path': 'x.js', 'language': 'javascript', 'mode': 'module', 'strict': False}
        bad = [
            {'mode': 'module'}, {'file_options': [{'path': 'x.py', 'language': 'python', 'mode': 'module'}]},
            {'file_options': [js]}, {'file_options': [{**js, 'mode': 'commonjs', 'strict': 'yes'}]},
            {'file_options': [{'path': 'x.php', 'language': 'php', 'input': 'auto'}]},
            {'file_options': [{'path': 'x.sh', 'language': 'bash', 'shell_mode': 'zsh'}]},
            {'file_options': [{'path': 'x.py', 'language': 'python'}] * 2},
            {**cpp, 'compilation_database': 'compile_commands.json'},
            {**cpp, 'compiler_options': cpp['compiler_options'] * 2},
            {**cpp, 'compiler_options': [{**cpp['compiler_options'][0], 'standard': 'c17'}]},
            {**cpp, 'file_options': [{'path': 'main.cpp', 'language': 'c'}]},
            {**cpp, 'compiler_options': [{**cpp['compiler_options'][0], 'include_roots': 'include'}]},
        ]
        for values in bad:
            with self.subTest(values=values), self.assertRaises(ValidationError):
                SemanticProfile.model_validate(values)

    def test_root_file_and_percent_decoded_boundary_validation(self):
        for path in ('.', '../escape', '/host', 'src//child', 'src/', '%2e%2e/escape',
                     '%2Fhost', 'src/%00', 'C:/host', 'src\\child', 'bad%xy'):
            with self.subTest(path=path), self.assertRaises(ValidationError):
                SemanticProfile.model_validate({'package_roots': [path]})
        for key in ('compilation_database',):
            with self.assertRaises(ValidationError):
                SemanticProfile.model_validate({key: ''})
        self.assertEqual(SemanticProfile.model_validate({'package_roots': ['']}).package_roots, [''])
        with self.assertRaises(ValueError):
            fixture_to_profile(self.by_id['cpp-test-member'], root='../outside')

    def test_inventory_owner_checks_are_separate_from_shape_validation(self):
        profile = SemanticProfile.model_validate({'file_options': [
            {'path': 'x.sh', 'language': 'zsh', 'cwd_snapshot': 'missing'}]})
        with self.assertRaisesRegex(ValueError, 'directory'):
            validate_profile_inventory(profile, {'x.sh': 'zsh'})
        with self.assertRaisesRegex(ValueError, 'dialect'):
            validate_profile_inventory(profile, {'x.sh': 'bash'})
        with self.assertRaisesRegex(ValueError, 'missing'):
            validate_profile_inventory(profile, {})
        profile = SemanticProfile.model_validate({'compilation_database': 'compile_commands.json'})
        with self.assertRaisesRegex(ValueError, 'database'):
            validate_profile_inventory(profile, {})
        validate_profile_inventory(profile, {'compile_commands.json': None})
        aliases = SemanticProfile.model_validate({'module_aliases': {'single': 'lib.js', 'tree': 'pkg'}})
        validate_profile_inventory(aliases, {'lib.js': 'javascript', 'pkg/index.js': 'javascript'})
        with self.assertRaisesRegex(ValueError, 'alias'):
            validate_profile_inventory(aliases, {'pkg/index.js': 'javascript'})

    def test_new_option_values_and_collections_are_frozen(self):
        profile = self.mapped('javascript-tdz')
        with self.assertRaises(ValidationError):
            profile.file_options[0].mode = 'commonjs'
        with self.assertRaises(AttributeError):
            profile.file_options.append(profile.file_options[0])
        compiler = self.mapped('cpp-test-member').compiler_options[0]
        with self.assertRaises(AttributeError):
            compiler.translation_units.append('extra.cpp')
        source = profile.model_dump(mode='json')
        clone = SemanticProfile.model_validate(source)
        source['file_options'][0]['mode'] = 'commonjs'
        self.assertEqual(clone.file_options[0].mode, 'module')

    def test_changed_extraction_semantics_invalidate_both_datasets(self):
        for name, field, value in [('javascript-tdz', 'mode', 'commonjs'),
                ('jsx-expression-owners', 'language', 'javascript'),
                ('php-mixed-closures', 'input', 'php-only'),
                ('bash-substitutions', 'language', 'zsh')]:
            before = self.mapped(name)
            data = before.model_dump(mode='json')
            data['file_options'][0][field] = value
            after = SemanticProfile.model_validate(data)
            with self.subTest(name=name):
                a, b = profile_fingerprints(before, INPUTS), profile_fingerprints(after, INPUTS)
                self.assertNotEqual(a.extraction, b.extraction)
                self.assertNotEqual(a.resolution, b.resolution)

    def test_resolution_only_changes_reuse_extraction_but_change_resolution(self):
        for name, change in [
            ('python-captured-import', lambda d: d.update(package_roots=['src'])),
            ('python-captured-import', lambda d: d.update(module_aliases={'pkg': 'src'})),
            ('bash-substitutions', lambda d: d['file_options'][0].update(cwd_snapshot=None)),
            ('cpp-test-member', lambda d: d['compiler_options'][0].update(standard='c++17')),
            ('cpp-test-member', lambda d: d['compiler_options'][0].update(include_roots=['include', ''])),
            ('cpp-test-member', lambda d: d['compiler_options'][0]['translation_units'].reverse()),
        ]:
            before = self.mapped(name)
            data = before.model_dump(mode='json')
            change(data)
            after = SemanticProfile.model_validate(data)
            with self.subTest(name=name, data=data):
                a, b = profile_fingerprints(before, INPUTS), profile_fingerprints(after, INPUTS)
                self.assertEqual(a.extraction, b.extraction)
                self.assertNotEqual(a.resolution, b.resolution)

    def test_resource_digests_and_operational_exclusion(self):
        profile = self.mapped('cpp-test-member')
        base = profile_fingerprints(profile, INPUTS)
        for field in ('parser_resources_digest', 'resolver_digest', 'compiler_inputs_digest'):
            changed = FingerprintInputs.model_validate({**INPUTS.model_dump(), field: '4' * 64})
            result = profile_fingerprints(profile, changed)
            self.assertNotEqual(base.resolution, result.resolution)
            self.assertEqual(base.extraction == result.extraction, field != 'parser_resources_digest')
        operational = merge_settings({'workers': {'heavy_slots': 8},
                                      'navigation': {'query_timeout_seconds': 60}})
        self.assertNotEqual(operational, Settings())
        self.assertEqual(base, profile_fingerprints(profile, INPUTS))
        with self.assertRaises(TypeError):
            profile_fingerprints(profile, INPUTS, settings=operational)
        with self.assertRaises(ValidationError):
            SemanticProfile.model_validate({'workers': {'heavy_slots': 8}})

    def test_exact_path_option_order_is_not_scheduling_identity(self):
        before = self.mapped('javascript-export-alias')
        data = before.model_dump(mode='json')
        data['file_options'].reverse()
        after = SemanticProfile.model_validate(data)
        self.assertEqual(extraction_projection(before), extraction_projection(after))
        self.assertEqual(resolution_projection(before), resolution_projection(after))
        self.assertEqual(profile_fingerprints(before, INPUTS), profile_fingerprints(after, INPUTS))

    def test_cli_emits_the_same_typed_production_profile(self):
        command = [sys.executable, '-B', str(VALIDATION / 'reference_profiles.py'),
                   '--fixture', 'php-only-namespace-alias']
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        self.assertEqual(json.loads(result.stdout), self.mapped('php-only-namespace-alias').model_dump(mode='json'))
        result = subprocess.run([*command, '--root', '../outside'], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
