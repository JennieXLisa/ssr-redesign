"""Review finding 6: source budgeting uses CRLF atoms, not single scalars."""
import sys
import unittest
from pathlib import Path
from uuid import UUID

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reference_paging import Subject, compact

ZERO = dict(total_files=0, completed_files=0, failed_files=0)
COVERAGE = dict(index_complete=False, extraction=ZERO, resolution=ZERO, flagging=ZERO)
IDS = [str(UUID(int=n)) for n in range(1, 6)]

class SourceBudgetTests(unittest.TestCase):
    def subject(self, text):
        return Subject(text.encode("utf-8"), "a.py", *IDS)

    def test_crlf_minimum_uses_an_indivisible_pair(self):
        subject = self.subject("\r\n")
        minimum = subject.minimum(50000, COVERAGE)
        self.assertEqual(minimum, subject.reserve(50000) + 4)
        self.assertEqual(list(subject.atoms()), [("\r\n", 2)])
        self.assertEqual(subject.initial(minimum, COVERAGE)["source"], "\r\n")
        with self.assertRaisesRegex(ValueError, "RESPONSE_BUDGET_TOO_SMALL"):
            subject.initial(minimum - 1, COVERAGE)

    def test_exact_minimum_progresses_and_reassembles(self):
        for text in ["a\r\nb\r\n", "猫\r\n🙂", "\x01\r\n\\\"", "a\rb\nc"]:
            with self.subTest(text=text):
                subject = self.subject(text)
                budget = subject.minimum(50000, COVERAGE)
                expected = subject.reserve(budget) + max(len(compact(a)) - 2 for a, _ in subject.atoms())
                self.assertEqual(budget, expected)
                page = subject.initial(budget, COVERAGE)
                output = ""
                end = 0
                while True:
                    self.assertEqual(page["range"]["start_byte"], end)
                    end = page["range"]["end_byte"]
                    self.assertLessEqual(len(compact(page)), budget)
                    output += page["source"]
                    self.assertFalse(subject.data[max(0, end-1):end+1] == b"\r\n")
                    token = page["next_continuation"]
                    if token is None:
                        break
                    page = subject.continuation(token, COVERAGE)
                    self.assertEqual(page["source"], subject.continuation(token, COVERAGE)["source"])
                self.assertEqual(output, text)
                self.assertEqual(end, len(subject.data))

    def test_prose_and_algorithm_share_atom_definition(self):
        text = (Path(__file__).resolve().parents[2] / "specification/source-reading.md").read_text()
        self.assertIn("a CRLF pair is one atom", text)
        self.assertIn("same atom iterator for minimum calculation, page selection", text)
        self.assertNotIn("JSON contribution per scalar", text)

if __name__ == "__main__":
    unittest.main()
