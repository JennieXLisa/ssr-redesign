# P1-F05 — Submission and return to analysis

Version: 0.1  
Behavior: AGREED AT PHASE LEVEL  
Detailed specification: PENDING FEATURE DISCUSSION  
Implementation plan: PENDING FEATURE DISCUSSION  
Implementation readiness: NOT READY

This file saves the agreements already reached. It is not an instruction to invent
missing schemas, mechanisms, budgets or implementation steps. A numbered file is
not evidence that its detailed design has been approved.

## 1. Agreed behavior

**P1-F05-B1.** Analytical agents choose when to submit. A repairable rejection must not permanently lock them into terminal-payload repair.

**P1-F05-B2.** A formatting/contract problem can be corrected directly; an analytical gap may lead back to source navigation, hypothesis revision, or a contextual request.

**P1-F05-B3.** Further analysis does not reset resource limits or authorize edits to accepted history.

**P1-F05-B4.** Authorization, integrity and unrecoverable execution failures are not invitations to continue research under an invalid attempt.

## 2. Existing implementation and reuse

Map the actual refactored owners before implementation. Use the
[reference baseline](../../SOURCES.md) and relevant existing source as navigation;
do not assume a new framework, service or store is required. No complete mapping
for this feature is asserted in this save.

## 3. Questions to discuss before detailed drafting

1. Runner transitions and tool-availability changes for each class of rejection.

2. How bounded retry/repair counters interact with renewed ordinary analysis without creating an infinite repair loop.

3. Role-specific bootstrap/terminal requirements that remain necessary versus restrictions deliberately being changed.

4. Exact tests showing the model can use the required tools after rejection and cannot mutate an accepted result.

## 4. Interfaces, state and implementation steps

Not yet specified. After the discussion, record exact inputs/outputs, validation,
required persistence and transaction ownership, dependencies, ordered changes,
and permitted developer discretion. Do not push all detail to Phase 7, but do not
fill this section with unapproved defaults now.

## 5. Tests and completion

Feature-level acceptance fixtures and regression mapping are pending discussion.
No tests are claimed to have run. Before implementation readiness, document
normal and negative outcomes, applicable race/retry cases, and how existing
contracts are preserved or deliberately changed.

## 6. Dependencies and scope

P1-F07 provides actionable failure classifications; P1-F04 preserves progress; Phase 3 supplies contextual requests and Phase 6 owns resource policy.

See the [phase specification](../SPECIFICATION.md) and
[decision register](../../DECISION_REGISTER.md). The future implementation must
remain inside the agreed feature scope rather than implement later phases by
accident.
