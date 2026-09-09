# Phase 4 — Shared knowledge, evidence, and whole-project coverage

Status: DRAFT COMPLETE · Version: 2.0 · 2026-09-09  
Implementation: NOT PERFORMED · Application validation: NOT RUN.

## Scope and intended behavior

Accepted source-backed results can be reused according to their contract, not their task label. Complete compatible unit artifacts can satisfy canonical review through explicit adoption, while partial answers remain useful without coverage credit. Corrections create revisions and material signals, not overwritten history.

The phase is a documentation boundary, not a mandatory global runtime stage. Its features may be delivered in another dependency order. The modular refactor is a separate behavior-preserving workstream; reconcile it through [BASELINE.md](../BASELINE.md).

## Features and authoritative detail

| Feature | Detailed specification / implementation / acceptance | Completion requirements | New test scenarios |
|---|---|---:|---:|
| P4-F01 | [Independent artifact acceptance and publication](features/P4-F01-accepted-artifacts-and-publication.md) | 6 | 6 |
| P4-F02 | [Coverage adoption and canonical file synthesis](features/P4-F02-coverage-adoption-and-file-synthesis.md) | 6 | 6 |
| P4-F03 | [Knowledge reuse, revision and conflict handling](features/P4-F03-knowledge-reuse-and-corrections.md) | 6 | 6 |
| P4-F04 | [Evidence integrity and sensitive-data boundaries](features/P4-F04-evidence-and-sensitive-data.md) | 6 | 6 |

P1-F01/P1-F02 additionally preserve their original approved requirement and test ledgers. Counts here refer to the current completion guide, not an assertion that application tests exist or pass.

## Ownership and shared contracts

The participating owners are: Existing document/evidence owners, Semantic/turn/runtime/transcript receipts, Canonical unit/file publication, Lineage/reuse and material-dependency index. Keep one rule authority even when several features use it. Use [TOOLS](../contracts/TOOLS.md), [STATE](../contracts/STATE.md), [CONFIGURATION](../contracts/CONFIGURATION.md) and [SDK](../contracts/SDK.md) for shared interfaces; feature documents define the actual behavior and implementation checks. Do not invent incompatible local fields or duplicate persistence to satisfy one feature in isolation.

## Invariants

Preserve immutable source and exact evidence, source-free ordinary persistence, host-controlled acceptance, real producer/attempt identity and independent falsification. Broader research does not grant broader mutation. Readiness and completion are explicit predicates, not inferred from an empty query, a model claim or another agent's summary. Unknown or unsupported input remains visible.

## Phase acceptance

Every feature's required tests and adjacent preserved regressions must pass in the actual selected checkout; cross-feature interactions must pass the integrated traces in [DELIVERY.md](../DELIVERY.md). Validate positive behavior and negative authority/cancellation/retry cases, not only the happy path. Record all failed or unrun checks, actual collection and environment. Document completeness does not certify a running implementation.

## Out of scope

Do not execute a reviewed target, install its dependencies/tools, expose a generic shell to analytical agents, bypass historical compatibility, run paid experiments, mutate live review databases or deploy from this document. Do not introduce speculative services, manager models or new global barriers. New delegated engineering choices are labeled in [ENGINEERING_DECISIONS.md](../ENGINEERING_DECISIONS.md).

Continue with this phase's [implementation plan](IMPLEMENTATION_PLAN.md).
