# Phase 6 — specifications and detailed implementation plans

Use these detailed plans for eligibility/claim logic, fairness state, actual attempt settlement, resource ledgers and generation-safe completion. Continuous admission is retained; this is not a replacement worker framework.

| Feature | Specification | Detailed build plan |
|---|---|---|
| P6-F01 Shared-pool scheduling | [Specification](P6-F01-shared-pool-scheduling.md) | [Implementation](P6-F01/IMPLEMENTATION_PLAN.md) |
| P6-F02 Execution lifecycle and yield | [Specification](P6-F02-execution-lifecycle-and-yield.md) | [Implementation](P6-F02/IMPLEMENTATION_PLAN.md) |
| P6-F03 Budgets, backpressure and limits | [Specification](P6-F03-budgets-backpressure-and-limits.md) | [Implementation](P6-F03/IMPLEMENTATION_PLAN.md) |
| P6-F04 Completion and reconciliation | [Specification](P6-F04-completion-and-reconciliation.md) | [Implementation](P6-F04/IMPLEMENTATION_PLAN.md) |

[Phase integration plan](../IMPLEMENTATION_PLAN.md) · [All feature plans](../../FEATURE_IMPLEMENTATION_INDEX.md) · [Delivery order](../../DELIVERY.md).

Logical work, physical slots, provider requests, leases and budget reservations have distinct identities. Unknown usage is not zero, waiting is not failure, and an empty queue is not completion. The W=1/2/3/100 traces are specified deterministic tests, not claimed production throughput measurements.
