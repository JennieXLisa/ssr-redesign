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

Workers build a staging publication identified by `(work_id, generation)`. Insert its output in bounded database batches; these inserts remain invisible to normal navigation because every result query joins a committed publication. Record counts and a SHA-256 digest of its sorted output manifest. In one short transaction, lock the work row, validate its lease/generation and all input dataset references, validate counts/foreign references, mark the publication committed, and set the work row SUCCEEDED with that publication ID. The worker does not publish by committing arbitrary individual result rows.

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
