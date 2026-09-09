# P1-F09 — Grouped read-only retrieval

Version: 0.1  
Behavior: AGREED AT PHASE LEVEL  
Detailed specification: PENDING FEATURE DISCUSSION  
Implementation plan: PENDING FEATURE DISCUSSION  
Implementation readiness: NOT READY

This file saves the agreements already reached. It is not an instruction to invent
missing schemas, mechanisms, budgets or implementation steps. A numbered file is
not evidence that its detailed design has been approved.

## 1. Agreed behavior

**P1-F09-B1.** Allow optional grouped independent read-only lookups whose inputs are already known.

**P1-F09-B2.** Keep each result’s identity, source/evidence references, provenance, status and pagination distinguishable.

**P1-F09-B3.** Enforce a combined response budget rather than multiplying a per-call allowance by the group size; explicitly report deferred, partial or failed items.

**P1-F09-B4.** Do not guess unresolved targets to complete a group. Agents can still choose one read at a time when findings determine the next query.

**P1-F09-B5.** Grouped reads do not imply atomic batch writes. Lead registration, checkpoints and terminal submissions retain individual acknowledgment and recovery.

## 2. Existing implementation and reuse

Map the actual refactored owners before implementation. Use the
[reference baseline](../../SOURCES.md) and relevant existing source as navigation;
do not assume a new framework, service or store is required. No complete mapping
for this feature is asserted in this save.

## 3. Questions to discuss before detailed drafting

1. Whether existing native parallel calls suffice or a small grouped-read interface is needed for the configured backends.

2. Result ordering, cumulative accounting, paging, per-item errors and cancellation behavior.

3. Concurrency supported by existing DB connections and read handlers without sharing unsafe mutable broker state.

4. Tests for mixed success/failure, bounded responses, stale authorization and actual provider-visible behavior.

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

P1-F01 applies authorization to every item; P1-F02 supplies retrieval; P1-F07 supplies results; Phase 6 owns aggregate resource policy.

See the [phase specification](../SPECIFICATION.md) and
[decision register](../../DECISION_REGISTER.md). The future implementation must
remain inside the agreed feature scope rather than implement later phases by
accident.
