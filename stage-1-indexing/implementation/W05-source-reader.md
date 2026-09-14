# W05 — Implement byte-accurate reading and stable continuations

Depends on: W03. Owner: source reader, encoding/positions, token codec and shared errors.

Requirement traceability: S1-NV-R04, S1-NV-R05, S1-NV-R06, S1-NV-R12, S1-NV-R13, S1-NV-R14, S1-NV-R15, S1-NV-R16, S1-NV-R20, S1-NV-R21, S1-NV-R22, S1-NV-R23, S1-ER-R01, S1-ER-R02, S1-ER-R03, S1-ER-R04, S1-ER-R05, S1-ER-R06.

## Read before editing

Read ../IMPLEMENTATION.md, the specification sections for this capability, and the directly related contracts. Reuse settled types/algorithms; do not restart a repository-wide architecture survey.

## Intended files and boundary

- `src/ssr/source/reader.py`
- `src/ssr/source/positions.py`
- `src/ssr/source/continuation.py`
- `src/ssr/contracts/errors.py`
- `tests/source/`

## Implementation recipe

1. Implement original-byte lookup by validated snapshot/file identity using Git cat-file or its verified spool. Test exact binary protocol framing; never send file contents as an object request.
2. Implement codec and original-byte/Unicode coordinate mapping, preserving BOM and newline semantics. Centralize start-inclusive/end-exclusive ranges; no parser-specific conventions leak into navigation.
3. Implement read_function and read_file through one reader owner. Tests may publish valid fixture occurrences directly through the storage owner before real extraction exists.
4. Implement canonical compact JSON serialization and exact whole-response sizing. Default to 50,000 bytes, validate the initial override ceiling and calculate the safe-paging minimum/reserve.
5. Implement self-contained typed source tokens, fixed page intervals and one-page lookahead. Replays may update coverage only; the selected source interval and effective budget remain unchanged.
6. Implement errors[] with independent validation batching and prerequisite-aware association checks. An impossible source budget does not suppress the separately bounded error response.
7. Connect the CLI source read to the same owner and verify formatted line labels never alter JSON source text.

## Verification commands

These are the required implementation commands/test targets; they are not claims that tests already exist or were run while writing this specification.

```sh
uv run pytest tests/source tests/contracts/test_errors.py tests/cli/test_read.py
```

## Acceptance evidence

- All source paging proof cases in source-reading.md pass, including replay after coverage grows.
- A successful sequence covers the selected bytes without gaps/duplicates.
- Missing Git blobs produce integrity errors, not a live filesystem fallback.

## Stop condition and receipt

No search implementation, cursor-session database table or automatic draining into model context.

Complete W05 only after its real entry-point/owner tests pass. Record implemented requirement IDs, changed files, actual command results, unrun checks and the commit in IMPLEMENTATION_RECEIPT.md. Commit/push when authorized; do not silently advance the next task or add another planning document.
