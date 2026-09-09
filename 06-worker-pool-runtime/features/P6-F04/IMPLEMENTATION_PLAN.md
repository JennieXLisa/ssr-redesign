# P6-F04 — Completion and reconciliation: implementation plan

Updated: 2026-09-09. Documentation only. Read the [feature](../P6-F04-completion-and-reconciliation.md), [STATE.md](../../../contracts/STATE.md), P4-F01 receipt acceptance and P5-F03 unresolved reassessment. An empty dispatch queue, a generated report or exhausted budget is not review completion.

## 1. One completion authority

Locate the existing ReviewService/coordinator completion, export gates, required runtime/transcript acceptance queries and task summaries. Extract a collaborative completion query/validator under that owner. Public status, supervisor decisions and final transition must use it rather than independently count task rows in the controller.

Return a structured completion assessment containing review/input/control generation, canonical inventory progress, outstanding required-work counts, acceptance/reconciliation blockers, physical/financial uncertainty and permitted limitation dispositions. Count distinct obligations, not merely physical attempts. A failed attempt followed by successful continuation does not create a second incomplete canonical unit.

## 2. Enumerate the real closure conditions

Canonical coverage: every included file/unit has a valid required disposition, sealed accepted contribution and canonical file publication, or an explicit permitted unreviewable/limitation disposition. No-hit files remain obligations. Adopted complete units use their real adoption receipts; partial answers do not satisfy them.

Admitted analysis: every accepted lead, focused inquiry, contextual production, investigation, falsification and material reassessment is completed, cancelled under valid policy, or explicitly closed with a recorded limitation. Optional seeds never admitted as required work may remain deferred with their disclosed status; registered leads cannot be relabeled optional solely to close the review.

Dependencies: no live blocking consumer remains unresolved without an explicit closure disposition. Shared producer cancellation and old request revisions must be settled correctly. A context question that became unanswered after producer completion has a durable rerouting obligation.

Acceptance: no required prepared/pending artifact, runtime receipt, transcript turn/prefix seal, canonical parent publication or material-validity transition is stranded. A persisted semantic result with failed required receipt is not complete acceptance.

Execution: no live or uncertain task lease/provider execution/active reservation remains. Unknown financial usage is represented and handled under the budget closure policy, not released as zero. Durable outbox/wake/task-materialization/reassessment intents must be applied or explicitly terminally dispositioned.

Optional freshness interests/notices are not work-completion blockers and must not create artificial never-ending reviews. They close with logical work. They still cannot suppress mandatory stale-input checks.

## 3. Assess using bounded indexed queries

Use existing task/coverage/receipt indexes and new operation/request association indexes. Return bounded blocker samples plus accurate totals from a consistent short database view. Do not load all artifact bodies or scan every transcript to compute a status page.

Distinguish 'no eligible work now' from 'all required work settled'. Waiting on dependency, lease expiry, backpressure, budget, receipt recovery and operator action are separate reasons. The SDK projects those reasons; the controller does not infer them from model log text.

Keep the assessed state fingerprint: review generation, relevant coverage/work mutation sequence and acceptance/validity counters. Every transaction that creates a required obligation or changes closure eligibility must advance the owning generation, or closure must recheck the exact corresponding predicates inside its final transaction. Do not trust a cached count with no invalidation contract.

## 4. Final transition is compare-and-recheck

```text
assessment = assess_completion_in_short_read(review)
if assessment.has_required_blockers:
    return IN_PROGRESS_WITH_BLOCKERS
with review_transaction():
    require_current_control_and_mode()
    require_review_not_already_terminal_or_recover_same_operation()
    if closure_generation_changed(assessment):
        reassess_required_predicates_or_retry()
    require_no_new_required_obligation_or_live_writer()
    commit_terminal_review_disposition_and_receipt()
    retire_nonblocking_interests_for_closed_work()
```

The final transaction must serialize against lead/request registration and availability/material propagation. If report_lead commits first, its new obligation blocks closure. If closure commits first, a later stale attempt cannot create a new lead in that terminal review; its tool outcome is explicit and recoverable, not lost silently.

Never hold a transaction open while waiting for provider results, reading full source, rendering an export or terminating a process. Final closure records a state-as-of fingerprint and disposition. Export is a separate operation and neither triggers nor proves closure.

## 5. Reconciliation worklist

Use a bounded coordinator pass over durable owner-tagged pending operations/intents, keyed by stable IDs and progress cursor. Prioritize integrity/receipt and required wake/materialization work before declaring quiescence. Each item dispatches to its owning idempotent reconciler; no generic 'set task completed' repair function is allowed.

Examples: resolve an existing committed tool-operation receipt; verify/link an already sealed transcript turn; expose a fully accepted artifact and its one availability event; apply a wake to its exact wait generation; reroute an unanswered request from a terminal producer; settle exact predecessor resources without mutating a successor; materialize a unique lead/reassessment task intent.

Record repair success, still-blocked prerequisite or explicit unrecoverable integrity issue. Do not repeatedly count the same immutable event as new work. A pass that reaches its bound returns a continuation and cannot claim reconciliation is globally complete. No model call is required merely to reconcile host metadata.

## 6. Safe lease and orphan recovery

Keep the existing task lease/heartbeat, coordinator session and authenticated child liveness evidence. A slow/stalled transcript or absent UI update is not sufficient proof that an active writer is dead. Do not force reclaim a task while the old process may still hold mutation authority.

After verified expiry/orphan control, settle original attempt identity, revocation generation, usage uncertainty and required receipt state before requeueing. A postcommit semantic result should recover finalization, not be blindly reinvestigated. A successor claim must never be overwritten by predecessor recovery using the mutable current task row.

## 7. Explicit limitation closure

Unfunded or unresolvable required work stays a blocker by default. If the operator chooses an allowed limitation closure, verify actual authenticated control authority, exact review/blocker set and expected generation. Operator-supplied name/reason is audit data, not authorization.

Record which obligations were closed with limitations and why, preserve candidates/evidence/failed attempts, and label the review/report accordingly. A held finding remains not currently upheld. No unsupported/unreviewed file becomes DOCUMENTED, and no missing receipt becomes verified by a generic override.

If configuration/policy does not permit a given limitation closure, reject it explicitly. Do not add an undocumented 'force complete' flag in the controller to bypass the harness.

## 8. Acceptance traces

Empty ready queue with a WAITING_DEPENDENCY consumer: completion false. All candidates dismissed but one required file incomplete: false. All tasks apparently complete but a required transcript receipt pending: false. No findings and all true obligations settled: completion may be true. Budget exhausted with accepted leads deferred: false until explicit allowed limitation disposition.

Race report_lead against final closure using two connections/barriers. In each order, either the lead commits and prevents closure or closure commits and the stale registration is rejected. Repeat for a material challenge and pending artifact availability intent.

Crash midway through each reconciliation item, replay twice and assert one domain effect/availability event/task. Keep optional notices pending for otherwise closed work and verify they do not block closure or reopen it. Test unknown live writer/usage and prove no unsafe success. Compare public completion projection with final transition validator using identical fixtures.

## 9. Delivery and definition of done

Implement obligation queries and state fingerprint first; integrate every obligation-producing transaction; add final compare-and-recheck; add owner-tagged reconciliation and explicit limitation command; wire SDK/supervisor projections. Run closure races and reconciliation fault injection before exposing final completion.

Completion evidence is a blocker matrix, exact state transitions and proof that cached/status views cannot bypass the final gate. No queue-empty heuristic, report-exists heuristic, broad repair SQL, background model poller or force-completion shortcut is permitted.
