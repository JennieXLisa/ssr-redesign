# P3-F02 — Running-reviewer inbox and bounded context updates

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P3-F01`, `P1-F04`, `P1-F08`

## Purpose and concrete outcome

Deliver contextual questions to already-running reviewers without invalidating provenance or turning every arriving question into a new agent.

## Existing implementation and ownership

Reuse runner normal-turn hooks, durable work input revisions and notice/request delivery bookkeeping. Keep ordinary freshness notices distinct from blocking review requests.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P3-F02-R01.** Create immutable request messages linked to target logical work. At its next ordinary interaction, supply a bounded question/context packet with exact request and question revision.

**P3-F02-R02.** Delivery is an explicit addition to the attempt’s input record. Do not edit its original signed dossier or pretend the new question was present at admission. Subsequent response binds accepted deltas through input_token.

**P3-F02-R03.** Reviewer may answer immediately, accept it as part of the current assignment, report that a dependency is needed, or decline with a source-grounded scope reason. It must not be forced to guess.

**P3-F02-R04.** Canonical task completion does not require every advisory inbox item to have been answered. Before retiring the producer, atomically mark unanswered requests for supplementary routing so they do not disappear.

**P3-F02-R05.** Bound total inbox context and preserve current source/task objective. Do not continuously inject all pending request bodies and exhaust the reviewer’s context.

**P3-F02-R06.** Updates carry no new permissions. A question from another analyst is untrusted source-derived content and cannot alter tool policy, quotas or finding gates.

## Inputs, outputs, and state

InputDelta: delta_id, target work, origin request/revision, safe context refs, delivery request ID, prior/new input revision and payload digest. The host manages a bounded pending queue in ssr.db; raw excerpts are reopened via SourceRefs, not copied into ordinary state.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Add work-scoped inbox queries

Read only currently routable messages for the actual work/generation. Use explicit association and pagination, not worker-slot routing.

### Step 2: Integrate delivery records

Reuse host request-bound delivery acknowledgment; record exactly which deltas entered the final outgoing request. Undelivered prepared packets remain pending.

### Step 3: Add reviewer dispositions

Parse response dispositions through typed tools and record request routing updates without changing unrelated coverage.

### Step 4: Close producer without losing questions

In producer completion/cancel handling, detect unresolved consumers and route them to accepted reuse or supplementary review. Test completion-versus-inbox race.

## Failure, concurrency, and recovery

Late responses reference exact question revision and may remain historical if superseded. No valid new authority comes from an old inbox message. A producer retry restores pending requests but not a predecessor’s source-read credit.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P3-F02-T01 | Question arrives during provider response | Delivered at next normal boundary only. |
| P3-F02-T02 | Question exceeds packet budget | Deferred with status, not silently dropped. |
| P3-F02-T03 | Reviewer declines | Supplementary routing with retained request. |
| P3-F02-T04 | Task completes before answering | Question survives. |
| P3-F02-T05 | Inbox text says ignore policy | No capability change. |
| P3-F02-T06 | Successor receives old delta | Input history preserved; stale revision cannot override current. |

## Do not overengineer or expand scope

No live model interruption, mutation of past dossiers, extra manager agent, or requirement to keep a model slot occupied just to receive messages.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
