# Shared state, ownership, and transaction contract

Contract: collaborative-v1 · Design specification; append-only migrations are allocated from the implementation checkout, not from this document.

**Contract-hardening amendments are indexed in [CONTRACT_HARDENING.md](../CONTRACT_HARDENING.md).** STATE_MACHINE.md and MIGRATION_PLAN.md freeze transitions/cutover; PREFIX_RECEIPTS.md and INPUT_REVISIONS.md freeze producer/input proof; FILE_SYNTHESIS.md replaces unbounded model synthesis. Real harness integration and migration tests remain implementation gates, not results claimed by this specification.

## 1. Identities and authorities

Use existing project, snapshot, review, file, symbol, relationship, task, agent-run, candidate, evidence and document IDs. A logical inquiry is a task with a typed work descriptor; its ID survives attempt changes. A worker slot has no durable knowledge ownership. `root_work_id` groups an inquiry and its requested work for accounting, not an authority grant. A context request has its own identity because multiple callers can depend on one producer.

Three checks stay separate: execution authority (attempt/lease/control generation), research authority (snapshot/source policy), and submission authority (owned deliverable, candidate revision and accepted inputs). Source readability does not imply result visibility. Permission is rechecked at use; signed IDs or cursors do not bypass any check.

The existing orchestration/coordinator authority owns transitions. Add `WAITING_DEPENDENCY` only through the complete state-machine hardening/migration gate. A yield first records a durable prepared intent while the task remains RUNNING with its original lease. Only after the exact predecessor is terminal and its required runtime/transcript receipts have settled may one guarded transaction publish PENDING or WAITING_DEPENDENCY and clear that lease. Answers arriving during settlement record wake information but do not requeue the task. WAITING_DEPENDENCY → PENDING requires the same settlement and wait-generation checks. [YIELD_SETTLEMENT.md](YIELD_SETTLEMENT.md) defines the mandatory ordering, recovery rules and race tests; it supersedes the earlier early-requeue prescription. Terminal work never reopens because of an optional notice. Retry/failure counters are separate from normal continuation count; every actual execution still increments the attempt identity and consumes its actual resources.

New task kinds: `FOCUSED_ANALYSIS` and `CONTEXT_REVIEW`. Existing SYMBOL_REVIEW, FILE_REVIEW, LINK_REVIEW, INVESTIGATION and FALSIFICATION retain their domains. The sole executing workflow has ANALYZING after indexing. Historical reviews retain their old contract/state meanings but are read-only under CUTOVER.md. A review's activity state is not the candidate readiness predicate.

## 2. Minimum logical persistence additions

These are logical records with required unique/index constraints, not a requirement for one database per concern or an ORM rewrite. Existing tables may satisfy a row if all semantics and migration history are preserved. Store no raw source, tool transcript or provider body here.

