# P1-F08 — Reliable tool actions and outcome recovery

Version: 0.1  
Behavior: AGREED AT PHASE LEVEL  
Detailed specification: PENDING FEATURE DISCUSSION  
Implementation plan: PENDING FEATURE DISCUSSION  
Implementation readiness: NOT READY

This file saves the agreements already reached. It is not an instruction to invent
missing schemas, mechanisms, budgets or implementation steps. A numbered file is
not evidence that its detailed design has been approved.

## 1. Agreed behavior

**P1-F08-B1.** The host should recover the outcome of an interrupted state-changing tool action before repeating its effects.

**P1-F08-B2.** A validated operation that committed must return its existing lead/task or checkpoint outcome on replay, not create another effect solely because acknowledgment was lost.

**P1-F08-B3.** If no action committed, say so; if the outcome is unknown, report uncertainty and reconcile the original action before claiming success or safe repetition.

**P1-F08-B4.** Transient persistence problems should reuse the already validated input where safe. The model intervenes for argument or analytical corrections, not to reconstruct an artifact unnecessarily.

**P1-F08-B5.** Operation replay identity is distinct from semantic lead deduplication. The same symbol can legitimately have multiple separately reported issues.

## 2. Existing implementation and reuse

Map the actual refactored owners before implementation. Use the
[reference baseline](../../SOURCES.md) and relevant existing source as navigation;
do not assume a new framework, service or store is required. No complete mapping
for this feature is asserted in this save.

## 3. Questions to discuss before detailed drafting

1. Exact operation identity, input binding, retention and replay/conflict protocol across attempts and restarts.

2. Existing persistence-retry machinery to reuse versus genuine new durable state.

3. Crash windows, registration/checkpoint transaction boundaries, and committed-versus-unknown outcome reporting.

4. Deterministic tests for lost acknowledgment, duplicate delivery, conflicting replay and recovery without duplicate work.

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

P1-F03 binds trusted identity; P1-F04/P1-F06 are consumers; P1-F07 reports outcomes. Phase 4/7 reconcile durable contracts.

See the [phase specification](../SPECIFICATION.md) and
[decision register](../../DECISION_REGISTER.md). The future implementation must
remain inside the agreed feature scope rather than implement later phases by
accident.
