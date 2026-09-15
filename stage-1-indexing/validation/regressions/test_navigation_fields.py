"""Review finding 4: required selection context and incoming caller names."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from uuid import UUID
from pydantic import ValidationError
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("navigation_contracts", ROOT / "contracts/v1/models.py")
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)
IDS = [str(UUID(int=n)) for n in range(1, 7)]
ZERO = dict(total_files=0, completed_files=0, failed_files=0)
COVERAGE = dict(index_complete=False, extraction=ZERO, resolution=ZERO, flagging=ZERO)

class NavigationFieldTests(unittest.TestCase):
    def test_rule_context_survives_every_progress_state(self):
        for state in ("PLANNED", "RUNNING", "PAUSED", "FAILED", "SUCCEEDED"):
            for mode in ("combined", "custom_only"):
                data = dict(index_run_id=IDS[0], snapshot_id=IDS[1], state=state,
                    query_ready=True, extraction_id=IDS[2], resolution_id=IDS[3],
                    flagging_id=IDS[4], rule_mode=mode, rule_manifest_digest="a" * 64,
                    coverage={**COVERAGE, "index_complete": state == "SUCCEEDED"})
                value = m.Progress.model_validate(data)
                self.assertEqual(value.rule_mode, mode)
                self.assertEqual(value.rule_manifest_digest, "a" * 64)
                for missing in ("rule_mode", "rule_manifest_digest"):
                    with self.assertRaises(ValidationError):
                        m.Progress.model_validate({k: v for k, v in data.items() if k != missing})

    def reference(self):
        return dict(reference_id=IDS[0], usage="CALL", path="src/caller.py",
            range=dict(start_byte=10, end_byte=20, start_line=2, end_line=2, start_column=1, end_column=11),
            owner_symbol_id=IDS[1], owner_name="module.handle_request", receiver=None,
            arguments=[], resolution_state="SUCCEEDED", outcome="RESOLVED",
            basis="LEXICAL_DECLARATION", targets=[dict(symbol_id=IDS[2], name="execute_command", definition=None)],
            external_name=None, arguments_cursor=None, targets_cursor=None)

    def test_incoming_caller_is_not_confused_with_target(self):
        item = m.ReferenceItem.model_validate(self.reference())
        self.assertEqual(item.owner_name, "module.handle_request")
        self.assertNotEqual(item.owner_name, item.targets[0].name)
        self.assertEqual(item.path, "src/caller.py")

    def test_owner_pair_is_consistent(self):
        data = self.reference()
        for change in ({"owner_name": None}, {"owner_symbol_id": None}):
            with self.assertRaises(ValidationError):
                m.ReferenceItem.model_validate({**data, **change})
        m.ReferenceItem.model_validate({**data, "owner_name": None, "owner_symbol_id": None})

    def test_exported_schema_contains_required_fields(self):
        schema = json.loads((ROOT / "contracts/v1/api.schema.json").read_text())
        Draft202012Validator.check_schema(schema)
        for name, fields in {"Progress": ["rule_mode", "rule_manifest_digest"], "ReferenceItem": ["owner_name"]}.items():
            for field in fields:
                self.assertIn(field, schema["$defs"][name]["properties"])
                self.assertIn(field, schema["$defs"][name]["required"])

if __name__ == "__main__":
    unittest.main()
