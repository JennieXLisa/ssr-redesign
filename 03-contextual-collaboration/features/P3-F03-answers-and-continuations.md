# P3-F03 — Accepted answers and inquiry continuation

Version: 1.1 · Updated: 2026-09-09
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P3-F01`, `P3-F02`, `P4-F01`, `P6-F02`

**Contract-hardening revision:** apply the concrete corrections in [P3-F03/IMPLEMENTATION_PLAN.md](P3-F03/IMPLEMENTATION_PLAN.md) and the [hardening index](../../CONTRACT_HARDENING.md). Earlier summary wording is not a substitute for the exact input, receipt, state, synthesis, context and cutover contracts.

## Purpose and concrete outcome

Once useful answers are available, an analyst resumes from its prior state rather than starting the same analysis again. A reviewer can answer one question before finishing all coverage.

## Existing implementation and ownership

Reuse existing result validators, source/evidence readers, acceptance receipts, task leases and checkpoint recovery. Add an independently accepted answer artifact and request-resolution transaction.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P3-F03-R01.** publish_context_answer supplies answered facets, checked scope, assumptions, counterevidence, unknowns and refs for the exact request revision. It may be nonterminal for the producer’s canonical assignment.

**P3-F03-R02.** An answer becomes usable only after its own semantic, source and required turn-level receipts pass. Private partial prose or merely finished task status is insufficient. No forced wait for whole-file publication.

**P3-F03-R03.** An explicit yield atomically records a durable preparation binding the current checkpoint and registered blocking requests while retaining RUNNING and the original lease. Continuation state is published only after mandatory predecessor settlement. A query or nonblocking context request alone never yields work.

**P3-F03-R04.** An answer, contradiction or explicit unresolved disposition may enable continuation according to the registered prerequisite predicate. During prepared yield/settlement, the host records that disposition without making the consumer PENDING. After mandatory predecessor settlement, the finalizer or a generation-checked wake transaction may publish PENDING idempotently. No answer event may reopen terminal work.

**P3-F03-R05.** Consumer resumes with exact new answer refs, previous checkpoint and outstanding questions. The logical work ID stays fixed; a new execution attempt has independent lease, accounting and source-read credit.

**P3-F03-R06.** No automatic candidate promotion follows from a reviewer’s answer. The investigator must integrate it, inspect material source and account for contradicted assumptions.

## Inputs, outputs, and state

Consumer prerequisites use a small explicit ALL/ANY set of request/facet refs, not an arbitrary executable expression language. Default blocking request is an independent enabling event: wake the consumer when it has at least one new disposition to process; the analyst may re-yield after updating its checkpoint.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Implement answer artifact preparation

Use source-free analysis schema and exact input revision. Register evidence with original producers, then await only the contribution’s required turn receipts.

### Step 2: Commit request resolution and wake eligibility

The publication/availability transaction records request-answer association and a durable task-wake intent. For a consumer already in WAITING_DEPENDENCY, the task owner verifies predecessor settlement and the current wait generation before converting it to PENDING idempotently. For a consumer still RUNNING with a prepared yield, record the wake information only; the settlement finalizer performs the later continuation decision.

### Step 3: Prepare yield, settle the predecessor, then publish continuation

The initial orchestration transaction validates the exact active attempt, input revision, checkpoint and registered dependency revisions, then records a durable yield intent and wait predicate. The task remains RUNNING with its original lease. This transaction must not publish PENDING or WAITING_DEPENDENCY, clear the lease, or permit a successor claim.

After preparation commits, the runner stops ordinary inference and new model-initiated effects while retaining exact-attempt host finalization authority. Once the predecessor satisfies the mandatory settlement barrier in [YIELD_SETTLEMENT.md](../../contracts/YIELD_SETTLEMENT.md), a separate guarded orchestration transaction rechecks cancellation, ownership, input identity and current accepted answer dispositions. It publishes PENDING when the registered predicate enables continuation, otherwise WAITING_DEPENDENCY, and clears the original lease atomically with that publication.

Answers arriving during preparation or settlement retain their durable associations/wake intents but cannot requeue the consumer. The finalizer rechecks them before publishing continuation. If WAITING_DEPENDENCY is published first, a subsequent qualifying answer may cause one idempotent, generation-checked transition to PENDING.

### Step 4: Build compact continuation

Attach only deltas and references, not full transcripts. Keep prior false paths and changed assumptions; do not replicate obsolete source dumps.

## Failure, concurrency, and recovery

If the producer dies after answer acceptance, the accepted answer remains usable. If its required turn transcript is incomplete, it stays pending and consumers see that blocker. Duplicate publication cannot wake multiple concurrent attempts. Full pool means PENDING queue, not oversubscription.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P3-F03-T01 | Answer accepted before producer file done | Consumer can resume; coverage still open. |
| P3-F03-T02 | All active analysts wait on helpers | Slots released so helpers run. |
| P3-F03-T03 | Answer races with yield | No lost wakeup. |
| P3-F03-T04 | One of several requests returns contradiction | Consumer may resume and revise its hypothesis. |
| P3-F03-T05 | Producer dies after valid answer receipt | Answer survives. |
| P3-F03-T06 | Duplicate answer/wake event | One eligible continuation, no duplicate lease. |

## Do not overengineer or expand scope

No raw transcript as answer, automatic finding truth, busy polling model calls, or one new persistent agent identity per small dependency.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
