# W08 — Add JavaScript/JSX and TypeScript/TSX adapters

Depends on: W07. Owner: languages.javascript and languages.typescript.

Requirement traceability: S1-IN-R08, S1-FN-R02, S1-FN-R03, S1-FN-R07, S1-FN-R09, S1-RF-R02, S1-RF-R03.

## Read before editing

Read ../IMPLEMENTATION.md, the specification sections for this capability, and the directly related contracts. Include [language-policies.md](../specification/language-policies.md), `contracts/v1/records.py`, and the JS/JSX/TS/TSX cases in `contracts/v1/language-fixtures.json`. Reuse settled types/algorithms; do not restart a repository-wide architecture survey.

## Intended files and boundary

- `src/ssr/languages/javascript/`
- `src/ssr/languages/typescript/`
- `tests/languages/test_javascript.py`
- `tests/languages/test_typescript.py`

## Implementation recipe

1. Compile query resources against the exact installed grammar capsules, selecting TSX separately from TypeScript and testing JSX syntax.
2. Implement field-aware scope walkers for declarations/expressions, arrows, generators, methods, classes and constructors. Emit parameter/write/import shadowing facts, hoisted declarations and block TDZ records as specified in language-policies.md; separate TypeScript type/value namespaces. Reuse the bundle/position/ID owners without duplicating them.
3. Record ES imports/exports and literal require occurrences, call/new/receiver/argument spans. Keep dynamic import/require expressions as unresolved source observations.
4. Preserve TypeScript declaration signatures, overload occurrences, modifiers and type text without inventing bodies or compiler-confirmed types.
5. Run the shared positive/negative/ownership/Unicode/CRLF suite and real worker publication tests for both adapters. Compare actual published extraction projections against the authored language fixtures using the reusable `assert_fixture` comparator; W12 later compares their binding outcomes. Preserve anonymous names, callback usage, type-only imports and null overload bodies.

## Verification commands

These are the required implementation commands/test targets; they are not claims that tests already exist or were run while writing this specification.

```sh
uv run pytest tests/languages/test_javascript.py tests/languages/test_typescript.py tests/languages/test_conformance.py
```

## Acceptance evidence

- JSX/TSX files expose nearby functions correctly.
- Overload declarations and implementation bodies remain distinguishable.
- Nested arrows are independently readable and own their body operations.
- The `javascript-tdz`, import/export alias, callback-not-call, JSX/TSX ownership, and TypeScript overload/receiver-write goldens match actual published records. Corpus self-consistency checks alone do not satisfy this task; record installed grammar/query compilation and adapter execution separately.

## Stop condition and receipt

No Node target execution, package installation or bundler/loader invocation.

Complete W08 only after its real entry-point/owner tests pass. Record implemented requirement IDs, changed files, actual command results, unrun checks and the commit in IMPLEMENTATION_RECEIPT.md. Commit/push when authorized; do not silently advance the next task or add another planning document.
