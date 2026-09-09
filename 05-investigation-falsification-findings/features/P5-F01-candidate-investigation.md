# P5-F01 — Candidate admission and continuous investigation

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P1-F05`, `P3-F03`, `P4-F01`, `P6-F01`

**Contract-hardening revision:** apply the concrete corrections in [P5-F01/IMPLEMENTATION_PLAN.md](P5-F01/IMPLEMENTATION_PLAN.md) and the [hardening index](../../CONTRACT_HARDENING.md). Earlier summary wording is not a substitute for the exact input, receipt, state, synthesis, context and cutover contracts.

## Purpose and concrete outcome

A source-grounded candidate can receive investigation while unrelated review work continues; admission must not require the finished argument the investigator is supposed to develop.

## Existing implementation and ownership

Reuse CandidateService, existing candidate stages/events, investigation result validation, evidence attachments, source reread gates and worker role profiles. Only collaborative scheduling/readiness and input revision behavior changes.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P5-F01-R01.** Admission requires a current SEEDED/TRIAGED or unfinished candidate, one actionable security question, permitted observed anchors and sufficient registered inputs to investigate. It does not require full path or prior falsification.

**P5-F01-R02.** Candidate maturity remains host-validated evidence progress. A coherent investigation submission may satisfy several facets together; do not force one model attempt per maturity enum when the full supported argument is already present.

**P5-F01-R03.** Investigation covers influence, path/state/lifecycle, reachability, controls, preconditions/configuration, bounded impact, counterevidence and unknowns, using fresh material source inspection.

**P5-F01-R04.** Investigators have the same project-wide research and contextual-request capabilities. Missing context creates registered dependencies and optional yield, not speculative completion.

**P5-F01-R05.** Bind every attempt/result to candidate family/revision and material input digest. Accepted changed inputs require explicit refresh/delta and re-evaluation; no silent latest-state substitution.

**P5-F01-R06.** Results may SUPPORT_FOR_FALSIFICATION, DISMISS_WITH_EVIDENCE, NEED_CONTEXT or INCONCLUSIVE. Only complete arguments with accepted material/receipts become falsification-ready.

## Inputs, outputs, and state

InvestigationArtifact retains the existing structured path and evidence schema through a compact agent envelope. Readiness is a deterministic projection over the exact current argument and material prerequisites. The legacy final-ready validator is not called to decide falsifier admission because it requires a verdict that does not yet exist.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Extract shared argument validation

Separate argument completeness from final upheld-verdict validation while keeping one canonical CandidateService authority. Test no circular falsifier prerequisite.

### Step 2: Build collaborative admission

Replace phase-only eligibility in planner/claim/submit/query and SQL guards for new mode. Reject historical-mode execution; use the collaborative readiness predicate on all new paths.

### Step 3: Integrate evidence and dependencies

Allow validated new refs and explicit context results; record input revision changes before analysis continues. Reuse canonical evidence attach/query methods.

### Step 4: Apply outcomes in host code

After required receipts, update candidate progress or schedule fresh falsifier using idempotent events. No extra model call just to promote a stage.

## Failure, concurrency, and recovery

Insufficient evidence is a legitimate nonfinal disposition, not a failed host transport. Two investigators cannot commit against the same current revision without CAS; stale one retains its historical attempt but cannot overwrite current argument. No unrelated phase barrier can hold a ready candidate.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P5-F01-T01 | Candidate A ready while file B active | A investigation starts without waiting for B. |
| P5-F01-T02 | Initial partial path | Admission succeeds for the missing question. |
| P5-F01-T03 | Complete multi-facet argument | No forced per-enum model loop. |
| P5-F01-T04 | Context arrives while investigator waits | Exact input revision and continuation. |
| P5-F01-T05 | Concurrent candidate revision update | Stale submission rejected. |
| P5-F01-T06 | No upheld verdict yet | Falsification readiness can be true; final-ready remains false. |

## Do not overengineer or expand scope

No new candidate store, generic LLM stage approver, automatic impact/severity, or completed-proof admission gate.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
