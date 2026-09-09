# Collaborative task/review state machine and migration

Contract: `state-v1`. Resolves H01/H06 and the state portion of H07. The machine-readable transition and disposition rows are in `schemas/state-transitions.json`. This is the normative transition matrix for the new runtime; imported historical rows are never scheduled through it. YIELD_SETTLEMENT.md supplies the full settlement protocol, not an alternative ordering.

## SM-R01 — Domains are distinct

Task states: PENDING, LEASED, RUNNING, WAITING_DEPENDENCY, COMPLETED, FAILED, CANCELLED, SUPERSEDED, SKIPPED. New task kinds: FOCUSED_ANALYSIS and CONTEXT_REVIEW alongside SYMBOL_REVIEW, FILE_REVIEW, LINK_REVIEW, INVESTIGATION and FALSIFICATION. FILE_REVIEW means canonical synthesis after symbol-unit review; the old whole-file-alone execution route is not a second supported workflow.

New review states: CREATED, INDEXING, ANALYZING, COMPLETE, COMPLETE_WITH_LIMITATIONS, FAILED, CANCELLED. A blocked review stays ANALYZING with a blocker projection; BLOCKED is a query status, not a second durable review state. New task kinds share ANALYZING eligibility and their own prerequisites; there is no REVIEWING/LINKING/INVESTIGATING/FALSIFYING wave gate. Exports are snapshots of current accepted state, not a prerequisite for closing or a state transition to force findings through a wave.

Agent execution retains CREATED, RUNNING, WAITING_FOR_TOOL and its terminal outcomes COMPLETED, INVALID_OUTPUT, TIMED_OUT, REFUSED, FAILED, CANCELLED. A yielded execution terminates COMPLETED with the new runtime-contract termination_reason YIELDED; its logical task is not complete. An active yield intent can be PREPARED, SETTLING, PUBLISHED, CANCELLED or BLOCKED; these are not task states.

## SM-R02 — Exhaustive task transitions

Every row requires current review ownership, immutable input identity, exact actor/control generation, and one owner transaction. All unlisted pairs are forbidden. Multiple reasons for the same pair are distinct guarded operations, not a blanket permission.

| From | To | Allowed cause and additional guard | Atomic result |
|---|---|---|---|
| PENDING | LEASED | ADMIT: readiness, budgets, no active/unsettled predecessor, valid current input | New lease and actual attempt number; resource reservation and claim event |
| PENDING | COMPLETED | ADOPT_COMPLETE_UNIT: no active lease; full compatible artifact and adoption receipt | Canonical obligation adoption, no fake agent run |
| PENDING | CANCELLED | CANCEL_UNCLAIMED | Cancellation receipt, close interests/consumer eligibility |
| PENDING | SUPERSEDED | RETIRE_UNCLAIMED | Immutable retirement/replacement association |
| PENDING | SKIPPED | DECLARE_NONREVIEWABLE: authoritative inventory disposition only | Explicit exceptional coverage disposition, not clean reviewed coverage |
| LEASED | RUNNING | START: exact lease and dispatch prerequisites | Create/start exact agent, bind actual input and event |
| LEASED | PENDING | RELEASE_UNDISPATCHED or RETRY_SETTLED: prove never dispatched, or full predecessor settlement | Clear lease; preserve actual costs; readiness remains checked |
| LEASED | FAILED/CANCELLED/SUPERSEDED | Terminal failure/control after execution-safety proof | Final predecessor proof then terminal task receipt |
| RUNNING | RUNNING | PREPARE_YIELD or ordinary progress: no successor publication | Durable intent/checkpoint only; preserve lease |
| RUNNING | WAITING_DEPENDENCY | PUBLISH_SETTLED_WAIT: terminal predecessor plus runtime/required transcript receipts; unresolved registered predicate | Clear lease, bind wait generation/checkpoint, publish intent receipt |
| RUNNING | PENDING | PUBLISH_SETTLED_CONTINUATION or RETRY_SETTLED: required settlement and explicit continuation/retry cause | Clear lease; new input delta; exactly-once accounting |
| RUNNING | COMPLETED | COMPLETE_SETTLED: accepted role result and full required terminal settlement | Terminal task, canonical/candidate disposition binding |
| RUNNING | FAILED | FAIL_SETTLED: terminal failed execution, classified unrecoverable/exhausted retry | Visible required-work blocker/limitation, no inferred analytical dismissal |
| RUNNING | CANCELLED/SUPERSEDED | CANCEL_SETTLED/RETIRE_SETTLED: exact predecessor terminated and safe host settlement | No subsequent wake or ordinary model write |
| WAITING_DEPENDENCY | PENDING | WAKE: settled predecessor and current generation; new accepted answer/unresolved disposition satisfies recorded predicate | One explicit continuation delta and ready event |
| WAITING_DEPENDENCY | FAILED | STOP_NO_PROGRESS/DEPENDENCY_UNRECOVERABLE: finite policy disposition | Explicit unresolved required-work outcome |
| WAITING_DEPENDENCY | CANCELLED/SUPERSEDED | CANCEL_WAIT/RETIRE_WAIT: no active execution | Consumer removed; shared producer kept when others remain |
| FAILED | PENDING | EXPLICIT_RETRY: operator/recovery authority, new control generation, settled predecessor, available budget/credit | Audited retry; no rollback of old failures |
| FAILED/CANCELLED | SUPERSEDED | EXPLICIT_RETIRE | Historical task retained, successor is a distinct owned identity |