| Record | Essential fields / uniqueness | Owner |
|---|---|---|
| work_descriptors | task_id PK/FK, root_work_id, objective, safe assumptions, descriptor_hash; current input head belongs to tasks | task/work service |
| context_requests | request_id, caller_task_id, question_revision, question, subject_set_digest, assumptions_digest, requested_facets, equivalence_key, state, producer_task_id nullable | collaboration router |
| request_consumers | request_id + consumer_task_id + required_revision unique, blocking bool, disposition | collaboration router |
| analysis_artifacts | artifact_id, review/snapshot, kind, backing document/result ID, producer kind/ID, input digest, payload digest, acceptance state, current availability generation | existing result owner plus artifact registry |
| artifact_subjects | artifact_id + subject_kind + subject_id unique; explicit association role | result owner |
| artifact_receipts | artifact_id + receipt_kind + contract_version unique; real producer/turn/operation identities and digests | acceptance owner |
| review_change_counters | review_id PK, last_committed_sequence | coordinator persistence |
| review_changes | review_id + sequence PK, transition_key unique per review, change_kind, artifact/subject refs, availability_generation, safe detail | publication owner |
| analysis_interests | review_id + logical_work_id + subject + canonical_filter_digest unique; registration_H, processed_seq, lifecycle | retrieval owner |
| notice_batches | batch_id, interest_id, low/high sequence, included-result refs, omitted-count semantics, payload_digest, state | runner bookkeeping |
| notice_exchanges | batch_id + request_id unique; attempt, exact request digest, outcome receipt | runner |
| tool_operations | operation_id, review/work, contract, normalized_input_digest, input_revision, status, source-free prepared artifact/result receipt, effect IDs | tool action executor |
| delivery_records | request/turn + tool-call/result identity + actual returned ranges or artifact refs; outcome status | runner; no source bodies |
| coverage_adoptions | target review-unit/task + artifact ID unique; unit/content/contract hashes, validation receipt | canonical coverage owner |
| candidate_families | family_id, snapshot, current candidate_id/revision, validity generation | CandidateService |
| candidate_revisions | family + revision unique, existing candidate_id unique, predecessor, argument digest, required input refs | CandidateService |
| material_dependencies | candidate revision + subject/artifact/negative-search-domain unique; facet identity | candidate owner |
| budget_reservations | existing accounting extension: reservation id, task/attempt/provider request, dimensions, status | admission/accounting owner |
| snapshot_file_locators | snapshot + existing derived file_id unique; normalized path FK to manifest | index/query owner, only if current manifest cannot resolve the opaque file ID directly |

Reuse existing document/evidence payload storage; `analysis_artifacts` is an acceptance/reference registry, not a second knowledge store. Reuse current event/receipt tables when semantically compatible; document that mapping in the migration report. Add indexes on `(review_id, subject_kind, subject_id, sequence)` through explicit event-subject associations, request equivalence/state, consumers by producer, and ready tasks by mode/state/priority. Do not scan all project documents each model turn.

## 3. Publication and availability

Model-authored answers and observations are proposals. Validate shape, source-free prose, IDs, permissions, source anchors and claimed source-read coverage before accepting. This validates origin and contract, not the truth of a security interpretation.

A contextual answer may be accepted during a larger attempt. Its own producer exchange has an immutable accepted response and relevant source-delivery receipts. When full transcripts are required, a sealed per-turn contribution receipt is needed; the entire unfinished attempt need not be sealed. Implement runtime-prefix-v1/transcript-prefix-v1 and the exact event/input/capture validation in PREFIX_RECEIPTS.md before enabling mid-review publication. Never synthesize a completed agent or silently waive a transcript gap.

Result payload and semantic acceptance commit in ssr.db. If the required transcript receipt is not yet available, state is ACCEPTANCE_PENDING. Transcript storage is a separate database: commit and verify its turn seal, then link a source-free receipt in ssr.db. A short ssr.db transaction rechecks all prerequisites and changes the artifact to AVAILABLE, increments the review counter, and inserts exactly one `BECAME_AVAILABLE` event using a deterministic transition key. A retry returns the same transition. No inference or transcript-byte write is inside that ssr.db transaction.

Allocate sequence only inside the same serialized write transaction that publishes its event. Do not reserve sequence blocks per worker or announce a number before commit. Gaps are acceptable; a later committed availability transition may not appear behind an already visible H. Withdrawals and re-availability are new transitions; re-availability increments generation. Historical events stay immutable.

## 4. Lookup, interests, listings and notices

First lookup: in one short read transaction read H and an authorized bounded result page. Close it. In a separate short write, revalidate work, insert the equivalent interest at original H or preserve an existing interest, and record the lookup-operation outcome. A racing publication remains after H. Never replace original H with a fresher counter. Return success only after registration is durable. Failure is recoverable under tool_operations.

Analysis-list order is ascending `(availability_sequence, artifact_id)` within H, with one active availability epoch per artifact. A result restored after H does not reenter the old listing through its earlier epoch. Current acceptance/visibility/status filters always apply. Page continuation cannot advance interest acknowledgment or source credit. Detail reads use the exact selected artifact ID and its immutable body; no latest-result substitution.

