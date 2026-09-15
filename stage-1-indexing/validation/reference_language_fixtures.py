"""Reusable source-golden validation and comparison; no runtime adapters are run.

Runtime tests validate full production records, map IDs to physical locators,
and compare independent output to contracts/v1/language-fixtures.json.
This module performs no parsing, resolution, publication or target execution.
"""
from __future__ import annotations

import argparse
import ast
import difflib
import json
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "contracts/v1/language-fixtures.json"
PROJECTED_USAGES = {"CALL", "CONSTRUCT", "CALLBACK_ARGUMENT"}


def contract_values(name: str) -> set[str]:
    """Read a closed Literal vocabulary without importing optional dependencies."""
    tree = ast.parse((ROOT / "contracts/v1/models.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == name for t in node.targets
        ):
            value = node.value
            if isinstance(value, ast.Subscript) and isinstance(value.slice, ast.Tuple):
                return {ast.literal_eval(item) for item in value.slice.elts}
    raise AssertionError(f"Closed contract vocabulary not found: {name}")


LANGUAGES = contract_values("Language")
KINDS = contract_values("SymbolKind") - {"MODULE", "VARIABLE"}
CALLABLES = contract_values("CallableKind")
BASES = contract_values("BindingBasis")
OUTCOMES = contract_values("Outcome")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_fixtures(path: Path = CORPUS) -> list[dict]:
    """Load source and independent expectations; never derive bindings from code."""
    corpus = json.loads(path.read_text(encoding="utf-8"))
    require(corpus["schema_version"] == 1, "unsupported corpus version")
    require(corpus["format"] == "ssr-language-golden-v1", "unsupported corpus format")
    return corpus["fixtures"]


def _span(span: dict, raw: bytes, label: str) -> None:
    require(set(span) == {"start_byte", "end_byte", "text"}, f"{label}: span fields")
    start, end = span["start_byte"], span["end_byte"]
    require(type(start) is int and type(end) is int, f"{label}: integer byte offsets")
    require(0 <= start <= end <= len(raw), f"{label}: original-byte bounds")
    require(isinstance(span["text"], str), f"{label}: expected text must be a string")
    require(raw[start:end] == span["text"].encode("utf-8"), f"{label}: exact source slice")
    try:
        raw[:start].decode("utf-8")
        raw[:end].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AssertionError(f"{label}: split UTF-8 scalar") from exc


def _contains(outer: dict, inner: dict) -> bool:
    return outer["start_byte"] <= inner["start_byte"] <= inner["end_byte"] <= outer["end_byte"]


def _key(record: dict, kind: str) -> str:
    span = record["range"]
    return f"{record['path']}@{span['start_byte']}:{span['end_byte']}:{kind}"


def _groups(symbols: dict, associations: list) -> dict:
    parent = {key: key for key in symbols}

    def root(key):
        while parent[key] != key:
            parent[key] = parent[parent[key]]
            key = parent[key]
        return key

    seen = set()
    for pair in associations:
        require(isinstance(pair, list) and len(pair) == 2, "association must contain two keys")
        a, b = pair
        require(a in symbols and b in symbols and a != b, "association endpoints")
        require(tuple(sorted(pair)) not in seen, "duplicate association")
        seen.add(tuple(sorted(pair)))
        require(symbols[a]["kind"] == symbols[b]["kind"], "association kind mismatch")
        x, y = root(a), root(b)
        parent[max(x, y)] = min(x, y)
    return {key: root(key) for key in symbols}


def validate_fixture(case: dict) -> None:
    """Validate byte, ownership and reference integrity, not language semantics."""
    require(set(case) == {"id", "notes", "profile", "sources", "expected"}, "fixture fields")
    require(bool(case["id"]) and bool(case["notes"]), "fixture description")
    sources = {u["path"]: u for u in case["sources"]}
    require(len(sources) == len(case["sources"]) > 0, "unique nonempty source inventory")
    for path, source in sources.items():
        require(set(source) == {"path", "language", "encoding", "source"}, "source fields")
        require(not PurePosixPath(path).is_absolute() and ".." not in PurePosixPath(path).parts,
                "source paths must be relative fixture paths")
        require(source["language"] in LANGUAGES, "unsupported dialect")
        require(source["encoding"] == "utf-8", "corpus encodes exact UTF-8 source strings")
        require(isinstance(source["source"], str), "source must be actual text")
    raw = {path: u["source"].encode("utf-8") for path, u in sources.items()}
    extraction = case["expected"]["extraction"]
    require(set(extraction) == {"files", "symbols", "references", "imports"}, "projection fields")
    files = {item["path"]: item for item in extraction["files"]}
    require(len(files) == len(extraction["files"]) and set(files) == set(sources), "file inventory")
    for path, record in files.items():
        require(set(record) == {"path", "language", "status"}, "file status fields")
        require(record["language"] == sources[path]["language"], "file language mismatch")
        require(record["status"] in {"SUCCEEDED", "FAILED"}, "file extraction status")

    symbols = {s["key"]: s for s in extraction["symbols"]}
    references = {r["key"]: r for r in extraction["references"]}
    require(len(symbols) == len(extraction["symbols"]), "duplicate symbol occurrence")
    require(len(references) == len(extraction["references"]), "duplicate reference occurrence")
    require(not (set(symbols) & set(references)), "cross-kind locator collision")
    symbol_fields = {"key", "path", "local_name", "kind", "owner", "role", "range", "name", "body"}
    for key, symbol in symbols.items():
        require(set(symbol) == symbol_fields, "symbol projection fields")
        path = symbol["path"]
        require(path in raw and files[path]["status"] == "SUCCEEDED", "symbol in failed/missing file")
        require(symbol["kind"] in KINDS and key == _key(symbol, symbol["kind"]), "symbol key/kind")
        _span(symbol["range"], raw[path], key)
        require(symbol["role"] in {"declaration", "definition"}, "occurrence role")
        require(symbol["role"] != "declaration" or symbol["body"] is None, "fabricated declaration body")
        require((symbol["local_name"] is None) == (symbol["name"] is None), "anonymous name mismatch")
        if symbol["kind"] == "LAMBDA":
            require(symbol["local_name"] is None, "anonymous callable has fabricated local name")
        for field in ("name", "body"):
            child = symbol[field]
            if child is not None:
                _span(child, raw[path], f"{key}.{field}")
                require(_contains(symbol["range"], child), f"{field} lies outside occurrence")
        if symbol["name"] is not None:
            require(symbol["name"]["text"] == symbol["local_name"], "name is not original declared spelling")
            # A source slice can match "f" inside "def" and still be wrong.
            # This is a textual integrity check, not a language token parser.
            if symbol["local_name"].isidentifier():
                a, b = symbol["name"]["start_byte"], symbol["name"]["end_byte"]
                neighbors = (raw[path][:a].decode("utf-8")[-1:], raw[path][b:].decode("utf-8")[:1])
                require(not any(c and (c.isalnum() or c in "_$") for c in neighbors), "name lies inside another identifier")
        owner = symbol["owner"]
        if owner is not None:
            require(owner in symbols and owner != key, "unknown/self symbol owner")
            require(symbols[owner]["path"] == path, "cross-file physical owner")
            require(_contains(symbols[owner]["range"], symbol["range"]), "owner does not contain symbol")
        visited = {key}
        while owner is not None:
            require(owner not in visited, "symbol ownership cycle")
            visited.add(owner)
            owner = symbols[owner]["owner"]

    ref_fields = {"key", "path", "usage", "spelling", "owner", "range", "callee", "receiver", "arguments"}
    for key, ref in references.items():
        require(set(ref) == ref_fields, "reference projection fields")
        path = ref["path"]
        require(path in raw and files[path]["status"] == "SUCCEEDED", "reference in failed/missing file")
        require(ref["usage"] in PROJECTED_USAGES and key == _key(ref, ref["usage"]), "reference key/usage")
        _span(ref["range"], raw[path], key)
        for child in [ref["callee"], ref["receiver"], *ref["arguments"]]:
            if child is not None:
                _span(child, raw[path], key)
                require(_contains(ref["range"], child), "reference subrange")
        require(ref["spelling"] == ref["range"]["text"], "reference spelling")
        require(ref["usage"] != "CALLBACK_ARGUMENT" or not ref["arguments"], "callback is not a call")
        positions = [a["start_byte"] for a in ref["arguments"]]
        require(positions == sorted(positions), "argument source order")
        eligible = [s for s in symbols.values() if s["path"] == path
                    and s["kind"] in CALLABLES and s["body"] is not None
                    and _contains(s["body"], ref["range"])]
        owner = min(eligible, key=lambda s: s["body"]["end_byte"] - s["body"]["start_byte"])["key"] if eligible else None
        require(ref["owner"] == owner, f"{key}: wrong executable body owner")

    import_fields = {"path", "range", "kind", "module", "imported_name", "local_name", "exported_name", "relative_level"}
    import_keys = set()
    for record in extraction["imports"]:
        require(set(record) == import_fields, "import projection fields")
        path = record["path"]
        require(path in raw and files[path]["status"] == "SUCCEEDED", "import in failed/missing file")
        _span(record["range"], raw[path], "import")
        require(record["kind"] in {"import", "export", "require", "include", "source", "dynamic"}, "import kind")
        require(type(record["relative_level"]) is int and record["relative_level"] >= 0, "relative import level")
        for field in ("module", "imported_name", "local_name", "exported_name"):
            require(record[field] is None or isinstance(record[field], str), "import spelling fields")
        identity = json.dumps(record, sort_keys=True)
        require(identity not in import_keys, "duplicate import projection")
        import_keys.add(identity)

    if any(f["status"] == "FAILED" for f in files.values()):
        require(set(case["expected"]) == {"extraction"}, "failed inventory cannot finalize resolution")
        return
    resolution = case["expected"]["resolution"]
    require(set(resolution) == {"bindings", "associations"}, "resolution projection fields")
    groups = _groups(symbols, resolution["associations"])
    bindings = {b["reference"]: b for b in resolution["bindings"]}
    require(len(bindings) == len(resolution["bindings"]) and set(bindings) == set(references), "complete binding inventory")
    for ref, binding in bindings.items():
        require(set(binding) == {"reference", "outcome", "basis", "targets"}, "binding projection fields")
        require(binding["outcome"] in OUTCOMES and binding["basis"] in BASES, "closed binding vocabulary")
        targets = binding["targets"]
        require(len(targets) == len(set(targets)), "duplicate target")
        require(all(t in symbols and groups[t] == t for t in targets), "target absent or not association-normalized")
        cardinality = {"RESOLVED": len(targets) == 1, "UNRESOLVED": len(targets) == 0,
                       "AMBIGUOUS": len(targets) >= 2}
        require(cardinality[binding["outcome"]], "binding target cardinality")
    for observation in case["expected"].get("compiler_observations", []):
        require(set(observation) == {"reference", "declaration", "definition", "same_usr", "context"}, "compiler observation fields")
        require(observation["reference"] in references, "unknown compiler reference")
        a, b = observation["declaration"], observation["definition"]
        require(a in symbols and b in symbols and groups[a] == groups[b], "compiler identity association")
        require(symbols[a]["role"] == "declaration" and symbols[b]["role"] == "definition", "compiler occurrence roles")
        require(observation["same_usr"] is True, "compiler observation must prove equal nonempty USRs")
        require(observation["context"] in case["profile"]["translation_units"], "unknown translation unit")
    navigation = case["expected"].get("navigation")
    if navigation is not None:
        require(set(navigation) == {"callers", "callees", "reads"}, "navigation projection fields")
        for edge in navigation["callers"] + navigation["callees"]:
            require(set(edge) == {"reference", "owner", "target"}, "edge projection fields")
            ref = edge["reference"]
            require(ref in references and references[ref]["usage"] in {"CALL", "CONSTRUCT"}, "edge requires invocation")
            require(edge["owner"] == references[ref]["owner"], "edge source owner")
            require(bindings[ref]["outcome"] == "RESOLVED" and edge["target"] in bindings[ref]["targets"], "unproven navigation edge")
        for read in navigation["reads"]:
            require(set(read) == {"requested_symbol", "occurrence", "path", "range"}, "read projection fields")
            a, b = read["requested_symbol"], read["occurrence"]
            require(a in symbols and b in symbols and groups[a] == groups[b], "read crosses unproven association")
            require(read["path"] == symbols[b]["path"] and read["range"] == symbols[b]["range"], "read must return original occurrence bytes")


def _canonical(value, field: str = ""):
    if isinstance(value, dict):
        return {k: _canonical(v, k) for k, v in sorted(value.items())}
    if isinstance(value, list):
        items = [_canonical(v) for v in value]
        # Record collection order is irrelevant. Argument order is contractual.
        return items if field == "arguments" else sorted(items, key=lambda x: json.dumps(x, sort_keys=True, ensure_ascii=False))
    return value


def assert_fixture(case: dict, actual: dict | list, phase: str = "extraction") -> None:
    """Compare an independently produced runtime projection to authored goldens.

    Callers must map UUIDs to physical fixture locators, validate full production
    records, and normalize target groups only through proven associations first.
    Additional/missing projection fields and records are errors, not ignored.
    """
    require(phase in case["expected"], f"{case['id']}: no expected {phase} phase")
    expected = json.dumps(_canonical(case["expected"][phase]), sort_keys=True, ensure_ascii=False,
                          allow_nan=False, indent=2)
    observed = json.dumps(_canonical(actual), sort_keys=True, ensure_ascii=False,
                          allow_nan=False, indent=2)
    if expected != observed:
        diff = list(difflib.unified_diff(expected.splitlines(), observed.splitlines(),
                                       fromfile="expected", tofile="actual", lineterm=""))
        raise AssertionError(f"{case['id']} {phase} mismatch\n" + "\n".join(diff[:80]))


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare a runtime projection with an authored language golden")
    parser.add_argument("--actual", required=True, type=Path)
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--phase", default="extraction", choices=("extraction", "resolution", "compiler_observations", "navigation"))
    args = parser.parse_args()
    cases = {f["id"]: f for f in load_fixtures()}
    if args.fixture not in cases:
        parser.error(f"unknown fixture: {args.fixture}")
    try:
        case = cases[args.fixture]
        validate_fixture(case)
        actual = json.loads(args.actual.read_text(encoding="utf-8"))
        assert_fixture(case, actual, args.phase)
    except (OSError, ValueError, AssertionError) as exc:
        parser.exit(1, f"{exc}\n")
    print(f"Matched {args.fixture}: {args.phase} projection")


if __name__ == "__main__":
    main()
