# Detailed implementation plans — all phases and features

Updated: 2026-09-09. This is the developer-facing index of the feature-by-feature build plans added after the v2 handoff was found too broad. Each plan was committed individually to `main`. The plans describe implementation work; they do not report that the harness/controller code or runtime tests are complete.

## How to use this repository

For a feature, open its specification **and its detailed build plan** from the same row below. The phase implementation plans and [DELIVERY.md](DELIVERY.md) establish dependency order; they are not substitutes for these feature-level instructions. Shared contracts define common wire/state/configuration fields once. The individual plans explain how to implement them through existing owners, including processing order, transaction boundaries, failure/recovery behavior, concrete fixtures and acceptance evidence.

P1-F02's old five-step overview was insufficient. Its [detailed plan](01-operating-model-autonomy-tools/features/P1-F02/IMPLEMENTATION_PLAN.md) now gives the source/selector/page/search/query/availability/notice algorithms and integration sequence. Original approved requirements/tests remain mandatory companion material, not waived by the new plan.

## Phase 1 — Operating model, autonomy and tools

| Feature | Specification | Detailed implementation plan |
|---|---|---|
| P1-F01 Research access and assignment ownership | [Specification](01-operating-model-autonomy-tools/features/P1-F01-research-access-and-ownership.md) | [Build plan](01-operating-model-autonomy-tools/features/P1-F01/IMPLEMENTATION_PLAN.md) |
| P1-F02 Indexed navigation and retrieval | [Specification](01-operating-model-autonomy-tools/features/P1-F02-indexed-navigation-and-retrieval.md) | [Build plan](01-operating-model-autonomy-tools/features/P1-F02/IMPLEMENTATION_PLAN.md) |
| P1-F03 Reference-based inputs and submissions | [Specification](01-operating-model-autonomy-tools/features/P1-F03-reference-based-inputs-and-submissions.md) | [Build plan](01-operating-model-autonomy-tools/features/P1-F03/IMPLEMENTATION_PLAN.md) |
| P1-F04 Progress checkpoints | [Specification](01-operating-model-autonomy-tools/features/P1-F04-progress-checkpoints.md) | [Build plan](01-operating-model-autonomy-tools/features/P1-F04/IMPLEMENTATION_PLAN.md) |
| P1-F05 Submission and return to analysis | [Specification](01-operating-model-autonomy-tools/features/P1-F05-submission-and-return-to-analysis.md) | [Build plan](01-operating-model-autonomy-tools/features/P1-F05/IMPLEMENTATION_PLAN.md) |
| P1-F06 Independent lead registration | [Specification](01-operating-model-autonomy-tools/features/P1-F06-independent-lead-registration.md) | [Build plan](01-operating-model-autonomy-tools/features/P1-F06/IMPLEMENTATION_PLAN.md) |
| P1-F07 Actionable tool results and validation | [Specification](01-operating-model-autonomy-tools/features/P1-F07-tool-results-and-validation-errors.md) | [Build plan](01-operating-model-autonomy-tools/features/P1-F07/IMPLEMENTATION_PLAN.md) |
| P1-F08 Tool-action recovery | [Specification](01-operating-model-autonomy-tools/features/P1-F08-tool-action-recovery.md) | [Build plan](01-operating-model-autonomy-tools/features/P1-F08/IMPLEMENTATION_PLAN.md) |
| P1-F09 Grouped read-only retrieval | [Specification](01-operating-model-autonomy-tools/features/P1-F09-grouped-read-only-retrieval.md) | [Build plan](01-operating-model-autonomy-tools/features/P1-F09/IMPLEMENTATION_PLAN.md) |

## Phase 2 — Security discovery

| Feature | Specification | Detailed implementation plan |
|---|---|---|
| P2-F01 Security-operation index | [Specification](02-security-discovery/features/P2-F01-security-operation-index.md) | [Build plan](02-security-discovery/features/P2-F01/IMPLEMENTATION_PLAN.md) |
| P2-F02 Prioritized discovery | [Specification](02-security-discovery/features/P2-F02-prioritized-discovery.md) | [Build plan](02-security-discovery/features/P2-F02/IMPLEMENTATION_PLAN.md) |
| P2-F03 Conditional summaries and flow | [Specification](02-security-discovery/features/P2-F03-conditional-summaries-and-flow.md) | [Build plan](02-security-discovery/features/P2-F03/IMPLEMENTATION_PLAN.md) |
| P2-F04 Trusted analyzers | [Specification](02-security-discovery/features/P2-F04-trusted-analyzers.md) | [Build plan](02-security-discovery/features/P2-F04/IMPLEMENTATION_PLAN.md) |

## Phase 3 — Contextual collaboration

| Feature | Specification | Detailed implementation plan |
|---|---|---|
| P3-F01 Contextual requests and routing | [Specification](03-contextual-collaboration/features/P3-F01-contextual-requests-and-routing.md) | [Build plan](03-contextual-collaboration/features/P3-F01/IMPLEMENTATION_PLAN.md) |
| P3-F02 Active reviewer inbox | [Specification](03-contextual-collaboration/features/P3-F02-active-reviewer-inbox.md) | [Build plan](03-contextual-collaboration/features/P3-F02/IMPLEMENTATION_PLAN.md) |
| P3-F03 Answers and continuations | [Specification](03-contextual-collaboration/features/P3-F03-answers-and-continuations.md) | [Build plan](03-contextual-collaboration/features/P3-F03/IMPLEMENTATION_PLAN.md) |
| P3-F04 Dependency safety | [Specification](03-contextual-collaboration/features/P3-F04-dependency-safety.md) | [Build plan](03-contextual-collaboration/features/P3-F04/IMPLEMENTATION_PLAN.md) |

