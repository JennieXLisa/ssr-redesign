# Durable compiler contexts and reference reconciliation

This refines W02/W09/W12. `resolution.clang` produces observations;
`indexing.publication` owns their visibility and fencing; storage owns SQL only,
and W12 consumes the published observations.
[compiler_records.py](../contracts/v1/compiler_records.py) defines internal typed
values. [reference_contexts.py](../validation/reference_contexts.py) is a pure
decision/projection reference, not a compiler, scheduler or database adapter.
The accepted command grammar remains [compiler-profile.md](compiler-profile.md),
including rejection of `-c`, `-o` and every other unlisted action/output flag.

## Ownership and the two censuses

Each resolution dataset owns a `compiler_context_plans` row, including datasets
with no C/C++ work. Compiler contexts have separate `compiler_context_work` and
`compiler_publications` tables because a TU is not a physical file-step: several
commands can cover one source file and one command can cover several headers.
They use the same lease/publication owner and lifecycle policy as ordinary work.
There is no second public coverage object, process pool or queue service.

There are two immutable censuses:

1. The **input census** contains every selected command entry or conservative TU
   recipe, accepted or rejected, before compiler work starts. It is an input to
   resolution identity. Rows are `ContextDefinition` with a typed `ContextSpec`.
2. The **reference census** contains every actual C/C++ `ReferenceRecord` from the
   complete selected extraction dataset. It freezes after successful extraction.
   It is a prerequisite/output audit, never an input to dataset identity.

The expected context set for every physical reference is exactly the Cartesian
product of those two censuses, identified by the fixed rule
`ALL_CPP_REFERENCES_X_CONTEXTS_V1`. Store O(contexts + references) rows, not a dense
matrix of placeholder observations. Iterate the expected pairs when reconciling;
never derive expectations by taking DISTINCT over whichever observations arrived.
The conservative product avoids needing an untrusted build/include graph before
parsing. It can lose precision when a rejected context's affected files cannot be
known; this limitation is explicit rather than silently dropping that context.

## Input selection and fingerprint order

1. Start with a READY snapshot and a typed `SemanticProfile`. Use the frozen
   capture manifest and [language profile](language-profiles.md) path/dialect
   rules as data. Resolve canonical display paths to original inventory paths
   through the path owner; never discover configuration or files from a checkout.
2. With `compilation_database`, read that captured JSON file as a strict array.
   Invalid JSON, duplicate object keys, nonfinite numbers, or a non-array root is
   a profile/input error before dataset allocation; do not silently substitute an
   empty database or default profile. Every array element occupies its original
   ordinal, even a malformed command object. `arguments` precedence, tokenization
   and atomic rejection follow the strict sanitizer. Do not deduplicate repeated
   array entries; entry provenance and expected processing remain distinct.
3. With `compiler_options`, preserve the tuple's order and each options record's
   `translation_units` order. For each selected TU build an explicit conservative
   command using its `language` (`cpp` becomes `-x c++`), `standard`, ordered
   `include_roots`, and the installed profile's explicit target. Root `''` means
   the captured root. Pass it through the same sanitizer. These recipes contain
   no `-c`/`-o`. `conservative_context_specs` is the runnable mapping. No extra TU
   is discovered after an explicit selection.
4. When both selections are empty, enumerate captured regular files with `.c`,
   `.cc`, `.cpp`, or `.cxx` suffixes in original-path byte order; explicit frozen
   path/dialect overrides take precedence. Keep only selections whose dialect is
   C or C++. Use c17/c++20 and the captured root include path. This enumeration
   uses manifest names and profile overrides, not extraction results. Headers,
   extensionless files and other suffixes require explicit `CompilerOptions` to
   be standalone TUs. Do not run a parser/compiler/build to discover more contexts.
   An explicit empty database stays empty; default enumeration is not a fallback
   after database or context rejection.
5. A `ContextSpec` stores ordinal, origin, entry/recipe digest, nullable captured
   TU file ID, nullable effective digest/payload, and nullable rejection code.
   Accepted specs require all TU/effective fields; rejected specs require null
   effective fields. An invalid unmappable source has a null TU ID, not an invented
   file record. Captured objects use their canonical JSON digest as entry identity;
   conservative recipes hash `{language, standard, include_roots, translation_unit}`
   with logical paths, never generated native paths.
