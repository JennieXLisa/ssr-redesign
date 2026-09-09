# Dependency-ordered implementation delivery

Version: 2.0 · 2026-09-09. This is the implementing agent's primary work sequence. The eight phases organize documentation; the R0–R7 slices below organize implementation. They are **not** new runtime modes.

## Before any code change

Use the selected real worktree and installed import identities. Read its AGENTS.md and implemented SPECIFICATION.md. Inspect the observed modular-refactor maps but do not assume those branches are accepted or deployed. Preserve unrelated edits. This package authorizes no live controller restart, provider spend, schema change on real data or target execution. A separate implementation task must authorize code work.

## R0 — Baseline and contract inventory

Deliver a source/module/test map, current schema/protocol/package versions and the exact public SDK consumer checks. Run relevant existing tests before changes, including tool/source checks, distributed publication, investigation finalization/successor races, query/SDK compatibility and controller supervision. Verify unittest and pytest collection and public imports from the intended source/wheel. Record actual failures, never label them pre-existing without evidence.

Exit: owners and unchanged authority are documented; baseline tests have recorded outcomes; selected implementation branch is explicit. No new default or schema number is inferred from old design documents.

## H0 — Contract hardening (blocking gate after baseline inspection)

Read [CONTRACT_HARDENING.md](CONTRACT_HARDENING.md). R0 factual inspection and isolated contract fixtures may proceed, but do not begin affected R1–R7 feature implementation on the basis of the current draft. Close the listed receipt, synthesis, context, exact SDK/role, state migration, outcome, operation-IR and cutover contracts first. Structural document validation alone does not close H0.

The initial yield correction is [YIELD_SETTLEMENT.md](contracts/YIELD_SETTLEMENT.md): prepare durably while RUNNING, finish the original attempt's mandatory settlement, then publish WAITING_DEPENDENCY or PENDING atomically. Do not implement the former early-requeue sequence or use generic claim cleanup to terminate a settling predecessor.

The old-mode/default and four legacy/refactored-pair statements below are suspended requirements pending H09's explicit cutover scope. Preserving existing source/evidence and mutation authorities does not automatically require retaining the old runtime workflow. No destructive migration or live installation follows from this gate.

Exit: each H0 item has a concrete normative contract, executable contract fixtures, an owner and reviewed traceability. Runtime/installed-package validation remains a separate requirement during implementation. H10 refreshes baseline, manifest and publication/validation records over the final tree; do not reuse stale checksums as certification.

## R1 — Shared contract foundation, access and basic navigation

Implement shared outcome/reference/operation contracts and the new immutable mode/capability identity. Extend BrokerScope research policy separately from assignment ownership. Add file locator queries, symbol/file/relationship navigation, verified source pages and the persistent key codec. Preserve all legacy schemas/hashes and stored inputs. Include current source-selection/reference/error tests before expanding agent permissions.

Features: P1-F01, P1-F03, P1-F07, core P1-F08; source/catalogue/symbol/relationship part of P1-F02; P7-F01/P7-F03 foundations.

Exit: cross-file research succeeds without foreign coverage authority; malformed/stale/foreign refs fail; pagination exactness and installed source imports pass; no optional publication shortcut enabled.

## R2 — Search, checkpoints, repair, and grouped retrieval

Implement positioned per-file matcher and search continuation, strict decoding/byte maps, progress limits and match previews. Add ordinary checkpoints and return-to-analysis policy, then grouped read-like retrieval with aggregate budgeting and final delivery accounting. Use the existing runner, not a second agent loop.

Features: remainder of P1-F02 source/search; P1-F04/P1-F05/P1-F09 and complete P1-F08 delivery accounting.

Exit: page-size invariance, long-line/multibyte/zero-length/timeout cases, checkpoint CAS/restart and rejection→research tests pass. No duplicate read credit or resource resets. Regex capability is pinned/tested or explicitly unavailable; no fallback engine.

## R3 — Accepted artifacts, independent leads, availability and notices

