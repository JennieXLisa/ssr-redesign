# P6-F02 — Execution lifecycle and yield: implementation plan

Updated: 2026-09-09. Documentation only. **Use the corrected [hardening contracts](../../../CONTRACT_HARDENING.md); real integration tests are mandatory.** Read the [feature](../P6-F02-execution-lifecycle-and-yield.md), [STATE.md](../../../contracts/STATE.md), [YIELD_SETTLEMENT.md](../../../contracts/YIELD_SETTLEMENT.md), P1-F04 checkpoints and P3-F03 answer wakeups. This amendment removes the previous permission to claim a yielded successor before mandatory predecessor settlement.

## Contract-hardening integration — State migration and exact yielded terminal event

Use state-transitions.json as the exhaustive task/review/agent/intent matrix and MIGRATION_PLAN.md for DDL/SQL/recovery coverage. AGENT_TERMINAL statusCOMPLETED with termination_reasonYIELDED closes only the actual execution; it references yield_intent_id and never completes the logical task. A prefix receipt alone cannot satisfy this terminal settlement.

Generic expired-task recovery inspects prepared intents and original writer/receipt state before changing task eligibility. Permanent invalid mandatory receipts produce an explicit BLOCKED intent/required-work recovery outcome, not a successful PENDING continuation. Reconcile cancellation under the exact captured control fence. Run the real current scheduler/finalizer with transcript sealing deliberately blocked, then all YS interleavings.

Normative source: [hardening contract index](../../../CONTRACT_HARDENING.md). Preserve the existing feature procedure below except where this explicit correction replaces it; implement the linked exact schemas, not a local incompatible approximation.

## 1. One transition authority, three distinct milestones

At harness `0989172`, ReviewOrchestrator owns task claim and delegates connection-scoped orchestration operations; its claim path terminalizes active agents for a PENDING task. Keep task/lease mutation in this authority. The tool broker and controller cannot implement an alternative state machine.

Distinguish durable yield preparation, terminal attempt settlement, and continuation publication. The first does not imply the other two. Select the keep-RUNNING approach: YIELD_PREPARED/SETTLING are yield-intent progress, not new public task states. Introduce WAITING_DEPENDENCY only through H06's full schema/trigger/SQL/recovery/query migration.

Every attempt retains its actual agent_run_id, attempt number, lease/control identity and reservations. Logical work/root identity can persist, but execution identity, opaque provider continuation and source-delivery credit do not transfer to a new attempt.

## 2. Validate and prepare an explicit yield

Resolve yield_work's checkpoint/reason/request references under the current work and immutable input revision. Verify stored checkpoint digest, ownership and requested dependency revisions. A prose statement that the agent is waiting is not a registered predicate.

The requesting provider response must be complete and accepted. Earlier tool effects must have known or explicitly reconciled outcomes; do not abandon an in-flight mutation and release its capacity. In one short orchestration transaction:

```text
require task RUNNING and exact active agent/attempt/control/lease/input
verify checkpoint and consumer request revisions
recover same operation if already prepared
otherwise persist one yield intent, wait generation and checkpoint/predicate binding
record the prepared operation receipt
leave task RUNNING and retain its lease
```

Normal progress checkpointing has no yield effect. Duplicate preparation cannot allocate another wait generation or reset no-progress/budget counters. Do not publish PENDING, WAITING_DEPENDENCY, or another attempt's input from this tool handler.

## 3. Stop inference; settle the original execution

The prepared outcome stops the ordinary agent turn loop. Do not send another model request solely to consume its acknowledgment. Ordinary model write authority ends, but the captured original-attempt host finalization authority remains valid for reconciliation.

Finish actual tool/event records, terminal agent outcome, usage/reservations, runtime receipt and required terminal transcript receipt through their existing owners. Keep the original task lease and heartbeat/finalization supervision until publication or explicit controlled failure. Do not hold an ssr.db transaction open while writing/sealing transcript.db.

A normal yielded execution needs an exact versioned terminal/runtime representation without declaring the logical task complete. Defining and testing that representation is a gate, not permission to append arbitrary new event fields to the old receipt validator. A per-turn prefix seal is not a substitute for mandatory predecessor terminal settlement in this yield protocol.

## 4. Publish continuation after the settlement barrier

