# SSR collaborative review redesign

Version: 2.0 · 2026-09-09  
**Status: complete design draft; no harness/controller implementation, application test or deployment performed.**

This package completes the remaining specification and implementation-plan documents under the user's delegated authoring instruction. It retains previously agreed behavior and identifies remaining engineering choices as delegated selections, not approvals the user individually gave.

## Start here

Read [DELIVERY.md](DELIVERY.md) for the implementing agent's R0–R7 work sequence, [BASELINE.md](BASELINE.md) for observed code/refactor owners, and [ENGINEERING_DECISIONS.md](ENGINEERING_DECISIONS.md) for decisions and scope. Then use the relevant phase plan and feature guide. [TRACEABILITY.json](TRACEABILITY.json) indexes every feature, its dependencies and test IDs.

## Eight phases, detailed features

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

The main → phase → feature hierarchy is preserved. Feature documents include implementation steps and negative/race tests, not only architectural prose. There are 34 feature guides. Phase 1 keeps its nine agreed features; F02 has focused companion ledgers preserving earlier approved requirements/tests rather than requiring developers to navigate a 200 KB chronological discussion file.

## Shared developer contracts

[Tools and cursors](contracts/TOOLS.md) · [State/transactions](contracts/STATE.md) · [Configuration/bounds](contracts/CONFIGURATION.md) · [SDK/controller](contracts/SDK.md) · [Role submission projections](contracts/ROLE_PROJECTIONS.md) · [Reference JSON schemas](contracts/schemas/tool-inputs.schema.json).

These contracts close the earlier open choices: search continuation, key provisioning/rotation, name/path and graph paging, dynamic-result epochs, persistent interests, notice delivery, contextual-answer acceptance, coverage adoption, candidate revisions, scheduling and integration. Numeric defaults are initial engineering choices requiring evaluation, not benchmark claims.

## Architectural direction

Use one continuously admitted worker pool, existing source/index/evidence/candidate services and the modularized runtime. Analysts own questions, can read permitted project context, record independent leads and request contextual reviews. The host owns resources, durable work, accepted artifacts, source integrity and final gates. Waiting releases model slots. Complete compatible analysis can satisfy canonical coverage; partial answers cannot. Fresh falsification and current evidence validity remain mandatory for current findings.

No mandatory manager model, source-target execution, general agent shell, separate message service, second source/knowledge database, or global phase barrier is introduced.

## Approval and history

[DECISION_REGISTER.md](DECISION_REGISTER.md) preserves the approval history. [ENGINEERING_DECISIONS.md](ENGINEERING_DECISIONS.md) records delegated selections. The previous local F02 v0.16, decision register v1.16 and other checkpoint documents are preserved byte-for-byte under `history/before-delegated-completion/` with a manifest. They are historical records; use current phase/feature/contracts for implementation. Historical links/status text can describe superseded checkpoints.

## Verification and publication

[VALIDATION_REPORT.md](VALIDATION_REPORT.md) reports checks actually run on this documentation package. [PUBLISH_HANDOFF.md](PUBLISH_HANDOFF.md) describes publication to `JennieXLisa/ssr-redesign` only. Authoring did not modify either implementation repository, change repository visibility, or install/run the application. GitHub publication is not claimed unless a later verified commit is recorded.

The production design remains subject to R0 factual baseline verification and all implementation/release gates. Do not confuse document completeness, schema-example validation, scripted scheduler tests, live-provider compatibility and measured vulnerability quality.
