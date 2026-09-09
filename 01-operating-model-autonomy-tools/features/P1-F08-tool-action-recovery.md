# P1-F08 — Reliable tool actions and outcome recovery

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P1-F07`

## Purpose and concrete outcome

Durable nonterminal tools must not duplicate effects when their acknowledgments are lost. Persistence recovery should reuse validated work instead of asking the model to reconstruct it.

## Existing implementation and ownership

Extend existing ToolPersistenceError prepared-artifact retry, database transactions and terminal receipt identities. Reuse request/attempt records and original-attempt finalization guards.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P1-F08-R01.** Assign a host operation identity before authoritative mutation using the normalized semantic action and bound work revision. Map transport call IDs to it; do not rely only on a provider call ID surviving a model retry.

**P1-F08-R02.** Commit domain effects and the COMMITTED operation receipt atomically. Before commit, PREPARED stores source-free validated content/references sufficient for host retry, not raw source or an opaque transcript.

**P1-F08-R03.** Exact replay returns the same effect IDs and immutable receipt. Same operation identity with a different normalized digest is a conflict; a new proposal receives a new identity.

**P1-F08-R04.** On interruption, inspect the original owner’s receipt/effects before retry. Never say no effects were saved when the outcome is uncertain. External provider requests remain separately accounted and cannot be promised exactly-once.

**P1-F08-R05.** Authority rechecks apply to new writes; original committed outcome settlement uses exact old-attempt receipts without mutating the successor. A valid old operation ID does not permit an expired model to execute new actions.

**P1-F08-R06.** Observe source/model delivery separately from effect commitment. A tool result omitted from the final prompt grants no read credit; an accepted side effect is not rolled back merely because its response was undelivered.

## Inputs, outputs, and state

Operation states: PREPARED, COMMITTED, FAILED_NO_EFFECT, OUTCOME_UNKNOWN. Reconciliation is an owner-specific routine, not a second generic task scheduler. Store content digests and domain IDs; response display can be regenerated from immutable source-free receipt fields. Transaction errors keep their retryability classification.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Identify idempotent domain seams

Map lead seed, checkpoint CAS, request registration, answer publication, yield and final submission to their unique domain constraints. Add the minimal shared operation wrapper around those owners.

### Step 2: Build prepared/committed protocol

Validate once, retain safe prepared material, execute one short transaction and save the exact receipt. Never re-run inference on a transient SQLite write collision.

### Step 3: Add host reconciliation

Recover ambiguous returns from domain identity/receipt, retry only bounded transient failures, and return a safe typed blocker for unresolved cases. Preserve deadline/cancellation semantics.

### Step 4: Inject failures at each boundary

Simulate before commit, after commit, before response, after durable model response, and after successor claim. Assert exact effect counts and unchanged successor state.

## Failure, concurrency, and recovery

Two concurrent identical calls must converge via uniqueness/transaction serialization. Do not deduplicate two distinct actions by same file or sink. Receipt replay can still consume real model/transport resources; only the semantic mutation is reused. Deterministic test doubles validate persistence behavior, not live provider compatibility.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P1-F08-T01 | Commit then drop acknowledgment | Recovery returns original candidate/task. |
| P1-F08-T02 | Concurrent same checkpoint action | One checkpoint sequence increase. |
| P1-F08-T03 | Same key changed payload | Conflict with no second effect. |
| P1-F08-T04 | New attempt follows old receipt | No old lease authority inherited. |
| P1-F08-T05 | DB failure before commit | Prepared retry without another model call. |
| P1-F08-T06 | Late prior finalizer | No successor task modification. |

## Do not overengineer or expand scope

No distributed exactly-once claim, implicit background retry agent, raw tool-body persistence, or arbitrary transactional replay of external side effects.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
