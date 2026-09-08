# SSR collaborative-review design

A separate documentation workspace for the new `source-review-harness` design
and its integration with `ssr-control`.

**Publication status:** published to [`JennieXLisa/ssr-redesign`](https://github.com/JennieXLisa/ssr-redesign)
on branch `main`, at the user's explicit request. Repository visibility remains
public. The [content checkpoint](https://github.com/JennieXLisa/ssr-redesign/commit/50d0d31ff6b15c6192b2fc176b53cd7c65c5027b)
contains all 39 current Markdown files from the saved P1-F02 v0.7 package, with
byte-identical content verified by the Git tree hash. This publication-status
update does not approve new design choices. See the [publication record](PUBLISH_HANDOFF.md).

Historical save statements inside feature documents describe their original local
checkpoints; they are not the current GitHub publication status. Superseded
checkpoint folders remain in the previously supplied archive; see [history](history/README.md).

**Design status:** the eight phases, nine Phase 1 features, Phase 1 behavior
agreements, P1-F01 implementation direction, and P1-F02 source-reading/pagination, cursor
authentication, exact indexed symbol lookup and two-step analysis retrieval and subject-specific freshness notices have
been agreed in conversation.
Saving a first draft does not mean every contract or implementation detail has
been reviewed. No new runtime behavior is claimed to exist.

## Read in this order

Start with [PHASES.md](PHASES.md), then [DECISION_REGISTER.md](DECISION_REGISTER.md).
For the current phase, read its [specification](01-operating-model-autonomy-tools/SPECIFICATION.md),
[implementation plan](01-operating-model-autonomy-tools/IMPLEMENTATION_PLAN.md),
and the relevant feature document.

The hierarchy is **main roadmap → phase → feature → detailed behavior,
implementation steps, tests, and unresolved decisions**. A feature document owns
its detailed requirements; phase documents link them rather than reproduce them.

## Phase index

| Phase | Specification | Implementation plan | Status |
|---|---|---|---|
| 1 | [Operating model, agent autonomy, and tools](01-operating-model-autonomy-tools/SPECIFICATION.md) | [Plan](01-operating-model-autonomy-tools/IMPLEMENTATION_PLAN.md) | Nine features agreed; P1-F02 source reads, cursors, indexed lookup and two-step analysis retrieval and subject-specific freshness notices saved; remaining choices open. |
| 2 | [Security discovery and analysis strategy](02-security-discovery/SPECIFICATION.md) | [Plan](02-security-discovery/IMPLEMENTATION_PLAN.md) | Scope placeholder only; discussion not started. |
| 3 | [Contextual collaboration and delegation](03-contextual-collaboration/SPECIFICATION.md) | [Plan](03-contextual-collaboration/IMPLEMENTATION_PLAN.md) | Scope placeholder only; discussion not started. |
| 4 | [Shared knowledge, evidence, and whole-project coverage](04-knowledge-evidence-coverage/SPECIFICATION.md) | [Plan](04-knowledge-evidence-coverage/IMPLEMENTATION_PLAN.md) | Scope placeholder only; discussion not started. |
| 5 | [Investigation, independent falsification, and findings](05-investigation-falsification-findings/SPECIFICATION.md) | [Plan](05-investigation-falsification-findings/IMPLEMENTATION_PLAN.md) | Scope placeholder only; discussion not started. |
| 6 | [Worker-pool scheduling and runtime](06-worker-pool-runtime/SPECIFICATION.md) | [Plan](06-worker-pool-runtime/IMPLEMENTATION_PLAN.md) | Scope placeholder only; discussion not started. |
| 7 | [Technical contracts, persistence, and integration](07-contracts-persistence-integration/SPECIFICATION.md) | [Plan](07-contracts-persistence-integration/IMPLEMENTATION_PLAN.md) | Scope placeholder only; discussion not started. |
| 8 | [Validation and implementation plan](08-validation-delivery/SPECIFICATION.md) | [Plan](08-validation-delivery/IMPLEMENTATION_PLAN.md) | Scope placeholder only; discussion not started. |

## Phase 1 feature index

| Feature | Document | Status |
|---|---|---|
| P1-F01 | [Research access and assignment ownership](01-operating-model-autonomy-tools/features/P1-F01-research-access-and-ownership.md) | Direction agreed; first detailed draft saved; integration mapping open. |
| P1-F02 | [Indexed navigation and information retrieval](01-operating-model-autonomy-tools/features/P1-F02-indexed-navigation-and-retrieval.md) | Source reads, authenticated cursors, indexed lookup and exact analysis retrieval and freshness notices saved; final interfaces and integration remain open. |
| P1-F03 | [Reference-based tool inputs and submissions](01-operating-model-autonomy-tools/features/P1-F03-reference-based-inputs-and-submissions.md) | Behavior agreed; detailed implementation discussion pending. |
| P1-F04 | [Agent-initiated progress checkpoints](01-operating-model-autonomy-tools/features/P1-F04-progress-checkpoints.md) | Behavior agreed; detailed implementation discussion pending. |
| P1-F05 | [Submission and return to analysis](01-operating-model-autonomy-tools/features/P1-F05-submission-and-return-to-analysis.md) | Behavior agreed; detailed implementation discussion pending. |
| P1-F06 | [Independent lead registration](01-operating-model-autonomy-tools/features/P1-F06-independent-lead-registration.md) | Behavior agreed; detailed implementation discussion pending. |
| P1-F07 | [Actionable tool results and validation errors](01-operating-model-autonomy-tools/features/P1-F07-tool-results-and-validation-errors.md) | Behavior agreed; detailed implementation discussion pending. |
| P1-F08 | [Reliable tool actions and outcome recovery](01-operating-model-autonomy-tools/features/P1-F08-tool-action-recovery.md) | Behavior agreed; detailed implementation discussion pending. |
| P1-F09 | [Grouped read-only retrieval](01-operating-model-autonomy-tools/features/P1-F09-grouped-read-only-retrieval.md) | Behavior agreed; detailed implementation discussion pending. |

## Collaboration and document status

Discuss one feature's significant choices with the user. Ask when a requirement
is ambiguous; do not invent defaults. Record approval, write the feature's detail,
and review the result before calling it implementation-ready. Save approved feature progress to GitHub or local files and report the actual
location. Do not repeatedly reopen decisions already agreed unless a concrete
conflict requires it.

Detailed drafts are saved for [P1-F01](01-operating-model-autonomy-tools/features/P1-F01-research-access-and-ownership.md)
and the approved source-reading/pagination, cursor, indexed-lookup and analysis-retrieval portions of
[P1-F02](01-operating-model-autonomy-tools/features/P1-F02-indexed-navigation-and-retrieval.md).
P1-F02 remains in discussion; P1-F03–P1-F09 save their earlier approved behaviors
and open implementation questions. Phases 2–8 contain scope and status placeholders,
not invented specifications or delivery plans. Their `features/README.md` files
keep the folder structure explicit without inventing feature names.

Each completed feature document must cover purpose, baseline and reuse, precise
requirements, interfaces, ordered implementation, state/persistence, limits on
scope and complexity, tests, dependencies, and readiness. See the phase plan for
how these sections are used. Feature numbers are not an execution-stage order.

## Boundaries

The modular refactor is a separate workstream. This repository does not authorize
changes to either implementation repository, its existing root specification,
its historical design packages, or live review data. No new manager model,
framework, permission service, database, or fixed worker ratio is implied.
Approximately 100 workers is the user's scale example, not a mandatory default.

Keep source-derived facts, agreed requirements, implementation guidance, and
open decisions visibly distinct. Pin code references to the inspected commit;
verify their new owners after the refactor. [SOURCES.md](SOURCES.md) records the
reference baseline and its limits. Never treat a snapshot-bound evidence hash as
proof that a model interpretation is correct.

Earlier roadmap and feature checkpoint copies remain unchanged in the supplied
archive, as explained in [history](history/README.md).