## Phase 4 — Knowledge, evidence and coverage

| Feature | Specification | Detailed implementation plan |
|---|---|---|
| P4-F01 Accepted artifacts and publication | [Specification](04-knowledge-evidence-coverage/features/P4-F01-accepted-artifacts-and-publication.md) | [Build plan](04-knowledge-evidence-coverage/features/P4-F01/IMPLEMENTATION_PLAN.md) |
| P4-F02 Coverage adoption and file synthesis | [Specification](04-knowledge-evidence-coverage/features/P4-F02-coverage-adoption-and-file-synthesis.md) | [Build plan](04-knowledge-evidence-coverage/features/P4-F02/IMPLEMENTATION_PLAN.md) |
| P4-F03 Knowledge reuse and corrections | [Specification](04-knowledge-evidence-coverage/features/P4-F03-knowledge-reuse-and-corrections.md) | [Build plan](04-knowledge-evidence-coverage/features/P4-F03/IMPLEMENTATION_PLAN.md) |
| P4-F04 Evidence and sensitive data | [Specification](04-knowledge-evidence-coverage/features/P4-F04-evidence-and-sensitive-data.md) | [Build plan](04-knowledge-evidence-coverage/features/P4-F04/IMPLEMENTATION_PLAN.md) |

## Phase 5 — Investigation and findings

| Feature | Specification | Detailed implementation plan |
|---|---|---|
| P5-F01 Candidate investigation | [Specification](05-investigation-falsification-findings/features/P5-F01-candidate-investigation.md) | [Build plan](05-investigation-falsification-findings/features/P5-F01/IMPLEMENTATION_PLAN.md) |
| P5-F02 Falsification and current findings | [Specification](05-investigation-falsification-findings/features/P5-F02-falsification-and-current-findings.md) | [Build plan](05-investigation-falsification-findings/features/P5-F02/IMPLEMENTATION_PLAN.md) |
| P5-F03 Counterevidence, reassessment and export | [Specification](05-investigation-falsification-findings/features/P5-F03-counterevidence-reassessment-and-export.md) | [Build plan](05-investigation-falsification-findings/features/P5-F03/IMPLEMENTATION_PLAN.md) |

## Phase 6 — Worker pool and runtime

| Feature | Specification | Detailed implementation plan |
|---|---|---|
| P6-F01 Shared-pool scheduling | [Specification](06-worker-pool-runtime/features/P6-F01-shared-pool-scheduling.md) | [Build plan](06-worker-pool-runtime/features/P6-F01/IMPLEMENTATION_PLAN.md) |
| P6-F02 Execution lifecycle and yield | [Specification](06-worker-pool-runtime/features/P6-F02-execution-lifecycle-and-yield.md) | [Build plan](06-worker-pool-runtime/features/P6-F02/IMPLEMENTATION_PLAN.md) |
| P6-F03 Budgets, backpressure and limits | [Specification](06-worker-pool-runtime/features/P6-F03-budgets-backpressure-and-limits.md) | [Build plan](06-worker-pool-runtime/features/P6-F03/IMPLEMENTATION_PLAN.md) |
| P6-F04 Completion and reconciliation | [Specification](06-worker-pool-runtime/features/P6-F04-completion-and-reconciliation.md) | [Build plan](06-worker-pool-runtime/features/P6-F04/IMPLEMENTATION_PLAN.md) |

## Phase 7 — Contracts and integration

| Feature | Specification | Detailed implementation plan |
|---|---|---|
| P7-F01 Contracts and persistence | [Specification](07-contracts-persistence-integration/features/P7-F01-contracts-and-persistence.md) | [Build plan](07-contracts-persistence-integration/features/P7-F01/IMPLEMENTATION_PLAN.md) |
| P7-F02 Public SDK and controller | [Specification](07-contracts-persistence-integration/features/P7-F02-public-sdk-and-controller.md) | [Build plan](07-contracts-persistence-integration/features/P7-F02/IMPLEMENTATION_PLAN.md) |
| P7-F03 Configuration, versioning and rollout | [Specification](07-contracts-persistence-integration/features/P7-F03-configuration-versioning-and-rollout.md) | [Build plan](07-contracts-persistence-integration/features/P7-F03/IMPLEMENTATION_PLAN.md) |

## Phase 8 — Validation and delivery

| Feature | Specification | Detailed implementation plan |
|---|---|---|
| P8-F01 Deterministic acceptance | [Specification](08-validation-delivery/features/P8-F01-deterministic-acceptance.md) | [Build plan](08-validation-delivery/features/P8-F01/IMPLEMENTATION_PLAN.md) |
| P8-F02 Quality and cost evaluation | [Specification](08-validation-delivery/features/P8-F02-quality-and-cost-evaluation.md) | [Build plan](08-validation-delivery/features/P8-F02/IMPLEMENTATION_PLAN.md) |
| P8-F03 Delivery and release | [Specification](08-validation-delivery/features/P8-F03-delivery-and-release.md) | [Build plan](08-validation-delivery/features/P8-F03/IMPLEMENTATION_PLAN.md) |

## Handoff rules

Implement one coherent feature/slice through its existing owners, run its concrete fixtures and failure tests, and record exact commits/results before claiming code completion. A reference to shared contracts is not a substitute for executing the procedures in the build plan. Local helper names may vary; authorization, canonical ownership, original-byte evidence, accepted-result provenance, transaction boundaries and public compatibility may not be weakened silently.

The implementation plans preserve original approval/history files. A conflict between shared contracts and an implementation plan is a named contract defect to resolve explicitly—not permission to implement contradictory variants. Empirical limits, installed refactor mapping and actual package artifacts require verification in the authorized implementation environment.
