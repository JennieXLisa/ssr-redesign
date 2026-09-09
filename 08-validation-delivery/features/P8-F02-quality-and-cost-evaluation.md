# P8-F02 — Quality, latency, cost, and regression measurement

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P8-F01`, `P7-F02`

**Contract-hardening revision:** apply the concrete corrections in [P8-F02/IMPLEMENTATION_PLAN.md](P8-F02/IMPLEMENTATION_PLAN.md) and the [hardening index](../../CONTRACT_HARDENING.md). Earlier summary wording is not a substitute for the exact input, receipt, state, synthesis, context and cutover contracts.

## Purpose and concrete outcome

Measure whether collaboration actually yields correct findings earlier without losing coverage or spending more than its benefit justifies.

## Existing implementation and ownership

Reuse controller evaluation services, label-isolated gold/eval databases and source-backed scoring. Keep labels and benchmark answers out of analyst context.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P8-F02-R01.** Evaluate at least legacy baseline, continuous candidate progression only, reordered canonical review, and full collaborative discovery on identical captured source/configured budgets where comparable.

**P8-F02-R02.** Measure time to first independently upheld correct finding, per-candidate ready-to-start delay, falsifier-seal-to-current-validity delay, full coverage completion, duplicate analysis, tokens/cost and unresolved/failure counts.

**P8-F02-R03.** Record source/indexing time separately from model work, and distinguish structural scheduler speed from model analytical quality. A functional trace proves behavior, not improved finding quality.

**P8-F02-R04.** Report false positives, refutations, inconclusive and missed known cases alongside findings. Do not optimize only the first easy issue while starving difficult/no-hit code.

**P8-F02-R05.** Use repeated runs where model nondeterminism matters, matched snapshots/prompts/route profiles and confidence/variation reporting. Unknown costs remain explicit, not zero.

**P8-F02-R06.** Live provider experiments require independent authorization and bounded spend. Deterministic design defaults may change only with versioned configuration and recorded rationale.

## Inputs, outputs, and state

EvaluationRun: source/config/tool/model artifact identities, workload variant, random seeds where supported, exact provider usage state, timing breakdowns, canonical coverage and adjudication outcomes. Scorer output links result families/revisions and exact labels through isolated evaluation interfaces, not prompts.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Define benchmark protocol

Select source projects/cases with permitted provenance, include negative/no-hit files and cross-file controls. Record supported languages/limitations.

### Step 2: Instrument boundaries

Add timestamps only at real accepted transitions and admissions. Do not use legacy FALSIFICATION_PENDING as proof of when readiness could first have held; compute readiness from recorded inputs/receipts.

### Step 3: Run matched ablations

Keep the same budget/capacity constraints; change one architectural factor at a time. Compare distributions, not one unusually good example.

### Step 4: Audit duplication and failure costs

Measure repeated source/analysis effort per unit and sunk work in abandoned roots/repairs. Explain any greater cost rather than hiding it behind earlier first finding.

### Step 5: Publish honest decision report

Recommend parameter changes with evidence; separate correctness failures, infrastructure limits and quality variance. No deployment merely because a metric improved.

## Failure, concurrency, and recovery

Incomplete benchmark labels do not establish all missed vulnerabilities. Unsupported source is reported as a limitation. Model version drift or changed provider route invalidates a naive paired comparison and must be recorded.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P8-F02-T01 | Gold labels accessible to scorer only | Analyst context contains none. |
| P8-F02-T02 | Same snapshot differing budgets | Comparison explicitly controlled or labeled noncomparable. |
| P8-F02-T03 | Unknown provider usage | Cost marked unknown/estimated. |
| P8-F02-T04 | First finding early but coverage stalled | Tradeoff appears in result. |
| P8-F02-T05 | Legacy stage event after actual usable inputs | Readiness delay measured from real prerequisites. |
| P8-F02-T06 | Repeated model runs | Variance reported, no deterministic quality claim. |

## Do not overengineer or expand scope

No benchmark-label leakage, claimed cost saving from scheduler simulation, cherry-picked first result, or paid run without authorization.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