6. `EffectiveContext` persists the exact sanitizer hash payload: version,
   snapshot, toolchain, logical source, ordered logical flags and sorted default
   assumptions. Replace only validated path operands with `root_id:/relative`
   identities. Do not replace matching substrings inside a macro value.
   `effective_context` reconstructs this payload and checks its digest against
   `sanitize(...).fingerprint`. The installed frozen profile separately retains
   exact library/resource receipts and root inventories, so resource identities
   are content/version pins rather than mutable directory names. A DTO hash alone
   is not proof that its arguments passed the sanitizer.
7. Compute `compiler_input_digest(profile_digest, ordered_specs)` before allocating
   resolution or context IDs. `profile_digest` covers the frozen compiler policy,
   tokenizer, installed library/resources, target/driver allowlists and selection
   policy; it excludes context/result IDs, operational settings and temporary
   materialization paths. Feed the resulting input digest to
   `reference_profiles.profile_fingerprints` together with actual snapshot,
   parser-resource and resolver digests. Extraction identity uses only extraction
   inputs. The resolution fingerprint adds compiler inputs and resolution profile.
8. Derive the dataset IDs by storage.md. A context ID is UUIDv5 of the resolution
   dataset UUID and canonical JSON `['context', spec]`. Its work ID is UUIDv5 of
   the context UUID and `['work', {}]`. The spec already contains its input ordinal,
   so duplicate effective commands still have different context/work IDs. The
   input digest excludes these generated IDs and all observation/reference census
   values: there is no extraction/resolution/context fingerprint cycle.

Persist plan, contexts and one PENDING work row per expected context idempotently
under the dataset lock. `input_state=UNFROZEN` permits interrupted insertion to
resume; the planned input digest/count are already immutable. Before FROZEN,
reconstruct every `ContextSpec`, its effective digest, context ID, and exact work
census and compare to the captured selection. Missing/extra rows cannot be hidden
by a count. Freeze even a zero-context plan. Attach/reuse only matching dataset
identities; never append newly discovered contexts to an already frozen plan.

The existing query-ready file-plan gate additionally requires the compiler input
census to be frozen. It does **not** wait for the compiler reference census, which
depends on extraction and can remain UNFROZEN during partial navigation.

## Reference inventory and W09 admission

After all required extraction and metadata work succeeds, freeze one
`compiler_reference_inventory` row per visible reference whose selected bundle
language is `c` or `cpp`, regardless of reference usage or whether any compiler
cursor will exist. `ReferenceAnchor` retains its actual reference UUID, active
extraction publication ID, usage, captured file ID, original byte extent and
SHA-256 of exactly those source bytes. No reference is manufactured from a cursor.

The owner compares the full inventory with the selected immutable extraction
publications, not a caller-supplied partial list. Sort by reference UUID, replace
only extraction-publication audit links when hashing as defined in
`ReferenceCensus`, and store reference_count/reference_digest atomically with
`reference_state=FROZEN`. UNFROZEN requires both fields null; FROZEN requires both
non-null, including count zero. Freeze only against the input extraction selected
by the resolution dataset. Input/reference census edits after freeze are forbidden.

Context work is claimable only with the usual RUN demand/launching-run intent,
non-SUCCEEDED parent, due PENDING work, available heavy slot, frozen input census,
successful complete extraction and frozen reference inventory. It uses the same
heavy-worker budget as file work. W09 can create and test these observations
without any W12 association or public navigation implementation.

For a rejected `ContextSpec`, a context worker publishes INVALID with the exact
stored rejection code and no compiler invocation. For an accepted spec, the owner
reconstructs/rechecks the strict effective input against its captured entry or
logical recipe and pinned resources, materializes only validated paths, and invokes
the installed isolated library. No context source selects a driver or library.

## Compiler result evidence

Each complete `ContextOutput` identifies snapshot, extraction, resolution, context
and input digest. There are only two successful *processing outputs*:

| Output | Required evidence and meaning |
|---|---|
| VALID | Successful parse without binding-invalidating errors, complete captured file-visit census, mapped entities/references where actually established, and retained warnings/limitations. |
| INVALID | Sanitizer rejection or a completed parse with compiler binding errors. At least one typed error diagnostic; no file census, entities or reference observations. This is a completed limitation, not a compiler crash. |

Library startup failure, unexpected adapter exception, timeout, signal/crash,
missing source object or unavailable required isolation produces FAILED/retryable
context **work**, with `CompilerAttemptDiagnostic`, never an INVALID publication.
No guessed empty parse is used to turn a failed process into successful processing.

