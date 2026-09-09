# Phase 1 implementation plan

Version: 0.1  
Status: integration outline only; individual feature implementation choices remain
under discussion. Not a blanket instruction to implement all Phase 1 features.

## Starting point

Use the actual accepted modular-refactor result as the implementation starting
point. The historical mapping in [SOURCES.md](../SOURCES.md) is a navigation aid,
not a requirement to work inside the old large files. Verify branch, local changes,
applicable AGENTS.md, contracts and relevant tests before modifying code.

Preserve the separate behavior-preserving refactor. This phase intentionally
changes selected tool behavior; it must be developed and validated as feature work.

## Feature-local plans

P1-F01 contains the first [detailed implementation draft](features/P1-F01-research-access-and-ownership.md).
P1-F02–P1-F09 currently contain agreements and unresolved implementation questions,
not completed plans. Complete and review their interfaces, ownership, validation,
state/retry behavior and tests before implementation readiness.

## Known integration dependencies, not a fixed delivery order

| Capability | Required integration |
|---|---|
| Broader source and index access | P1-F01 authority boundary plus P1-F02 retrieval behavior. Do not expose private analysis merely because source access broadens. |
| Reference-based writes | P1-F03 resolution and provenance, P1-F07 actionable validation, and the owning publication contract. |
| On-demand checkpoints | P1-F04 ordinary tool exposure, P1-F08 safe persistence/recovery, and P1-F05 runner state behavior. |
| Separate lead registration | P1-F06 durable registration plus P1-F08 outcome recovery and Phases 3–4/6 follow-up acceptance and scheduling contracts. Do not ship an acknowledged-but-unrecorded proposal. |
| Research after rejection | P1-F05 must integrate P1-F07 classifications without treating authorization/integrity failure as a repairable invitation to continue. |
| Grouped reads | P1-F09 must preserve P1-F01 per-operation authority, P1-F02 reference/status integrity, and combined budgets. |

Do not implement a runtime feature with missing required persistence or receipt
contracts merely to match feature-number order. Equally, do not invent a generic
framework to anticipate every later feature.

## Local steps after each feature is agreed

Map old to current owners and record the retained public interfaces. Write the
missing behavioral tests at the real integration boundary. Make one coherent
change at a time, preserving unrelated policies and data. Verify new behavior
and negative cases, then verify shared callers, public contracts and package
imports as relevant. State unrun checks and baseline failures with evidence.

The phase-wide plan will be completed with the user once the individual feature
plans have enough detail. It must name actual implementation slices, dependencies,
contract/version impacts and exit checks, not merely say “add tools and tests.”
