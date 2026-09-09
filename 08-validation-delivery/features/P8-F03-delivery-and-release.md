# P8-F03 — Dependency-ordered delivery and release handoff

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P8-F01`, `P8-F02`, `P7-F03`

**Contract-hardening revision:** apply the concrete corrections in [P8-F03/IMPLEMENTATION_PLAN.md](P8-F03/IMPLEMENTATION_PLAN.md) and the [hardening index](../../CONTRACT_HARDENING.md). Earlier summary wording is not a substitute for the exact input, receipt, state, synthesis, context and cutover contracts.

## Purpose and concrete outcome

Give developer agents an executable sequence of bounded changes, each with tests and retained authorities, instead of a huge rewrite or an endless collection of half-enabled modes.

## Existing implementation and ownership

Reuse accepted modular refactor boundaries, AGENTS engineering rules, paired release checks and existing package manifests. The build order in DELIVERY.md reconciles cross-feature references into actual integration slices.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P8-F03-R01.** Follow R0–R7 implementation slices in DELIVERY.md. Slice numbers are development gates, not new runtime phases or user-visible modes.

**P8-F03-R02.** Complete common interfaces and tests before enabling dependent behavior. A feature may be coded behind disabled capability, but do not advertise it while its source/acceptance/receipt/gate path is incomplete.

**P8-F03-R03.** Keep changes one cohesive owner at a time with paired compatibility tests; preserve exact historical records while cutting over to the single new runtime contract. Do not mix unrelated refactor, bug fix and new policy without a documented prerequisite reason.

**P8-F03-R04.** For each slice report moved/extended owners, exact public/schema changes, tests run/not run, baseline issues, failure-injection results and remaining release gates.

**P8-F03-R05.** Developer discretion covers local names and small decomposition, not replacing selected algorithms/ownership with a new framework. Material departures require an explicit design amendment, not hidden assumptions.

**P8-F03-R06.** No code deployment, live DB migration, wheel installation, process restart or paid experiment follows automatically from documentation completion or a green deterministic suite.

## Inputs, outputs, and state

Deliver a code-baseline map, requirement/test matrix, migration and compatibility manifest, installed package checks, end-to-end trace and honest status. Complete final package only after all mandatory slice gates pass; separately retain limitations and unsupported capabilities.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Start from baseline evidence

Read actual refs/worktrees, existing AGENTS/specs, imports and test collection. Preserve user/concurrent changes and establish a branch/worktree under separately authorized development.

### Step 2: Implement dependency-ordered slices

Do not follow phase numbering blindly. Foundational refs/errors/operations precede artifact/request publication; scheduler and candidate authority must ship with matching SQL/SDK gates.

### Step 3: Review every checkpoint

Use deterministic tests, compatibility pairs, clean package imports and a diff inspection. Retain exact original failure/regression tests.

### Step 4: Prepare release coordinates

After separate release approval, build source-bound hash-pinned artifacts and pair controller/harness. Report installed results separately from editable-source results.

### Step 5: Close honestly

Mark documentation complete now, application implementation/test status separately. Outstanding real gates cannot be described as finished work.

## Failure, concurrency, and recovery

Unexpected baseline divergence pauses the affected slice while independent agreed work continues. No force reset, guessed migration ordinal, public compatibility bypass or live mutation to work around a development problem.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P8-F03-T01 | A slice lacks receipt integration | Capability remains disabled, not declared complete. |
| P8-F03-T02 | Both repos change together | Matching new pair and zero-mutation mismatch refusals recorded. |
| P8-F03-T03 | Wheel retains stale module | Clean packaging test detects it. |
| P8-F03-T04 | Unexpected local changes | Preserved and reported. |
| P8-F03-T05 | Implementation finished but live gate not run | Status distinguishes the two. |
| P8-F03-T06 | Release rollback required | Documented backup-backed operator path, no automatic downgrade. |

## Do not overengineer or expand scope

No big-bang rewrite, four permanent partial runtime modes, automatic deployment or handoff that merely says “add tests and integrate.”

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
