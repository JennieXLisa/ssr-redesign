from pathlib import Path
import sys
import tomllib
import unittest
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'contracts/v1'))
from settings import Settings, SemanticProfile, merge_settings


class SettingsTests(unittest.TestCase):
    def test_shipped_defaults_match_the_typed_schema_exactly(self):
        defaults = tomllib.loads((ROOT / 'contracts/v1/defaults.toml').read_text())
        self.assertEqual(Settings.model_validate(defaults).model_dump(mode='json'), defaults)
        self.assertEqual(Settings().model_dump(mode='json'), defaults)

    def test_precedence_and_no_mutation(self):
        installation = {'workers': {'heavy_slots': 8}, 'navigation': {'page_default': 10}}
        project = {'navigation': {'page_default': 20}}
        operation = {'navigation': {'page_default': 30}}
        actual = merge_settings(installation, project, operation)
        self.assertEqual(actual.navigation.page_default, 30)
        self.assertEqual(actual.workers.heavy_slots, 8)
        self.assertEqual(installation['navigation']['page_default'], 10)

    def test_cross_field_and_type_errors(self):
        for patch in [{'scanner_slots': 5}, {'heartbeat_seconds': 120},
                      {'memory_resume_available_bytes': 1}, {'retry_delays_seconds': [1]},
                      {'heavy_slots': True}, {'heavy_slots': '4'}]:
            with self.subTest(patch=patch), self.assertRaises(ValidationError):
                merge_settings({'workers': patch})

    def test_unknown_keys_are_rejected_even_in_lower_layers(self):
        for patch in [{'database_url': 'not-a-config-secret'}, {'workers': {'typo': 1}},
                      {'navigation': {'error_response_bytes': 65536}}]:
            with self.assertRaises(ValueError):
                merge_settings(patch, {})

    def test_semantic_profile_defaults_and_validation(self):
        self.assertEqual(SemanticProfile().package_roots, [])
        good = SemanticProfile.model_validate({'language_overrides': [{'path_glob': '*.h', 'language': 'cpp'}],
            'encoding_overrides': [{'path_glob': '*.py', 'codec': 'latin-1'}],
            'package_roots': ['src'], 'module_aliases': {'local': 'src'},
            'compilation_database': 'build/compile_commands.json'})
        self.assertEqual(good.language_overrides[0].language, 'cpp')
        for bad in [{'package_roots': ['../src']}, {'module_aliases': {'x': '/host'}},
                    {'compilation_database': ''}, {'package_roots': ['src', 'src']},
                    {'schema_version': True}, {'execute_build': True}]:
            with self.subTest(bad=bad), self.assertRaises(ValidationError):
                SemanticProfile.model_validate(bad)


if __name__ == '__main__':
    unittest.main()
