# W12 — Resolve cross-file references and one-hop relationships

Depends on: W08, W09, W10, W11. Owner: resolution scope/import/member/association owners and reference navigation.

Requirement traceability: S1-IX-R04, S1-FN-R06, S1-FN-R07, S1-RF-R01, S1-RF-R02, S1-RF-R03, S1-RF-R04, S1-RF-R05, S1-RF-R06, S1-NV-R09.

## Read before editing

Read ../IMPLEMENTATION.md, the specification sections for this capability, and the directly related contracts. Include [language-policies.md](../specification/language-policies.md), [compiler-work.md](../specification/compiler-work.md), `contracts/v1/records.py`, `contracts/v1/compiler_records.py`, and `contracts/v1/language-fixtures.json`. Reuse settled types/algorithms; do not restart a repository-wide architecture survey.

## Intended files and boundary

- `src/ssr/resolution/`
- `src/ssr/navigation/references.py`
- `tests/resolution/`
- `tests/navigation/test_references.py`

## Implementation recipe

1. Wait for the complete successful structural inventory, then build the scope and import maps from published records. Do not finalize missing targets while extraction remains pending/failed.
2. Implement the finite language-specific rules in resolution.md and language-policies.md in precedence order: nearest applicable binding/shadow/invalidation, explicit captured import, proven receiver binding, compiler reference, otherwise candidate/unresolved. Apply whole-scope shadowing, initialization/TDZ boundaries, type-only exclusions and deferred-body write checks; do not use one lexical lookup algorithm for every language.
3. Require frozen compiler input/reference censuses and successful active publications for every expected context, including diagnostic-only INVALID outcomes. Reconcile their exact expected Cartesian product by physical reference using compiler-work.md; distinguish pending/failed/missing work, invalid contexts, positive inactive/not-visited evidence, missing mappings and actual mapped/external/unsupported observations. Record validated context/USR/source evidence and declaration/definition equivalence. Never infer agreement from the observed subset or fabricate rows for absent compiler mappings.
4. Publish SAME_ENTITY associations without deleting original symbol/occurrence IDs. Build representative groups and ensure reads through previously returned IDs remain valid for proven members only.
5. Implement get_callers/get_callees/get_references from the same occurrence/binding tables. Preserve non-call uses, every repeated callsite and source-read links.
6. Compare actual final resolution projections to `language-fixtures.json` through the shared `assert_fixture` comparator. Include recursion, aliases, duplicate names, shadowing, overloads, receiver writes, unresolved dynamic calls, missing imports and delayed target-file extraction; extend the corpus for required cases not yet represented.
7. For `cpp-test-member`, consume W09's verified physical compiler observations and compare W12's separate resolution and navigation projections. Prove both declaration-to-definition and definition-to-declaration reads, exact member callsites, and incoming/outgoing ownership. The W09 observation check does not complete W12's navigation gate.

## Verification commands

These are the required implementation commands/test targets; they are not claims that tests already exist or were run while writing this specification.

```sh
uv run pytest tests/resolution tests/navigation/test_references.py tests/indexing/test_inventory_barrier.py
uv run pytest tests/indexing/test_compiler_context_recovery.py tests/storage/test_compiler_contexts.py
```

## Acceptance evidence

- Processing file order does not change final supported bindings.
- A callback argument is not manufactured into a direct call edge.
- The C++ member-call fixture remains a required success, not an optional test.
- Final bindings/readable associations are independent of context completion order and preserved after restart. Missing/failed expected context work blocks final publication; one local candidate plus invalid/missing/external evidence cannot become RESOLVED. Parent completion includes context obligations while public coverage remains distinct-file coverage.
- Authored corpus validation passes independently of actual resolver/publication/navigation tests; report both categories, and never present the former as execution evidence for the latter.

## Stop condition and receipt

No path-sensitive taint analysis, automatic graph traversal or guessed target promotion.

Complete W12 only after its real entry-point/owner tests pass. Record implemented requirement IDs, changed files, actual command results, unrun checks and the commit in IMPLEMENTATION_RECEIPT.md. Commit/push when authorized; do not silently advance the next task or add another planning document.
