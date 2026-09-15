from copy import deepcopy
from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'validation'))
from reference_manifest import extraction_manifest, publication_diagnostics
from records import ExtractionBundle, semantic_digest


class ManifestProjectionTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'contracts/v1/extraction-fixtures.json').read_text())['bundle']

    def test_stale_and_general_diagnostics_do_not_change_active_manifest(self):
        current = dict(code='OWNERSHIP_LIMITATION', severity='limitation', range=None, message='Current limitation')
        stale = {**current, 'message': 'Abandoned attempt limitation'}
        rows = [dict(publication_id='old', code=stale['code'], detail=stale),
                dict(publication_id=None, code='PARSE_ERROR', detail=dict(code='PARSE_ERROR', severity='error', range=None, message='Earlier failure')),
                dict(publication_id='active', code=current['code'], detail=current)]
        self.data['diagnostics'] = [current]
        expected = extraction_manifest(ExtractionBundle.model_validate(self.data))
        reconstructed = deepcopy(self.data)
        reconstructed['diagnostics'] = publication_diagnostics(rows, 'active')
        actual = extraction_manifest(ExtractionBundle.model_validate(reconstructed))
        self.assertEqual(actual, expected)
        self.assertEqual(semantic_digest(actual), semantic_digest(expected))
        reconstructed['diagnostics'].append(stale)
        wrong = extraction_manifest(ExtractionBundle.model_validate(reconstructed))
        self.assertNotEqual(semantic_digest(wrong), semantic_digest(expected))
        self.assertEqual(len(wrong['records']), len(expected['records']) + 1)

    def test_collection_order_does_not_affect_manifest(self):
        first = extraction_manifest(ExtractionBundle.model_validate(self.data))
        self.data['scopes'].reverse()
        self.data['declarations'].reverse()
        self.assertEqual(extraction_manifest(ExtractionBundle.model_validate(self.data)), first)

    def test_mismatched_diagnostic_code_is_rejected(self):
        value = dict(code='OWNERSHIP_LIMITATION', severity='limitation', range=None, message='Current')
        with self.assertRaises(ValueError):
            publication_diagnostics([dict(publication_id='active', code='OTHER', detail=value)], 'active')


if __name__ == '__main__':
    unittest.main()
