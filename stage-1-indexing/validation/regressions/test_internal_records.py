from copy import deepcopy
from pathlib import Path
import json
import sys
import unittest
from pydantic import ValidationError
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'contracts/v1'))
from models import ByteRange
from records import ExtractionBundle, SourceUnit, canonical_bytes, semantic_digest, source_record_id, validate_bundle_source

FIXTURE = json.loads((ROOT / 'contracts/v1/extraction-fixtures.json').read_text())


class InternalRecordTests(unittest.TestCase):
    def test_valid_fixture_and_exact_original_slices(self):
        bundle = ExtractionBundle.model_validate(FIXTURE['bundle'])
        source = FIXTURE['source'].encode('utf-8')
        self.assertEqual(bundle.byte_length, len(source))
        def excerpt(span):
            return source[span.start_byte:span.end_byte].decode('utf-8')
        occurrence = bundle.occurrences[0]
        self.assertEqual(excerpt(occurrence.name_range), 'outer')
        self.assertEqual(excerpt(occurrence.body_range), 'return missing(x)')
        self.assertEqual(excerpt(occurrence.signature_range), bundle.symbols[0].signature)
        self.assertEqual(excerpt(occurrence.parameters[0].default_range), '1')
        self.assertEqual(excerpt(occurrence.parameters[0].type.evidence[0]), 'int')
        self.assertEqual(excerpt(bundle.references[0].range), bundle.references[0].spelling)
        self.assertEqual(excerpt(bundle.references[0].arguments[0].range), 'x')

    def test_invalid_fixture_mutations(self):
        for mutation in FIXTURE['invalid_mutations']:
            with self.subTest(reason=mutation['reason']):
                value = deepcopy(FIXTURE['bundle'])
                target = value
                for key in mutation['path'][:-1]:
                    target = target[key]
                target[mutation['path'][-1]] = mutation['value']
                with self.assertRaises(ValidationError):
                    ExtractionBundle.model_validate(value)

    def test_empty_success_and_failed_parse_are_distinct(self):
        value = deepcopy(FIXTURE['bundle'])
        for key in ['symbols', 'occurrences', 'references', 'declarations', 'imports']:
            value[key] = []
        value['scopes'] = value['scopes'][:1]
        ExtractionBundle.model_validate(value)
        value['status'] = 'FAILED'
        value['scopes'] = []
        value['diagnostics'] = [dict(code='PARSE_ERROR', severity='error', range=None, message='Syntax error')]
        ExtractionBundle.model_validate(value)
        with self.assertRaises(ValidationError):
            ExtractionBundle.model_validate({**value, 'status': 'SUCCEEDED'})

    def source_unit(self, text, codec, bom):
        original = bom + text.encode(codec)
        boundaries = [dict(parser_byte=0, original_byte=len(bom))]
        p, o = 0, len(bom)
        for scalar in text:
            p += len(scalar.encode('utf-8'))
            o += len(scalar.encode(codec))
            boundaries.append(dict(parser_byte=p, original_byte=o))
        base = FIXTURE['bundle']
        return dict(snapshot_id=base['snapshot_id'], extraction_id=base['extraction_id'],
                    file_id=base['file_id'], path='fixture.py', language='python',
                    parser_profile_digest=base['parser_profile_digest'], codec=codec,
                    bom_bytes=len(bom), original_bytes=original,
                    parser_utf8=text.encode('utf-8'), boundaries=boundaries)

    def test_exact_codec_maps(self):
        cases = [('猫🙂\r\nx', 'utf-8', b''), ('猫🙂\r\nx', 'utf-8', b'\xef\xbb\xbf'),
                 ('猫🙂\r\nx', 'utf-16-le', b'\xff\xfe'), ('猫🙂\r\nx', 'utf-16-be', b'\xfe\xff'),
                 ('é\r\nx', 'latin-1', b''), ('€\r\nx', 'cp1252', b''), ('', 'utf-8', b'')]
        for text, codec, bom in cases:
            with self.subTest(codec=codec, bom=bom):
                data = self.source_unit(text, codec, bom)
                SourceUnit.model_validate(data)
                if text:
                    wrong = deepcopy(data)
                    wrong['boundaries'][-1]['original_byte'] -= 1
                    with self.assertRaises(ValidationError):
                        SourceUnit.model_validate(wrong)
                    with self.assertRaises(ValidationError):
                        SourceUnit.model_validate({**data, 'parser_utf8': text.replace('\r\n', '\n').encode()})

    def test_duplicate_ids_and_unknown_parent_rejected(self):
        value = deepcopy(FIXTURE['bundle'])
        value['symbols'].append(deepcopy(value['symbols'][0]))
        with self.assertRaises(ValidationError):
            ExtractionBundle.model_validate(value)
        value = deepcopy(FIXTURE['bundle'])
        value['scopes'][1]['parent_scope_id'] = '00000000-0000-0000-0000-000000000099'
        with self.assertRaises(ValidationError):
            ExtractionBundle.model_validate(value)

    def test_publication_source_identity_and_coordinates(self):
        source = SourceUnit.model_validate(self.source_unit(FIXTURE['source'], 'utf-8', b''))
        bundle = ExtractionBundle.model_validate(FIXTURE['bundle'])
        validate_bundle_source(bundle, source)
        for path, replacement in [(['references', 0, 'spelling'], 'fabricated(x)'),
                                  (['references', 0, 'range', 'start_column'], 11),
                                  (['snapshot_id'], '00000000-0000-0000-0000-000000000099')]:
            data = deepcopy(FIXTURE['bundle'])
            target = data
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = replacement
            with self.assertRaises(ValueError):
                validate_bundle_source(ExtractionBundle.model_validate(data), source)

    def test_scope_and_declaration_ownership_cannot_be_corrupted(self):
        for fault in ['function_owns_module', 'nested_module', 'self_declared_body', 'body_mismatch']:
            data = deepcopy(FIXTURE['bundle'])
            if fault == 'function_owns_module':
                data['scopes'][0]['owner_symbol_id'] = data['symbols'][0]['symbol_id']
            elif fault == 'nested_module':
                data['scopes'][1]['kind'] = 'module'
            elif fault == 'self_declared_body':
                data['symbols'][0]['owner_scope_id'] = data['scopes'][1]['scope_id']
            else:
                data['scopes'][1]['range']['start_byte'] += 1
            with self.subTest(fault=fault), self.assertRaises(ValidationError):
                ExtractionBundle.model_validate(data)

    def test_canonical_hash_and_identity_inputs(self):
        self.assertEqual(canonical_bytes({'z': None, 'a': ['猫', 1]}), b'{"a":["\xe7\x8c\xab",1],"z":null}')
        self.assertEqual(semantic_digest({'a': 1, 'b': 2}), '43258cff783fe7036d8a43033f830adfc60ec037382473548ac742b888292777')
        with self.assertRaises(ValueError):
            canonical_bytes({'bad': float('nan')})
        b = FIXTURE['bundle']
        span = ByteRange(start_byte=1, end_byte=2)
        a = source_record_id(b['extraction_id'], b['file_id'], 'reference', span, None, 0)
        self.assertEqual(a, source_record_id(b['extraction_id'], b['file_id'], 'reference', span, None, 0))
        self.assertNotEqual(a, source_record_id(b['extraction_id'], b['file_id'], 'symbol', span, None, 0))
        self.assertNotEqual(a, source_record_id(b['extraction_id'], b['file_id'], 'reference', span, None, 1))

    def test_exported_internal_schema_is_current(self):
        schema = json.loads((ROOT / 'contracts/v1/internal.schema.json').read_text())
        Draft202012Validator.check_schema(schema)
        self.assertIn('ExtractionBundle', schema['$defs'])
        self.assertIn('declarations', schema['$defs']['ExtractionBundle']['required'])


if __name__ == '__main__':
    unittest.main()
