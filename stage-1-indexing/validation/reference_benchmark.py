"""Deterministic benchmark source census; does not fetch, parse or run targets.

By default write only manifest JSON to stdout. --output may create a new trusted
absolute directory; every existing ancestor must be a real directory. The
descriptor-relative writer refuses symlinks and existing destinations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath

from reference_language_fixtures import validate_fixture

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "contracts/v1/benchmark-corpus.json"


def canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                      separators=(",", ":")).encode("utf-8")


def safe_parts(path: str) -> tuple[str, ...]:
    """Require a canonical relative POSIX path before any filesystem writes."""
    parts = tuple(path.split("/"))
    if not path or "\\" in path or "\0" in path or any(p in {"", ".", ".."} for p in parts):
        raise ValueError(f"Noncanonical relative source path: {path!r}")
    return parts


def build_corpus(replicas: int | None = None) -> tuple[dict, dict[str, bytes]]:
    """Return a complete manifest and exact source bytes, with no output writes."""
    spec_raw = SPEC.read_bytes()
    spec = json.loads(spec_raw)
    if spec["schema_version"] != 1 or spec["format"] != "ssr-benchmark-corpus-v1":
        raise ValueError("Unsupported benchmark specification")
    settings = spec["synthetic"]
    replicas = settings["replicas"] if replicas is None else replicas
    if type(replicas) is not int or not 1 <= replicas <= 9999:
        raise ValueError("replicas must be an integer from 1 to 9999")
    fixture_raw = ROOT.joinpath(*safe_parts(settings["fixtures"])).read_bytes()
    fixture_digest = hashlib.sha256(fixture_raw).hexdigest()
    if fixture_digest != settings["fixtures_sha256"]:
        raise ValueError("Language fixtures changed; review and repin the benchmark census")
    corpus = json.loads(fixture_raw)
    if corpus["schema_version"] != 1 or corpus["format"] != "ssr-language-golden-v1":
        raise ValueError("Unsupported language fixture format")
    selected = []
    seen_ids = set()
    for case in corpus["fixtures"]:
        validate_fixture(case)
        if len(safe_parts(case["id"])) != 1 or case["id"] in seen_ids:
            raise ValueError("Fixture IDs must be unique single path components")
        seen_ids.add(case["id"])
        if all(f["status"] == "SUCCEEDED" for f in case["expected"]["extraction"]["files"]):
            selected.append(case)
    expected = settings["expected"]
    counts = (len(selected), sum(len(c["sources"]) for c in selected),
              sum(len(s["source"].encode("utf-8")) for c in selected for s in c["sources"]))
    if counts != (expected["cases_per_replica"], expected["files_per_replica"], expected["bytes_per_replica"]):
        raise ValueError("Eligible fixture census differs from the reviewed benchmark pin")
    rows, payloads = [], {}
    for replica in range(settings["replica_start"], settings["replica_start"] + replicas):
        for case in selected:
            for source in case["sources"]:
                safe_parts(source["path"])
                path = settings["path_template"].format(
                    replica=replica, fixture_id=case["id"], source_path=source["path"])
                safe_parts(path)
                if path in payloads:
                    raise ValueError(f"Duplicate generated path: {path}")
                raw = source["source"].encode("utf-8")
                payloads[path] = raw
                rows.append(dict(path=path, fixture_id=case["id"], source_path=source["path"],
                                 language=source["language"], bytes=len(raw),
                                 sha256=hashlib.sha256(raw).hexdigest()))
    rows.sort(key=lambda row: row["path"])
    manifest = dict(schema_version=1, format="ssr-benchmark-manifest-v1",
                    corpus_id=settings["id"], specification_sha256=hashlib.sha256(spec_raw).hexdigest(),
                    fixtures_sha256=fixture_digest, replicas=replicas, cases_per_replica=len(selected),
                    file_count=len(rows), total_bytes=sum(row["bytes"] for row in rows),
                    census_sha256=hashlib.sha256(canonical_json(rows)).hexdigest(), files=rows)
    if replicas == settings["replicas"]:
        actual = (manifest["file_count"], manifest["total_bytes"], manifest["census_sha256"])
        pinned = (expected["default_file_count"], expected["default_total_bytes"], expected["default_census_sha256"])
        if actual != pinned:
            raise ValueError("Default full census differs from the reviewed benchmark pin")
    return manifest, payloads


def _open_directory(parent_fd: int, name: str) -> int:
    return os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)


def materialize(output: str, payloads: dict[str, bytes]) -> None:
    """Create a new tree, without following symlinks or replacing any entry.

    The caller owns/trusts the existing parent directory. Partial output on I/O
    failure is retained for inspection; this function never deletes directories.
    """
    if not output.startswith("/") or output.startswith("//"):
        raise ValueError("--output requires a new trusted absolute directory")
    parts = safe_parts(output[1:])
    paths = {path: safe_parts(path) for path in payloads}
    # Validate file/ancestor conflicts before creating anything.
    for path in paths:
        if any(str(parent) in paths for parent in PurePosixPath(path).parents if str(parent) != "."):
            raise ValueError(f"Source path is also a directory: {path}")
    if any(not isinstance(raw, bytes) for raw in payloads.values()):
        raise ValueError("Source payloads must be original bytes")
    parent_fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for component in parts[:-1]:
            next_fd = _open_directory(parent_fd, component)
            os.close(parent_fd)
            parent_fd = next_fd
        os.mkdir(parts[-1], mode=0o700, dir_fd=parent_fd)
        root_fd = _open_directory(parent_fd, parts[-1])
        try:
            for path, components in sorted(paths.items()):
                directory_fd = os.dup(root_fd)
                try:
                    for component in components[:-1]:
                        try:
                            os.mkdir(component, mode=0o700, dir_fd=directory_fd)
                        except FileExistsError:
                            pass  # Reuse our own directory only after a no-follow open.
                        next_fd = _open_directory(directory_fd, component)
                        os.close(directory_fd)
                        directory_fd = next_fd
                    file_fd = os.open(components[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                      mode=0o600, dir_fd=directory_fd)
                    with os.fdopen(file_fd, "wb") as stream:
                        stream.write(payloads[path])
                finally:
                    os.close(directory_fd)
        finally:
            os.close(root_fd)
    finally:
        os.close(parent_fd)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicas", type=int, help="Replica count, default 100; use 1 for a smoke test")
    parser.add_argument("--output", help="NEW trusted absolute directory; existing parent must have no symlink components")
    args = parser.parse_args(argv)
    try:
        manifest, payloads = build_corpus(args.replicas)
        if args.output is not None:
            materialize(args.output, payloads)
    except (OSError, ValueError, KeyError, AssertionError) as exc:
        parser.exit(1, f"benchmark corpus: {exc}\n")
    print(canonical_json(manifest).decode("utf-8"))


if __name__ == "__main__":
    main()