A VALID result contains the main TU and the complete set of captured files actually
visited, with exact full-file digests and visit counts. Record no source-namespace
file for an installed external header. An incomplete/unavailable visitation report
is an adapter failure, not a complete empty set. The libclang inclusion callback
and physical-location APIs supply relevant inputs; W09 must test their behavior
with its installed library and the selected parse options. [CW1–CW2]

`CompilerFileVisit.inactive_ranges` contains positively established skipped-source
extents from complete preprocessing evidence, in original bytes with exact slice
digests. A reference is inactive only when its entire nonempty source interval is
contained in such a range. Absence of a cursor does not establish inactivity.
This edition permits inactive proofs only for files visited once; a header visited
multiple times under differing macros cannot claim universal inactivity from one
skipped visit. An observed reference cannot overlap an inactive proof.

`CompilerEntity` retains a nonempty USR, cursor kind, and an `OccurrenceAnchor` to
an actual captured declaration/definition: exact symbol/occurrence/file IDs,
selected active extraction publication, role, original extent and bytes digest.
Collect declaration and definition observations separately; a name or USR string
without the captured occurrence evidence cannot establish a readable target.

`CompilerObservation` retains the actual physical reference ID, original source,
spelling and expansion evidence, cursor kind, dispatch support, and exactly one
captured entity link or `ExternalEntity`. In this edition all three source extents
must be identical and uniquely match the structural occurrence's file/range/kind.
Multiple template/macro cursor mappings or differing extents produce
MULTIPLE_PHYSICAL_MAPPINGS/UNMAPPED_CURSOR diagnostics and no guessed observation.
Aggregate neither a nearest-line match nor an arbitrary last visitor into a target.

An external identity has its pinned resource digest, resource-relative path,
original range/slice digest, USR and name. It never has a captured symbol/file ID.
Direct compiler references support `dispatch=DIRECT`; virtual or otherwise
unsupported runtime dispatch retains `UNSUPPORTED`, never a proven runtime edge.
Compiler cursor/source semantics are independent from that conservative SSR
navigation policy. [CW2]

## Per-reference states and reconciliation

Compute the following state for each expected context/reference pair by joining
the frozen censuses to context work and **only its active committed publication**.
These are derived states, not synthetic rows in `compiler_observations`.

| State | Exact condition and effect |
|---|---|
| MISSING_WORK | An expected work row is absent after input freeze: integrity failure, no final binding. |
| PENDING | Expected work is PENDING/RUNNING; no final binding yet. |
| FAILED | Expected context work failed; blocks W12 success, never an unresolved output. |
| INVALID | SUCCEEDED context with diagnostic-only INVALID output. Binding limitation for every possibly affected reference; v1 conservatively includes all expected pairs. |
| NOT_IN_TU | VALID complete file census proves this reference's captured file was not visited. Not an agreement vote. |
| INACTIVE | VALID single-visit skipped-source evidence contains the entire reference. Not an agreement vote. |
| MISSING | VALID visited file but no unique mapped observation. UNMAPPED_CURSOR diagnostics may explain why; do not fabricate a reference/target. |
| MAPPED | Actual observation with supported dispatch and an exact captured entity anchor. |
| EXTERNAL | Actual supported observation of an exact external resource identity. |
| UNSUPPORTED | Mapped source/cursor evidence exists but dispatch cannot establish the required binding. |

W12 waits for complete successful extraction, both frozen censuses and **every
expected context work row SUCCEEDED with a valid active publication manifest**.
INVALID is a successful processing result for this barrier; a crash/timeout is not.
The barrier is global to the selected context census even when a particular file
has no compiler observations. This prevents publication order from deciding which
build contexts count. Missing expected context rows are an integrity error; an
unmapped reference after successful parsing is an ordinary limitation.

After that barrier, group VALID entity observations by exact USR under the same
frozen compiler profile and verified occurrence identities. Only these establish
SAME_ENTITY edges; names, signatures or arity do not. Use the existing stable
representative rule (smallest member UUID); retain every original symbol and
occurrence for navigation. W12 records the proving context/publication/entity IDs
in association provenance. `same_entity_representatives` is the pure grouping
reference over previously validated, active outputs.

Ignore INACTIVE/NOT_IN_TU for voting. One captured target with only agreeing MAPPED
active contexts yields RESOLVED/CLANG_REFERENCE. At least two distinct proven
captured targets yield AMBIGUOUS/CONTEXT_DISAGREEMENT, even with additional INVALID
or missing evidence. A single candidate plus INVALID/MISSING/UNSUPPORTED/external
conflict is UNRESOLVED with no public target IDs; its candidate remains in compiler
evidence. Agreement on one external resource/USR is
UNRESOLVED/EXTERNAL_SOURCE_NOT_CAPTURED. Conflicting external identities remain
unresolved. No active context, all-inactive contexts, or an explicit zero-context
census cannot manufacture a binding. `reconcile_reference` fixes these decisions.

