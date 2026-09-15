# W07 — Build the shared adapter contract and Python inventory

Depends on: W06. Owner: languages.protocol, registry and python adapter.

Requirement traceability: S1-FN-R01, S1-FN-R02, S1-FN-R03, S1-FN-R04, S1-FN-R05, S1-FN-R06, S1-FN-R07, S1-FN-R08, S1-FN-R09, S1-RF-R01, S1-RF-R02, S1-RF-R03.

## Read before editing

Read ../IMPLEMENTATION.md, the specification sections for this capability, and the directly related contracts. Reuse settled types/algorithms; do not restart a repository-wide architecture survey.

## Intended files and boundary

- `src/ssr/languages/protocol.py`
- `src/ssr/languages/registry.py`
- `src/ssr/languages/python/`
- `tests/languages/conformance.py`
- `tests/languages/test_python.py`

## Implementation recipe

1. Adopt the SourceUnit/ExtractionBundle and all nested records already fixed by contracts/v1/records.py in W02. Follow extraction.md's two-pass traversal and language-policies.md's visibility/ownership rules. Keep parser results separate from publication; validation rejects wrong ranges/owners before staging activation. Run the valid/invalid shared-record fixtures before adding Python-specific producers.
2. Implement classification and source-to-parser offset mapping. Python uses tokenize encoding detection and ast positions converted from UTF-8 parser coordinates to original bytes.
3. Extract callable/class/module scopes, definitions, lambda bodies, signatures/parameters/default spans, imports, call/receiver/argument references and declared properties.
4. Assign deterministic IDs from source coordinates and ownership, not traversal scheduling. Keep anonymous display names distinct from declared local names.
5. Implement SyntaxError diagnostics and failed-work treatment. A valid no-function file succeeds with an empty inventory; an invalid file does not.
6. Create reusable conformance fixtures and assertions for range round-trips, same-name scopes, lambdas, errors and publication. Other language tasks extend this suite rather than copy it.

Adopt [language-profiles.md](../specification/language-profiles.md) at the shared
registry boundary. Map each golden with `reference_profiles.fixture_to_profile`,
freeze exact-path dialect selection and parser options before adapter creation,
and verify SourceUnit/profile identity. Keep `extract(source)` unchanged. Python
`package_root` maps to production `package_roots` for resolution; no package
import or host cwd supplies missing context. Passing the profile regression is
not proof that the real registry consumes these options.

## Verification commands

These are the required implementation commands/test targets; they are not claims that tests already exist or were run while writing this specification.

```sh
uv run pytest tests/languages/test_python.py tests/languages/test_conformance.py tests/indexing/test_real_python_pipeline.py
```

## Acceptance evidence

- A Python repo can go from READY snapshot through durable extraction to a byte-correct function read.
- Lambda-body calls have the lambda owner, not only the outer function.
- Unresolved calls retain source/argument ranges without fabricated targets.

## Stop condition and receipt

No importlib import of target modules or general Python execution/type inference.

Complete W07 only after its real entry-point/owner tests pass. Record implemented requirement IDs, changed files, actual command results, unrun checks and the commit in IMPLEMENTATION_RECEIPT.md. Commit/push when authorized; do not silently advance the next task or add another planning document.