COMPLETED, SKIPPED and SUPERSEDED have no outgoing execution transitions. A new candidate argument after completion creates a successor revision/task rather than reopening a completed task. PENDING-to-COMPLETED adoption is the sole no-new-agent completion route and must satisfy the canonical unit validator.

Cancellation has two milestones: a durable cancel request/control fence stops new ordinary dispatch immediately; final CANCELLED task state is published after execution safety/settlement or with an explicit irrecoverable-terminal proof. No cancelled task is returned to the normal queue to finish its receipts. Later host reconciliation touches only original receipt/accounting history, never successor input or task state.

## SM-R03 — Claim and wake predicate

A task is claimable only when all conditions hold: mode is collaborative-v1; review is ANALYZING; snapshot is READY; state is PENDING; all required unit/request/candidate input prerequisites match current accepted generations; not_before has passed; failure/continuation budget allows another attempt; provider/host resources can be reserved; no unresolved prepared yield, terminal settlement or active predecessor exists. The same predicate is called by planner, ordinary claim, exact-task claim and recovery admission.

Keep `_terminalize_active_agents` as a fail-closed repair for corrupt historical conditions, not a normal successor-admission mechanism. For a collaborative PENDING row with an unsettled predecessor, return SETTLEMENT_BLOCKED and reconcile it; do not terminalize the predecessor to make the row eligible. PENDING is never proof that physical resources were freed. The claim CAS must compare state, current input generation and last-settlement fence, not only task_id.

An answer arriving while a yield is PREPARED/SETTLING records a durable wake intent but cannot requeue. The finalizer observes it at settled publication. A later wake checks WAITING plus the same wait generation, exact request revisions, current accepted dispositions and settled predecessor fence. ALL/ANY predicates are bounded lists, not user code. Optional freshness notices never wake work.

## SM-R04 — Investigation and completion are total

Candidate workflow disposition is a new revision-owned axis, separate from the existing maturity/evidence fields. Closed dispositions: OPEN, INVESTIGATING, NEEDS_CONTEXT, READY_FOR_FALSIFICATION, DISMISSED, INCONCLUSIVE, CONFIRMED, REFUTED, REVALIDATION_REQUIRED. Existing domain validators determine supported maturity; the disposition does not invent an exploit path.

| Investigator result | Accepted artifact and candidate disposition | Task destination | Successor work | Completion meaning |
|---|---|---|---|---|
| SUPPORT_FOR_FALSIFICATION | Valid complete investigation argument; READY_FOR_FALSIFICATION only after required proof availability | COMPLETED after terminal settlement | One idempotent FALSIFICATION task for exact argument/input revision | Required until independent verdict/receipt/host promotion settles |
| DISMISS_WITH_EVIDENCE | Disproving evidence and scoped rationale; DISMISSED | COMPLETED after terminal settlement | None automatically | Revision disposed; does not assert global program safety |
| INCONCLUSIVE | Explicit unresolved facets and reason; INCONCLUSIVE | COMPLETED after terminal settlement | None automatically; new material/operator request creates explicit successor revision | Limitation contributes to COMPLETE_WITH_LIMITATIONS, never COMPLETE or a supported finding |
| NEED_CONTEXT | Nonterminal progress artifact bound to registered request IDs and checkpoint; NEEDS_CONTEXT | RUNNING through yield preparation/settlement, then WAITING or PENDING | Existing contextual producer tasks; same logical investigation resumes | Open required work until a later terminal analytical disposition |

NEED_CONTEXT uses `record_investigation_progress` (`$defs.InvestigationProgress`), then explicit yield_work. It is not an accepted terminal `submit_investigation` outcome. If submitted to the terminal endpoint, return MORE_ANALYSIS with those available tool actions and no terminal effect. This removes the ambiguity of “terminal NEED_CONTEXT but task still running.” Shape failures, refusals, truncation and timeouts are operational errors, not automatic INCONCLUSIVE/DISMISS.

Falsifier UPHELD publishes an independent verdict; the host promotes to CONFIRMED only when the exact current argument, all material and all required producer/falsifier receipts are valid. REFUTED yields REFUTED and no finding. Falsifier INCONCLUSIVE yields INCONCLUSIVE and an explicit completion limitation; no infinite automatic stronger-model loop. Missing context before a verdict uses the same nonterminal contextual tools. Material counterevidence creates REVALIDATION_REQUIRED and removes current-finding eligibility in the same transaction, preserving prior historical exports.

