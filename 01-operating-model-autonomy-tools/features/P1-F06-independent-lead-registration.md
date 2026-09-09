# P1-F06 — Independent lead registration

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P1-F03`, `P1-F07`, `P1-F08`, `P4-F01`, `P5-F01`

**Contract-hardening revision:** apply the concrete corrections in [P1-F06/IMPLEMENTATION_PLAN.md](P1-F06/IMPLEMENTATION_PLAN.md) and the [hardening index](../../CONTRACT_HARDENING.md). Earlier summary wording is not a substitute for the exact input, receipt, state, synthesis, context and cutover contracts.

## Purpose and concrete outcome

A reviewer can report a separate source-grounded suspicion and continue its assignment. The harness durably owns the lead and follow-up immediately, even if the original reviewer later fails.

## Existing implementation and ownership

Reuse CandidateService seed creation, evidence preparation, candidate provenance and canonical investigation scheduling. Add an authorized nonterminal producer path rather than publishing private symbol proposals accidentally.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P1-F06-R01.** Registration accepts a specific hypothesis/question, observed facts, exact permitted subject/source/evidence refs and unknowns. A complete exploit path or known CWE is not required; unknown categories do not silently reject valid work.

**P1-F06-R02.** In one ssr.db transaction record the SEEDED candidate, registration receipt and a ready-or-blocked independent investigation task or durable scheduling intent. A success acknowledgment means the durable handoff exists, not that an investigator ran.

**P1-F06-R03.** No dependency on the proposer’s terminal result or file synthesis may gate the new lead. Validate its own producer turn and relevant source receipts independently; required transcript gaps are explicit acceptance blockers for that turn, not a whole-file barrier.

**P1-F06-R04.** Return CREATED, ASSOCIATED_EXISTING or RECORDED_WAITING with exact allowed IDs and reason. A full pool queues; lack of runtime capacity never erases accepted registration or preempts a healthy worker.

**P1-F06-R05.** The proposing agent has no duty to poll, wait for or manage investigation. A separate contextual request is used when its original work actually needs an answer.

**P1-F06-R06.** Exact retry identity and exact originating proposal lineage can reuse a lead. Same file, sink, vulnerability category or similar prose can only suggest a duplicate relation; preserve distinct claims unless their complete equivalence is established.

## Inputs, outputs, and state

Input is report_lead in TOOLS.md. The durable record is the existing candidate with an explicit registration origin and associated task, not a new leads database. Candidate priority is provisional scheduling metadata; severity remains unset. Explicit source refs are converted to canonical evidence through P1-F03 before acceptance.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Add role capability and normal tool dispatch

Expose report_lead to analytical roles, including synthesis and falsification for genuinely separate concerns. Do not let the tool complete the original task or force a provider conversation restart.

### Step 2: Validate one self-contained handoff

Prepare evidence/prose and check current authority outside the short commit. Require the requested check to explain the uncertainty, not an exploit recipe or fabricated proof.

### Step 3: Commit seed and work consistently

Use the canonical candidate and task owners under one transaction or transactional scheduling intent. The coordinator must reconcile intents before claiming closure. Preserve original contributor identity if the parent later publishes related proposals.

### Step 4: Connect follow-up visibility

Expose registration/queue outcomes in query projections. Independent investigator can retrieve the accepted handoff and reopen source without accessing the proposer’s private transcript.

## Failure, concurrency, and recovery

A queued lead survives creator cancellation. Cancellation of the entire review separately prevents new work from running. Host retry after acknowledgment loss returns the original candidate/task. Unknown outcome is reconciled before a second effect; an exact duplicate operation is not a new investigative hypothesis.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P1-F06-T01 | Lead reported while parent still running | Durable candidate/task exists and parent remains RUNNING. |
| P1-F06-T02 | All slots occupied | Task queues without exceeding W or interrupting peers. |
| P1-F06-T03 | Parent fails after success response | Lead survives and can run. |
| P1-F06-T04 | Replay identical registration | Same effect IDs. |
| P1-F06-T05 | Same sink but distinct trust assumptions | Separate leads or explicit duplicate suggestion, no silent merge. |
| P1-F06-T06 | Reviewer never reads follow-up | No responsibility or completion penalty imposed on proposer. |

## Do not overengineer or expand scope

No automatic full candidate approval, parallel shadow candidate lifecycle, semantic-dedup model call on every lead, or target execution.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
