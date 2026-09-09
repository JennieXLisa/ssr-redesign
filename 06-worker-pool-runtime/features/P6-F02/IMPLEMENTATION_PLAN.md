# P6-F02 — Execution lifecycle and yield: implementation plan

Updated: 2026-09-09. Documentation only. Read the [feature](../P6-F02-execution-lifecycle-and-yield.md), [STATE.md](../../../contracts/STATE.md), P1-F04 checkpoints and P3-F03 answer wakeups. Logical work is durable; model executions are replaceable bounded attempts.

## 1. Central transition owner

Locate TaskService/coordinator claim/lease transitions, worker_guards, worker_finalization, worker_transcripts and worker_context_recovery. Add collaborative WAITING_DEPENDENCY through append-only schema/contract updates. Do not implement state changes directly in the tool handler, UI or scheduler helper.

Retain one active lease per task. Each execution has its own agent_run_id, attempt number, lease/control generation and reservation IDs. Root/logical work identity persists across attempts, but provider conversation and source-delivery intervals do not become portable by copying an object.

Mode-select transitions: legacy attempts retain old state interpretation. Collaborative RUNNING may become PENDING for useful continuation or WAITING_DEPENDENCY for registered unresolved requirements. WAITING_DEPENDENCY becomes PENDING only on a qualifying new disposition or explicit authorized recovery, not a polling model call.

## 2. Validate explicit yield

`yield_work` supplies exact checkpoint_id, reason and request_ids. Resolve the checkpoint for the same work/review/input revision and verify its stored digest. Validate that each blocking request is actually registered for this consumer and current revision; prose saying 'waiting' is insufficient.

The provider response requesting yield must already be a completed accepted exchange. Do not abandon an unknown in-flight provider request and immediately release its reservation. A normal tool-triggered yield happens at the ordinary safe boundary after current tool effects are settled or represented by explicit durable pending operations.

## 3. Atomic task transition

```text
with task_transaction():
    require_current_lease_control_and_input()
    checkpoint = verify_exact_checkpoint_binding()
    requests = load_current_registered_requirements()
    enabling = find_new_available_dispositions(requests)
    if reason == WAITING_FOR_CONTEXT and not enabling:
        new_state = WAITING_DEPENDENCY
    else:
        new_state = PENDING
    record_checkpoint_wait_predicate_and_continuation_reason()
    revoke_old_attempt_write_authority_and_transition(new_state)
    record_exact_yield_operation_receipt()
```

Re-evaluate answers inside the transaction to close the answer-before-wait race. An enabling answer can produce explicit CONTINUE instead if no physical yield is needed, but the returned outcome must be recorded and tested; it cannot silently put the task to sleep.

Normal yield increments continuation accounting, not failure-retry count. Every actual new attempt still gets a new attempt identity and charges real resources. An old checkpoint reference cannot reset the work's cumulative budget or no-progress history.

## 4. End the attempt without another model exchange

After accepting yield, return a host-control outcome to the runner and stop ordinary inference for that attempt. Do not make an extra model call solely to consume the yield ACK. The worker settles its exact usage, operation/result events, runtime receipt and required transcript state through existing finalization.

Release physical model/provider reservations according to actual safe settlement. Task PENDING does not imply the old worker's physical capacity has already been released. The pool refills only its actually available slot; another independently available slot may claim the new attempt through ordinary limits.

An older finalizer can coexist with a successor task lease. It operates on captured original attempt/reservation identities, never the current task row's attempt number. Do not overwrite a successor's state, lease, usage or checkpoint when recording a late predecessor failure.

## 5. Claim a continuation

The claim owner validates current task state, work generation, prerequisite fingerprint, policy and budgets. It issues a fresh lease and bound input token. Build the dossier from current assignment, the exact compatible checkpoint, accepted answer deltas, outstanding requests and relevant interests. Mark inherited hypotheses as prior work and preserve counterevidence.

Initialize source-read intervals empty. Saved source/search cursors remain locators requiring fresh authorization; opaque provider state from another attempt is not reused as if it were a conversation continuation. Any required earlier source must be reread by the new attempt.

A normal checkpoint without yield never creates PENDING or relinquishes the slot. A freshness notice alone never wakes terminal/waiting work. Context request registration alone never yields it.

## 6. Cancellation and recovery

Use existing authenticated control generation and targeted cancellation identity. Recheck before new claims/provider dispatch and before domain writes. Cancellation cannot be inferred solely from a frontend connection closing. A late accepted original operation can be settled by host recovery, but expired/cancelled agents cannot initiate new effects.

On crash, reconcile semantic commits, operation outcomes, provider delivery/usage uncertainty, pending receipts, lease expiry and reservations before deciding to requeue. Silence or slow output is not independent proof that a writer is dead. Existing orphan-recovery evidence and coordinator authority remain required.

A semantically committed investigation result should recover its finalization rather than rerun inference blindly. An attempt with no committed result may retry under its actual failure policy. Waiting is not provider failure; fatal authentication/configuration errors are not normal dependency waits.

## 7. Race fixtures

Fill W scripted slots with analysts waiting for queued helper tasks. After explicit durable yields, W physical slots become reusable and helpers run. Verify no failure-retry charge and real usage settlement. Use W=1 to expose hidden self-deadlocks.

Publish an answer immediately before and after yield commit; the consumer remains runnable or receives exactly one wake. Replay yield and wake receipts and assert one task/lease. Save a checkpoint but do not yield: attempt continues. Supply a foreign checkpoint/request revision and assert atomic rejection.

Delay predecessor finalization, claim a successor, then execute old success/failure/transcript settlement. Snapshot all successor fields before/after; they must remain unchanged. Cancel between prepare/commit and before provider dispatch. Simulate unknown live writer state and prove no unsafe force reclaim. Test legacy mode transitions separately.

## 8. Delivery sequence and exit

Characterize current state/receipt transitions; add collaborative state schemas and public projections; implement yield transaction; wire runner stop/finalization outcome; integrate continuation dossier and wake claim; run all race/cancellation fixtures. No idle persistent worker per inquiry, thread-global task identity, portable hidden reasoning or retry-budget reset belongs here. Completion evidence is a state-transition trace with exact attempt/resource identities, not just final task statuses.
