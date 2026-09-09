# P6-F01 — Work-conserving shared-pool scheduling

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P3-F03`, `P5-F01`, `P6-F03`, `P7-F02`

## Purpose and concrete outcome

Run the collaborating team through the existing continuous-admission pool, prioritizing useful unblocking and findings while protecting whole-project coverage.

## Existing implementation and ownership

Reuse drive_slice pool refill, task claim/lease owners, provider pressure, controller shared-resource admission and refactored application.review_planning. Existing continuous admission is retained, not rewritten.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P6-F01-R01.** One coordinator admits work across eligible canonical coverage, focused analysis, context review, investigation and falsification in collaborative mode. Each free slot is refilled independently; slow peers do not create a wave barrier.

**P6-F01-R02.** Recompute readiness from exact task/candidate prerequisites and accepted results. Coverage SCC/dependency constraints remain; an unrelated review phase or candidate does not become a prerequisite.

**P6-F01-R03.** Use the configured every-fourth-dispatch coverage service opportunity whenever coverage and other work are both eligible. If that category is empty or cannot fit its provider capacity, loan the slot work-conservingly and retain its service entitlement for the next eligible opportunity.

**P6-F01-R04.** Within noncoverage work prioritize required dependency answers and current-candidate adjudication before optional discovery. Apply age promotion and stable tie-breakers; exact scoring never overrides readiness, budgets or source policy.

**P6-F01-R05.** Context requests can boost existing canonical review priority. Canonical tasks still count toward coverage service; do not double-reserve them as focused work.

**P6-F01-R06.** Full pool means queue. No healthy worker preemption, arbitrary pool expansion, per-agent scheduler or model manager approving routine reads.

## Inputs, outputs, and state

Persist dispatch service counters and waiting-category entitlement in the review’s scheduling state. Ready order: eligibility → category entitlement → required-unblocking/adjudication rank → waiting-age → declared discovery score → stable task ID. Provider resource groups come from the existing backend identity/capacity owner. Numeric weights beyond the declared lexicographic rules are not required.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Generalize eligibility, not pool implementation

Audit planner, SQL claim filters, worker role validation, submit validators, public plan/query and closure together. Route new mode through shared predicate functions; leave legacy mode unchanged.

### Step 2: Implement deterministic category selection

Use a small pure selector over a bounded eligible task page, then atomically revalidate and reserve/claim. Persist the service state so restart does not reset fairness.

### Step 3: Integrate dynamic boosts

Incoming accepted requests and candidate readiness events enqueue or reprioritize only affected tasks. No scan of all work per model token or manager-model ranking.

### Step 4: Validate capacity and refill

Hold one slow attempt while other slots complete repeatedly. Test W=1/2/3/100, empty categories and per-provider/per-file caps.

## Failure, concurrency, and recovery

An eligible task may still be resource-blocked; expose that reason rather than calling it not ready. Starvation backoff cannot block independent work. Queue pagination must not repeatedly hide low-priority old work behind a fixed top-N page; age promotion is part of query ordering.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P6-F01-T01 | One slow peer, many short tasks | Slots refill without cohort wait. |
| P6-F01-T02 | W=1 with both categories | Coverage receives protected service; remaining turns advance candidates. |
| P6-F01-T03 | Focused queue empty | Coverage can use all fitting capacity. |
| P6-F01-T04 | Coverage blocked on real dependencies | Other eligible work runs; entitlement retained. |
| P6-F01-T05 | Shared provider limit tighter than W | Calls stay within shared cap. |
| P6-F01-T06 | Restart mid-fairness cycle | Recorded service state preserved. |

## Do not overengineer or expand scope

No second executor, rigid permanently split worker teams, global phase barriers in new mode, or unvalidated throughput claim.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
