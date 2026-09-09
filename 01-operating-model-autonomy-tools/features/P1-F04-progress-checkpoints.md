# P1-F04 — Agent-initiated progress checkpoints

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P1-F03`, `P1-F08`

## Purpose and concrete outcome

Allow analysts to preserve what they know, what they doubt and their next action at any time without ending their attempt. Restore work, not another agent’s claimed reading history.

## Existing implementation and ownership

Extend current CheckpointState/save_checkpoint and worker_context_recovery. Remove checkpoint_state from host-only exposure in collaborative ordinary turns, while retaining the same validated save owner and optimistic sequence.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P1-F04-R01.** Expose checkpoint_state during ordinary analytical work. Saving is nonterminal; yield_work is an explicit separate action. Host-requested saves use the identical schema, validator and persistence path.

**P1-F04-R02.** Persist source-free facts/hypotheses/unknowns, next action, exact subject/artifact/evidence refs, valid source/search cursors and outstanding request refs. Never persist a raw conversation, source passage or provider-opaque state as portable memory.

**P1-F04-R03.** Use expected_sequence CAS. Exact operation replay returns its original saved sequence, not an extra revision. A genuine conflicting update returns current sequence and safe merge guidance.

**P1-F04-R04.** Checkpoint authorship remains the original attempt. A new attempt gets a compact dossier with current assignment, accepted prior state and deltas; source inspection credit starts empty.

**P1-F04-R05.** Interests and blocking requests are already durable host state and need not await a model checkpoint. Checkpoint references link them; they are not copied into a competing subscription store.

**P1-F04-R06.** Host context pressure reserves a save/terminal margin before exhaustion. If saving fails, retain the last valid checkpoint and explicit incomplete work. No silent successful finalization or budget reset.

## Inputs, outputs, and state

Use existing checkpoint row identity and contract version with new typed state. Authoring/reflection text is bounded and source-free. `next_action` is a concise explanation plus typed action class READ, QUERY, REQUEST_CONTEXT, INVESTIGATE, SUBMIT or WAIT; it is guidance, not a command automatically executed from untrusted text.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Extend portable state

Add reference/cursor/request fields to the collaborative checkpoint variant, leaving legacy records parseable. Validate size and ownership before writing.

### Step 2: Expose common saving

Wire ordinary and host control calls through the same save function. Keep failure/sequence messages actionable and operation replay before generating duplicate saves.

### Step 3: Build continuation dossier

Load the most recent valid checkpoint, durable requests/interests, current bound inputs and material deltas. Preserve hypotheses/counterevidence labels and explicitly identify stale referenced artifacts.

### Step 4: Keep normal attempt accounting

At yield, atomically bind checkpoint digest to task transition; release capacity only after runtime-safe settlement. Operational retries and no-progress continuations have distinct counters.

## Failure, concurrency, and recovery

An expired attempt cannot overwrite a successor checkpoint. A cursor remains only a locator and needs fresh authorization. Unsupported checkpoint version yields a host compatibility blocker, not best-effort prose parsing. Losing an unsaved thought is reported as such; do not fabricate reconstructed private reasoning.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P1-F04-T01 | Save twice during active work | Task continues; sequences increase only for distinct saves. |
| P1-F04-T02 | Replay after lost acknowledgment | Same checkpoint ID and sequence. |
| P1-F04-T03 | Stale expected sequence | Conflict; no overwrite. |
| P1-F04-T04 | Restart after durable context request but before save | Request and interest survive. |
| P1-F04-T05 | Resume from checkpoint with old source refs | References retained, read credit empty. |
| P1-F04-T06 | Context threshold with no save capacity | Explicit incomplete boundary, no false completion. |

## Do not overengineer or expand scope

No provider-side memory dependency, full transcript in ssr.db, auto-spawn on checkpoint, or checkpoint-specific scheduler.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
