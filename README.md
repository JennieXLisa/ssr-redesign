# SSR collaborative review redesign

Version: 3.0 · Updated: 2026-09-09

**Design documentation only. Harness/controller implementation, application tests, live installation and deployment are not established by this repository.**

## Corrected developer handoff

**Start with [CODEX_HANDOFF.md](CODEX_HANDOFF.md).** [CONTRACT_HARDENING.md](CONTRACT_HARDENING.md) maps all ten Codex findings to concrete corrected protocols, generated schemas and executable reference fixtures. The plans are prepared for implementation under those contracts; this is not a claim that the harness/controller, migrations or gateway are already tested.

The fixes include settlement-before-requeue, versioned prefix/input proof, immutable-manifest/staged synthesis, exact new SDK/role schemas, enforceable170k dispatch policy, exhaustive state/outcome mappings, typed Python callsite pilot, finite quotas and collaborative-only cutover. Every feature's dedicated build plan identifies its integration steps. Historical approvals remain unchanged.

## Start here: the detailed build plans

**[Open all 34 feature implementation plans](FEATURE_IMPLEMENTATION_INDEX.md).** Every feature now has a dedicated `features/Px-Fyy/IMPLEMENTATION_PLAN.md`, with its own processing algorithms, existing owners/call paths, input/state handling, transaction boundaries, failure/recovery rules, concrete tests and implementation sequence.

**[P1-F02 — detailed navigation and retrieval plan](01-operating-model-autonomy-tools/features/P1-F02/IMPLEMENTATION_PLAN.md)** is the direct replacement for relying on its former five-step overview. It covers selector normalization, original-byte paging, cursor provisioning/validation, positioned search and safe resumption, exact metadata/artifact queries, availability/interest transactions and request-bound notice recovery.

The v2 feature summaries were too broad to serve as implementation handoffs. The dedicated plans add procedural detail, but the subsequent review found the defects now corrected and mapped in H0. They were written and committed feature by feature, rather than claiming the phase-level checklists already supplied the necessary detail.

Read [BASELINE.md](BASELINE.md) to map the actual implementation owners, then [DELIVERY.md](DELIVERY.md) for the dependency-ordered R0–R7 slices. For each feature, read its specification and detailed plan together from the index. Shared contracts define reusable fields once; they do not replace feature-specific implementation procedures. [TRACEABILITY.json](TRACEABILITY.json) preserves the prior requirement/test inventory and should be extended with actual code/test outcomes during development.

## Eight documentation phases

| Phase | Specification | Phase integration plan | Feature specifications and detailed plans |
|---:|---|---|---|
| 1 | [Operating model, autonomy and tools](01-operating-model-autonomy-tools/SPECIFICATION.md) | [Dependencies/integration](01-operating-model-autonomy-tools/IMPLEMENTATION_PLAN.md) | [9 features](01-operating-model-autonomy-tools/features/README.md) |
| 2 | [Security discovery](02-security-discovery/SPECIFICATION.md) | [Dependencies/integration](02-security-discovery/IMPLEMENTATION_PLAN.md) | [4 features](02-security-discovery/features/README.md) |
| 3 | [Contextual collaboration](03-contextual-collaboration/SPECIFICATION.md) | [Dependencies/integration](03-contextual-collaboration/IMPLEMENTATION_PLAN.md) | [4 features](03-contextual-collaboration/features/README.md) |
| 4 | [Knowledge, evidence and coverage](04-knowledge-evidence-coverage/SPECIFICATION.md) | [Dependencies/integration](04-knowledge-evidence-coverage/IMPLEMENTATION_PLAN.md) | [4 features](04-knowledge-evidence-coverage/features/README.md) |
| 5 | [Investigation and findings](05-investigation-falsification-findings/SPECIFICATION.md) | [Dependencies/integration](05-investigation-falsification-findings/IMPLEMENTATION_PLAN.md) | [3 features](05-investigation-falsification-findings/features/README.md) |
| 6 | [Worker pool and runtime](06-worker-pool-runtime/SPECIFICATION.md) | [Dependencies/integration](06-worker-pool-runtime/IMPLEMENTATION_PLAN.md) | [4 features](06-worker-pool-runtime/features/README.md) |
| 7 | [Contracts and integration](07-contracts-persistence-integration/SPECIFICATION.md) | [Dependencies/integration](07-contracts-persistence-integration/IMPLEMENTATION_PLAN.md) | [3 features](07-contracts-persistence-integration/features/README.md) |
| 8 | [Validation and delivery](08-validation-delivery/SPECIFICATION.md) | [Dependencies/integration](08-validation-delivery/IMPLEMENTATION_PLAN.md) | [3 features](08-validation-delivery/features/README.md) |

These are documentation boundaries, not sequential runtime phases. Implementation order follows actual prerequisites. A feature folder does not require its own service, database or model role.

## Shared developer contracts

[Tools/cursors](contracts/TOOLS.md) · [State and transaction ownership](contracts/STATE.md) · [Configuration and limits](contracts/CONFIGURATION.md) · [Public SDK/controller](contracts/SDK.md) · [Role submission projections](contracts/ROLE_PROJECTIONS.md) · [Input schema fixtures](contracts/schemas/tool-inputs.schema.json).

[ENGINEERING_DECISIONS.md](ENGINEERING_DECISIONS.md) distinguishes delegated engineering selections from behavior individually approved by the user. Initial numeric defaults require evaluation; they are not throughput, quality or cost-saving claims. A conflict between shared contracts and a feature plan is an explicit contract defect to reconcile, not permission to implement incompatible local variants.

## Retained architecture and actual changes

Use the existing continuously admitted pool, immutable snapshot/index/evidence/candidate services and modularized runtime boundaries. Analysts own questions and assignments, may navigate permitted project context, record independent leads, request contextual reviews and resume from durable progress. The host owns resources, task/attempt authority, accepted artifacts and final gates.

Waiting releases physical model capacity only through safe exact-attempt settlement. Complete compatible analysis may satisfy canonical unit coverage through explicit adoption; partial answers may not. Fresh falsification and current material validity remain required for current findings. Current validity, canonical coverage and overall completion are different predicates.

No mandatory manager model, reviewed-target execution, general agent shell, separate message service, cloned source/knowledge store, generic workflow framework or global role-phase barrier is introduced. Local helper decomposition is discretionary; immutable identity, provenance, permissions and transaction semantics are not.

## History and scope of approval

[DECISION_REGISTER.md](DECISION_REGISTER.md) and the P1-F01/P1-F02 companion ledgers preserve earlier approvals. The original checkpoint files remain under `history/` with their original status text. They are historical evidence, not an excuse to make the developer reconstruct missing implementation instructions. The current detailed plans are available directly through the index above.

The user's delegated writing and repository-publication authorization does not claim implementation results or authorize live operations. Neither implementation repository is changed by documentation commits.

## Verification and handoff

[VALIDATION_REPORT.md](VALIDATION_REPORT.md) distinguishes full-tree structural/schema/reference results from application tests not run. [MANIFEST.json](MANIFEST.json) covers current source files and all34 feature plans with explicit non-self-referential exclusions. [TRACEABILITY.json](TRACEABILITY.json) points to each actual plan and hardening contract. The GitHub validation workflow runs on each published commit; its exact run/commit artifacts are publication evidence, not runtime certification.

The handoff order is CODEX_HANDOFF → CONTRACT_HARDENING → DELIVERY → selected feature plan and shared schemas. Codex must report actual code/test/build outcomes before any release claim. Neither application repository nor live state is modified by these design commits.
