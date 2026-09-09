# P8-F01 — Deterministic end-to-end and failure acceptance

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P1-F02`, `P3-F03`, `P4-F02`, `P5-F02`, `P6-F04`, `P7-F02`

**Contract-hardening revision:** apply the concrete corrections in [P8-F01/IMPLEMENTATION_PLAN.md](P8-F01/IMPLEMENTATION_PLAN.md) and the [hardening index](../../CONTRACT_HARDENING.md). Earlier summary wording is not a substitute for the exact input, receipt, state, synthesis, context and cutover contracts.

## Purpose and concrete outcome

Prove the complete collaborative behavior through repeatable fixtures, scripted worker seams and failure injection, before any live quality or performance claims.

## Existing implementation and ownership

Use existing SSR test seams, unit/publication/SDK/finalization race tests and controller frontend/backend suites. Synthetic target snippets are data for static review; never execute them.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P8-F01-R01.** Test the entire path: sensitive operation → contextual request → promoted existing review → accepted early answer → yielded/resumed inquiry → candidate investigation → fresh falsification → host current finding while unrelated coverage continues.

**P8-F01-R02.** Preserve the original approved F01/F02 scenario identifiers and add feature tests from every document. A green discovery command collecting zero relevant tests is not acceptance.

**P8-F01-R03.** Use deterministic model-response scripts at existing worker seams for coordination tests, not as evidence of real model quality or live protocol compatibility.

**P8-F01-R04.** Inject crashes before/after every authoritative boundary: preparation, semantic commit, transcript-turn seal, availability event, request registration, yield/wake, provider request, response receipt, notice acknowledgment, candidate hold and closure.

**P8-F01-R05.** Simulate W=1,2,3 and100 with controlled completions, budgets and shared-provider limits. Prove fairness, no oversubscription, no lost wakeup, idempotency and restart equivalence without claiming hardware throughput.

**P8-F01-R06.** Keep target-content injection, source/secret leakage, stale identity, cyclic dependencies, malformed matchers and cursor tampering in adversarial acceptance.

## Inputs, outputs, and state

The acceptance manifest generated in this package indexes each feature and required test IDs. Test reports must record actual runner, collection, environment, commit and outcomes. Deterministic scripted responses cannot satisfy the existing separately authorized live-gateway protocol gates.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Build minimal canonical fixture

Include handler/helper/config/store boundary, two candidate families, canonical no-hit code and one intentionally unresolved binding. Capture/index only; do not run fixture code.

### Step 2: Implement trace assertions

Record event/action IDs and assert valid source/producer/receipt linkage at each handoff. Hold unrelated coverage and candidate B until A reaches current finding.

### Step 3: Add crash/replay matrix

Restart at each injected boundary from persisted stores and compare canonical effects/invariants, not incidental timestamps or random IDs.

### Step 4: Run preserved regression suites

Check both unittest and pytest collection plus controller/frontend affected tests. State which test doubles were used and which real integrations remain gated.

## Failure, concurrency, and recovery

An unavailable live gateway is a not-run live test, not a reason to skip deterministic correctness. Failure to reconstruct a receipt must block acceptance honestly. Randomized/property tests retain seeds and minimized counterexamples.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P8-F01-T01 | A finding while B and coverage held | A current finding/export eligibility independent. |
| P8-F01-T02 | All workers waiting | Helpers get capacity and wake consumers. |
| P8-F01-T03 | Crash at notice ACK | No lost update; safe uncertain duplicate allowed. |
| P8-F01-T04 | Source/search pagination varied | Same complete occurrence set and no false read credit. |
| P8-F01-T05 | 100 virtual workers | Limits/fairness/accounting invariant. |
| P8-F01-T06 | Malicious target AGENTS/comments | No policy/tool/egress escalation. |

## Do not overengineer or expand scope

No fake live test claim, fixture execution, screenshot-only acceptance, exact-prose golden model output or tests weakened to match refactor defects.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
