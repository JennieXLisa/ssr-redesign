# PostgreSQL storage and data ownership

Implements S1-IN-R07/R20/R21, S1-IX-R01–R05, S1-FN-R01–R09, S1-RF-R01–R06 and S1-FL-R01–R12. The SQL in `contracts/v1/schema.sql` is the initial relational layout. New installations apply numbered immutable SQL migrations in a transaction with a PostgreSQL advisory migration lock. Do not create old-harness migration paths.

## Identity and reuse

A snapshot is an immutable source identity, not an index run. A dataset is a versioned derived result collection. A requested index run points to three datasets: extraction, resolution, and flagging. The extraction fingerprint includes snapshot ID, parser/grammar versions, language overrides and encoding configuration. Resolution adds the extraction fingerprint, resolver version and sanitized compilation-context digest. Flagging adds extraction fingerprint, rule-manifest digest, name matcher version and Semgrep version/options. All fingerprints use SHA-256 of the canonical JSON semantic configuration, not mutable file paths.

Changing a rule creates a new run/flagging dataset while reusing compatible extraction/resolution datasets. Encoding/language overrides produce a new extraction profile and its own file_metadata publications; never overwrite another run's interpretation in the shared snapshot file row. Retrying an interrupted run does not create new source or semantic configuration. A unique `(snapshot_id, kind, fingerprint)` dataset key makes concurrent requests converge on compatible work. Hardware/concurrency changes do not invalidate datasets. A run's dataset references never change after creation.

Use UUIDv4 for project/snapshot/run IDs. Dataset IDs are UUIDv5 of the project UUID and `kind + ':' + fingerprint`. File IDs are UUIDv5 of the snapshot UUID and the canonical encoded project-relative path. Source record IDs are UUIDv5 of the extraction dataset UUID and a canonical tuple of file ID, record kind, byte interval, enclosing occurrence ID and ordinal. Sort siblings by original source position before assigning an ordinal. Never include a worker ID, task order, transient path or timestamp in a source record identity.

## Entity ownership and keys

| Table | Owner and key meaning |
|---|---|
| projects | Storage root association and project label; not a target repository checkout. |
| snapshots | Capture state, managed commit/tree OIDs, source kind and frozen intake manifest. |
| files | Immutable snapshot entry, raw path bytes/display path, Git mode/blob and size. Capture-time classification fields are hints, not a mutable analysis profile. |
| file_metadata | Published extraction-profile-specific encoding, language classification and original-byte line map. |
| exclusions | Selected path/prefix exclusion, reason and parent/submodule provenance; not a successful processed file. |
| rule_manifests | Immutable effective mode, complete canonical rule definitions and all source references. |
| datasets | Snapshot-bound extraction/resolution/flagging identities, fingerprints and lifecycle. |
| index_runs | Requested composition of datasets and aggregate processing status. |
| work_units | One dataset/file/component job, current lease, attempt generation, failure and published result digest. |
| publications | Candidate result set identity, owning work/generation, manifest and visibility marker. |
| symbols | Stable extracted callable/type/module identities and local/qualified names. |
| occurrences | Exact definition/declaration/body/signature/default-expression ranges; one source fact may have multiple roles. |
| reference_occurrences | The source expression, usage, receiver span, enclosing scope and processing input identity. |
| arguments | Ordered positional/keyword/spread argument ranges linked to a call occurrence. |
| bindings | Resolution outcomes, target/candidate IDs and explicit basis, separate from observations. |
| symbol_associations | Proven declaration/definition equivalence links; never name-only merges. |
| flags | Rule-qualified observations, exact range, category and nullable known owner. |
| diagnostics | Structured errors/limitations and correlation IDs; no secret-bearing raw exception strings. |

The schema stores normalized linked records, not caller/callee arrays in a function row or complete function bodies in PostgreSQL. Small signature text and rule definitions are intentional metadata. Original source, including documentation, remains in managed Git. A read-only blob/materialization cache can be deleted and reconstructed; it is not another authority.

## Publication strategy

Workers build a staging publication identified by `(work_id, generation)`. Insert its output in bounded database batches; these inserts remain invisible to normal navigation because every result query joins a committed publication. Record counts and a SHA-256 digest of its sorted output manifest. In one short transaction, lock the involved datasets in UUID order before the work row and publication, validate its unexpired lease/generation and all input dataset references, validate counts/foreign references, mark the publication committed, and set the work row SUCCEEDED with that publication ID. The common order and shared-run guards in execution.md apply to every writer. The worker does not publish by committing arbitrary individual result rows.

