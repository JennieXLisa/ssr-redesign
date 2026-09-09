# P3-F03 — Accepted answers and inquiry continuation

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P3-F01`, `P3-F02`, `P4-F01`, `P6-F02`

## Purpose and concrete outcome

Once useful answers are available, an analyst resumes from its prior state rather than starting the same analysis again. A reviewer can answer one question before finishing all coverage.

## Existing implementation and ownership

Reuse existing result validators, source/evidence readers, acceptance receipts, task leases and checkpoint recovery. Add an independently accepted answer artifact and request-resolution transaction.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P3-F03-R01.** publish_context_answer supplies answered facets, checked scope, assumptions, counterevidence, unknowns and refs for the exact request revision. It may be nonterminal for the producer’s canonical assignment.

**P3-F03-R02.** An answer becomes usable only after its own semantic, source and required turn-level receipts pass. Private partial prose or merely finished task status is insufficient. No forced wait for whole-file publication.

**P3-F03-R03.** An explicit yield atomically binds the current checkpoint and unresolved blocking requests before relinquishing the slot. A query or nonblocking context request alone never yields work.

**P3-F03-R04.** When an answer, contradiction or explicit unresolved disposition enables a meaningful next action, the host makes the consumer task PENDING once. It need not wait for all other answers unless the registered prerequisite expression requires them.

**P3-F03-R05.** Consumer resumes with exact new answer refs, previous checkpoint and outstanding questions. The logical work ID stays fixed; a new execution attempt has independent lease, accounting and source-read credit.

**P3-F03-R06.** No automatic candidate promotion follows from a reviewer’s answer. The investigator must integrate it, inspect material source and account for contradicted assumptions.

## Inputs, outputs, and state

Consumer prerequisites use a small explicit ALL/ANY set of request/facet refs, not an arbitrary executable expression language. Default blocking request is an independent enabling event: wake the consumer when it has at least one new disposition to process; the analyst may re-yield after updating its checkpoint.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Implement answer artifact preparation

Use source-free analysis schema and exact input revision. Register evidence with original producers, then await only the contribution’s required turn receipts.

### Step 2: Commit request resolution and wake eligibility

The publication/availability transaction records request-answer association and a durable task-wake intent. The task owner revalidates generation and converts WAITING_DEPENDENCY to PENDING idempotently.

### Step 3: Make yield race-safe

Within one transaction recheck whether any required answer already became available. If yes, return CONTINUE or yield-to-PENDING instead of sleeping forever on an already-satisfied event.

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
