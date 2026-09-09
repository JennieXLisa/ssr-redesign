# Phase 1 — Operating model, agent autonomy, and tools

Status: DRAFT COMPLETE · Version: 2.0 · 2026-09-09  
Implementation: NOT PERFORMED · Application validation: NOT RUN.

## Scope and intended behavior

An analyst starts with its actual assignment and a small context, navigates existing IDs or manifest/name discovery, reads verified source, retrieves exact accepted analysis, and may checkpoint, request context or report independent leads. Submission rejection can return to research. Source visibility, result visibility and mutation ownership remain separate.

The phase is a documentation boundary, not a mandatory global runtime stage. Its features may be delivered in another dependency order. The modular refactor is a separate behavior-preserving workstream; reconcile it through [BASELINE.md](../BASELINE.md).

## Features and authoritative detail

| Feature | Detailed specification / implementation / acceptance | Completion requirements | New test scenarios |
|---|---|---:|---:|
| P1-F01 | [Research access and assignment ownership](features/P1-F01-research-access-and-ownership.md) | 6 | 6 |
| P1-F02 | [Indexed navigation and information retrieval](features/P1-F02-indexed-navigation-and-retrieval.md) | 6 | 8 |
| P1-F03 | [Reference-based inputs and submissions](features/P1-F03-reference-based-inputs-and-submissions.md) | 6 | 6 |
| P1-F04 | [Agent-initiated progress checkpoints](features/P1-F04-progress-checkpoints.md) | 6 | 6 |
| P1-F05 | [Submission and return to analysis](features/P1-F05-submission-and-return-to-analysis.md) | 6 | 6 |
| P1-F06 | [Independent lead registration](features/P1-F06-independent-lead-registration.md) | 6 | 6 |
| P1-F07 | [Actionable tool results and validation errors](features/P1-F07-tool-results-and-validation-errors.md) | 6 | 6 |
| P1-F08 | [Reliable tool actions and outcome recovery](features/P1-F08-tool-action-recovery.md) | 6 | 6 |
| P1-F09 | [Grouped read-only retrieval](features/P1-F09-grouped-read-only-retrieval.md) | 6 | 6 |

P1-F01/P1-F02 additionally preserve their original approved requirement and test ledgers. Counts here refer to the current completion guide, not an assertion that application tests exist or pass.

## Ownership and shared contracts

The participating owners are: BrokerScope and tooling contracts/diagnostics, SourceResolver and source/metadata handlers, Runner request composition, checkpoints and delivery records, Candidate/result submission owners and receipt finalizers. Keep one rule authority even when several features use it. Use [TOOLS](../contracts/TOOLS.md), [STATE](../contracts/STATE.md), [CONFIGURATION](../contracts/CONFIGURATION.md) and [SDK](../contracts/SDK.md) for shared interfaces; feature documents define the actual behavior and implementation checks. Do not invent incompatible local fields or duplicate persistence to satisfy one feature in isolation.

## Invariants

Preserve immutable source and exact evidence, source-free ordinary persistence, host-controlled acceptance, real producer/attempt identity and independent falsification. Broader research does not grant broader mutation. Readiness and completion are explicit predicates, not inferred from an empty query, a model claim or another agent's summary. Unknown or unsupported input remains visible.

## Phase acceptance

Every feature's required tests and adjacent preserved regressions must pass in the actual selected checkout; cross-feature interactions must pass the integrated traces in [DELIVERY.md](../DELIVERY.md). Validate positive behavior and negative authority/cancellation/retry cases, not only the happy path. Record all failed or unrun checks, actual collection and environment. Document completeness does not certify a running implementation.

## Out of scope

Do not execute a reviewed target, install its dependencies/tools, expose a generic shell to analytical agents, bypass historical compatibility, run paid experiments, mutate live review databases or deploy from this document. Do not introduce speculative services, manager models or new global barriers. New delegated engineering choices are labeled in [ENGINEERING_DECISIONS.md](../ENGINEERING_DECISIONS.md).

Continue with this phase's [implementation plan](IMPLEMENTATION_PLAN.md).
