# P7-F01 — Contracts and persistence integration: implementation plan

Updated: 2026-09-09. Documentation only. Read the [feature](../P7-F01-contracts-and-persistence.md), [STATE.md](../../../contracts/STATE.md), [TOOLS.md](../../../contracts/TOOLS.md), [role projections](../../../contracts/ROLE_PROJECTIONS.md) and [baseline map](../../../BASELINE.md). Logical record names below are design names; allocate actual migrations from the selected checkout, not from historical schema numbers.

## 1. Build the integration ledger

For every new logical record/API, list: existing owning module/table or proposed extension, key identity, source sensitivity, writer, readers, unique constraints, transaction owner, event consequence and recovery function. Do this against actual sqlite_master/migration files and public exports. Reuse compatible structures; a table per feature is not required.

The minimum mapping covers work descriptors/inputs, context requests/consumers/inbox, artifact registry/subjects/receipts, availability counter/events, interests/batches/exchanges, operation outcomes, source-delivery records, adoption receipts, candidate families/revisions/material dependencies and budget reservations. Existing candidate/evidence/task/source IDs remain authoritative.

Record module dependencies: source verification and passive contracts must not import the mutable broker; domain acceptance must not depend on the controller; query projections must not mutate domain state. Small caller-transaction primitives stay with domain owners, not a generic repository that copies their rules.

## 2. Canonical contract types

Implement one discriminated typed representation for SourceRef/EvidenceRef/ArtifactRef, producer variants, operation outcomes, contextual outcomes, notices and work input revisions. Reject unknown discriminators/fields and invalid integer-versus-bool inputs. Preserve source-free ordinary projections separately from explicit sensitive-content responses.

Generate provider-supported input schemas from the full host contracts and validate the host result against the full schema regardless of provider subset support. Retain role-specific analytical requirements. Host-derived identity removal is the reviewed P1-F03 mapping, not deleting every nested ID. Add schema fixtures for every tool/role variant, not only the generic envelope.

Canonical JSON/hashes use one utility, with explicit key ordering, Unicode handling, finite numbers and set-versus-sequence normalization. Version and hash tool definitions, output contracts, input/delta bodies, registry/models, policy and configuration. Do not change serialization behind an existing version/hash identity.

## 3. Key and constraint plan

Use foreign keys and CHECK/UNIQUE constraints where compatible with the existing migration conventions. Application validation still supplies useful errors; database constraints protect concurrent writes.

| Logical data | Required identity/invariant | Query index intent |
|---|---|---|
| work input revisions | Unique work+revision; immutable digest/body; current pointer CAS | Work/current revision and generation |
| tool operations | Unique review+logical-work+semantic-operation identity; committed receipt immutable | Recoverable status+owner+operation ID |
| request production | Exact equivalence key and producer revision; consumer links independently unique | Consumer wait generation; producer live demand |
| artifact subjects | Unique artifact+subject association; artifact points to one typed immutable payload | Subject+artifact availability lookup |
| review changes | Unique review+sequence and unique transition key/generation | Review+sequence; indexed subject association |
| interests | Unique review+work+subject+normalized-filter digest | Work active interests; last processed position |
| notice batch/exchange | Exact interest/generation/batch payload and final request identity | Pending batches; response-recorded/unacknowledged |
| coverage adoption | At most one current acceptance per canonical obligation/generation | Canonical unit and original artifact |
| candidate revisions | Unique family+revision; current pointer CAS | Current family and material facet consumers |
| reservations | Exact request/attempt+dimension identity; one settlement per usage identity | Held/uncertain resource group |

Do not turn a nullable field into a loophole for duplicate logical keys. SQLite UNIQUE permits multiple NULL values; normalize key variants or use appropriate partial unique indexes/CHECK constraints to express the actual discriminated identity. Avoid arbitrary composite text concatenation without versioned escaping/canonical hashing.

## 4. Required SQL/query boundaries

Parameterize all model-derived filters. Scope every identity lookup by its governing review/snapshot/registration, not bare globally formatted IDs alone. Build authorization and current-availability predicates before metadata release, grouping and paging. Do not fetch an entire manifest/document store into Python to apply permission filters.

H-bounded analysis query joins the artifact's currently active availability epoch and constrains its sequence to H. Keyset continuation uses `(availability_sequence,artifact_id)` rather than OFFSET. A restored artifact uses a new epoch; its old sequence cannot reintroduce it to an old traversal. Select per-subject indexed event associations without copying the whole publication history per interest.