Keep result rows keyed by publication plus stable logical record ID, so an abandoned staging set cannot block a successor with uniqueness conflicts. All public lookups include the selected run's dataset and the work row's active committed publication. IDs from an abandoned publication are not resolvable. Published extraction occurrences are immutable. If two executions of identical semantic inputs produce different sorted manifests, report NONDETERMINISTIC_OUTPUT; do not overwrite a successful set.

Foreign keys establish containment where possible: publication→work, work→dataset/file, file→snapshot and record→publication. Composite constraints and publication-time validation establish that a source record belongs to the dataset's snapshot. Binding targets must refer to visible occurrences in the exact selected extraction dataset. No worker may link to an occurrence from a later run merely because its local name matches.

## Minimum indexes

Create B-tree indexes on files `(snapshot_id, path_prefix)` (first 512 raw path bytes), work `(dataset_id, component, state, next_attempt_at, file_id)`, symbols `(publication_id, md5(local_name))` for equality acceleration, occurrences `(publication_id, file_id, start_byte, occurrence_id)`, references `(publication_id, owner_symbol_id, start_byte, reference_id)`, bindings `(target_symbol_id, reference_id)` and `(reference_id, outcome)`, flags `(publication_id, category, file_id, start_byte, flag_id)`. Index all foreign-key columns used for cleanup and run queries. Use PostgreSQL `C` collation or explicit byte-sort keys for portable ordering; host locale must not reorder pagination. Full raw path bytes break ties after the bounded path-prefix index; never treat its prefix or path hash as the path identity. Verify raw equality after a digest lookup and report a digest collision as an integrity error. Long source paths must not be silently omitted.

Wildcard/regex semantics are defined by the shared pattern library, not PostgreSQL's different regex dialect. Fetch candidate metadata in ordered batches and apply the authoritative matcher. A sound literal-prefix optimization is allowed only with equivalence tests; do not introduce a shortcut that can lose matches. No embeddings or full-source text columns are required.

## Query consistency and completion

Read a navigation page, related occurrences, and its coverage counters inside one short REPEATABLE READ read-only transaction. This keeps a page from combining pre-publication records with post-publication completed counts. Never hold that transaction between pages or across user think time. Source materialization can happen after obtaining immutable references. Each later page is a new live view.

Dataset success is an owner-controlled transition: all required work units SUCCEEDED; inapplicable components were never queued; unresolved bindings are valid outputs; failed extraction/scanning is not. Dataset publication cannot continue after SUCCEEDED. A run is complete only when all selected datasets and captured-file metadata obligations complete. The displayed per-step totals derive from applicable distinct files, not attempts, matches, publication batches or historical failures. Flagging combines the name and Semgrep components per file: failed if either required component is FAILED, complete only if all required components succeed.

## Retention and repair

Do not implement automatic deletion of completed snapshots or datasets in Stage 1. A backup must include PostgreSQL and each managed Git repository/ref. Test restoring them together. An absent Git blob is STORAGE_INTEGRITY_ERROR, not a cue to fetch newer source. Abandoned staging data may be removed only when its lease generation is no longer active and no committed publication refers to it. Maintenance operates through storage ownership, not an agent issuing ad-hoc SQL.

## Internal records and JSON column mapping

`contracts/v1/records.py` is the executable internal extraction contract, separate from public response DTOs. `SourceUnit` is ephemeral; its original bytes/parser buffer are never serialized into a stored result. `ExtractionBundle` carries snapshot/extraction/file/profile identity once. The publication owner compares these to its claimed work and passes the original SourceUnit to byte/line validation before any activation.

| Bundle record | Durable representation |
|---|---|
| ScopeRecord | scopes; parent links and executable owner IDs remain explicit, including one full-file module scope. |
| SymbolRecord | symbols; owner_scope_id is the declaration scope. owner_symbol_id is a derived nearest enclosing owner, never an independently guessed parent. return_type is TypeFact; properties is an array of PropertyFact; provenance is Provenance. |
| OccurrenceRecord | occurrences; scalar range columns and typed nullable ByteRange subranges; parameters is an ordered ParameterRecord array. Derive missing public columns from immutable source metadata, not parser offsets. |
| ReferenceRecord | reference_occurrences plus arguments; scope_id is evaluation scope. spelling is the original decoded expression. provenance is Provenance; no binding outcome is stored here. |
| ImportRecord / DeclarationRecord | imports / declarations, not ad-hoc JSON hidden inside a reference. Declaration invalidations include parameters, assignments and deletions even when they have no target symbol. |
| ExtractionDiagnostic | diagnostics.detail contains exactly the typed diagnostic; snapshot/dataset/file/work identity is stored in its columns. Successful-bundle limitations additionally require publication_id pointing to that output's publication. Failed-attempt and general work errors have null publication_id and cannot enter a successful output manifest. A failed bundle has error diagnostics and no publishable inventory. |

