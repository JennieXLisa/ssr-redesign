# P6-F04 — Completion, quiescence, and reconciliation

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P4-F01`, `P5-F03`, `P6-F02`, `P6-F03`

## Purpose and concrete outcome

Finish a review only when its required obligations and durable effects are accounted for, while allowing valid findings to appear and be exported earlier.

## Existing implementation and ownership

Reuse current coordinator, task/coverage queries, publication/receipt recovery, package verification and explicit limitation closure. New work contributes to the same truthful completion decision.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P6-F04-R01.** Completion checks canonical included-file/unit dispositions, required link reconciliation, all admitted focused/context/investigation/falsification work, request consumers and current candidate dispositions.

**P6-F04-R02.** Also settle semantic publication, required runtime/transcript receipts, mandatory material propagation, leases, provider/host reservations and durable scheduling intents. An empty ready queue alone is insufficient.

**P6-F04-R03.** Optional undisplayed freshness notices on terminal work do not block closure. Required answers or unresolved material validity holds do block or require an explicitly authorized limitation disposition.

**P6-F04-R04.** No finding surviving review is a valid outcome, not failure. Failed coverage or exhausted required work remains FAILED/BLOCKED or explicit completed-with-limitations according to the control contract.

**P6-F04-R05.** Closure is checked and committed against a current review-state/change fingerprint under coordinator authority, preventing a late accepted lead/publication from being omitted.

**P6-F04-R06.** Explicit export can run while work is unfinished. Packages and status must preserve the actual state-as-of and current candidate validity; export does not mark review complete.

## Inputs, outputs, and state

ClosureReport includes required counts, blocked task/request/candidate refs, receipt/propagation gaps, live reservations and accepted limitation receipts. Work closure and package creation are separate actions. The same public projection powers UI and CLI.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Enumerate every new durable obligation

Add request routing, lead intents, artifact availability, validity holds and continuation state to current closure queries. Avoid one component’s private completion heuristic.

### Step 2: Implement bounded reconciliation

Process durable outbox/intents and receipt gaps through owner-specific idempotent handlers. No model work solely to apply accepted facts.

### Step 3: Commit closure by fingerprint

Recheck expected generation/change high-water and work counts in the final short transaction. Late work invalidates the closure attempt; retry rather than dropping it.

### Step 4: Expose honest limitation outcomes

Separate terminal success, completed-with-limitations and blocked progress in SDK/UI. An operator’s typed receipt can close an allowed limitation but cannot manufacture falsification or completed coverage.

## Failure, concurrency, and recovery

Concurrent valid lead registration before closure commit prevents completion until its obligation is handled. Registration after a terminal review fails active-scope checks rather than reopening implicitly. Unknown writer/process state cannot be ignored during quiescence.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P6-F04-T01 | No ready tasks but required answer pending | Not complete. |
| P6-F04-T02 | All coverage done but receipt gap | Not complete. |
| P6-F04-T03 | Late lead races closure | Atomic outcome includes obligation or rejects inactive registration. |
| P6-F04-T04 | Only optional old notices remain | Does not block terminal closure. |
| P6-F04-T05 | No candidates survive valid review | Normal successful review possible. |
| P6-F04-T06 | Budget exhausted with material hold | Explicit blocked/unresolved state, no upheld export. |

## Do not overengineer or expand scope

No packaging-as-readiness gate, empty-queue completion heuristic, automatic waiver, or deletion of unfinished work.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
