"""Reference corpus generation and write boundaries, not benchmark timings."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

VALIDATION = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(VALIDATION))
import reference_benchmark as benchmark


class BenchmarkTests(unittest.TestCase):
    def test_default_full_census_pin_and_determinism(self):
        first, payloads = benchmark.build_corpus()
        second, _ = benchmark.build_corpus()
        self.assertEqual(first, second)
        self.assertEqual((first["replicas"], first["cases_per_replica"], first["file_count"], first["total_bytes"]),
                         (100, 20, 2800, 255700))
        self.assertEqual(first["census_sha256"], "80e587efafa7aae01de833cf92b6c4435adaf05a445cbec49ea32659ebd9f66a")
        rows = first["files"]
        self.assertEqual(len({r["path"] for r in rows}), len(rows))
        self.assertEqual([r["path"] for r in rows], sorted(payloads))
        self.assertTrue(any(r["path"].startswith("replica-0001/") for r in rows))
        self.assertTrue(any(r["path"].startswith("replica-0100/") for r in rows))
        self.assertEqual(first["census_sha256"], hashlib.sha256(benchmark.canonical_json(rows)).hexdigest())

    def test_cli_default_emits_only_manifest_and_creates_nothing(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run([sys.executable, "-B", str(VALIDATION / "reference_benchmark.py")],
                                    cwd=temporary, capture_output=True, text=True, check=True)
            self.assertEqual(result.stderr, "")
            self.assertEqual(json.loads(result.stdout)["file_count"], 2800)
            self.assertEqual(list(Path(temporary).iterdir()), [])
            self.assertEqual(len(result.stdout.splitlines()), 1)

    def test_one_replica_cli_materializes_exact_all_success_sources(self):
        cases = json.loads((benchmark.ROOT / "contracts/v1/language-fixtures.json").read_bytes())["fixtures"]
        expected = {f"replica-0001/{case['id']}/{source['path']}": source["source"].encode("utf-8")
                    for case in cases
                    if all(f["status"] == "SUCCEEDED" for f in case["expected"]["extraction"]["files"])
                    for source in case["sources"]}
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary).resolve() / "new-corpus"
            result = subprocess.run([sys.executable, "-B", str(VALIDATION / "reference_benchmark.py"),
                                     "--replicas", "1", "--output", str(output)],
                                    capture_output=True, text=True, check=True)
            manifest = json.loads(result.stdout)
            actual = {p.relative_to(output).as_posix(): p.read_bytes() for p in output.rglob("*") if p.is_file()}
            self.assertEqual(actual, expected)
            self.assertEqual((manifest["file_count"], manifest["total_bytes"]), (28, 2557))
            self.assertEqual(manifest["census_sha256"], "a2bf7b637aa3ce623fdf97c4d612c8e2a9a9bd0873792b62ceceed3b9d5da4a2")
            for row in manifest["files"]:
                raw = actual[row["path"]]
                self.assertEqual((row["bytes"], row["sha256"]), (len(raw), hashlib.sha256(raw).hexdigest()))
            self.assertTrue(any(b"\r\n" in raw and b"caf\xc3\xa9" in raw for raw in actual.values()))
            self.assertIn(b"", actual.values())
            self.assertFalse(any(p.is_symlink() for p in output.rglob("*")))
            self.assertEqual({p.name for p in output.parent.iterdir()}, {"new-corpus"})

    def test_existing_file_directory_and_symlink_are_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            file = root / "file"
            file.write_bytes(b"keep")
            directory = root / "directory"
            directory.mkdir()
            link = root / "link"
            link.symlink_to(file)
            dangling = root / "dangling"
            dangling.symlink_to(root / "absent")
            for output in (file, directory, link, dangling):
                with self.subTest(output=output.name), self.assertRaises(FileExistsError):
                    benchmark.materialize(str(output), {"a.txt": b"source"})
            self.assertEqual(file.read_bytes(), b"keep")
            self.assertEqual(list(directory.iterdir()), [])
            self.assertFalse((root / "absent").exists())

    def test_symlink_ancestor_and_noncanonical_output_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            actual = root / "actual"
            actual.mkdir()
            (root / "alias").symlink_to(actual, target_is_directory=True)
            with self.assertRaises(OSError):
                benchmark.materialize(str(root / "alias" / "new"), {"a.txt": b"source"})
            for output in ("relative", "/", "//tmp/corpus", str(root) + "/../new", str(root) + "/new/"):
                with self.subTest(output=output), self.assertRaises(ValueError):
                    benchmark.materialize(output, {"a.txt": b"source"})
            self.assertEqual(list(actual.iterdir()), [])

    def test_unsafe_source_paths_rejected_before_directory_creation(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary).resolve() / "new"
            for path in ("../escape", "/absolute", "a//b", "a/./b", "a/../b", "a\\b", "bad\0name"):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    benchmark.materialize(str(output), {path: b"source"})
                self.assertFalse(output.exists())
            with self.assertRaises(ValueError):
                benchmark.materialize(str(output), {"file": b"a", "file/child": b"b"})
            self.assertFalse(output.exists())

    def test_bad_replica_count_and_changed_fixture_pin_fail(self):
        for value in (0, -1, 10000, True, 1.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                benchmark.build_corpus(value)
        with tempfile.TemporaryDirectory() as temporary:
            spec = json.loads(benchmark.SPEC.read_bytes())
            spec["synthetic"]["fixtures_sha256"] = "0" * 64
            changed = Path(temporary) / "spec.json"
            changed.write_text(json.dumps(spec), encoding="utf-8")
            with patch.object(benchmark, "SPEC", changed), self.assertRaisesRegex(ValueError, "repin"):
                benchmark.build_corpus(1)


if __name__ == "__main__":
    unittest.main()
