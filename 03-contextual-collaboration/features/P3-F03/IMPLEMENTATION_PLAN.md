# P3-F03 — Answers and continuations: implementation plan

Updated: 2026-09-09. Documentation only. **Use the corrected [hardening contracts](../../../CONTRACT_HARDENING.md); real integration tests are mandatory.** Read the [feature](../P3-F03-answers-and-continuations.md), [STATE.md](../../../contracts/STATE.md), [yield settlement contract](../../../contracts/YIELD_SETTLEMENT.md), P4-F01 publication and P6-F02 finalization. This amendment replaces the unsafe early requeue in the previous section 4; it does not claim an implementation or runtime test.

## Contract-hardening integration — Executable answer/proof and total continuation contracts

Use ContextAnswer/ContextResult with exact requested facet coverage and artifact hashes; close prefix proof through runtime-prefix-v1 and transcript-prefix-v1. A terminal context worker seals its accepted answer reference, while a canonical reviewer can publish that same typed answer nonterminally and continue.

Implement the YIELD_SETTLEMENT state ordering with state-transitions.json's task/agent/yield-intent domains. Use the finalizer's exact current wait-generation CAS and settled predecessor fence for both normal and exact-task claims. Run the existing YS scenarios plus context facet/unknown schemas and two-database prefix reconciliation. The Python reference state tests are specifications, not a substitute for real orchestration/service.py race tests.

Normative source: [hardening contract index](../../../CONTRACT_HARDENING.md). Preserve the existing feature procedure below except where this explicit correction replaces it; implement the linked exact schemas, not a local incompatible approximation.

## 1. Validate an answer for the exact question revision

`publish_context_answer` supplies request_id, request_revision, outcome, analysis, evidence/source refs, unresolved facets and scope_checked. Resolve the request under the producer's routed authority and current review/snapshot. Reject an unknown revision or unrelated producer; broad source permission alone is not permission to answer a hidden request.

Outcomes are ANSWERED, CONTRADICTED_ASSUMPTION, INCONCLUSIVE and NEEDS_DIFFERENT_SCOPE. Identify which requested facets were checked and which remain unresolved. A contradicted assumption is useful analytical output, not validation failure. A malformed structure or reference is a rejection, not INCONCLUSIVE.

Prepare source-free analysis and verified references through P1-F03. Preserve producer authorship and source-delivery evidence. Do not use another worker's private notes as supporting evidence or infer complete scope from a generic summary. Exact new-role terminal schemas and input tokens remain H05 prerequisites.

## 2. Independent acceptance during an active review

Create an immutable contextual-answer artifact from the validated payload. Its producer receipt must authenticate the completed exchange that requested publication; acceptance must not depend on that operation's own acknowledgment. Required transcript mode needs a genuine versioned prefix/turn contract, not a forged full-attempt completion. **Implement and test the exact PREFIX_RECEIPTS.md contract before enabling this nonterminal publication path.**

Absent required receipts, keep ACCEPTANCE_PENDING with explicit blockers. Once the receipt owner verifies all prerequisites, P4-F01's short availability transaction marks the artifact AVAILABLE and emits its review sequence event. Do not expose pending content through request status.

The same project transaction associates the exact request/revision with the accepted answer and records a unique, recoverable wake/re-evaluation intent for compatible consumers. This is not permission to make a settling consumer runnable. If scheduling is deferred, reconcile the durable intent; do not rely on an in-memory callback.

## 3. Determine which consumers can continue

Compare the consumer's exact request/facet revisions, source/assumption/policy compatibility and accepted outcome. Historical answers may remain useful history without satisfying newer inputs. Use explicit associations, not name similarity.

The default predicate is at least one new relevant disposition available to process. A bounded ALL or ANY request set remains data, not an arbitrary expression interpreter. Contradiction or an explicit scope/uncertainty outcome can enable a next action without proving a vulnerability.

Availability never promotes a candidate by itself. The resumed analyst may reject its hypothesis, revise its question or yield again. Ordinary optional freshness notices do not wake unrelated or terminal work.

## 4. Prepare yield without exposing a successor

The current harness claim path selects PENDING and terminalizes active agents before reclaim. Therefore the earlier `transition_for_continuation(PENDING)` and direct RUNNING-to-WAITING prescription before receipt settlement are withdrawn.

Save the checkpoint through P1-F04, then use the single orchestration-owned preparation path:

```text
with task_transaction():
    require exact RUNNING task/agent/attempt/control/lease and input revision
    verify checkpoint ID/hash and registered request revisions
    recover an identical already-prepared yield, or persist one new intent
    persist wait generation/predicate and prepared-operation receipt
    leave task RUNNING, with the original lease and attempt identity
```