Implement one orchestration-owned guarded function following YS-R08. It requires the exact intent, predecessor terminal outcome, valid runtime receipt, required verified transcript seal, resolved operation outcomes and valid input/checkpoint/wait generation. If already published, return the original receipt.

Re-evaluate current accepted answer dispositions inside the final transaction. Publish PENDING for useful voluntary continuation or an enabled wait predicate; otherwise publish WAITING_DEPENDENCY. Bind the checkpoint and explicit input deltas, clear the old lease, record the continuation generation and event, and seal the publication receipt atomically. A cancelled or retired work item never becomes runnable.

Physical capacity and accounting use original reservation identities. Unknown usage stays conservative; PENDING is not an accounting refund. The task cannot be claimed before mandatory predecessor settlement even if a different model slot happens to be idle. Completion and resource queries must expose settling/blocker state rather than counting it as successful waiting.

## 5. Wake and claim

An answer arriving during RUNNING/prepared settlement only records its wake information. The finalizer will check it. An answer after WAITING publication may trigger one guarded WAITING-to-PENDING transition after verifying the settled predecessor and current wait generation. Duplicate/stale events cannot create a second continuation.

Every ordinary, exact-task and recovery admission path must exclude unresolved yield preparation/settlement. Generic `_terminalize_active_agents` is not a mechanism for making an intentional prepared yield claimable. Test the actual current claim path, not just a mock queue predicate.

Once PENDING is legitimately published, normal admission checks resource, policy and input readiness, and issues a fresh attempt/lease/input token. Build context from the exact checkpoint, authorized accepted deltas, outstanding requests and work-scoped interests under the 170k context policy. Initialize source-delivery intervals empty; reopening material source remains explicit.

## 6. Cancellation, lease expiry, and recovery

Retain authenticated targeted cancellation and control-generation checks. A disconnected frontend is not cancellation. If cancellation wins during settlement, host recovery finalizes the old execution/history but cannot requeue the cancelled work. Guarded updates may not overwrite a successor or independently committed terminal task state.

Expired/interrupted-task recovery first inspects yield intents. Resume the exact finalization if its proofs allow it; do not infer successful settlement from silence, elapsed time, a checkpoint or task status. No new model attempt is required just to import an already sealed transcript receipt. Permanently invalid receipt/writer outcomes require the specified failure/recovery table; until the STATE_MACHINE/MIGRATION_PLAN integration tests pass, the feature is not enableable.

Crash after preparation, transcript seal, project receipt reconciliation and continuation publication must each have a deterministic replay path. Recover accepted domain work rather than rerunning inference. Any late callback is fenced to its original attempt/reservations and cannot alter the successor's checkpoint, lease, counters or current inputs.

Normal continuation counts once and is separate from operational retry credit. Neither continuation nor recovery resets cumulative spend. Existing investigation predecessor/successor regression tests remain required, but their legacy early-progress behavior cannot justify reintroducing this yield race.

## 7. Race and capacity fixtures

Run YS-T01–YS-T18 from the normative contract. In particular, block finalization after durable preparation, call both real claim variants from worker B, and prove no new lease and no superseding terminal event. Then complete settlement and verify one new task-state publication.

Exercise all answer-before/after-prepare/seal/publication orderings, cancellation between every durable boundary, duplicate operation and wake replay, wrong checkpoint/revision, missing required receipt, old finalizer after successor claim, and lease expiry during settlement. Snapshot successor fields before/after every late callback.

Fill W=1 and W=100 virtual slots with parents needing helpers. Host finalization must finish without acquiring an additional model slot. Refill only after original executions cannot consume their reservations; waiting parents then occupy no model slots. Failed settlement must be visible, not hidden by preemption or fabricated success.

These are specified scenarios, not results run by this documentation amendment.

## 8. Implementation order and exit

Map current orchestration/receipt owners; freeze H06 state migration and yielded-terminal contracts; add durable intent preparation; wire terminal runner control; reuse exact finalization; add guarded continuation publication and settling-aware claim/recovery checks; integrate wakeups and context-budgeted continuation; execute all adversarial fixtures.

No second scheduler, notification agent, task-state mutation inside tool handlers, thread-global identity or arbitrary replay of old leases is allowed. The exit evidence is a real trace proving that predecessor settlement precedes successor claim, with the corresponding transcript/runtime/resource identities. Document correction alone does not close that gate.
