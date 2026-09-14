# W14 — Complete researcher navigation and live pages

Depends on: W05, W12, W13. Owner: navigation functions/files/text/flags/paging and thin CLI adapters.

Requirement traceability: S1-NV-R01, S1-NV-R02, S1-NV-R03, S1-NV-R07, S1-NV-R08, S1-NV-R10, S1-NV-R11, S1-NV-R12, S1-NV-R17, S1-NV-R18, S1-NV-R19, S1-ER-R01, S1-ER-R02, S1-ER-R03, S1-ER-R04, S1-ER-R05, S1-ER-R06.

## Read before editing

Read ../IMPLEMENTATION.md, the specification sections for this capability, and the directly related contracts. Reuse settled types/algorithms; do not restart a repository-wide architecture survey.

## Intended files and boundary

- `src/ssr/navigation/`
- `src/ssr/cli/query.py`
- `src/ssr/cli/rendering.py`
- `tests/navigation/`
- `tests/cli/`

## Implementation recipe

1. Implement the exact operation signatures/DTOs in navigation.md. Search returns direct readable occurrence IDs and bounded declaration/definition subcollections.
2. Implement raw-path discovery, immediate-child listings and file outlines with parent IDs/positions. Do not hide unflagged, unsupported, binary-metadata or unfinished files.
3. Implement regex content search over captured text, including comments/config/docs, with byte-accurate result ranges and optional known owner enrichment.
4. Implement stateless query tokens binding operation/run/effective query and last key. Distinguish live cursor semantics from fixed source continuations; permit only a changed valid page limit.
5. Read results plus coverage in one short read-only transaction; bound serialized metadata pages without losing the next record or returning a fake terminal cursor after an internal batch.
6. Implement bounded nested argument/target/occurrence reads, actionable batched errors, rule-mode visibility and all CLI-to-owner entry points.
7. Run the complete Search → select IDs → read → continue → callers/callees → open callsite workflow with the original checkout removed.

## Verification commands

These are the required implementation commands/test targets; they are not claims that tests already exist or were run while writing this specification.

```sh
uv run pytest tests/navigation tests/cli tests/contracts
uv run lint-imports
```

## Acceptance evidence

- An unflagged function and text without a parser are navigable.
- Fresh completed-run pagination enumerates all recorded matches exactly once.
- Live insert-before-cursor and group-merge cases require refresh without corrupting source tokens.

## Stop condition and receipt

No HTTP frontend, model adapter, ranking/embedding service, recursive graph dump or workflow expansion.

Complete W14 only after its real entry-point/owner tests pass. Record implemented requirement IDs, changed files, actual command results, unrun checks and the commit in IMPLEMENTATION_RECEIPT.md. Commit/push when authorized; do not silently advance the next task or add another planning document.
