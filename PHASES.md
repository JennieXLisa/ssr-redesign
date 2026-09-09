# Agreed eight-phase roadmap

Version: 2.0 · 2026-09-09. Phase order is documentation order, not runtime barriers.

The user approved the phase/feature structure and subsequently delegated completion of the remaining engineering detail without additional consultation. The existing harness and controller implementation specifications remain untouched. The modular refactor remains a separate preparatory workstream.

| Phase | Specification | Implementation plan | Features | Document status |
|---:|---|---|---:|---|
| 1 | [Operating model, agent autonomy, and tools](01-operating-model-autonomy-tools/SPECIFICATION.md) | [Implementation plan](01-operating-model-autonomy-tools/IMPLEMENTATION_PLAN.md) | 9 | DRAFT COMPLETE |
| 2 | [Security discovery and analysis strategy](02-security-discovery/SPECIFICATION.md) | [Implementation plan](02-security-discovery/IMPLEMENTATION_PLAN.md) | 4 | DRAFT COMPLETE |
| 3 | [Contextual collaboration and delegation](03-contextual-collaboration/SPECIFICATION.md) | [Implementation plan](03-contextual-collaboration/IMPLEMENTATION_PLAN.md) | 4 | DRAFT COMPLETE |
| 4 | [Shared knowledge, evidence, and whole-project coverage](04-knowledge-evidence-coverage/SPECIFICATION.md) | [Implementation plan](04-knowledge-evidence-coverage/IMPLEMENTATION_PLAN.md) | 4 | DRAFT COMPLETE |
| 5 | [Investigation, independent falsification, and findings](05-investigation-falsification-findings/SPECIFICATION.md) | [Implementation plan](05-investigation-falsification-findings/IMPLEMENTATION_PLAN.md) | 3 | DRAFT COMPLETE |
| 6 | [Worker-pool scheduling and runtime](06-worker-pool-runtime/SPECIFICATION.md) | [Implementation plan](06-worker-pool-runtime/IMPLEMENTATION_PLAN.md) | 4 | DRAFT COMPLETE |
| 7 | [Technical contracts, persistence, and integration](07-contracts-persistence-integration/SPECIFICATION.md) | [Implementation plan](07-contracts-persistence-integration/IMPLEMENTATION_PLAN.md) | 3 | DRAFT COMPLETE |
| 8 | [Validation and implementation delivery](08-validation-delivery/SPECIFICATION.md) | [Implementation plan](08-validation-delivery/IMPLEMENTATION_PLAN.md) | 3 | DRAFT COMPLETE |

Every feature document contains purpose, existing reuse, detailed requirements, inputs/outputs/state, ordered implementation, failure/concurrency handling, acceptance tests, exclusions and definition of done. Shared contracts are centralized under `contracts/`. The dependency-ordered implementation plan is [DELIVERY.md](DELIVERY.md); it does not require completing entire phases in numeric order.

Earlier approvals are retained in [DECISION_REGISTER.md](DECISION_REGISTER.md). New engineering selections are explicit in [ENGINEERING_DECISIONS.md](ENGINEERING_DECISIONS.md). All application work and measured performance remain unperformed by this documentation task.