An occurrence assigned different USRs across valid contexts cannot bridge two
otherwise distinct USR groups through its physical symbol ID. Suppress its
SAME_ENTITY association; one physical target with conflicting semantic identities
remains UNRESOLVED/CONTEXT_DISAGREEMENT, not one-target agreement. The pure grouping
and reconciliation tests include this context-dependent identity case.

W12 writes final per-file bindings and associations through ordinary resolution
publications. Their provenance includes the input/reference census digests and
the contributing active context publication digests; those are output audit links,
not new input fingerprints. The same member-call fixture must then support final
declaration/definition association and exact definition/declaration reads.

## SQL projection and manifest reconstruction

`ContextPublication` represents a sealed candidate or committed receipt with
complete count/digest/output. Raw staging rows can temporarily have null
count/digest while batches are incomplete; they are not instances of that model
and cannot appear in the active view. Validate the sealed receipt before activation.

| Typed value | Durable representation |
|---|---|
| ContextCensus / ContextDefinition | compiler_context_plans plus compiler_contexts. Store all spec scalars and the full EffectiveContext JSON; recompute its hash and IDs on reconstruction. |
| ReferenceCensus / ReferenceAnchor | compiler_reference_inventory plus plan reference state/count/digest. Its FK points to the exact extraction publication/reference/file. |
| ContextWork / ContextPublication | compiler_context_work and compiler_publications. One work row per context; at most one candidate publication per work/generation. |
| ContextOutput header | compiler_context_results.detail is the full typed header excluding files/entities/observations/diagnostics. Its status and file_census_complete columns must agree. |
| CompilerFileVisit | compiler_file_visits.detail is the exact model JSON, including ordered inactive evidence. |
| CompilerEntity | compiler_entities.detail is the exact model JSON. Scalar identity, source, occurrence, USR columns must agree with it. |
| CompilerObservation | compiler_observations.detail is the exact model JSON. Physical-reference/file/target scalar columns must agree with it. |
| CompilerDiagnostic | compiler_output_diagnostics.detail is exact typed JSON, diagnostic_key is its canonical value digest, code equals detail.code. It is always scoped to a compiler publication. |
| CompilerAttemptDiagnostic | compiler_attempt_diagnostics.detail is exact typed JSON, with work/generation/id/code columns matching it. It has no successful-output publication association. |

SQL enforces keys, selected input-extraction linkage, same-publication captured
target references, context/work ownership, lease nullability and the active
publication's owning work. SQL checks deliberately do not pretend to validate
JSON model semantics or a compiler's evidence. PostgreSQL CHECK/FK semantics and
their null behavior require explicit complementary owner guards. [CW3]

Before activation the owner validates exact selected dataset kinds, frozen census
membership, active extraction provenance, scalar/detail equality, source encoding
boundaries and bytes, all entity/reference mappings, trusted resource membership,
diagnostic codes, result shape, and deterministic IDs. Byte buffers/digests are
prepared before taking mutation locks; do not do Git/compiler work under locks.
The reference accepts explicit catalogs in place of those database/source owners;
it cannot prove that a caller really supplied a complete selected inventory.

The exact manifest is `{schema_version:1, records:[{collection, record_id, value}]}`.
There is one `summary` record keyed by context ID, plus `files`, `entities`,
`observations` and `diagnostics`. Keys are respectively file ID, entity ID,
observation ID, and canonical diagnostic digest. Sort by collection ASCII bytes
then record_id. `result_count` includes the summary and every diagnostic. Hash
the entire typed values after removing only extraction_publication_id audit links;
never remove source ranges/digests, target identity, dispatch or limitations.
Entity/observation UUIDv5 names use that same audit-free typed projection. No lease,
generation, publication UUID, timestamp or native path enters result identity.

`output_rows`, `reconstruct_output`, `output_manifest` and `output_signature` are
runnable definitions. Reconstruction selects one active publication ID, rejects
unknown/duplicate collections and scalar key mismatches, and reconstructs the full
typed result before comparing count/digest. Joining diagnostics by work alone is
forbidden: old attempts and abandoned publications can have different diagnostics.
Attempt errors never enter a successful manifest. INVALID's diagnostic-only
manifest still includes its summary and error records.

