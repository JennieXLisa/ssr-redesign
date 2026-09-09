# Collaborative-v1 storage and state-machine cutover plan

Normative companion to [STATE_MACHINE.md](STATE_MACHINE.md), [CUTOVER.md](CUTOVER.md), [PREFIX_RECEIPTS.md](PREFIX_RECEIPTS.md) and [FILE_SYNTHESIS.md](FILE_SYNTHESIS.md). This is implementation guidance against inspected baseline `09891721b9d3509a3d618c7a25d3a3f184b0e225`, not a migration already executed. Numeric migration ordinals and actual historical object SQL are read from the implementing checkout; none may be guessed from a stale branch.

## MP-R01 — Inventory the real dependency closure

Before editing DDL, build `migration-object-map.json` from `sqlite_schema` and the checkout's migration resources. For each affected table list its full CREATE SQL, inbound/outbound FKs, indexes, triggers and views; for each view recurse its known dependents. Record existing schema version, migration checksums, schema fingerprint and rows/hashes for immutable evidence, result, candidate and transcript-link records. The current schema validator checks canonical object identity; it must be updated from actual new canonical DDL, not bypassed.

Minimum root set is tasks, agent_runs, review_runs, their transition triggers; `dependency_ready_tasks_v46` and any replacement readiness views; file_review_units/graphs and contribution/adoption references; candidate revision/disposition projections; runtime event/receipt and transcript-link tables. The exact view suffix is a baseline observation, not a name to retain blindly. Search all SQL and Python switches for task_type, task/status, review phase and agent terminal outcomes and attach every found consumer to this map.

Verified code owners: orchestration/contracts.py, service.py, admission.py, recovery.py, events.py; db/database.py and db/schema_contract.py; agent/runtime.py and events.py; runtime_receipt.py; transcript/receipt.py and reconciliation.py; language base.py for the IR extension. Existing application/query services and worker-finalization responsibilities must be mapped from the current package directories during R0, not recreated under obsolete monolithic filenames.

## MP-R02 — Quiescence and durable activation barrier

Acquire the project coordinator. Verify no active legacy process identity, agent, lease, unresolved provider request or recoverable live writer remains. Do not make this true by rewriting their states. Require explicit stop/settlement using the old release before migration. Back up both stores through the current safe backup authority; record each backup hash and schema version.

Record a source-free cutover intent with project ID, source schemas/fingerprints, target `collaborative-v1` bundle hash and stage PREPARED. The coordinator owns it, not a worker. Project storage and transcript storage are upgraded independently, with stage receipts `PROJECT_SCHEMA_VALID` and `TRANSCRIPT_SCHEMA_VALID`. Activation becomes `ACTIVE` only after both validate and exact new runtime/SDK capabilities match. If one store fails, new review creation remains disabled; restart resumes the missing stage using its idempotent receipt. There is no cross-database atomicity claim.

## MP-R03 — Rebuild constrained tables safely

Use the existing migration runner's single writer transaction. If its supported table-rebuild path requires foreign_keys OFF, change that setting before BEGIN and restore it after commit/rollback; changing it inside a transaction is ineffective. Record the prior setting and never leave it disabled on a returned connection.

1. Snapshot dependent object definitions and counts. Create replacement tables under temporary new names with the final columns, CHECKs and FKs.
2. Copy explicit named columns; add mode/history classification based on the pinned original review contract, not heuristic phase names. Preserve every historical ID, timestamp, digest and receipt byte unchanged. Do not use SELECT * against differently ordered schemas.
3. Remove dependent views/triggers in their dependency order, drop old tables, then rename replacements to canonical names. Recreate indexes, triggers and views from reviewed final DDL. Do not rename the old parent first or patch writable_schema strings.
4. New checks allow the selected state/kind domains, but admission only permits collaborative rows. Transition triggers reject unlisted pairs and mutation of immutable history. Guarded runtime operations additionally validate semantic proof; a legal state pair alone is not an authority grant.
5. Run foreign_key_check, quick_check/integrity_check as required by the existing runner; compare copied row counts, immutable body hashes and complete expected-object inventory. Abort on any difference not enumerated in the migration transform. Commit migration checksum and schema outcome with the project change.
6. Restore FK enforcement, reopen read-only and run schema_contract validation. Build an isolated installed wheel and confirm new migration resources are packaged. Never edit prior migration files to hide mismatched checksums.

The transcript migration adds prefix-seal rows and versioned v2 capture support without rewriting v1 captures. Its own validator checks original capture identity/record bytes and new immutable seal constraints. Old terminal receipts remain historical and cannot certify new prefixes.

## MP-R04 — Selected new table invariants

All identities are TEXT with the schema bounds; byte/token/count fields are INTEGER with nonnegative CHECKs and the 2^53-1 ceiling. Digests are lowercase 64-character hexadecimal TEXT. Timestamps are canonical UTC text. JSON uses closed canonical schemas, not arbitrary dictionaries. Every record carries a project/review foreign-key path; include composite ownership guards where an ID alone would allow a cross-review association.

