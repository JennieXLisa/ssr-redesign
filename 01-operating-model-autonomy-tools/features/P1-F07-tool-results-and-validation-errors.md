# P1-F07 — Actionable tool results and validation errors

Version: 0.1  
Behavior: AGREED AT PHASE LEVEL  
Detailed specification: PENDING FEATURE DISCUSSION  
Implementation plan: PENDING FEATURE DISCUSSION  
Implementation readiness: NOT READY

This file saves the agreements already reached. It is not an instruction to invent
missing schemas, mechanisms, budgets or implementation steps. A numbered file is
not evidence that its detailed design has been approved.

## 1. Agreed behavior

**P1-F07-B1.** Model-visible outcomes must distinguish missing analysis, unresolved relationships, no matches, incomplete search, partial pages, invalid inputs, operational failure, and authorization/integrity failure.

**P1-F07-B2.** Identify affected fields and provide a brief specific explanation with a recovery action the agent can actually execute using exposed tools.

**P1-F07-B3.** Collect independent validation problems in one bounded response where safe, rather than revealing one avoidable error per paid model turn.

**P1-F07-B4.** Stop when prerequisites, authority or integrity prevent further meaningful validation. Mark dependent checks as not evaluated rather than invent secondary errors.

**P1-F07-B5.** Do not convert failures into empty success, silently omit limits, or keep useful detail only in host logs. Recovery guidance must not invent analytical answers or leak protected content.

## 2. Existing implementation and reuse

Map the actual refactored owners before implementation. Use the
[reference baseline](../../SOURCES.md) and relevant existing source as navigation;
do not assume a new framework, service or store is required. No complete mapping
for this feature is asserted in this save.

## 3. Questions to discuss before detailed drafting

1. Shared outcome structure and stable error vocabulary, using existing broker/diagnostic definitions where applicable.

2. Per-tool detail fields, issue bounds/pagination, committed/unknown status linkage, and provider-visible serialization.

3. Which errors permit more research, retry, or narrowing, and which terminate/revoke further operations.

4. End-to-end tests through broker and provider-facing tool response construction, not just isolated error constructors.

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

All tool features consume these meanings; P1-F05 uses them for return-to-analysis behavior and P1-F08 for operation recovery.

See the [phase specification](../SPECIFICATION.md) and
[decision register](../../DECISION_REGISTER.md). The future implementation must
remain inside the agreed feature scope rather than implement later phases by
accident.
