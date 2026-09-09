# P1-F03 — Reference-based tool inputs and submissions

Version: 0.1  
Behavior: AGREED AT PHASE LEVEL  
Detailed specification: PENDING FEATURE DISCUSSION  
Implementation plan: PENDING FEATURE DISCUSSION  
Implementation readiness: NOT READY

This file saves the agreements already reached. It is not an instruction to invent
missing schemas, mechanisms, budgets or implementation steps. A numbered file is
not evidence that its detailed design has been approved.

## 1. Agreed behavior

**P1-F03-B1.** The model supplies its analysis, uncertainty and explicitly selected references. The host supplies trusted execution identity and resolves existing index/source/evidence metadata.

**P1-F03-B2.** Apply this to progress, observations and final submissions. Resolve against the attempt’s bound inputs; detect stale changes rather than silently substituting the latest state.

**P1-F03-B3.** Existing symbol IDs, a reference to newly read source, and accepted evidence IDs have different meanings. Do not treat a source read as an accepted evidence claim.

**P1-F03-B4.** The host must not guess supporting evidence from prose, invent a missing path/control assessment, merge different claims just because their source spans match, or misattribute reused evidence.

## 2. Existing implementation and reuse

Map the actual refactored owners before implementation. Use the
[reference baseline](../../SOURCES.md) and relevant existing source as navigation;
do not assume a new framework, service or store is required. No complete mapping
for this feature is asserted in this save.

## 3. Questions to discuss before detailed drafting

1. Exact reference variants and lifetime, lookup and range-selection operations, and restart behavior.

2. Minimal model-facing payload versus full host-bound internal result; which fields remain required for the analyst.

3. Provenance of existing evidence reuse and new evidence preparation/acceptance, coordinated with Phase 4.

4. Compatibility of terminal schemas, version binding and refactored evidence/submission owners.

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

P1-F01, P1-F02 and P1-F07; Phase 4 owns durable evidence/claim publication. Phase 7 reconciles shared contracts after feature-level decisions.

See the [phase specification](../SPECIFICATION.md) and
[decision register](../../DECISION_REGISTER.md). The future implementation must
remain inside the agreed feature scope rather than implement later phases by
accident.