At a normal runner boundary, inspect interests in stable round-robin order. Query a bounded sequence span after each processed position. Recheck current visibility. Events that are now irrelevant may be marked processed without claiming an advertisement; a later relevant visibility transition receives a later sequence. For eligible events, create an immutable bounded notice batch. Do not advance beyond an unrepresented eligible event. A coalesced notice may state an exact count for the examined span and include only bounded example IDs plus refresh instructions, explicitly identifying omitted details.

Acknowledge only batches actually present in the final outgoing request, after its valid response and request/response association are durably recorded. This is observable exchange acknowledgment, not model comprehension. A response with malformed tool arguments can still acknowledge a preceding notice. A partial stream without a conclusive outcome is uncertain; safe repeated advertisement at the next normal turn is allowed. Never create a notice-only model call.

Crash after response recording but before acknowledgment: replay host acknowledgment. Acknowledge exact batches, not newest H. Publications during inference remain pending. At most one outstanding batch per interest is advanced in sequence; duplicate or late acknowledgments are idempotent and cannot jump a gap. A previous attempt can only settle its exact recorded exchange, not mutate the successor's task/control/input state. Restored work gets pending notices and a bounded reference to acknowledged-but-unretrieved updates in its continuation context; this is not repeated per-turn advertising.

Interests survive waiting and retryable interruptions. Close them when logical work is terminal. Retain them with review metadata until explicit review retention. No per-worker subscription map and no automatic deletion of active interest history. If the configured interest bound is reached, return an actionable bookkeeping failure and the existing release-interest operation; do not silently unsubscribe older interests.

## 5. Tool operations and exact retries

The host derives an operation identity from `(review, logical_work, operation_kind, contract_version, bound_input_revision, canonical_semantic_arguments)` and maps provider call IDs to it. An exact repeat returns the original receipt. A different payload is a new proposal; this is not fuzzy vulnerability deduplication. Checkpoint expected_sequence and request revision participate in identity. Operations intentionally repeatable as distinct actions require an explicit host-issued action ticket, not a random model identity.

PREPARED contains only source-free validated semantic content and references. COMMITTED contains the immutable receipt and effect IDs. Domain writes and COMMITTED outcome occur in one ssr.db transaction. Persistence retry reuses the same prepared artifact; no extra provider call is needed. Never maintain a generic PENDING row without knowing which owner can reconcile its effects. External provider exchanges are not exactly-once: uncertain retries consume budget and remain explicitly uncertain.

Runtime state must distinguish effect commitment, response preparation, request delivery, and receipt sealing. Current agent access is rechecked before returning a receipt. Recovery of an old committed operation is host-authorized settlement of that original identity, not a way for an expired agent to make new writes.

## 6. Coverage and findings

A complete canonical review-unit artifact may be adopted only if snapshot, exact subject membership/content, review policy, output contract, required fields, evidence and producer receipts all match. Adoption preserves original producer identity; the canonical parent publishes the normal file result and coverage records. A targeted answer covering one question has no unit-completion credit.

New independent lead registration commits a SEEDED candidate through the existing CandidateService plus an investigation task/outbox intent atomically. Queued work does not depend on completion of the proposer. Origin provenance identifies the exact lead tool operation. Canonical file synthesis can reference that origin and avoid recreating the same seed; mere semantic similarity cannot fuse claims.

Every candidate revision binds its argument, material evidence/artifact revisions, assumptions and readiness fingerprint. Fresh falsification is a different agent run/conversation. Final promotion and current export share one host predicate: current revision + complete argument + current accepted material + all required receipts + distinct upheld falsification + no validity hold.

Source-backed material counterevidence accepted through an authorized result sets REVALIDATION_REQUIRED in the same authoritative transaction that exposes the challenge. Store the exact challenged revision/facet. If a historical facet is identically reused by the current revision, hold that revision too; otherwise retain the historical challenge and route applicability assessment without blindly refuting new claims. A successor revision gets a new canonical candidate identity linked to the same family. Historical FINAL_READY rows and exports remain immutable and explicitly historical.

Completion requires all canonical obligations, required collaboration/discovery work, candidate dispositions, publication/receipt reconciliation, leases, reservations and mandatory event propagation to settle. An empty ready queue, optional notices, budget exhaustion, or existence of an export is not proof of completion. Optional undelivered freshness notices on terminal work do not themselves block closure.

