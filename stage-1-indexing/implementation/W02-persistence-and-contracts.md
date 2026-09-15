# W02 — Install the relational schema and strict contracts

Depends on: W01. Owner: storage and contracts.

Requirement traceability: S1-IN-R07, S1-IX-R02, S1-FN-R01, S1-RF-R01, S1-ER-R01.

## Read before editing

Read ../IMPLEMENTATION.md, the specification sections for this capability, and the directly related contracts. Reuse settled types/algorithms; do not restart a repository-wide architecture survey.

## Intended files and boundary

- `src/ssr/storage/connection.py`
- `src/ssr/storage/migrations/001_initial.sql`
- `src/ssr/contracts/`
- `tests/storage/`
- `tests/contracts/`

## Implementation recipe

The initial schema includes both file work/publications and the compiler context
family in [compiler-work.md](../specification/compiler-work.md). Adopt
compiler_records.py with the other internal contracts; test typed scalar/JSON
round-trips, partial-null constraints and selected-extraction membership in real
PostgreSQL. Later W09 supplies compiler observations, not another schema design.

1. Adopt the reference schema.sql as the initial migration and models.py plus records.py as public/internal production contracts, divided by responsibility. Include scopes, imports, lexical declarations, typed JSON fields, run control_intent and the frozen per-file applicability plan. W07 consumes these contracts; it must not invent competing records. Do not retain two DTO authorities. Export complete JSON Schemas from the production models.
2. Implement a migration ledger with filename/digest and an advisory migration lock. Apply each migration in one transaction. Refuse changed hashes for applied migrations; do not silently repair them.
3. Implement narrow repositories for projects/captures, datasets/work, source records and navigation. All write methods accept an explicit caller-owned transaction; none commits internally.
4. Enforce same-snapshot dataset composition, dataset-kind checks, file-range bounds, and result target/cardinality checks in the publication owner with deferred constraints where appropriate. Test both valid and maliciously mismatched references.
5. Implement deterministic UUIDv5 builders and canonical JSON fingerprints. Exclude worker counts/log levels from semantic identity; include parser/resolver/rule versions.
6. Provide disposable PostgreSQL fixtures that run real migrations and roll back/remove only test-owned data. Do not substitute SQLite for these tests.

## Verification commands

These are the required implementation commands/test targets; they are not claims that tests already exist or were run while writing this specification.

```sh
uv run pytest tests/contracts tests/storage
uv run ruff check src tests
uv run lint-imports
```

## Acceptance evidence

- Concurrent creation of identical compatible datasets returns one identity.
- Invalid run composition and cross-snapshot publication are rejected.
- An uncommitted publication is absent from all normal query views.

## Stop condition and receipt

No scanner, cloning or language extraction logic belongs in storage helpers.

Complete W02 only after its real entry-point/owner tests pass. Record implemented requirement IDs, changed files, actual command results, unrun checks and the commit in IMPLEMENTATION_RECEIPT.md. Commit/push when authorized; do not silently advance the next task or add another planning document.
