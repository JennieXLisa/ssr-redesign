# Phase 1 — specifications and detailed implementation plans

The specification/overview is not the build plan. Use both links for each feature. The detailed plans provide concrete call paths, normalization, algorithms, transactions, recovery cases and test fixtures. Documentation is not a claim that runtime code or tests are complete.

| Feature | Specification | Detailed build plan |
|---|---|---|
| P1-F01 Research access and ownership | [Specification](P1-F01-research-access-and-ownership.md) | [Implementation](P1-F01/IMPLEMENTATION_PLAN.md) |
| P1-F02 Indexed navigation and retrieval | [Specification](P1-F02-indexed-navigation-and-retrieval.md) | [Implementation](P1-F02/IMPLEMENTATION_PLAN.md) |
| P1-F03 Reference-based inputs and submissions | [Specification](P1-F03-reference-based-inputs-and-submissions.md) | [Implementation](P1-F03/IMPLEMENTATION_PLAN.md) |
| P1-F04 Progress checkpoints | [Specification](P1-F04-progress-checkpoints.md) | [Implementation](P1-F04/IMPLEMENTATION_PLAN.md) |
| P1-F05 Submission and return to analysis | [Specification](P1-F05-submission-and-return-to-analysis.md) | [Implementation](P1-F05/IMPLEMENTATION_PLAN.md) |
| P1-F06 Independent lead registration | [Specification](P1-F06-independent-lead-registration.md) | [Implementation](P1-F06/IMPLEMENTATION_PLAN.md) |
| P1-F07 Tool results and validation errors | [Specification](P1-F07-tool-results-and-validation-errors.md) | [Implementation](P1-F07/IMPLEMENTATION_PLAN.md) |
| P1-F08 Tool-action recovery | [Specification](P1-F08-tool-action-recovery.md) | [Implementation](P1-F08/IMPLEMENTATION_PLAN.md) |
| P1-F09 Grouped read-only retrieval | [Specification](P1-F09-grouped-read-only-retrieval.md) | [Implementation](P1-F09/IMPLEMENTATION_PLAN.md) |

Read the [phase integration plan](../IMPLEMENTATION_PLAN.md) for dependencies, [all feature plans](../../FEATURE_IMPLEMENTATION_INDEX.md) for cross-phase work, and [DELIVERY.md](../../DELIVERY.md) for implementation slices. Keep the P1-F01/P1-F02 approved-requirement and test ledgers active; the detailed plans do not waive them. Shared wire/state/configuration definitions live in [contracts](../../contracts/TOOLS.md), while the feature plans explain how to implement their behavior through existing owners.
