# Phase 3 — implementation plan

Version: 2.0 · DRAFT COMPLETE · 2026-09-09. This is implementation guidance, not a claim that code or tests ran.

## Start from the real implementation

Read this phase's [specification](SPECIFICATION.md), each feature guide and [BASELINE.md](../BASELINE.md). Confirm selected branch, dirty worktree, module owners, public consumers, migration horizon and actual imported distribution. Do not assume historical paths are still the only code location or overwrite concurrent refactor work.

## Recommended implementation approach

Build request identity/equivalence/routing before inbox delivery. Implement independently accepted answers and atomic yield/wake together. Add cycle/fan-out/cancellation tests before enabling broad delegated collaboration.

The cross-phase build order is [DELIVERY.md](../DELIVERY.md). Feature references describe interface dependencies and can be mutually referential; they are not an import graph or a requirement to implement an entire future phase before a small common contract. Delivery slices break those integrations into buildable steps.

## Feature work packages

| Local reading order | Feature | Interfaces it depends on | Required verification |
|---:|---|---|---|
| 1 | P3-F01 | P1-F02, P1-F03, P1-F08, P4-F01 | All P3-F01 completion tests plus referenced regressions |
| 2 | P3-F02 | P3-F01, P1-F04, P1-F08 | All P3-F02 completion tests plus referenced regressions |
| 3 | P3-F03 | P3-F01, P3-F02, P4-F01, P6-F02 | All P3-F03 completion tests plus referenced regressions |
| 4 | P3-F04 | P3-F01, P3-F03, P6-F03 | All P3-F04 completion tests plus referenced regressions |

Each linked feature document contains its exact inputs/outputs, ordered implementation steps, transaction/resource ownership, failure behavior, negative cases and definition of done. Do not replace those details with “implement service and add tests.”

## Integration checkpoints

1. **Characterization:** establish existing behavior and acceptance boundaries using real fixtures. Preserve baseline failures with evidence rather than guessing they are unrelated.
2. **Contract-first change:** add typed fields/variants and negative tests before wiring new behavior. Update the shared schema, semantic validators and public capability registry in one coherent change.
3. **Owner implementation:** extend the identified responsibility without importing parent facades into low-level internals or passing an entire application object to extracted helpers.
4. **Transactional connection:** connect callbacks/events/receipts under the canonical owner. Test interruption immediately before and after each commit and after a new attempt claims work.
5. **External surfaces:** update controller/SDK/prompt/schema hashes only through versioned capability changes. Rebuild relevant packaged resources and verify installed imports, not only editable source.
6. **End-to-end gate:** run the feature tests, affected existing tests and a cross-phase trace. Keep new capability disabled when any required gate is missing.

## How to avoid overengineering

Keep the implementation in the existing harness/controller architecture. Introduce a small typed record or helper only for a real missing boundary. No feature requires a separate database, microservice, manager model, plugin system or frontend authority merely because it has its own document. Preserve each transaction owner and domain rule once. Numeric defaults are the pinned initial configuration, not a reason to add adaptive-learning infrastructure.

## Handoff required from the implementing agent

Report the actual starting and ending commits, changed modules and owners, added/retained contracts, migrations and tested schema versions, exact commands/collected tests/results, baseline failures, unrun live or package gates, generated artifact identities, paired repository changes and remaining risks. Never claim live performance, production deployment or complete vulnerability detection from static documentation or scripted fixtures.
