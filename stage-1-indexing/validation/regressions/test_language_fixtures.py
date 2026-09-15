"""Authored corpus integrity and comparator regressions; not parser integration."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

VALIDATION = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(VALIDATION))
from reference_language_fixtures import (
    LANGUAGES, assert_fixture, load_fixtures, validate_fixture,
)


class LanguageFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = load_fixtures()
        cls.by_id = {case["id"]: case for case in cls.cases}

    def test_all_authored_source_spans_and_relations(self):
        self.assertEqual(len(self.cases), len(self.by_id))
        for case in self.cases:
            with self.subTest(fixture=case["id"]):
                validate_fixture(case)

    def test_every_dialect_has_source_positive_negative_and_error(self):
        seen, positive, negative, errors, unicode_crlf = set(), set(), set(), set(), set()
        for case in self.cases:
            for unit in case["sources"]:
                language = unit["language"]
                seen.add(language)
                if "\r\n" in unit["source"] and any(ord(c) > 127 for c in unit["source"]):
                    unicode_crlf.add(language)
            for file in case["expected"]["extraction"]["files"]:
                if file["status"] == "FAILED":
                    errors.add(file["language"])
            refs = {r["key"]: r for r in case["expected"]["extraction"]["references"]}
            languages = {u["path"]: u["language"] for u in case["sources"]}
            for b in case["expected"].get("resolution", {}).get("bindings", []):
                (positive if b["outcome"] == "RESOLVED" else negative).add(languages[refs[b["reference"]]["path"]])
        for category in (seen, positive, negative, errors, unicode_crlf):
            self.assertEqual(category, LANGUAGES)

    def test_comparator_accepts_collection_reordering(self):
        case = self.by_id["python-shadow-lambdas"]
        actual = deepcopy(case["expected"]["extraction"])
        actual["symbols"].reverse()
        actual["references"].reverse()
        assert_fixture(case, actual)

    def test_comparator_rejects_wrong_span_name_owner_or_inventory(self):
        case = self.by_id["python-shadow-lambdas"]
        for fault in ("byte", "name", "owner", "missing", "extra"):
            actual = deepcopy(case["expected"]["extraction"])
            if fault == "byte":
                actual["symbols"][0]["range"]["start_byte"] -= 1
            elif fault == "name":
                actual["symbols"][3]["local_name"] = "inferred_assignment_name"
            elif fault == "owner":
                actual["references"][0]["owner"] = actual["symbols"][1]["key"]
            elif fault == "missing":
                actual["symbols"].pop()
            else:
                actual["symbols"].append(deepcopy(actual["symbols"][0]))
            with self.subTest(fault=fault), self.assertRaises(AssertionError):
                assert_fixture(case, actual)

    def test_comparator_rejects_argument_reordering(self):
        case = self.by_id["zsh-anonymous-invocation"]
        actual = deepcopy(case["expected"]["extraction"])
        command = next(r for r in actual["references"] if r["callee"] and r["callee"]["text"] == "print")
        command["arguments"].reverse()
        with self.assertRaises(AssertionError):
            assert_fixture(case, actual)

    def test_comparator_rejects_pointer_function_and_declaration_body(self):
        case = self.by_id["c-prototype-pointer"]
        for fault in ("pointer_function", "declaration_body"):
            actual = deepcopy(case["expected"]["extraction"])
            if fault == "pointer_function":
                invented = deepcopy(actual["symbols"][0])
                invented["local_name"] = "fp"
                actual["symbols"].append(invented)
            else:
                actual["symbols"][0]["body"] = deepcopy(actual["symbols"][1]["body"])
            with self.subTest(fault=fault), self.assertRaises(AssertionError):
                assert_fixture(case, actual)

    def test_comparator_rejects_guessed_target_and_collapsed_overload(self):
        for fixture_id, predicate in (("python-shadow-lambdas", "UNRESOLVED"),
                                      ("typescript-overload-type-only", "AMBIGUOUS")):
            case = self.by_id[fixture_id]
            actual = deepcopy(case["expected"]["resolution"])
            b = next(b for b in actual["bindings"] if b["outcome"] == predicate)
            b["outcome"] = "RESOLVED"
            b["targets"] = [case["expected"]["extraction"]["symbols"][0]["key"]]
            with self.subTest(fixture=fixture_id), self.assertRaises(AssertionError):
                assert_fixture(case, actual, "resolution")

    def test_callback_cannot_become_call(self):
        case = self.by_id["javascript-callback-not-call"]
        actual = deepcopy(case["expected"]["extraction"])
        next(r for r in actual["references"] if r["usage"] == "CALLBACK_ARGUMENT")["usage"] = "CALL"
        with self.assertRaises(AssertionError):
            assert_fixture(case, actual)

    def test_compiler_observation_does_not_satisfy_final_navigation(self):
        case = self.by_id["cpp-test-member"]
        assert_fixture(case, deepcopy(case["expected"]["compiler_observations"]), "compiler_observations")
        with self.assertRaises(AssertionError):
            assert_fixture(case, case["expected"]["compiler_observations"], "navigation")
        actual = deepcopy(case["expected"]["resolution"])
        actual["associations"] = []
        with self.assertRaises(AssertionError):
            assert_fixture(case, actual, "resolution")
        actual = deepcopy(case["expected"]["navigation"])
        actual["reads"][0]["path"] = "main.cpp"
        with self.assertRaises(AssertionError):
            assert_fixture(case, actual, "navigation")

    def test_parse_failure_is_not_empty_success_or_final_resolution(self):
        case = self.by_id["zsh-parse-error"]
        actual = deepcopy(case["expected"]["extraction"])
        actual["files"][0]["status"] = "SUCCEEDED"
        with self.assertRaises(AssertionError):
            assert_fixture(case, actual)
        with self.assertRaises(AssertionError):
            assert_fixture(case, {"bindings": [], "associations": []}, "resolution")

    def test_integrity_rejects_invalid_authored_bytes_and_owner(self):
        for fault in ("byte", "owner", "declaration_body"):
            case = deepcopy(self.by_id["c-prototype-pointer"])
            symbols = case["expected"]["extraction"]["symbols"]
            if fault == "byte":
                symbols[0]["range"]["start_byte"] -= 1
            elif fault == "owner":
                case["expected"]["extraction"]["references"][0]["owner"] = None
            else:
                symbols[0]["body"] = deepcopy(symbols[1]["body"])
            with self.subTest(fault=fault), self.assertRaises(AssertionError):
                validate_fixture(case)

    def test_name_slice_cannot_match_inside_definition_keyword(self):
        case = deepcopy(self.by_id["python-evaluation-owners"])
        symbol = next(s for s in case["expected"]["extraction"]["symbols"] if s["local_name"] == "f")
        symbol["name"]["start_byte"] -= 2
        symbol["name"]["end_byte"] -= 2
        with self.assertRaisesRegex(AssertionError, "inside another identifier"):
            validate_fixture(case)


if __name__ == "__main__":
    unittest.main()
