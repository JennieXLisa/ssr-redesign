# SSR collaborative review — agreed documentation phases

Version: 1.0  
Recorded: 2026-09-08  
Status: Phase sequence approved; detailed phase specifications and implementation plans are not yet approved.

## Purpose and scope

This is the saved roadmap for the new collaborative-review design for
`source-review-harness` and its integration with `ssr-control`.

The user approved the eight phases below. They are discussion and documentation
boundaries, not sequential runtime stages. The future worker pool must not be
made to wait for a repository-wide phase merely because its specification was
written in this order.

The modular refactor and the repository `AGENTS.md` files are a separate
preparatory workstream. They do not replace this roadmap or authorize the new
runtime behavior. Refactor completion has not been established by this record.

This package records the agreed conversation. It is not a new code audit,
implementation, benchmark, migration, deployment, or amendment to the existing
root `SPECIFICATION.md`. Existing specifications, design packages, and handoffs
remain untouched.

## Working agreement

For each phase:

1. Discuss its actual design choices, relevant current behavior, alternatives,
   failure cases, and tradeoffs. Reuse prior answers instead of asking the user
   to approve the same decision again.
2. Record agreed choices and explicit unresolved questions. A recommendation
   becomes a requirement only after agreement; silence is not approval.
3. Write that phase's detailed `SPECIFICATION.md` and `IMPLEMENTATION_PLAN.md`
   from the agreed decisions. Clearly label any remaining proposed material.
4. Review both documents with the user, correct them, and record their status.
5. Proceed to the next phase. Reopen an earlier decision explicitly when a later
   discussion reveals a conflict; identify affected requirements and plans.

Keep substantial engineering contributions in the discussion: actual mechanism,
ownership, failure behavior, alternatives, compatibility, and verification—not
merely a paraphrase of the user's workflow. Conversely, do not invent limits,
roles, schedulers, or approval rules and present them as settled.

Document approval is separate from approval to implement, commit, push, install,
restart, migrate live state, or run paid model experiments. This task authorizes
saving the roadmap and developing the new documents collaboratively.

## Approved phases

| Phase | Topic | Specification scope | Implementation-plan scope | Current status |
|---|---|---|---|---|
| 1 | Operating model, agent autonomy, and tools | Agent responsibilities, ownership, autonomous decisions, tool capabilities, and host authority. Retained, extended, and replaced capabilities. | Existing owners and tool/runtime integration points; incremental changes; authorization and contract tests. | IN DISCUSSION |
| 2 | Security discovery and analysis strategy | User-facing code, sensitive operations, project wrappers, controls, and issues without conventional sinks. How analysts select, investigate, and revise questions. | Reuse of inventory/search/relationships; discovery and analyzer integration where agreed; observation provenance, limitations, and evaluation cases. | NOT STARTED |
| 3 | Contextual collaboration and delegation | Contextual review requests; reuse or routing to existing/new work; shared requests; answers; contradictions; supplementary work; continuation. | Request/answer lifecycle, routing, dependencies, continuation integration, and coordination/failure tests. | NOT STARTED |
| 4 | Shared knowledge, evidence, and whole-project coverage | Published observations and analysis; when results are usable; evidence/knowledge reuse; canonical coverage; corrections and conflicts. | Changes to acceptance/publication/query owners, provenance and coverage integration, atomicity, and replay tests. | NOT STARTED |
| 5 | Investigation, independent falsification, and findings | Candidate handoffs, end-to-end investigation, independent challenge, early findings, and later counterevidence/reassessment. | Integration with existing candidate/evidence/falsification authorities; admission and submission rules; export and reassessment validation. | NOT STARTED |
| 6 | Worker-pool scheduling and runtime | Shared continuous admission, prioritization, protected coverage, dependency waiting, yielding/resuming, budgets, cancellation, and recovery. | Existing pool/planner/worker integration; durable accounting and readiness; concurrency, restart, and failure tests. | NOT STARTED |
| 7 | Technical contracts, persistence, and integration | Consolidated module ownership, exact cross-phase contracts, durable state/events, and harness–controller SDK compatibility. | Coherent schema/API/event changes where necessary, versioning, migration and compatibility strategy, and integration tests. | NOT STARTED |
| 8 | Validation and implementation plan | End-to-end acceptance, regression protection, quality/cost evaluation, and release criteria for the agreed design. | Reconcile the phase-local plans into dependency-ordered delivery slices, with exit criteria, compatibility checks, and separately authorized rollout. | NOT STARTED |