After preparation, the runner stops ordinary inference and new model-initiated effects. It requires no model call to consume a yield ACK. Host finalization retains exact predecessor authority. Keep the task non-claimable until the [settlement barrier](../../../contracts/YIELD_SETTLEMENT.md) is satisfied; merely preparing a terminal tool response is insufficient.

An answer available before or during preparation is not lost: its association is durable and will be checked again at final publication. Recording an answer does not change the consumer state while the predecessor is still settling.

## 5. Publish waiting/runnable state after settlement

Only the finalization/orchestration owner performs this transaction:

```text
with task_transaction():
    require exact prepared yield and original task ownership
    require predecessor terminal, runtime receipt valid,
            and required terminal transcript receipt sealed/verified
    recheck cancellation, input/checkpoint identity and wait generation
    re-evaluate current accepted dispositions for the exact wait predicate
    publish PENDING if a disposition enables progress, else WAITING_DEPENDENCY
    atomically bind checkpoint/deltas, clear old lease and seal yield publication
```

A voluntary useful yield without dependencies publishes PENDING after the same barrier. A cancelled/retired consumer never gets requeued. Unexpected changed ownership or input is a reconciliation conflict, not authority to rebind the old checkpoint. See YS-R08 for already-committed cancellation behavior.

A wake arriving after WAITING publication uses the same task owner, validates the settled predecessor and current wait generation, and publishes one PENDING transition with its explicit answer delta. An answer arriving earlier leaves a durable intent and cannot bypass the finalizer. These two orderings close the answer/wait race without making the old execution reclaimable.

Duplicate answer/wake/yield receipts are idempotent. A full pool leaves a legitimately PENDING continuation queued. Request publication never grants another concurrent lease or transfers source-read credit.

## 6. Construct the resumed context

At claim, preserve the logical task/root identity and create a new attempt and lease. Bind the new input revision to the exact compatible checkpoint, accepted answer deltas/dispositions, outstanding requests and changed assumptions. Keep prior hypotheses and counterevidence distinguishable. Use compact recorded context rather than the whole transcript.

The new attempt's source-delivery intervals start empty. It must reopen material source when its result contract requires it. A cursor or summary is not proof that the new attempt already inspected those bytes. Dossier construction and actual provider submission are additionally gated by H04's final-request context algorithm.

## 7. Failure and recovery

A producer crash before accepted answer availability leaves no usable answer; the router may recover or reassign required work. An independently accepted answer survives later producer failure, subject to its own valid prefix receipt. A missing prefix receipt remains ACCEPTANCE_PENDING rather than generating a fake wake.

A consumer crash after yield preparation must resume exact host settlement; generic lease expiry cannot immediately requeue it. Crash after transcript seal reconciles the existing seal. Crash after task publication recovers its immutable receipt and existing continuation rather than cloning work. Invalid mandatory receipts block successful yield publication.

Consumer completion/cancellation removes only that consumer's eligibility. Other consumers may still use the answer. Invalidation before claim or a mismatched input revision requires current re-evaluation; repeated inconclusive answers use finite request/continuation limits, not automatic success.

## 8. End-to-end and race tests

Preserve the primary trace: A requests B's contextual review, saves progress, prepares yield, finishes receipt settlement, then waits; B publishes an independently accepted answer while its canonical file remains unfinished; A becomes PENDING and resumes. Assert all source, input, producer and capacity identities and absence of premature candidate promotion.

Add a barrier inside A's transcript finalization and call the real ordinary and exact-task claim paths from another worker. Both must fail to claim A, and `_terminalize_active_agents` must not terminate A as a reclaim side effect. Release the barrier and verify one settled waiting/runnable publication.

Publish an answer before preparation, between preparation and seal, concurrent with final publication and after WAITING. Every order leads to post-settlement continuation or one wake. Test stale wait generations, cancellation during settlement, lost ACK, duplicate intents, invalid receipts and late predecessor callbacks. Reuse YS-T01–YS-T18 rather than inconsistent local variants.

Test W=1 and full-pool scripted dependencies: host-only finalization must require no spare model slot; only safely released slots may run helpers. Checkpoint-without-yield must keep running. Test ALL and ANY predicates, a contradicting disposition, and no inferred full-coverage credit.

## 9. Delivery sequence and exit

Close H03/H05/H06 contracts; implement answer preparation and pending/available association; implement durable wake intents; implement yield preparation plus finalizer publication; wire exact continuation dossiers; run claim/finalization/answer race fixtures. This feature is not complete merely because the happy-path answer handler changes WAITING to PENDING. No model polling, unfinished private-note handoffs, early requeue or separate persistent-agent framework is permitted.