## Locks, retries, visibility and completion

Use the existing order: datasets by UUID, index_runs by UUID, work, publications.
At the work level sort mixed rows by `(family, work_id)` with file work first and
compiler work second. At the publication level use the corresponding family then
publication UUID. One-row claims lock one dataset first and select eligible context
work by input ordinal/work_id with SKIP LOCKED. Multirow retry/recovery/control
never locks a context row and then an earlier file-work/dataset/run row.

Bounded staging transactions may write only their context publication's rows and
do not later acquire dataset locks. The staging owner locks that publication,
checks it is uncommitted and owned by the current attempt, and forbids append/edit
after activation. Final publication follows dataset -> work -> publication order,
rechecks the unexpired database-clock token/generation, verifies the sealed output
manifest and activates it atomically. An acknowledgment loss replays only the exact
committed generation/publication/digest; changed output is NONDETERMINISTIC_OUTPUT.

`visible_compiler_publications` requires committed publication, SUCCEEDED work,
its active publication ID, and equal work/generation/context/resolution identities.
W09 evidence queries and W12 consumers always join that view. A raw staging row is
not successful evidence. Published context results are immutable even if a
different consumer pauses, another context fails, or a worker restarts.

Context claims, heartbeats, failure reports, expiry and explicit retry retain the
same lifecycle rules: RUN demand, launch-run intent, no reset on resume, drain on
pause, expiry fenced before reclaim, bounded automatic transient retries, retained
lifetime attempts/generation, and explicit retry of FAILED resetting only the
retry-cycle count/error pointer/due time. Record typed attempt diagnostics in the
same owner transaction; retain earlier history. Retry on PAUSE does not set RUN.
An INVALID successful context is terminal for its inputs; changing compiler
semantics/captured source requires another dataset rather than retrying it in place.

Resolution dataset state is computed over both work families using the existing
precedence. A failed context does not cancel independent pending context work.
Completion additionally audits both censuses, their exact work/active publication
sets, no current-generation unfinished staging, and all ordinary required file
work. `resolution_can_complete` is the pure decision guard over owner-audited
inputs. W12 file resolution cannot succeed before its context barrier.

Keep compact coverage unchanged: totals/completed/failed counts refer to distinct
applicable physical file jobs. Context attempts do not add files or increment
those counters. Files waiting for compiler context work remain PENDING; a context
failure can therefore make resolution/run FAILED while resolution.failed_files is
zero. Paged status names the failed context/TU and blocked files. index_complete
remains false until both work families and every existing metadata obligation pass.

## Verification boundary

Run from the repository root:

```sh
uv run --no-project --python 3.12 --with-requirements stage-1-indexing/validation/requirements.txt python -B -m unittest discover -s stage-1-indexing/validation/regressions -p test_compiler_contexts.py -v
```

On this development Mac `/opt/homebrew/bin/uv` is the equivalent absolute entry
point when uv is absent from PATH. The tests exercise the actual pure path from
sanitization/CompilerOptions through census, source checks, lease transitions,
publication projection/reconstruction and reconciliation. They cover invalid
contexts, missing expected work/cursors, inactive/not-visited proof distinctions,
external/dynamic/conflicting targets, retries, stale attempts, and manifest history.

W02/W09 must separately apply the schema to disposable PostgreSQL 17 and test wrong
dataset kinds, cross-snapshot/active-extraction membership, keys, invalid context
null combinations, lossless row reconstruction, interrupted census freeze, restart
with staged/historical results, and refusal to mutate committed outputs. Repeat the
common A/B pause/retry/expiry/publication/completion race schedules across both work
families, including reversed input orders with bounded timeouts. SQL syntax parsing
or pure truth tables are not transaction, lock-order or crash-recovery evidence.

W09 additionally uses the installed libclang to prove actual file/skip/cursor/USR
evidence and isolated access for the captured Test header/member fixture, rejected
commands, missing headers, repeated includes, macro/template mapping, external
resources and worker crashes. W12 proves final associations and public source
reads. None of those runtime gates is marked complete by these reference tests.

## Primary references

- CW1: [libclang inclusion visitors](https://clang.llvm.org/doxygen/group__CINDEX__MISC.html).
- CW2: [libclang physical source locations](https://clang.llvm.org/doxygen/group__CINDEX__LOCATIONS.html) and [cursor/USR API](https://clang.llvm.org/docs/LibClang.html).
- CW3: [PostgreSQL 17 constraints](https://www.postgresql.org/docs/17/ddl-constraints.html).
