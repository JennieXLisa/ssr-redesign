# P6-F03 — Resource budgets, backpressure, and finite discovery

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P6-F01`, `P6-F02`, `P1-F08`

**Contract-hardening revision:** apply the concrete corrections in [P6-F03/IMPLEMENTATION_PLAN.md](P6-F03/IMPLEMENTATION_PLAN.md) and the [hardening index](../../CONTRACT_HARDENING.md). Earlier summary wording is not a substitute for the exact input, receipt, state, synthesis, context and cutover contracts.

## Purpose and concrete outcome

Bound real provider and host work without confusing concurrency, money, context, source delivery or coverage-completion estimates.

## Existing implementation and ownership

Reuse existing provider/shared-capacity reservations, token/cost accounting, backend_pressure and controller admission. Extend dimensions and projections only where the new work requires them.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P6-F03-R01.** Reserve the next actual provider request/attempt under all enforced dimensions before granting its execution. Every real call, failure and repair is charged once; unknown usage remains estimated/unknown, never zero.

**P6-F03-R02.** No hidden budget reset on source pagination, lookup refresh, checkpoint, task yield, child request or normal continuation. Keep command-wide accounting distinct from per-attempt limits.

**P6-F03-R03.** Protect required canonical work using explicit remaining-cost estimates in addition to dispatch fairness. An estimate is not a guarantee; optional discovery pauses when its admission would consume the required estimate allowance.

**P6-F03-R04.** Limit optional backlog, unresolved request fan-out, dependency depth and no-progress continuation using pinned review settings. Retain recorded leads/questions with explicit deferred or blocked reasons at limits.

**P6-F03-R05.** Host matcher/analyzer I/O, memory, CPU and process concurrency are separate from model slots and share their own bounded executor. Two host-heavy reads cannot assume W×maximum memory is available.

**P6-F03-R06.** Backpressure suspends admission for affected resources while unrelated work continues. Preserve provider Retry-After/pressure semantics and never use broad retry to hide authentication/configuration failures.

## Inputs, outputs, and state

Reservation records bind actual task/attempt/provider request and resource group; states HELD, PARTIALLY_USED, SETTLED, RELEASED_UNKNOWN_RECONCILED as supported by existing owner. Do not free uncertain live reservations just to admit new work. Status projection separates hard balance, held amounts, uncertain amounts and remaining canonical estimate.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Inventory current dimensions

Map provider calls, command budget, source delivery, host scanning and context memory. Avoid double charging one semantic replay while still accounting real new provider or scanning work.

### Step 2: Implement atomic reserve/claim

Within existing admission transaction verify balances and insert reservation with lease claim. Revalidate before provider dispatch if relevant control changed.

### Step 3: Add optional-work guard

Use configured startup estimate then committed accepted sample estimates; record estimator version/sample size. Do not let a coverage percentage imply funded full completion.

### Step 4: Integrate bounded host resources

Reserve matcher/analyzer job memory/process capacity separately; return actionable backpressure instead of launching unlimited children.

### Step 5: Exercise uncertain and failed accounting

Test timeouts with missing usage, canceled in-flight calls, deferred work and restart reconciliation. Never claim strict currency enforcement when price/usage is unavailable.

## Failure, concurrency, and recovery

Insufficient budget retains unresolved work and prevents false completion. Recovery cannot settle unknown provider usage as zero. A queued accepted lead is not lost because optional admission is paused; investigation can run later only when legitimately funded.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P6-F03-T01 | W concurrent claims near balance | No over-reservation. |
| P6-F03-T02 | Provider timeout lacks usage | Unknown/estimated amount visible. |
| P6-F03-T03 | Cursor replay | No allowance reset; actual work accounted. |
| P6-F03-T04 | Canonical estimate exceeds remaining | Optional discovery pauses; shortfall visible. |
| P6-F03-T05 | Many regex requests | Host process/memory caps respected. |
| P6-F03-T06 | Capacity unavailable for one backend | Other eligible backend work continues. |

## Do not overengineer or expand scope

No virtual free retries, empirically unsupported 50/50 spending guarantee, unlimited fan-out, or accounting in model prose.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
