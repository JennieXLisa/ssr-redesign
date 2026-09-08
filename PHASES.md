# SSR collaborative review — documentation phases

Version: 1.7  
Recorded: 2026-09-08  
Updated: 2026-09-09  
Status: phase sequence and feature-level documentation structure agreed.

This roadmap supersedes the earlier status snapshot, not its agreed phase order.
The previous files remain under [history](history/README.md).

## Working agreement

The user and assistant discuss significant decisions together, one feature at a
time. Approval to save the structure is not approval to fill undiscussed sections
with assumed designs. A meaningful uncertainty requires a question. Requirements
must be traced to the decisions actually agreed.

For each feature: discuss behavior and implementation choices, record the choices,
draft its detailed specification and implementation guidance, review it, then
record readiness. A phase is reviewed as a whole after its features are reconciled.
Routine developer choices may be delegated inside an approved boundary; lifecycle,
authority, persistence, and compatibility semantics must not be invented silently.

These are documentation boundaries, not runtime stages. Implementation order may
cross feature or phase numbers where dependencies require it. The existing
continuous-admission worker pool remains a reuse baseline.

Save approved feature progress to GitHub or local files after agreement; report
the actual location. Do not wait for the whole phase to finish or turn a partial
feature agreement into approval of undiscussed details.

## Approved phases

| Phase | Specification | Implementation plan | Current status |
|---|---|---|---|
| 1 | [Operating model, agent autonomy, and tools](01-operating-model-autonomy-tools/SPECIFICATION.md) | [Plan](01-operating-model-autonomy-tools/IMPLEMENTATION_PLAN.md) | Nine features agreed; P1-F02 source reads, cursors, indexed lookup and two-step analysis retrieval and subject-specific freshness notices saved; remaining choices open. |
| 2 | [Security discovery and analysis strategy](02-security-discovery/SPECIFICATION.md) | [Plan](02-security-discovery/IMPLEMENTATION_PLAN.md) | Scope placeholder only; discussion not started. |
| 3 | [Contextual collaboration and delegation](03-contextual-collaboration/SPECIFICATION.md) | [Plan](03-contextual-collaboration/IMPLEMENTATION_PLAN.md) | Scope placeholder only; discussion not started. |
| 4 | [Shared knowledge, evidence, and whole-project coverage](04-knowledge-evidence-coverage/SPECIFICATION.md) | [Plan](04-knowledge-evidence-coverage/IMPLEMENTATION_PLAN.md) | Scope placeholder only; discussion not started. |
| 5 | [Investigation, independent falsification, and findings](05-investigation-falsification-findings/SPECIFICATION.md) | [Plan](05-investigation-falsification-findings/IMPLEMENTATION_PLAN.md) | Scope placeholder only; discussion not started. |
| 6 | [Worker-pool scheduling and runtime](06-worker-pool-runtime/SPECIFICATION.md) | [Plan](06-worker-pool-runtime/IMPLEMENTATION_PLAN.md) | Scope placeholder only; discussion not started. |
| 7 | [Technical contracts, persistence, and integration](07-contracts-persistence-integration/SPECIFICATION.md) | [Plan](07-contracts-persistence-integration/IMPLEMENTATION_PLAN.md) | Scope placeholder only; discussion not started. |
| 8 | [Validation and implementation plan](08-validation-delivery/SPECIFICATION.md) | [Plan](08-validation-delivery/IMPLEMENTATION_PLAN.md) | Scope placeholder only; discussion not started. |

## Required structure

Every phase contains `SPECIFICATION.md`, `IMPLEMENTATION_PLAN.md`, and `features/`.
Phase-level documents own shared principles and integration. One Markdown file per
feature owns its detailed behavior, implementation, and acceptance tests together.
Do not split a feature into numerous tiny documents or duplicate its requirements
in the phase overview. Phase 1's nine feature IDs are fixed by the agreed grouping.

## Required feature detail

| Section | Required content before implementation readiness |
|---|---|
| Purpose | User-visible behavior and a concrete interaction. |
| Baseline and reuse | Verified existing owner, what is retained/extended/replaced, and why. |
| Requirements | Stable IDs, authority, permissions, normal/failure behavior, invariants. |
| Interfaces | Required inputs, outputs, reference kinds, validation, paging, and errors. |
| Implementation | Recommended mechanism, dependency direction, ordered changes and callers. |
| State | Transient versus durable data, update ownership, transactions, replay, stale inputs. |
| Scope limits | What not to build; no unjustified framework or second authority. |
| Tests | Concrete fixtures, expected outcomes, negative/race cases, relevant regressions. |
| Readiness | Unresolved decisions, external dependencies, checks required, completion evidence. |

The Phase 7 contract work reconciles these feature-level interfaces; it is not a
reason to leave an otherwise implementation-ready feature vague. Phase 8 integrates
phase-local delivery plans; it is not where all implementation thinking starts.

## Current checkpoint

Phase 1's overall behavior and nine-feature grouping are agreed. P1-F01's approved
mechanism separates execution identity, assignment ownership, and snapshot-wide
research policy checked on demand. Its initial detailed document is saved for
review; exact refactored owners and contract/rollout impacts remain open.

P1-F02 now records approved symbol-based source selection, host-managed source
pagination, independent authenticated cursors, exact indexed symbol lookup and
two-step analysis retrieval and subject-specific freshness notices, with implementation guidance and acceptance scenarios.
Exact-result reads and separate work availability are agreed. Final lookup/retrieval
fields, normalization, changing-list paging and remaining navigation interfaces
are still in discussion.
P1-F03–P1-F09 retain their earlier behavior agreements; their detailed discussions
are pending. Phases 2–8 remain scope placeholders. No application tests, feature
implementations, or benchmarks are reported by this save operation.

## Out of scope for this checkpoint

Do not implement the new design as part of the behavior-preserving refactor. Do
not assume the refactor has landed. Do not reinstate unapproved old-design limits,
manager roles, sealed-unit-only sharing, fixed lane ratios, or old M0–M3 delivery
modes. Discuss the relevant decisions in their owning feature/phase.

See [DECISION_REGISTER.md](DECISION_REGISTER.md) for the current agreements and open choices.
