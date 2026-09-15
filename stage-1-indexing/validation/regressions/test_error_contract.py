from pathlib import Path
import json
import sys
import unittest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'contracts/v1'))
from models import ErrorResponse, FindFlagsRequest


def error_item(index=0, code='INVALID_ARGUMENT'):
    return dict(code=code, operation='find_flags', field_path=['categories', index],
                component=None, position=None, message='Invalid category slug.',
                expected='lower-case category slug', received='invalid!',
                remediation='Use a category matching [a-z][a-z0-9_]{0,63}.',
                retryable=False, diagnostic_id=None)


class ErrorContractTests(unittest.TestCase):
    def test_every_independent_category_error_survives(self):
        payload = dict(index_run_id='00000000-0000-0000-0000-000000000001',
                       categories=['invalid!'] * 33, limit=0)
        try:
            FindFlagsRequest.model_validate(payload)
        except ValidationError as exc:
            actual = exc.errors()
        else:
            self.fail('invalid request was accepted')
        self.assertEqual(len(actual), 34)
        items = [{**error_item(n), 'field_path': list(e['loc'])} for n, e in enumerate(actual)]
        result = ErrorResponse.model_validate({'errors': items})
        self.assertEqual(len(result.errors), 34)
        self.assertEqual(result.errors[-1].field_path, ['limit'])

    def test_large_batch_is_not_truncated_to_byte_target(self):
        value = ErrorResponse.model_validate({'errors': [error_item(n) for n in range(300)]})
        serialized = json.dumps(value.model_dump(mode='json'), separators=(',', ':')).encode()
        self.assertGreater(len(serialized), 65536)
        self.assertEqual(len(json.loads(serialized)['errors']), 300)

    def test_operational_codes_use_the_same_envelope(self):
        for code in ['SUBMODULE_PIN_UNAVAILABLE', 'NONDETERMINISTIC_OUTPUT',
                     'RESOURCE_REQUIRED', 'SCANNER_FILE_NOT_PROCESSED']:
            self.assertEqual(ErrorResponse.model_validate({'errors': [error_item(code=code)]}).errors[0].code, code)
        with self.assertRaises(ValidationError):
            ErrorResponse.model_validate({'errors': [error_item(code='ARBITRARY_BACKEND_STRING')]})

    def test_safe_echo_bounds_and_required_nonempty_array(self):
        for patch in [{'received': 'x' * 257}, {'expected': 'x' * 257}]:
            with self.assertRaises(ValidationError):
                ErrorResponse.model_validate({'errors': [{**error_item(), **patch}]})
        with self.assertRaises(ValidationError):
            ErrorResponse.model_validate({'errors': []})


if __name__ == '__main__':
    unittest.main()