## 7. Subject associations and change visibility

On artifact acceptance, store every explicitly covered symbol and the containing file resolved through the inventory. This mechanical file association means relevant analysis exists for that file, not that the file is completely reviewed. A file-level lookup subscribes to artifacts explicitly associated with that file; a symbol-level lookup subscribes only to that exact symbol and its explicit result associations. Do not subscribe to every graph neighbor or guess semantic similarity.

The current visibility predicate is versioned by the review policy and artifact availability generation. A previously unavailable accepted artifact becoming visible after a receipt/revision/association change receives a new availability event/epoch. A new review importing eligible reused analysis creates its own explicit artifact-availability record; it cannot reuse another review's cursor or notice sequence. Existing legacy reviews are not silently backfilled into collaborative mode.

Advance notice processed positions only over the exact event span checked for that interest. Matching events outside a bounded scan stay pending. If the normal outgoing request cannot fit any eligible notice, leave the prepared batch pending; never mark it advertised. Minimum notice form names the subject, known examined change span and availability count/omission status, enabling refresh without requiring all result IDs in context.

## 8. Avoid self-dependent turn sealing

The producer contribution receipt for a model-authored tool action seals the completed provider exchange that **requested** that action: its final request inputs, provider response and tool arguments. Record that exchange outcome before executing the side-effecting tool. Its semantic acceptance does not wait for the tool's own success acknowledgment to be sent in a later model request. Tool-effect and acknowledgment records are subsequent attributable events, not prerequisites that create a cycle.

A transcript contribution seal can authenticate an immutable completed prefix/exchange of an ongoing attempt capture; it must not falsely label the unfinished entire attempt complete. Later turns append normally. A partial/malformed stream without an accepted tool-call response cannot publish an artifact. Test specifically that publish_context_answer/report_lead can commit while the parent attempt continues and before their own ACK is consumed.

## 9. Checkpoint search queries and sensitive text

A source search query can itself contain source or a discovered secret. Do not persist arbitrary query strings in ordinary checkpoint/operation/audit rows just because they are tool arguments. Saved search state always includes its authenticated cursor, query digest, mode, flags and manifest selection; query text is optional and may be saved only if the existing persistent-prose/content guard accepts it as source-free and credential-free. Otherwise store `query_omitted_reason: SOURCE_SENSITIVE` and tell the resumed analyst that exact query text must be supplied again to continue; it may instead start a fresh suitable query. Do not pretend the cursor digest can reconstruct the text or create a new sensitive store solely for pagination. This explicit limitation does not affect source-reading cursors, which need no query text.

## 10. Exact hardening owners

Use [STATE_MACHINE.md](STATE_MACHINE.md) and machine-readable `schemas/state-transitions.json` for every task, agent, review and investigation/falsification transition; all unlisted transitions are forbidden. [MIGRATION_PLAN.md](MIGRATION_PLAN.md) covers DDL, views, triggers, fingerprints, two-store activation and guarded SQL. The new runtime executes only collaborative-v1 under [CUTOVER.md](CUTOVER.md).

[INPUT_REVISIONS.md](INPUT_REVISIONS.md) and [PREFIX_RECEIPTS.md](PREFIX_RECEIPTS.md) define exact immutable revision/request/prefix bodies, hashing and replay. Prefix proof never substitutes for mandatory terminal predecessor settlement on yield. [FILE_SYNTHESIS.md](FILE_SYNTHESIS.md) defines manifest/journal/CAS/final-seal storage; the model cannot be required to retransmit the complete canonical graph. [RESOURCE_BOUNDS.md](RESOURCE_BOUNDS.md) freezes transactional root/review/consumer/pending counters and finite progress. These are shared contracts, not separate state authorities.

The new task row owns `input_revision_id`, `input_generation` and `last_settlement_id` for guarded admission. work_descriptors does not maintain a competing writable revision head. Input revisions are immutable; the task head and descriptor projection change in one task-owner transaction.