JSON columns accept only the named model's JSON projection (`model_dump(mode='json')`), including explicit nulls; unknown fields are rejected before SQL. IDs in all per-file collections must be unique; owners, scopes, imports and occurrences reference the same bundle. SourceRange endpoints are recomputed against original bytes/codecs during publication. A symbol occurrence must cover its actual syntax, not just pass a size check. Database foreign keys complement rather than replace these owner predicates.

For publication-associated diagnostics the owner verifies publication.work_id equals diagnostics.work_id and that all snapshot/dataset/file identities match that work. The diagnostic code column must equal detail.code. Reconstruct output diagnostics only by the selected committed publication_id, never by work_id alone: a stale/failed attempt may have different limitations under the same work identity. General diagnostic listing may show historical errors, but result_count/result_digest cannot include them. The pure manifest regression includes both abandoned and active publications; W02 must repeat this round-trip with PostgreSQL.

## Durable applicability plan

Bootstrap exactly one extraction `text_metadata` unit for every included file. After all these publications succeed, insert one dataset_plan_files row per included file **for each selected dataset**, referring to the same extraction-profile metadata publication. Each row states treatment, reason and an ordered duplicate-free components array; an empty array explicitly means no applicable work, not a missing file. Extraction components are text_metadata plus extract where supported; resolution uses resolve where the structural language supports reference inventory; flagging uses name_flags/semgrep_flags according to the frozen selection. LFS pointers/symlinks/binary treatment remains explicit.

Under dataset locks, verify the complete captured-file census, same-snapshot/profile visible metadata, allowed dataset/component combinations and exact work-unit set; compute the canonical plan digest and atomically set plan_state=FROZEN, plan_digest and plan_file_count. Zero-file captures freeze a zero-row plan rather than remaining initializing forever. Resume an interrupted unfrozen plan idempotently; changing its semantic inputs allocates another dataset. Frozen plans cannot add/remove/reclassify files. query_ready is derived from all three frozen plans and their metadata visibility; no mutable snapshot-wide classification is used.

## Canonical manifests and hashes

Use `records.canonical_bytes`: recursively sorted string object keys, original array order, UTF-8, ensure_ascii=False, allow_nan=False, no BOM/whitespace/newline, and explicit null fields. No Unicode normalization, machine paths, timestamps, worker identity or locale affects semantic identity. Profile objects are versioned; absent and null are distinct unless their typed model supplies the same default. SHA-256 is lower-case hex of these bytes, never Python repr or PostgreSQL jsonb textual formatting.

The exact plan hash input is `{schema_version:1, dataset_id, snapshot_id, files:[{file_id, metadata_publication_id, components, treatment, reason}, ...]}`. Sort files by their original path bytes, then file UUID; order components as text_metadata, extract, resolve, name_flags, semgrep_flags. Metadata publication IDs are audit provenance: for the **semantic** plan digest replace metadata_publication_id with its committed result_digest, so retries with identical output do not change semantic identity.

The output manifest is `{schema_version:1, records:[{collection, record_id, value}, ...]}`. value is the full typed record JSON, without publication ID, lease, generation or timestamps; collection is one of the bundle collection names; record_id is its stable logical UUID (diagnostics use a canonical value digest). Sort by collection ASCII bytes then record_id. result_count counts these records, including scopes and declarations; it is not just the symbol count. Compute/compare manifests from typed values before SQL and reconstructed visible rows after SQL. Failed diagnostic-only outputs are not activated as successful extraction. Record UUID names use the canonical JSON array `[file_id, record_kind, start_byte, end_byte, enclosing_id, ordinal]`, with UTF-8 UUIDv5 name semantics. The namespace is the extraction UUID; kinds distinguish scopes, symbols, occurrences, declarations, imports and references. Assign an enclosing record before its children and sort same-kind siblings by original range then deterministic syntax role before ordinal assignment.