Use EXPLAIN QUERY PLAN and representative large fixtures to verify index intent for manifests, incoming/outgoing relationships, active requests and pending reconciliation. A bounded returned page does not imply a bounded query if the planner scans millions of unrelated rows; record actual plan and candidate-scan work.

## 5. Transaction ownership matrix

Lead registration: candidate/origin/evidence links plus follow-up task or durable intent plus COMMITTED operation receipt. Request routing: request/consumer plus producer/inbox/task intent plus blocking-edge check. Yield: exact checkpoint/wait predicate, lease transition and operation receipt. Availability: acceptance state plus committed sequence/event and required wake intents. Challenge acceptance: material relation, current validity hold/generation and reassessment intent. Closure: final obligation recheck plus terminal disposition.

Each operation has one project-transaction owner and caller-connection helpers. No helper silently commits midway. Expensive parsing, source verification, subprocess work, inference and file rendering occur outside write transactions, followed by rechecking mutable authority inside them.

Transcript/key/artifact filesystem stores have explicit staged receipts and recovery; they are not made atomic by a comment saying 'transaction'. Model action acceptance requires the real completed producer exchange, never its own later ACK. Preserve pending state if a cross-store prerequisite is missing.

## 6. Migration batches and enablement

Treat M-A through M-D in STATE.md as logical batches, not filenames: mode/contracts/operations; collaboration/artifacts/availability; adoption/current validity; claim/closure/projections. A developer may combine compatible additions, but no intermediate schema advertises capabilities whose writer/reader/recovery path is missing.

Create historical fixtures by applying actual original migrations to their supported horizons, then insert valid historical data through period-correct fixtures/services. Never create the newest schema and manually change its version row to simulate an older database. Verify old migration checksums remain byte-identical.

For each new migration: backup disposable input, apply using the existing coordinator migration lock, verify foreign keys/constraints/indexes and preserved row identities/content hashes, reopen from a clean process, and repeat upgrade/recovery behavior. Allocate the next real migration ordinal only after checking concurrent branch changes. A failed upgrade cannot set the new compatibility/mode-ready flag.

Backfill mode as legacy for existing reviews. Do not reinterpret stored task inputs, prompt/tool hashes or old enum semantics. Any new current pointers/generations need deterministic verified backfill or remain explicitly not applicable to legacy state. A new parser cannot read an old payload under the wrong contract merely because fields look similar.

## 7. Cross-feature validation and conflicts

Build a matrix from each feature requirement to its authoritative type/function/query and test. Detect competing state names, retry_kind enums, capability strings and ownership rules before coding. For example REFRESH_INPUTS is a repair action, not an undeclared retry_kind; current-finding validity is not task completion; SourceRef is not accepted evidence.

If shared prose/schema and a detailed plan conflict, record a contract discrepancy and make one explicit versioned correction with test impact. Do not implement two local variants or weaken the host validator to accept both silently. Local private names are discretionary; wire semantics, historical identities and transaction guarantees are not.

## 8. Recovery and migration tests

Concurrently insert identical operations/events/requests and assert one canonical effect with legitimate consumer/provenance links. Alter immutable payload fields under an existing ID and require integrity failure. Interrupt staged receipt linkage and verify the artifact remains unavailable until the actual receipt is recovered.

Run migration tests at each supported historical horizon, including old active/terminal review records, failed receipts, adopted-like legacy data and current config hashes. Compare original bytes/IDs and legacy public query results. Test partial migration rollback/restart and unsupported future schema failure before provider execution.

Round-trip each tool/role input through provider projection and full host validator. Negative fixtures include discriminant mismatch, unknown fields, boolean integers, stale revision, wrong snapshot and sensitive content. Verify query plans on large synthetic metadata and no protected identity leakage.

## 9. Delivery and exit evidence

Deliver the integration ledger; typed/schema fixtures; append-only migration patches; caller-owned mutation interfaces; read/query plans; recovery dispatch; then whole tool→artifact→availability→request→candidate→closure traces. This feature is a foundation implemented incrementally with its consumers, not an excuse to build all tables before any usable path.

Completion requires actual migration/constraint/query-plan results and preserved old hashes. No generic ORM rewrite, universal workflow interpreter, duplicated contract classes, guessed schema horizon or distributed-transaction fiction is allowed.