| Logical relation | Required primary/unique indexes | Required transition/immutability rule |
|---|---|---|
| input_revisions | revision_id PK; UNIQUE(task_id,generation); predecessor FK | Body/hash immutable; task input head CAS only |
| request_input_bindings | request_id PK; UNIQUE(agent_run_id,request_id); input revision FK | PREPARED→OBSERVED only for matching valid response; IDs/digests never change |
| yield_intents | intent_id PK; UNIQUE(task_id,wait_generation); operation_id unique | PREPARED→SETTLING→PUBLISHED/CANCELLED; BLOCKED recovery only with original fence; no early task requeue |
| attempt_settlements | agent_run_id PK; task/attempt/control tuple unique | Valid terminal proof or explicit irrecoverable disposition; source-free immutable receipt |
| runtime_prefix_receipts | prefix_id PK; UNIQUE(agent_run_id,end_event_sequence); parent FK | One chain; append increasing end; no body update/delete |
| transcript_prefix_seals (transcript.db) | prefix_id PK; UNIQUE(capture_id,end_record_sequence); parent FK | Capture remains appendable; sealed included records cannot change |
| synthesis_manifests/items | manifest_id PK; UNIQUE(manifest_id,ordinal), UNIQUE(manifest_id,item_key) | Header/root/items immutable after construction seal |
| synthesis_sessions/entries | session_id PK; UNIQUE(task_id,input_revision_hash); UNIQUE(session_id,revision) | CAS journal append; no entry rewrite; session seal freezes writes |
| synthesis_reference_pages | UNIQUE(session_id,set_key,page_index) | Contiguous pages, one final page, duplicate-identical replay only |
| synthesis_current_decisions | UNIQUE(session_id,decision_key) | CAS by prior entry hash; every version retained in entries |
| candidate_revision_dispositions | UNIQUE(candidate_id,revision) plus current-family pointer | Total outcome mapping; later material creates new revision or validity hold, not historical rewrite |
| quota_receipts/counters | UNIQUE(operation_id,dimension,key); UNIQUE(dimension,key) | Multi-counter guarded update in same domain transaction; exact replay consumes no quota |

Reuse an existing relation when it supplies all invariants. This list is not permission to create a competing source, evidence, candidate or notification store. Schema-level FK/integrity rules and domain validation are complementary.

## MP-R05 — Claim and publication SQL must agree

The following is a selected guarded pattern; map actual column names from the verified DDL and keep the predicates together in the orchestration owner:

```sql
UPDATE tasks
SET status = 'LEASED', attempt_count = attempt_count + 1,
    lease_owner = :worker, lease_token = :token, lease_expires_at = :expiry
WHERE task_id = :task AND status = 'PENDING'
  AND input_generation = :expected_input_generation
  AND last_settlement_id IS :expected_settlement_id
  AND NOT EXISTS (
      SELECT 1 FROM yield_intents y WHERE y.task_id = tasks.task_id
      AND y.state IN ('PREPARED','SETTLING','BLOCKED'))
  AND NOT EXISTS (
      SELECT 1 FROM agent_runs a WHERE a.task_id = tasks.task_id
      AND a.status IN ('CREATED','RUNNING','WAITING_FOR_TOOL'));
```

Use exact row-count=1 assertion after the full readiness/resource checks in the same immediate transaction. Initial never-dispatched tasks have an explicit null predecessor fence; a resumed task requires the sealed predecessor association. Parent receipt reconciliation cannot be replaced by a boolean provided by the model.

The final yield-publication update compares task RUNNING, exact captured attempt/control/lease, input generation and yield-intent generation. It changes state, clears lease, records last_settlement_id, binds checkpoint/deltas and marks intent PUBLISHED atomically. Wake uses WAITING_DEPENDENCY plus that same published settlement/generation. Update planning, exact-task selection, driver, query and completion to call the same predicates; remove the old type-to-phase CASE for new work.

## MP-R06 — Acceptance and rollback fixtures

Seed fixtures for every old task/review/agent state, existing constrained graph and candidate links, required/optional/missing transcript receipts, and both FK-valid and deliberately invalid histories. Active-old cutover must reject before writes. Settled old rows must survive byte-identically and remain unclaimable. Test every new task kind through plan→claim→start→settle; test every matrix pair with and without its required cause.

Inject failures after create/copy/drop/recreate, before ledger commit, between the two database migrations, and before capability activation. Either old valid schema remains or the exact pending activation stage is recoverable; no partial new runtime admission. Verify migration resources and schema fingerprints in a clean installed artifact. The reference suite's small SQL fence test is not this full migration test; Codex must implement and run these against real baseline fixtures before enabling the new runtime.
