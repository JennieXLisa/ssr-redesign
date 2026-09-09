# P5-F02 — Independent falsification and current findings

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P5-F01`, `P4-F01`, `P5-F03`, `P7-F02`

## Purpose and concrete outcome

A complete current argument is challenged by a fresh analyst, then promoted by deterministic host logic without waiting for unrelated work or packaging.

## Existing implementation and ownership

Reuse falsification task/result contracts, fresh conversation policy, evidence gate and existing export services. Add current-revision validity projection, not a second finding authority in the UI.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P5-F02-R01.** Falsifier is a distinct agent run and fresh provider conversation. It receives the claim, cited evidence, assumptions, counterevidence and targeted challenges, not the investigator’s opaque reasoning transcript.

**P5-F02-R02.** Falsifier can search for contrary callers/controls/configuration and request contextual review beyond the investigator-selected path. Broad research access does not compromise its independent verdict.

**P5-F02-R03.** Only UPHELD, REFUTED or INCONCLUSIVE from the exact assigned revision is accepted. The final host gate verifies current complete material, source rereads, independent identity and required receipts.

**P5-F02-R04.** Promote a valid upheld result in host work as soon as all gates pass; no additional model task, global peer wait or package phase is required.

**P5-F02-R05.** All query, export and scoring consumers use the same current-finding predicate. Historical FINAL_READY data alone cannot certify a currently valid finding.

**P5-F02-R06.** Expose review incompleteness alongside current findings. Priority, confidence, maturity and severity remain different fields; model agreement or a scanner hit is insufficient evidence.

## Inputs, outputs, and state

Falsification artifact binds candidate/revision/argument digest, challenge answers, evidence/counterevidence refs, verdict, limitations and distinct producer. CurrentFinding includes family/current candidate revision, validity generation, upheld verdict receipt and incompleteness/limitations. Same-model falsification is permitted by current policy but its limitation remains explicit.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Admit fresh falsifiers independently

Use argument_ready and usable input receipts, not legacy global FALSIFYING phase. Preserve separate task identity and provider conversation.

### Step 2: Enable contrary-context research

Use P1 tools and P3 requests; requests carry claim assumptions as hypotheses, not commands to agree.

### Step 3: Centralize host promotion

Implement one transactional ready-and-current predicate and event. Reject stale/partial/invalid verdicts; promotion consumes no model slot.

### Step 4: Update SDK/export consumers

Expose concurrent findings/review status through public collaborative projections. Exports check exact validity generation in a consistent read before producing immutable artifacts.

## Failure, concurrency, and recovery

Refusal, timeout or malformed response is not INCONCLUSIVE unless the analytical verdict was actually produced and accepted. Later counterevidence immediately removes current export eligibility without rewriting historical verdicts. A valid falsifier from another revision cannot be reused silently.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P5-F02-T01 | Fresh falsifier challenges additional caller | Allowed source access and independent conclusion. |
| P5-F02-T02 | UPHELD while all model slots busy | Host promotion still occurs. |
| P5-F02-T03 | REFUTED or INCONCLUSIVE | No final finding. |
| P5-F02-T04 | Same run as investigator | Independence gate rejects. |
| P5-F02-T05 | Old revision upheld | No current promotion. |
| P5-F02-T06 | Finding exported with coverage ongoing | Report accurately states IN_PROGRESS. |

## Do not overengineer or expand scope

No model-vote consensus shortcut, copied investigator conversation, UI-computed readiness or waiting for another candidate’s phase.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