A semantically accepted result awaiting mandatory receipts remains ACCEPTANCE_PENDING; its task remains non-claimable/settling and cannot create an executable successor. Record successor intent atomically, but eligibility waits for accepted availability. Failed receipt reconciliation is a named blocker, not a provider rerun invitation.

Review closure is one serialized recheck after no writer can still add required work: all canonical obligations have accepted reviewed/explicit exceptional dispositions, required contextual and candidate work is terminal/disposed, no live lease/reservation uncertainty or pending mandatory receipt/material/wake propagation remains. Inconclusive or unsupported required scope produces COMPLETE_WITH_LIMITATIONS with recorded count/reasons. Operationally stranded required work yields BLOCKED/FAILED according to its explicit recovery policy; a depleted budget alone is not successful closure. Optional undelivered notices on terminal work do not block it.

## SM-R05 — Migration is a complete state-machine change

Baseline is `09891721b9d3509a3d618c7a25d3a3f184b0e225`: orchestration/contracts.py, service.py claim selection, admission/recovery/events; db/database.py, db/schema_contract.py and db/migrations; agent/runtime.py/events.py; runtime_receipt.py; transcript/receipt.py/reconciliation.py. These paths are verified locations, not claims that new contracts are implemented.

Migrate only under the project coordinator with proven no active legacy writers. The new runtime does not execute legacy reviews. Require the prior engine/operator to settle/stop old active runs before cutover; never reinterpret an in-flight old receipt. Back up using the existing project backup owner. Retain all old rows as historical, read-only data under their original contract identity; new review rows are collaborative-v1. This is data preservation, not four-way runtime compatibility.

The schema change must cover this inventory as one reviewed migration bundle:

| Surface | Required change and verification |
|---|---|
| tasks and review_runs CHECK constraints | Accept the new state/kind/mode values; preserve historical old values only for historical rows; forbid new legacy execution rows |
| task/agent/review transition triggers | Implement the complete matrix with guarded host operations; protect immutable terminal/history rows and prepared intents |
| task input/status indexes and ready views | Replace role-to-global-review-phase CASE gating with ANALYZING plus exact prerequisites; add predecessor settlement exclusion |
| file_review_units/graphs and dependency/SCC views | Preserve canonical membership/closure and one-adoption semantics; contextual edges are not silently coverage edges |
| work/input/yield/operation tables | Unique immutable revisions, preparation and settlement fences, wait generations and replay keys |
| artifact/prefix/transcript tables | Typed prefix/terminal versions, pending/available eligibility and immutable cross-ledger proof references |
| candidate disposition/lineage tables | Add exact revision-owned workflow dispositions and total successor/completion mapping |
| query/SDK/export/event schemas | New enums, reason fields and current/historical distinction; no unknown-kind rows silently filtered away |
| schema admission fingerprints/migration ledger | Regenerate expected object inventories from the new canonical schema; preserve old migration checksums |
| recovery/driver/completion switches | Handle every new kind/state, prepared yield, pending prefix, no-progress stop and limited completion explicitly |

Use SQLite's documented create-new/copy/drop/rename/recreate procedure when modifying table CHECK constraints: inventory dependent indexes/triggers/views first; disable FK enforcement only outside the exclusive migration transaction if required by the supported migration owner; create replacement tables with final columns; copy every preserved column explicitly; drop/recreate affected views/triggers/indexes in dependency order; verify row counts, immutable result/evidence hashes, foreign_key_check and integrity checks before commit; restore FK enforcement and validate schema fingerprints afterward. Never use writable_schema text surgery or rename the old parent first and hope dependent SQL remains correct. A migration failure rolls back the whole project change; backup remains available. Separate transcript migration cannot be claimed atomic with project migration: mark capability pending until both compatible schemas validate.

The migration ordinal is the next unused entry returned by the selected implementation checkout's ledger; this document deliberately does not invent an ordinal against a moving branch. Its exact file/checksum and final schema inventory are mandatory implementation outputs. That allocation is mechanical, not permission to change the protocol/matrix.

## SM-R06 — Concrete migration and state acceptance

Build a disposable fixture with every old task/agent/review terminal state, explicit pending/active legacy rows, adopted coverage, candidates, transcript receipts, and a rollback-triggering FK. Verify active-old cutover rejection; settled historical rows survive byte-identically and cannot be claimed. For every new task kind exercise planning→claim→start→normal result and failure; prove no old CASE gate strands it.

Enumerate every task state pair: accepted pairs require their named guards, every other pair rejects with zero writes. Exercise all review and agent transitions similarly. Inject crashes before/after yield preparation, terminal event, transcript seal, project receipt link, wait publication and wake. Use real claim SQL in the harness integration suite; the included reference state model only validates the specified ordering.

Test PENDING-to-COMPLETED adoption against simultaneous claim, old callback against a new lease, cancellation during settlement, expired prepared intent, unknown state values, every investigation/falsification outcome, and queue-empty-with-pending-receipt closure. Verify query/SDK serialization sees the same states as SQL. No runtime capability is enabled until schema, broker, scheduler, receipt, query and exporter agree on the same state-contract digest.
