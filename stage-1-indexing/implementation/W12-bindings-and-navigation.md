# W12 — Resolve cross-file references and one-hop relationships

Depends on: W08, W09, W10, W11. Owner: resolution scope/import/member/association owners and reference navigation.

Requirement traceability: S1-IX-R04, S1-FN-R06, S1-FN-R07, S1-RF-R01, S1-RF-R02, S1-RF-R03, S1-RF-R04, S1-RF-R05, S1-RF-R06, S1-NV-R09.

## Read before editing

Read ../IMPLEMENTATION.md, the specification sections for this capability, and the directly related contracts. Reuse settled types/algorithms; do not restart a repository-wide architecture survey.

## Intended files and boundary

- `src/ssr/resolution/`
- `src/ssr/navigation/references.py`
- `tests/resolution/`
- `tests/navigation/test_references.py`

## Implementation recipe

1. Wait for the complete successful structural inventory, then build the scope and import maps from published records. Do not finalize missing targets while extraction remains pending/failed.
2. Implement the finite language-specific rules in resolution.md in precedence order: nearest lexical binding, explicit local import, proven receiver binding, compiler reference, otherwise candidate/unresolved.
3. Reconcile C/C++ translation-unit observations by physical reference. Record context agreement/disagreement, USR evidence and declaration/definition equivalence.
4. Publish SAME_ENTITY associations without deleting original symbol/occurrence IDs. Build representative groups and ensure reads through previously returned IDs remain valid for proven members only.
5. Implement get_callers/get_callees/get_references from the same occurrence/binding tables. Preserve non-call uses, every repeated callsite and source-read links.
6. Add conformance cases for recursion, aliases, duplicate names, shadowing, overloads, member reassignment, unresolved dynamic calls, missing imports and delayed target-file extraction.

## Verification commands

These are the required implementation commands/test targets; they are not claims that tests already exist or were run while writing this specification.

```sh
uv run pytest tests/resolution tests/navigation/test_references.py tests/indexing/test_inventory_barrier.py
```

## Acceptance evidence

- Processing file order does not change final supported bindings.
- A callback argument is not manufactured into a direct call edge.
- The C++ member-call fixture remains a required success, not an optional test.

## Stop condition and receipt

No path-sensitive taint analysis, automatic graph traversal or guessed target promotion.

Complete W12 only after its real entry-point/owner tests pass. Record implemented requirement IDs, changed files, actual command results, unrun checks and the commit in IMPLEMENTATION_RECEIPT.md. Commit/push when authorized; do not silently advance the next task or add another planning document.