## Phase detail and boundaries

### Phase 1 — Operating model, agent autonomy, and tools

Establish what the analyst is responsible for, what it may investigate, what it
can ask the harness to do, and what only the host can authorize or accept.
Separate analytical responsibility from an execution attempt and from canonical
coverage ownership. Do not use the current restrictive tool permissions as an
unexamined requirement for the new design.

Discuss existing tools individually or in coherent capability groups: retain,
extend, replace, or add. Include navigation, analysis retrieval, contextual
requests, incremental publication, and continuation at the capability level.
Detailed collaboration and publication semantics remain owned by Phases 3–4;
exact shared schemas are consolidated in Phase 7.

### Phase 2 — Security discovery and analysis strategy

Develop a broad, extensible way to find and investigate security-relevant
behavior. Include process execution, filesystem reads/writes and related
operations, dynamic execution/loading, database and network operations,
parsing/deserialization, native memory/lifetime behavior, security decisions,
and business invariants without familiar dangerous APIs.

Resolve meaning through binding, call mode, arguments, wrappers, and context;
function names alone are not vulnerability conclusions. Include externally
exposed entrypoints, source/operation/control-centered analysis, stored or
asynchronous influence, and explicit unsupported/unknown cases. Decide where
host code, an applicable analyzer, and model interpretation each help. Exact
pool scheduling and resource allocation remain Phase 6 decisions.

### Phase 3 — Contextual collaboration and delegation

Specify how an analyst requests another component's review with its question,
relevant facts, evidence, and assumptions. Address queued, running, completed,
failed, and supplementary review work. Determine when to inspect context
locally, join work, or delegate.

Define useful answers, contradictions, missing answers, unexpected leads,
request identity, shared consumers, delivery, and continuation. A contextual
request must not automatically imply spawning another worker. Coordinate with
Phase 4 on when an answer becomes accepted and shareable, without silently
choosing a sealed-unit-only or mid-review policy in advance.

### Phase 4 — Shared knowledge, evidence, and whole-project coverage

Specify the meaning and acceptance of facts, hypotheses, questions, conditional
summaries, evidence, contextual answers, and canonical review results. Establish
which outputs may be reused, by whom, at what acceptance boundary, and under
which assumptions.

Resolve early answer publication versus full-file completion and any reuse that
can satisfy canonical obligations. Reading a file is not by itself complete
coverage. At the same time, do not mandate a duplicated pass merely because
useful analysis originated in a focused inquiry. Preserve necessary complete
coverage and make incomplete/unsupported work explicit.

### Phase 5 — Investigation, independent falsification, and findings

Define the handoff from a lead to a grounded candidate and from investigation
to a fresh independent challenge. Distinguish starting an investigation from
having its complete answer already available. Investigators and falsifiers must
have the capabilities agreed in Phase 1 and the collaboration behavior agreed
in Phase 3.

Keep supported, refuted, and inconclusive outcomes distinct. Define early
finding visibility during unfinished coverage, later counterevidence,
reassessment, and historical versus current conclusions through explicit agreed
contracts. Reuse existing evidence and candidate authorities where appropriate.

### Phase 6 — Worker-pool scheduling and runtime

Start from continuous admission as an existing capability, not a missing feature.
The user's example is approximately 100 active workers; this is not an approved
hard-coded count or evidence of measured throughput.

