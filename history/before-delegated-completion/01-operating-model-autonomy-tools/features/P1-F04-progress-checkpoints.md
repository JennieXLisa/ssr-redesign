# P1-F04 — Agent-initiated progress checkpoints

Version: 0.1  
Behavior: AGREED AT PHASE LEVEL  
Detailed specification: PENDING FEATURE DISCUSSION  
Implementation plan: PENDING FEATURE DISCUSSION  
Implementation readiness: NOT READY

This file saves the agreements already reached. It is not an instruction to invent
missing schemas, mechanisms, budgets or implementation steps. A numbered file is
not evidence that its detailed design has been approved.

## 1. Agreed behavior

**P1-F04-B1.** Agents may save structured progress during ordinary work without ending the current attempt.

**P1-F04-B2.** Agent-initiated and host-requested saving use the same underlying mechanism.

**P1-F04-B3.** Progress includes established facts, references, hypotheses, counterevidence, uncertainty and next useful steps; it is not a copied source/transcript dump.

**P1-F04-B4.** Saving does not reset budgets, publish a finding, complete coverage, or prove that a resumed attempt has already inspected source. Saved hypotheses remain hypotheses.

## 2. Existing implementation and reuse

Map the actual refactored owners before implementation. Use the
[reference baseline](../../SOURCES.md) and relevant existing source as navigation;
do not assume a new framework, service or store is required. No complete mapping
for this feature is asserted in this save.

## 3. Questions to discuss before detailed drafting

1. Exact checkpoint shape and revision/sequence behavior based on the current checkpoint implementation.

2. How ordinary tool exposure coexists with host-requested saving and context-pressure behavior.

3. Reference validation and retrieval/reconstruction after interruption, with honest attempt provenance.

4. Persistence, replay/idempotency tests and interaction with existing compact-restart paths.

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

P1-F03 for references, P1-F08 for durable action recovery, and Phase 6 for continuation/resource accounting.

See the [phase specification](../SPECIFICATION.md) and
[decision register](../../DECISION_REGISTER.md). The future implementation must
remain inside the agreed feature scope rather than implement later phases by
accident.
