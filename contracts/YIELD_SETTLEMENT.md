# Yield preparation, settlement, and continuation publication

Revision: 1 · 2026-09-09  
Status: corrective design contract; not implemented or runtime-tested.  
Addresses: Codex review finding 1 against harness `09891721b9d3509a3d618c7a25d3a3f184b0e225`.  
Owners: P6-F02 execution/finalization, P3-F03 answer wakeups, P7-F01 state migration.

This contract replaces the premature-yield sequences in STATE.md and the P3-F03/P6-F02 implementation plans. It does not reopen the already agreed analyst workflow: waiting still releases execution capacity, follow-up work remains independent, and no model call is required merely to finalize a yield.

## 1. Confirmed baseline and failure

At the reviewed harness revision, `ReviewOrchestrator.claim_task()` selects PENDING tasks and then invokes `_terminalize_active_agents()` before leasing the selected task. Its comment explicitly assumes a PENDING task has no active execution. The earlier design made a yielding task PENDING while its predecessor still had terminal events and receipts to settle. Another available pool slot could therefore reclaim the task and terminalize that predecessor.

Source: [orchestration/service.py, pinned revision](https://github.com/JennieXLisa/source-review-harness/blob/09891721b9d3509a3d618c7a25d3a3f184b0e225/src/ssr/orchestration/service.py#L1158-L1260). Existing state contracts are in [orchestration/contracts.py](https://github.com/JennieXLisa/source-review-harness/blob/09891721b9d3509a3d618c7a25d3a3f184b0e225/src/ssr/orchestration/contracts.py). The new WAITING_DEPENDENCY state is not present in that baseline.

This is a confirmed incompatibility between the proposed design and the inspected claim path, not a claim that the live application already implements the proposed yield API.

## 2. Selected correction: keep the task RUNNING while settlement is pending

**YS-R01.** A successful yield request first records a durable preparation. The task remains RUNNING with the same attempt/lease identity. Do not expose PENDING or WAITING_DEPENDENCY, clear the lease, increment the next attempt, or enable a successor claim at this point.

**YS-R02.** Represent YIELD_PREPARED/SETTLING as host-owned yield-intent progress, not two new public task states. The logical task remains RUNNING until the final publication transaction. The public projection may explain the settling reason without pretending the agent is still performing inference. This is the selected approach, not a choice left to the implementer.

**YS-R03.** The prepared yield contains the exact review/task/agent/attempt/control identity, input-revision digest, checkpoint ID/hash, operation identity, wait generation, reason, and required request revisions/predicate. Reference existing records rather than copying source or transcripts. Never expose raw lease credentials through a tool or public DTO. Storage/migration is owned by P7-F01; no separate database is required.

**YS-R04.** A preparation is a terminal *runner control outcome*, not task completion. Once it commits, the runner stops ordinary inference and new model-initiated mutations for that attempt. It must not make another provider request solely to consume the yield acknowledgment. Host finalization remains authorized for this exact attempt. Prepare only after the requesting provider response is complete and earlier tool effects in that exchange are settled or explicitly reconciled; do not race preparation with an unaccounted mutation in the same tool batch.

## 3. Preparation transaction

Prepare/validate the safe checkpoint and request references outside the write lock. In one short transaction owned by ReviewOrchestrator or its connection-scoped delegate:

```text
require current RUNNING task and exact active agent/attempt/control/lease
require current immutable input token and checkpoint identity/hash
require the blocking requests actually belong to this consumer and revision
recover an identical already-committed yield preparation, if present
otherwise allocate one wait generation and persist one prepared yield intent
persist the yield operation's PREPARED acknowledgment with that intent identity
leave task state, attempt count, and lease ownership unchanged
```

**YS-R05.** Checkpoint saving and yield preparation are distinct. An ordinary checkpoint does not stop the runner, relinquish the lease, or create continuation readiness. Replaying yield preparation does not allocate another generation or count another continuation.

The tool operation acknowledges the committed *preparation effect* and returns the intent identity. Its ordinary operation journal may therefore be COMMITTED while the separate yield intent is still PREPARED; that must not mean continuation is published. Recovery returns the same preparation receipt and separately queries intent progress. Do not leave visible effects behind a generic operation row whose meaning still says nothing was committed.

The handler can record whether a useful answer currently exists, but this observation is advisory. It is not the final WAITING/PENDING decision: the finalizer must re-evaluate it after settlement. A useful voluntary yield with no dependency predicate is eligible for PENDING only after settlement. A source-free CONTINUE response before any yield preparation may be supported by a separate specified API; it is not an alternative hidden inside this terminal yield protocol.

## 4. Settle the exact predecessor before making continuation runnable

**YS-R06.** Finish the original attempt's event graph, usage and tool-operation records, runtime receipt, and required terminal transcript capture through the existing owners. A yielded execution can terminate normally without completing its logical task; its terminal outcome must be explicitly represented in the versioned runtime contract. Do not forge full task completion or reuse another attempt's terminal receipt.

The settlement barrier requires all of the following:

| Proof | Required meaning |
|---|---|
| Terminal execution outcome | The exact producer attempt has a durably recorded terminal outcome for the prepared yield; no ordinary model execution or untracked tool mutation remains active. |
| Runtime receipt | The receipt validates the actual terminal graph and yield/input/checkpoint association under the selected contract. A task-status flag alone is not a receipt. |
| Required transcript receipt | When capture is required, the original attempt's terminal capture is sealed and verified. No invented prefix or waiving a failed required capture. |
| Operation reconciliation | The yield operation and prior relevant effects have known durable outcomes; replay does not require repeating accepted inference or domain mutations. |
| Resource settlement | Original attempt/provider reservations are settled or conservatively held by their original identities under the accounting contract. Unknown provider usage is not set to zero. Physical capacity is reusable only once no original execution can consume it. |

**YS-R07.** Keep heartbeat/host finalization supervision until success, explicit failure, or takeover by authorized recovery. A lease deadline passing is not evidence that receipt settlement succeeded. Recovery must inspect the prepared intent before any generic expired-task requeue or `_terminalize_active_agents()` path. It may resume exact host settlement; it must not make the task claimable merely to obtain a new worker to finish the old receipts.

An authorized recovery coordinator may settle the captured predecessor after its ordinary lease expires, but only under the existing exclusive recovery/writer-safety proof and an exact settlement fence. This is not an extension of the expired agent's model-write authority, and it cannot borrow a successor's lease or input generation.

Do not hold an ssr.db write transaction while sealing transcript.db, waiting for I/O, or calling a provider. Finish and verify transcript-side records first, then reconcile their exact source-free receipt into the project database. There is no distributed-transaction claim between the two databases.

## 5. Final continuation publication transaction

**YS-R08.** Once the barrier is verified, use a single short project transaction to publish the continuation outcome. The finalizer uses captured predecessor identities, not `tasks.attempt_count` read as an identity substitute.

```text
with orchestrator_transaction():
    intent = load_prepared_yield_for_exact_operation()
    if intent already published:
        return its immutable publication receipt
    require predecessor terminal and its required settlement proofs valid
    if task already CANCELLED/retired under authorized control:
        settle original intent as cancelled/history without updating task state
        return its exact cancellation-settlement receipt
    require task still RUNNING and matching intent's attempt/control/lease
    require original checkpoint and input/wait-generation bindings valid
    if a current authorized cancellation command wins this transaction:
        publish that terminal disposition; do not enqueue a continuation
    else:
        dispositions = load_current_accepted_dispositions_for_exact_wait_predicate()
        if voluntary_yield or predicate_enables_next_action(dispositions):
            destination = PENDING
            bind checkpoint plus explicit accepted continuation deltas
        else:
            destination = WAITING_DEPENDENCY
        publish destination, wait predicate, checkpoint and continuation generation
        clear the old task lease as part of this same transition
    mark intent published and persist exact settlement/publication receipt
    append the task event and reconcile original reservation disposition
```

Cancellation reconciliation must never revive a terminal work item. If an independent cancellation authority already moved the task to CANCELLED, finalize the old intent as cancelled/history without overwriting that state; the guarded RUNNING transition is not attempted. A changed input generation or other unexpected ownership mismatch is an explicit reconciliation conflict, not permission to apply the old checkpoint to new state.

**YS-R09.** The event and publication receipt become visible with the state change. Claim eligibility must additionally exclude any unresolved prepared yield or settling predecessor for this continuation generation. Direct/exact-task claims and ordinary pool claims use the same guard. The claim path must not terminalize the prepared predecessor as a normal way to enable this continuation.

## 6. Serialize answer availability with settlement and waiting

**YS-R10.** An answer becoming available while the consumer is RUNNING with a prepared yield records its durable answer association/wake intent only. It does not change the task to PENDING. The finalizer's publication transaction rechecks accepted dispositions and chooses PENDING when a new relevant disposition enables progress.

If the finalizer publishes WAITING_DEPENDENCY first, a later answer handler rechecks the same work and wait generation, predecessor-settlement barrier, and predicate before atomically changing WAITING_DEPENDENCY to PENDING. Duplicate events are idempotent. A stale-generation event cannot satisfy a newer request revision. No shared transaction remains open between these operations.

| Answer timing | Required result |
|---|---|
| Before yield preparation | Preparation still leaves RUNNING; finalizer observes the answer after settlement. |
| After preparation, before receipts seal | Durable answer association retained; task remains non-claimable. |
| Concurrent with final publication | Shared task authority serializes the transactions; finalizer sees it or subsequent wake sees WAITING. |
| After WAITING publication | One eligible wake changes WAITING to PENDING. |
| After cancellation/completion | Artifact may remain valid for other consumers; this consumer is not reopened. |

## 7. Failure and recovery rules

**YS-R11.** Preparation failure commits no half-yield and leaves the prior execution state unchanged. After successful preparation, a response-delivery interruption does not resume ordinary model activity; host recovery reuses the prepared operation and finalizes the exact predecessor.

**YS-R12.** A crash after transcript seal but before project reconciliation recovers the existing seal. A crash after receipt reconciliation but before task publication retries the guarded final transaction. A crash after publication returns the existing publication receipt. These cases do not generate another model attempt, wait generation, or continuation charge solely to reconstruct the old outcome.

A permanently invalid required receipt or unrecoverable writer state cannot become a successful yield. Report a named settlement blocker and use the explicit failed-attempt/recovery policy only after original execution termination is established. Do not claim that a failed receipt was repaired by launching the successor. Exact failure-state mapping remains a hardening gate for the full state machine; until specified, the capability is not enableable.

**YS-R13.** A late predecessor callback may update only its own still-unsettled receipt/accounting records through the recovery authority. It cannot publish a new continuation generation, revoke a successor lease, rewrite a newer checkpoint, or charge the successor for the predecessor's usage. With this protocol, a successful-yield successor never starts before mandatory predecessor receipts are sealed; existing legacy investigation-race tests remain regression evidence, not authorization to reintroduce the early-yield sequence.

**YS-R14.** Waiting must release usable execution capacity after safe settlement without a provider poll. With W=1, host-only finalization must complete without obtaining another model slot; the freed slot can run the helper. With W concurrent yields, each predecessor must settle independently. Do not add a second agent pool just to work around incorrect state ordering.

## 8. Concrete implementation steps

1. In the selected checkout, trace `ReviewOrchestrator.claim_task`, direct-task admission, recovery helpers, agent termination, transcript finalization, and runtime-receipt reconciliation. Record the exact SQL/view predicates involved. The inspected baseline is not permission to assume unchanged paths.
2. Add the yield-intent representation and uniqueness/fencing constraints through the migration owner. Keep public task RUNNING during preparation. Define the terminal yielded-execution receipt contract before enabling the handler.
3. Change the `yield_work` adapter to validate and commit preparation only, returning a typed terminal runner-control result. Do not clear the lease in this handler. Block further ordinary dispatch after that result.
4. Reuse original-attempt finalization owners. Carry the intent ID through finalization without adding nested transactions that independently commit. Required transcript failures remain visible.
5. Add one guarded continuation-publication function owned by orchestration. All successful yield and yield-recovery paths call it only after settlement proof. Do not duplicate the readiness predicate in the broker, scheduler, and wake handler.
6. Make wake application distinguish PREPARED/RUNNING from published WAITING. Add settlement-aware guards to every claim/recovery path and completion/resource projection. Waiting, settling, and runnable work must be distinguishable in public metadata.
7. Run the reference scenarios below against the real claim/finalization code in an isolated project database, plus existing successor-isolation tests. Record results before closing the gate.

## 9. Acceptance scenarios (specified; not executed here)

| ID | Fixture/interleaving | Required assertion |
|---|---|---|
| YS-T01 | Prepare yield; block terminal transcript sealing; call real claim from worker B. | No successor lease; task RUNNING; predecessor not terminalized by reclaim. |
| YS-T02 | Same setup with exact-task admission. | Same exclusion as ordinary claim; no bypass. |
| YS-T03 | Make answer available before preparation. | Still no early PENDING; after successful settlement, publish PENDING once. |
| YS-T04 | Publish answer after preparation but before runtime/transcript seal. | Answer retained, task RUNNING until barrier, final destination PENDING. |
| YS-T05 | Barrier-order answer commit against final WAITING/PENDING transaction. | Either immediate post-settlement PENDING or one subsequent wake; never a lost waiter. |
| YS-T06 | No answer until after WAITING is published. | Lease cleared only with final publication; matching-generation wake produces one PENDING. |
| YS-T07 | Replay prepare and publication operations. | One intent/generation, one continuation-accounting change, same receipt. |
| YS-T08 | Crash after transcript seal, before project receipt import. | Reconcile original seal; no fake terminal capture or new inference. |
| YS-T09 | Crash after receipt import, before continuation publication. | Retry only final guarded transaction; preserve checkpoint and input identity. |
| YS-T10 | Crash after publication before acknowledgment. | Recover committed destination; do not re-publish or re-charge. |
| YS-T11 | Cancel work during settlement. | No PENDING/wake after cancellation; original receipts settle as history. |
| YS-T12 | Lease expires while an intent is prepared. | Generic recovery cannot expose PENDING before exact settlement/recovery policy. |
| YS-T13 | Required runtime or transcript receipt is invalid. | Explicit blocker/failure; no successful continuation claim. |
| YS-T14 | Deliver a stale wait-generation answer or mismatched input token. | No unearned wake or checkpoint rebinding. |
| YS-T15 | Late predecessor callbacks after a legitimately claimed successor. | Successor task/lease/checkpoint/reservations remain byte-for-byte unchanged. |
| YS-T16 | W=1 and W=100 scripted yielding parents. | Host settlement needs no model slot; only safely released capacity is refilled; no oversubscription. |
| YS-T17 | Attempt yield while an earlier tool mutation is unresolved. | No preparation that pretends the operation settled; explicit reconciliation/validation outcome. |
| YS-T18 | All mandatory receipts sealed but provider usage remains uncertain. | Preserve conservative accounting/reservations; do not invent zero cost or free capacity still in use. |

## 10. Gate status

This document corrects the design order. It is not evidence that any harness test passed. Remaining prerequisites are the full state-machine migration, exact yielded-runtime/input contracts, cancellation/failure transition map, and tested integration with current receipt/resource owners. The coordinated hardening milestone tracks them. Do not enable collaboration from this document alone.