Specify how useful leads, dependency answers, investigation, falsification, and
background coverage compete for capacity. Include shared-provider limits,
prioritization, preventing coverage starvation, waiting without consuming a
worker slot, continuation, finite accounting, failure isolation, cancellation,
and restart. Ratios, time limits, queue algorithms, and fan-out caps require
agreement; do not import old proposal defaults automatically.

### Phase 7 — Technical contracts, persistence, and integration

Consolidate the prior phases into exact contracts rather than redesigning their
behavior through implementation details. Resolve shared identifiers, schemas,
state/event ownership, tool surfaces, failure semantics, acceptance boundaries,
SDK projections, and compatibility.

Map to the refactored implementation as actually delivered. Keep one owner for
each rule, explicit dependency directions, and existing invariants where retained.
Do not assume a module move has happened or allocate migrations from an old
snapshot. Cross-repository changes must respect the public SDK boundary.

### Phase 8 — Validation and implementation plan

Assemble all phase-local plans into buildable delivery slices in dependency order.
Documentation order need not equal implementation order. Do not automatically
reuse the older proposal's M0–M3 modes or treat partial delivery as completion.

Include end-to-end collaborative traces, preserved coverage, accepted evidence,
independent challenge, waiting/recovery, counterevidence, and controller visibility.
Define quality, latency, duplicate-work, coverage, and cost measurements without
claiming unmeasured benefits. Distinguish implementation acceptance from live
experiments and release/deployment authorization.

## Two deliverables per phase

The folders below are reserved names in this roadmap, not a claim that all files
exist or that their contents have been drafted.

```text
01-operating-model-autonomy-tools/
02-security-discovery/
03-contextual-collaboration/
04-knowledge-evidence-coverage/
05-investigation-falsification-findings/
06-worker-pool-runtime/
07-contracts-persistence-integration/
08-validation-delivery/
```

Each phase eventually contains:

```text
SPECIFICATION.md
IMPLEMENTATION_PLAN.md
```

### Required specification detail

- Status, scope, terminology, and explicit exclusions.
- Relevant observed baseline and retained/extended/replaced capabilities.
- Agreed requirements with stable identifiers and an owning phase.
- Responsibilities, permissions, inputs/outputs, and relevant state transitions.
- Normal flows and concrete examples.
- Failure, concurrency, cancellation, and recovery behavior where relevant.
- Security, evidence, coverage, and compatibility implications.
- Acceptance criteria and cross-phase dependencies.
- Open decisions and clearly labeled proposals, separate from requirements.

### Required implementation-plan detail

- Verified starting point and assumptions; reconcile with refactor outputs.
- Existing component owners and proposed changes, without unnecessary rewrites.
- Incremental implementation slices and their prerequisites.
- Contracts, storage, migration, configuration, and SDK impacts where applicable.
- Tests/fixtures per slice, including negative and race cases where relevant.
- Compatibility, recovery, rollback considerations, and unchanged invariants.
- Definition of done, verification evidence, and remaining limitations.
- Decisions that must be resolved before a slice is implementable.

Each plan must be useful on its own, but Phase 8 assembles and reconciles the
whole delivery order. Cross-phase references should point to the owning
requirement, not introduce a competing definition.

## Current checkpoint

- Approved: eight-phase sequence and separate detailed specification/plan pairs.
- Current phase: **1 — Operating model, agent autonomy, and tools**.
- Phase 1 specification: not drafted or approved by this save operation.
- Phase 1 implementation plan: not drafted or approved by this save operation.
- Phases 2–8: not started; their open choices must not be pre-decided in Phase 1.
- Next discussion: agent/host ownership and tool capabilities, using the
  previously agreed direction and existing implementation as the reuse baseline.

See [DECISION_REGISTER.md](DECISION_REGISTER.md) for settled direction and
explicitly unresolved proposals, and the [Phase 1 discussion brief](01-operating-model-autonomy-tools/DISCUSSION.md).