Implement typed artifact registry, independent model-turn receipts, accepted availability epochs/sequence and exact result queries. Add durable interests, original-H registration, H-bounded lists and request-bound notice acknowledgment. Implement report_lead through CandidateService with atomically recorded follow-up intent; the scheduler may still keep new-mode model execution disabled until R5.

Features: P4-F01/P4-F04, P1-F06, analysis/notice portion of P1-F02, P7-F01 persistence.

Exit: an accepted lead survives proposer failure; artifact remains pending until genuine required receipts; no gap in lookup/registration; no lost ACK update; historical and current artifact identities preserved; no claim that whole application is delivered yet.

## R4 — Context collaboration, early answers and coverage adoption

Implement contextual request equivalence/routing, canonical-review promotion, running-reviewer inbox/deltas, answer publication, explicit yield and atomic wake. Add shared-consumer cancellation, cycle/depth/fan-out checks. Adopt only complete compatible canonical unit artifacts, retaining existing file publication.

Features: all Phase 3, P4-F02/P4-F03, P6-F02 transitions.

Exit: all workers can yield and helpers run; answer/yield race loses nothing; queued/running/completed routing works; source-free accepted mid-review answer unblocks consumer without false coverage. Incomplete answers never satisfy full units.

## R5 — Continuous mixed-role scheduling and candidate adjudication

Enable prerequisite eligibility in every relevant planner/claim/SQL/role/submit/query gate for collaborative-v1. Keep the continuously refilling pool, add coverage entitlement and required-work priority, finite resource/fan-out controls and current candidate revision readiness. Integrate fresh falsification, host promotion, counterevidence holds and successor revisions before exposing current findings. Add full-work closure/reconciliation.

Features: Phases 5–6; coordinated P7-F01 guards/projections.

Exit: candidate A completes fresh upheld falsification/host promotion while candidate B and unrelated coverage remain active; no phase/wave barrier; all W=1/2/3/100 virtual resource/fairness/restart traces pass. A later control discovery holds export immediately. No overall completion from empty queues or exhausted budget.

## R6 — Security discovery and controller experience

Add operation/entrypoint catalogue, deterministic prioritization of required work, bounded focused roots and conditional wrapper/channel summaries. Optional trusted analyzers run through host capability boundaries. Ship public collaborative SDK, child protocol, negotiated controller views and API/SSE/frontend projections. Preserve source/transcript sensitivity and lazy loading.

Features: Phase 2 and P7-F02/P7-F03 completion. Domain readiness remains identical with optional analyzer disabled.

Exit: no-hit canonical coverage continues, API aliases/shadowing and stored-flow fixtures behave correctly, no one-task-per-alert explosion, mixed capacity plans work, all four legacy/refactored SDK pairs and clean packaged controller assets pass.

## R7 — Integrated acceptance and separately authorized evaluation/release

Run all acceptance suites and crash injections, archive exact trace/contract/build identities and remaining limitations. Perform live-gateway protocol tests and quality/cost ablations only under separately supplied authorization/budget. Produce exact paired wheel/source/hash coordinates in clean build environments. Release/default enablement is an operator decision after these gates.

Features: Phase 8 and final cross-phase validation.

Exit: full implementation acceptance is recorded; unrun live/quality gates are explicitly NOT_RUN rather than silently passed. Documentation completeness is not a release claim.

## Developer rules that prevent overengineering

One operation owner per state transition. Shared contracts live once; feature code calls those owners. Use source-bound queries and small typed services in the existing modular harness, not manager models, new message servers, universal workflow engines or cloned stores. Preserve receipts, exact source and schema history. Local helper names may vary, but the selected public semantics, transactions and proof boundaries cannot drift silently.

When an empirical/environmental gate fails, explain the actual failure and keep dependent capability disabled. A material design change gets a written amendment and impact/test map; do not quietly weaken requirements or ask a model to fill missing host state.

## Required handoff record for each R slice

Record starting/ending commit, touched owner map, public/schema/contract changes, tests/collection/results, migration fixtures, failure-injection outcomes, installed import/artifact hashes, compatibility pairs, unresolved actual blockers and absence/presence of live actions. Keep temporary release coordinates out of durable AGENTS.md. Do not assert speed/cost improvement without P8-F02 measurements.
