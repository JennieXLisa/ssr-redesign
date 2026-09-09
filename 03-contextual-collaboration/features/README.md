# Phase 3 — specifications and detailed implementation plans

Use both documents for each feature. The detailed plans specify normalization/equivalence, routing transactions, active-reviewer input deltas, independent answer acceptance, wait/wake races, shared cancellation and cycle checks.

| Feature | Specification | Detailed build plan |
|---|---|---|
| P3-F01 Contextual requests and routing | [Specification](P3-F01-contextual-requests-and-routing.md) | [Implementation](P3-F01/IMPLEMENTATION_PLAN.md) |
| P3-F02 Active reviewer inbox | [Specification](P3-F02-active-reviewer-inbox.md) | [Implementation](P3-F02/IMPLEMENTATION_PLAN.md) |
| P3-F03 Answers and continuations | [Specification](P3-F03-answers-and-continuations.md) | [Implementation](P3-F03/IMPLEMENTATION_PLAN.md) |
| P3-F04 Dependency safety | [Specification](P3-F04-dependency-safety.md) | [Implementation](P3-F04/IMPLEMENTATION_PLAN.md) |

[Phase integration plan](../IMPLEMENTATION_PLAN.md) · [All feature plans](../../FEATURE_IMPLEMENTATION_INDEX.md) · [Delivery order](../../DELIVERY.md).

Do not turn advisory notices into blocking dependencies, mutate an in-flight request hash, lose questions when a producer completes, or keep model slots idle while waiting. Required tests are specified in the build plans; they are not claimed executed by this documentation.
