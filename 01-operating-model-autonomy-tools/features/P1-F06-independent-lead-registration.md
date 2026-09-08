# P1-F06 — Independent lead registration

Version: 0.1  
Behavior: AGREED AT PHASE LEVEL  
Detailed specification: PENDING FEATURE DISCUSSION  
Implementation plan: PENDING FEATURE DISCUSSION  
Implementation readiness: NOT READY

This file saves the agreements already reached. It is not an instruction to invent
missing schemas, mechanisms, budgets or implementation steps. A numbered file is
not evidence that its detailed design has been approved.

## 1. Agreed behavior

**P1-F06-B1.** An agent can flag an additional source-grounded suspected issue outside its assignment or a predefined catalogue and propose follow-up work.

**P1-F06-B2.** Registration is an immediate, nonterminal tool action. The harness durably records a self-contained lead, with observations, references, uncertainty and the question requiring analysis.

**P1-F06-B3.** After successful registration the harness owns follow-up. The proposer continues its assignment and is not required to wait, poll, obtain the investigation result or manage another worker.

**P1-F06-B4.** The harness creates or associates independent follow-up work without waiting for the original assignment or file synthesis. If the pool is full, record and queue; do not interrupt healthy workers or exceed capacity.

**P1-F06-B5.** An accepted lead survives failure of the original attempt. Registration needs its own accepted record/provenance and must not depend on the proposer’s later terminal receipts.

**P1-F06-B6.** A registered suspicion is not a confirmed finding. Reporting a separate lead differs from requesting an answer needed by the current analysis.

## 2. Existing implementation and reuse

Map the actual refactored owners before implementation. Use the
[reference baseline](../../SOURCES.md) and relevant existing source as navigation;
do not assume a new framework, service or store is required. No complete mapping
for this feature is asserted in this save.

## 3. Questions to discuss before detailed drafting

1. How to represent the record using existing lead/candidate infrastructure without inventing a duplicate store.

2. Exact minimum payload, accepted registration record, acknowledgment, provenance and cross-file source references.

3. Atomicity of registration and durable follow-up obligation, plus recovery when acknowledgment is interrupted.

4. Routing/joining of compatible work, task types, candidate maturity and queue priority belong with Phases 3–6, not implicit defaults here.

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

P1-F03 references, P1-F07 result meanings, P1-F08 retry recovery, Phase 3 routing, Phase 4 publication/persistence, Phase 5 adjudication and Phase 6 scheduling.

See the [phase specification](../SPECIFICATION.md) and
[decision register](../../DECISION_REGISTER.md). The future implementation must
remain inside the agreed feature scope rather than implement later phases by
accident.
