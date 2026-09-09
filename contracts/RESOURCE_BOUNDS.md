# Bounded collaboration, proposal admission, and progress

Contract: `limits-v1`. This completes the metadata/fanout/no-progress part of H04/H06 and the cross-feature bound required by H0. Values below are selected engineering defaults, not measured optimal throughput. Bind them in the immutable review policy; model calls cannot change them. The existing hard time/token/provider limits remain independently enforced.

## LB-R01 — Exact limits and counting units

| Setting | Default | Counter meaning | On exhaustion |
|---|---:|---|---|
| leads.per_root_total | 128 | Distinct accepted or receipt-pending lead operations for one root; exact replay counts once | LIMIT_REACHED; no fabricated registration; preserve existing leads |
| leads.per_review_total | 10000 | Distinct lead origins across the review, excluding exact repeated origin references | LIMIT_REACHED; expose review limitation; operator may authorize a new policy/review, never silently reset |
| collaboration.open_requests_per_work | 8 | Unresolved owned request revisions; joining an existing producer creates a consumer, not another producer | LIMIT_REACHED with exact owned request references that may be resolved/cancelled |
| collaboration.requests_per_root_total | 256 | Distinct contextual requests and revisions initiated within a root | LIMIT_REACHED; explicit unresolved disposition rather than recursive spawning |
| collaboration.consumers_per_request | 64 | Live consumer/revision associations; each consumer task/revision appears once | LIMIT_REACHED for the attempted join; no automatic duplicate producer as a loophole |
| collaboration.max_dependency_depth | 8 | Longest path of live blocking work edges after proposed join | Reject the edge with safe cycle/depth explanation; retain independent existing work |
| collaboration.request_revisions | 8 | Distinct immutable revisions of one question | Require a genuine new scoped work decision; no automatic reword-and-retry |
| freshness.interests_per_work | 256 | Active distinct subject/normalized-filter interests; repeat lookup reuses one | LIMIT_REACHED without silent eviction; release-interest is explicit |
| publication.pending_per_work | 32 | Prepared domain proposals awaiting required prefix/acceptance reconciliation | Stop new publication proposals; reconciliation remains admissible |
| publication.pending_per_review | 4096 | Same pending proposals across all work | Expose RECEIPT_PENDING pressure; do not create more pending rows or declare completion |
| runtime.no_progress_continuations | 3 | Consecutive completed continuations without the eligible progress delta below | Stop automatic continuation; explicit INCONCLUSIVE/NO_PROGRESS limitation |
| synthesis.journal_bytes_per_file | 536870912 | Canonical encoded committed entries and staged reference pages, not a single provider request | Preserve resumable session; visible quota blocker; no false seal |

All counters are integers, not floats or bools. Configuration schemas enforce positive bounds and maximum 2^53-1; effective per-call/transport limits are the smaller enclosing limits. A full worker pool is not metadata-capacity exhaustion: a valid lead still registers and queues. A strict recording limit is an explicit tool outcome, not silent discard.

## LB-R02 — Atomic reservation and replay

The operation identity is derived before admission. Within the domain owner's short write transaction: revalidate scope/input; return any exact already-committed operation; check the applicable root/review/live counters; reserve or increment each dimension through guarded UPDATEs; create the original domain rows and work/acceptance intent; commit the operation receipt. Roll back all increments if any bound or domain write fails. No separate counter owner may commit outside that transaction.

Use `UPDATE ... SET used=used+1 WHERE used < maximum` plus row-count verification or an equivalent uniquely indexed count under the same immediate transaction. Check every dimension; succeeding at root count but failing review count rolls back both. Each accepted operation has one counter receipt linking dimension/key/increment. Resuming a receipt-pending operation does not increment it again. A rejected invalid payload does not consume a lifetime lead slot; once a valid origin is recorded, later dismissal does not refund a lifetime slot and allow an endless sequence of new proposals.

Live counters are released only on the owning association's unique terminal transition: request answered/cancelled, consumer detached, interest explicitly retired or work closed, pending proposal available/rejected. Lifetime counters are never released. Reconciliation can derive/repair counters from authoritative operation/association rows under the coordinator; it cannot erase reservations based on a missing in-memory object. Counter drift is a visible integrity/recovery error.

Receipt recovery and host settlement must not require another free proposal slot. Otherwise a full pending table could make every pending receipt impossible to reconcile. The existing root identity is inherited by delegated contextual work for accounting, while publication, research and consumer authority remain separately checked.

## LB-R03 — Fanout and cycles are checked on the resulting graph

Before adding a blocking edge, resolve the actual producer task, not just a subject name. Check reachability back to the consumer and the resulting depth under the same graph/task transaction used to register the edge. Two concurrent individually safe edges must not commit a cycle together. Joining existing work still counts a live consumer and a blocking edge; it is not an exemption.

Do not hold a worker slot while waiting. Cycle/depth rejection is an actionable unresolved dependency result: the analyst may inspect source locally, use a narrower nonblocking question, or conclude inconclusive. It does not authorize a manager model, automatic duplication of the producer, or removal of canonical coverage edges. Only live blocking inquiry edges participate in this depth; the separate canonical SCC graph retains its own valid recursion semantics.

## LB-R04 — What progress means

Compare the completed attempt's durable progress fingerprint with the prior continuation baseline: accepted new artifact/disposition IDs, newly processed exact dependency dispositions, newly delivered material source intervals attached to the assigned question, and checkpoint references to new host-recorded evidence/subjects or a changed scoped analytical disposition. Sort and hash canonical identifiers; do not hash display order, timestamp, whitespace or the model's unverified `progress` field.

A changed phrase alone, another attempt number, repeated page, duplicated lead origin, fresh cursor token for the same bytes, or re-saving identical reference content is not progress. New unrelated source reads do not reset the assigned question's no-progress counter. This is a bounded host observable, not a claim that it understands or certifies the hypothesis. Actual cumulative budgets remain the final hard bound even when legitimate progress continues.

At successful settlement: if the fingerprint adds eligible progress, set consecutive_no_progress=0; otherwise increment it once for that completed continuation. An exact replay returns the recorded settlement and changes no counter. At 3, do not automatically publish a new PENDING continuation. Persist an explicit no-progress disposition and checkpoint. For investigation/falsification this becomes an honest INCONCLUSIVE limitation only through the role's analytical result or a separately labeled host resource-stop outcome; never fabricate model reasoning. Required canonical review stays incomplete/blocked when it has not actually met its coverage contract.

## LB-R05 — Failure and tests

LB-T01 races two valid registrations for the last root/review slot and permits exactly one. LB-T02 fails the second counter dimension and verifies total rollback. LB-T03 repeats a committed operation after the limit is reached and returns the original result. LB-T04 a dismissed lead does not replenish lifetime quota. LB-T05 producer completion releases each live consumer once. LB-T06 a full pending-publication quota still permits existing receipt reconciliation. LB-T07 concurrent opposing dependency edges cannot both commit. LB-T08 duplicate interest lookup consumes no new slot. LB-T09 three unchanged continuations stop, including after restart. LB-T10 newly processed relevant answer resets the no-progress counter, but a newer attempt number does not. LB-T11 pending required work or exhausted budget never produces COMPLETE. LB-T12 large synthesis staging remains bounded per input and independently accounts journal storage.

Implement counter checks behind current transaction owners, not a new quota server. Tests in the documentation reference suite exercise counter rollback/replay and progress arithmetic; production concurrency/graph/admission tests are required in the harness checkout.
