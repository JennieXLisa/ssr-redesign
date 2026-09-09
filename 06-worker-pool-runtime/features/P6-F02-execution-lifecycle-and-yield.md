# P6-F02 — Execution lifecycle, yield, and restart

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P1-F04`, `P3-F03`, `P1-F08`

**Contract-hardening revision:** apply the concrete corrections in [P6-F02/IMPLEMENTATION_PLAN.md](P6-F02/IMPLEMENTATION_PLAN.md) and the [hardening index](../../CONTRACT_HARDENING.md). Earlier summary wording is not a substitute for the exact input, receipt, state, synthesis, context and cutover contracts.

## Purpose and concrete outcome

Keep long-lived analytical work durable while execution attempts remain bounded, independently leased and replaceable. Waiting must not exhaust a pool of 100 slots.

## Existing implementation and ownership

Reuse existing task/agent/attempt states, worker_guards, worker_finalization, context recovery, transcript lifecycle and original-attempt finalization protections.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P6-F02-R01.** A work item has at most one active lease at a time. New attempts receive fresh lease/control identity, use current authorized role profiles and retain all predecessor history.

**P6-F02-R02.** Normal checkpoint/yield is not an operational model failure and does not consume failure-retry allowance. It still creates actual attempt/resource receipts and counts toward no-progress continuation limits.

**P6-F02-R03.** yield_work validates checkpoint and unresolved dependencies atomically before RUNNING→WAITING_DEPENDENCY or PENDING. Release reservations only according to actual usage and safe request/finalization settlement.

**P6-F02-R04.** An answer event racing with yield is rechecked so work cannot wait forever on an already-satisfied request. Duplicate wakeups converge on one pending task and one later claim.

**P6-F02-R05.** Cancellation revokes current authority through the existing control generation/lease mechanism. A late old worker can settle only its exact accepted records, never the successor’s state.

**P6-F02-R06.** Crash recovery reconciles committed semantic results, pending required receipts, provider outcomes, leases and reservations before requeue. Silence is not independent proof that a writer is dead.

## Inputs, outputs, and state

Attempt-local source ranges and provider opaque content stay attempt-local. Portable checkpoints/interests/dependencies stay work-owned. WAITING_DEPENDENCY is a real new collaborative task state; queue reasons such as budget/provider pressure are separate projections, not fake terminal outcomes.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Extend centralized transitions

Append schema/application/SDK updates for new state under mode rules. Preserve illegal-transition tests and legacy stored-state behavior.

### Step 2: Implement yield acceptance

Save/verify checkpoint, atomically inspect dependencies and record normal-continuation cause. Do not release a slot merely because a model said it was waiting in prose.

### Step 3: Wire settlement and recovery

Keep current finalization transaction cluster and independent transcript handling. Make normal continuation receipts distinguishable from infrastructure interruption.

### Step 4: Test deterministic races

Use existing scripted worker seams and virtual clocks for answer/yield, cancellation/submit, late finalizer/new lease and lost receipt replay.

## Failure, concurrency, and recovery

If an accepted result committed before a crash, recover persistence/finalization instead of rerunning inference blindly. A fatal provider configuration error is not a normal dependency wait. Pending notices do not keep a terminal task alive or create a new model call.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P6-F02-T01 | All W analysts yield for queued helpers | W slots become available for helpers. |
| P6-F02-T02 | Answer arrives just before yield commit | Task remains runnable or immediately pending. |
| P6-F02-T03 | Old finalizer runs after new claim | Successor untouched. |
| P6-F02-T04 | Normal continuation | No failure-retry charge; actual usage charged. |
| P6-F02-T05 | Unknown live writer | No forced reclaim from silence alone. |
| P6-F02-T06 | Review cancellation | No new claims or late unauthorized writes. |

## Do not overengineer or expand scope

No long-running idle worker per inquiry, portable provider chain-of-thought, thread-global task identity or force-reclaim based on latency.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
