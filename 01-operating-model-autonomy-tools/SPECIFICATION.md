# Phase 1 specification — operating model, agent autonomy, and tools

Version: 0.7  
Status: first phase overview draft; behavior agreements recorded; not approved as
an implementation-complete phase specification.

## Purpose

Give agents room to investigate and collaborate without confusing research access,
canonical assignment ownership, and host-controlled acceptance. Reuse the existing
index, source verification, tool broker, execution, and publication infrastructure.
This is new functional design, not an instruction to alter the separate refactor.

## Feature index

| Feature | Detailed document | Status |
|---|---|---|
| P1-F01 | [Research access and assignment ownership](features/P1-F01-research-access-and-ownership.md) | Direction agreed; first detailed draft. |
| P1-F02 | [Indexed navigation and information retrieval](features/P1-F02-indexed-navigation-and-retrieval.md) | Source selection, pagination, authenticated cursors, indexed lookup and two-step analysis retrieval and subject-specific freshness notices agreed/saved; remaining contracts and integration open. |
| P1-F03 | [Reference-based tool inputs and submissions](features/P1-F03-reference-based-inputs-and-submissions.md) | Behavior saved; implementation details pending. |
| P1-F04 | [Agent-initiated progress checkpoints](features/P1-F04-progress-checkpoints.md) | Behavior saved; implementation details pending. |
| P1-F05 | [Submission and return to analysis](features/P1-F05-submission-and-return-to-analysis.md) | Behavior saved; implementation details pending. |
| P1-F06 | [Independent lead registration](features/P1-F06-independent-lead-registration.md) | Behavior saved; implementation details pending. |
| P1-F07 | [Actionable tool results and validation errors](features/P1-F07-tool-results-and-validation-errors.md) | Behavior saved; implementation details pending. |
| P1-F08 | [Reliable tool actions and outcome recovery](features/P1-F08-tool-action-recovery.md) | Behavior saved; implementation details pending. |
| P1-F09 | [Grouped read-only retrieval](features/P1-F09-grouped-read-only-retrieval.md) | Behavior saved; implementation details pending. |

## Shared meaning

An assignment defines a deliverable and publication authority. An execution attempt
identifies the currently authorized worker activity. Research permissions define
what captured project material the attempt may navigate. These are different
responsibilities; P1-F01 owns their detailed boundary.

Analytical roles include background reviewers, focused analysts, investigators,
falsifiers and file synthesizers. Their reading freedom does not erase differences
in their required results. A synthesizer reads for reconciliation rather than
routinely repeating every child review.

The index and existing IDs are the navigation foundation. Hashes establish source
identity, not interpretive truth. Checkpoints are working progress, not accepted
findings. A registered separate lead transfers follow-up ownership to the harness;
it is not a contextual dependency that the proposing agent must wait on.

## Phase boundary

Phase 1 specifies the tool-facing behaviors in its features. It does not silently
settle general mid-review answer sharing, coverage credit, semantic lead dedup,
new task types, finding gates, scheduling priority, numeric limits, or database
layout. Feature documents track required later-phase dependencies explicitly.
The independent lead-registration boundary already agreed in P1-F06 must not be
weakened into waiting for the proposer's final submission.

## Phase acceptance

The phase is not complete until its nine detailed documents have been discussed,
reviewed, reconciled and paired with an actionable implementation plan. A feature's
approved direction is not proof that code exists or that its integration blockers
are resolved. Documentation and implementation approval remain separate.

See the [implementation plan](IMPLEMENTATION_PLAN.md) and [decision register](../DECISION_REGISTER.md).
