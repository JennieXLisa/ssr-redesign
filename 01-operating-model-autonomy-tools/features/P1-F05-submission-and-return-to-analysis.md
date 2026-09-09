# P1-F05 — Submission and return to analysis

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P1-F03`, `P1-F04`, `P1-F07`, `P1-F08`

**Contract-hardening revision:** apply the concrete corrections in [P1-F05/IMPLEMENTATION_PLAN.md](P1-F05/IMPLEMENTATION_PLAN.md) and the [hardening index](../../CONTRACT_HARDENING.md). Earlier summary wording is not a substitute for the exact input, receipt, state, synthesis, context and cutover contracts.

## Purpose and concrete outcome

An analyst can attempt a result, learn what is missing, and return to research instead of being trapped in a shrinking terminal JSON repair loop.

## Existing implementation and ownership

Reuse agent loop, agent_policy repair classification, typed submit tools, existing final validators and source-read preconditions. Preserve reusable validation and accounting, not an old-mode repair workflow.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P1-F05-R01.** Until a result is accepted, a repairable rejection returns to normal authorized analytical tool availability. It does not implicitly terminate the agent or grant new resources.

**P1-F05-R02.** Classify formatting/schema errors as FIX_INPUT, semantic missing facts as MORE_ANALYSIS, stale bound material as REFRESH_INPUTS, transient persistence as host RETRY_SAME_OPERATION, and authority/integrity failure as stop or HOST_RECOVERY.

**P1-F05-R03.** Validated semantic acceptance is immutable. Later corrections are new artifact/revision actions; an agent cannot rewrite a previously committed result by submitting again with changed prose.

**P1-F05-R04.** Repeated invalid submissions count toward the configured tool/attempt/no-progress policy but do not convert into supported findings. Progress is validated new evidence, answered questions or a changed checked argument, not word count.

**P1-F05-R05.** Input refresh is an explicit recorded host delta to the work revision. The agent receives what changed and recomputes its affected argument. Do not normalize a stale result against new inputs silently.

**P1-F05-R06.** Finalize only after semantic commit and required runtime/transcript settlement, preserving predecessor/successor isolation. Distinct failure classes remain visible through the SDK.

## Inputs, outputs, and state

Use the common result envelope and existing role-specific semantic errors. An error may include required source_refs or missing facet names but cannot prefill a correctness conclusion. Return the actual remaining budget and allowed next operations, not a fabricated fresh allowance.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Separate rejection from terminal failure

Change runner policy classification in collaborative mode. Keep one provider conversation and ordinary tools for repairs, preserving opaque provider continuation only within that attempt.

### Step 2: Make repairs actionable

Map internal validation paths to model fields through P1-F03; aggregate independent issues through P1-F07. If additional source checks are needed, normal reads stay available rather than only one hard-coded corrective range.

### Step 3: Implement explicit input deltas

Refresh via a host-owned work service that records previous/new input digests and the actual delta exposed. Preserve completed artifacts and cancel or supersede only work with genuine invalid inputs.

### Step 4: Protect finalization

Run the existing investigation-finalization race regression through success, rejection, post-commit error and late prior-attempt cases. Do not derive old outcome from the current mutable task row.

## Failure, concurrency, and recovery

A persistence failure after commit recovers its receipt, not another model judgment. A safety refusal or exhausted budget stays a distinct outcome. Cancelled tasks cannot use repair mode to continue operating. Updating a conversation does not update accepted historical source-read evidence.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P1-F05-T01 | Rejected result needs another helper read | Ordinary research resumes under same remaining limits. |
| P1-F05-T02 | Invalid enum plus missing field | Both safe issues returned. |
| P1-F05-T03 | Stale candidate revision | Explicit refresh, no automatic rebinding. |
| P1-F05-T04 | Commit succeeds and finalization errors | No duplicate accepted result or successor mutation. |
| P1-F05-T05 | Repeated no-progress repairs | Visible bounded stop, no false finding. |
| P1-F05-T06 | Accepted result resubmitted changed | Rejected or new revision path; original immutable. |

## Do not overengineer or expand scope

No separate repair agent, universal manager approval, automatic successful defaults, or infinite repair loop.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
