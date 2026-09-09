# P1-F02 — Indexed navigation and information retrieval

Version: 0.16  
Updated: 2026-09-09  
Feature status: IN DISCUSSION  
Approved detail saved: source selection, authenticated cursors, indexed lookup, exact analysis retrieval, durable freshness interests, availability sequencing, notice acknowledgment, H-bounded analysis-list continuation, direct-relationship navigation, manifest-backed file discovery, bounded source-text search, per-file cross-line matching, and ordered non-overlapping occurrence retrieval  
Detailed specification: PARTIAL — further interfaces and navigation choices remain open  
Implementation readiness: NOT READY  
Implementation and application tests: NOT PERFORMED

This feature file records explicit approvals from the design conversation. The
source-reading, pagination, cursor-design, authentication and indexed-lookup
requirements below record approved choices; their written formulation is available for review.
The user has approved HMAC-SHA-256 and a persistent project-local host secret.
Earlier approvals add automatic interest tracking when an agent queries a
subject's analysis, followed by lightweight notices at the ongoing work's next
ordinary interaction when relevant new analysis is available. Retrieval and refresh
remain the agent's choice. This amends R35's previous blanket prohibition on
subscriptions; it does not add contextual dependencies, task creation or waiting.
The durable-interest approval requires source-free interests registered with
successful lookups, independently of worker memory or model checkpoints. Restore
interests for the same ongoing work; do not transfer them to unrelated work.
R49-R55 select a committed availability sequence within each review and the original
lookup position H across separate short read/registration transactions. R56-R61
require acknowledgment of exactly the notices included in an ordinary model request
after its valid response is durably recorded, with recovery or safe uncertain
repeat at a normal interaction. No model acknowledgment call is required.
The preceding approval adds R62-R67: continue each analysis listing within its original
availability boundary H using a stable availability-based position, while newer
results remain available through notices, exact retrieval, or an explicit refresh.
The preceding relationship approval adds R68-R75: extend direct-relationship retrieval while
preserving actual direction, callsites, recorded resolution and provenance. Do not
guess incoming bindings, expose protected targets or mutate the graph through reads.
Every page still applies current visibility and result-status rules.
The preceding approval adds R76-R83: one manifest-backed catalogue for immediate-child
directory browsing and filtered exact file discovery. Preserve existing file
references, metadata visibility and recorded inventory limitations; discovery does
not implicitly read source, create work, or register analysis-update interests.
R84-R90 record explicit literal/regex search, bounded non-backtracking matching,
manifest-backed selection, match-centered previews and honest scan/output limitations.
R91-R95 make each file the matching input; explicitly requested cross-line matches
must survive preview/output boundaries. Process one verified file at a time and
report unsupported resource cases without silently changing matching semantics.
The latest approval adds R96-R101: one result per non-overlapping occurrence,
ordered by canonical relative file path and original match byte positions. Resume
from matching progress, not preview length, preserve original-file context, and
report a produced zero-length match as an explicit unsupported-occurrence outcome.
Exact matcher dialect/flags, selection among competing regex alternatives,
case-to-byte mapping, search cursor encoding and interrupted-scan continuation
remain open; this approval does not select those implementations.
The feature remains partial. Final wire/key-file formats, rotation/expiry, other
matching modes, exact listing keys/filter semantics, interest/availability schema,
concrete delivery-record/outcome mapping, new publication rules, and rollout remain open.
Do not fill open choices with defaults without discussion.

## 1. Purpose and earlier agreements

Use the existing index as the navigation foundation while making source inspection
convenient. An analyst who already has a symbol ID should not need to retrieve its
metadata solely to copy source coordinates into a second tool call.

**P1-F02-B1.** Use existing symbol, relationship and file identities directly when
known. Do not ask the model to rediscover indexed subjects.

**P1-F02-B2.** Names and paths provide another route into that same inventory.
Ambiguous lookups return alternatives rather than invent a unique binding.

**P1-F02-B3.** Source search complements structural gaps and challenges to indexed
interpretations. Index-first is guidance, not a compulsory sequence of calls.

**P1-F02-B4.** Retrieval is bounded and makes unresolved bindings, partial results
and limitations explicit. Do not load the entire graph into every prompt.

## 2. Baseline and reuse

These are historical observations at the inspected harness commit
`8b7ed0e335d4f4fb5ae53ef6e059334661279f20`, not a fresh audit of the refactored
branch or installed runtime. See [SOURCES.md](../../SOURCES.md).

| Existing capability | Reuse and intended extension |
|---|---|
| `indexing.py` persists snapshot-bound symbol IDs, names, full/declaration/body ranges and hashes. | Resolve known symbols through that inventory; do not add a second parser or symbol identity system. |
| `ToolBroker` provides `symbol_get`, `source_read` and other lookup tools in `tools.py`. | Keep metadata retrieval separate; extend the source-read selection path rather than implement another source reader. |
| `SourceResolver.resolve()` and `read_verified_file()` in `source.py` verify snapshot bytes, bounds and hashes. | Converge both selection modes and continuations on this verified source-reading authority or its refactored equivalent. |
| The broker tracks source ranges for the executing attempt. | Record actual source delivered, not the size of the requested symbol; do not inherit another attempt's read credit. |
| The inspected `source.py` lookup reads `snapshot_files` and available `file_inventories` metadata by snapshot/path. | Reuse the manifest/inventory catalogue and existing file references for discovery; do not call the byte reader merely to enumerate file metadata. |

Before implementation, map these responsibilities to the actual accepted modular
refactor. Historical names locate responsibilities, not mandatory destination
files. The new functional behavior must not be folded into a behavior-preserving
refactor without being identified as feature work.

## 3. Approved source-selection requirements

### P1-F02-R01 — Metadata-only symbol retrieval

Keep `symbol_get` metadata-only. Looking up a symbol must not implicitly return
its source body, callers' bodies or related analysis in an unbounded package.

### P1-F02-R02 — One source reader, two initial selections

Extend `source_read` to support either:

- An existing symbol ID resolved in the attempt's bound snapshot.
- The existing explicit file-ID and line-range selection.

The agent need not call `symbol_get` before reading a known symbol. Both selection
modes use one authorization, verified-reading and result-accounting path.
Mutually conflicting selectors are invalid; do not silently choose one or fall
back to a different file. Exact JSON fields and schema representation remain open.

### P1-F02-R03 — Full indexed symbol range by default

For an initial symbol selection, use the indexed full-symbol range by default,
not merely its body. Include the signature and declaration material contained in
that indexed range. Include decorators or annotations only where the inventory
actually places them in that range; do not promise parser coverage not established
by the index.

Do not automatically expand the selection to its containing class, whole file,
callers or helpers. They remain independently selectable source subjects.
Alternative body-only/declaration-only options have not been agreed.

### P1-F02-R04 — Bound identity and precise returned source

Resolve the selector in the actual attempt's snapshot and apply P1-F01 research
policy independently of assignment ownership. Return the selected subject/file
identity, the original selected range, the actual range returned, and the relevant
file and returned-span hashes. Use the existing coordinate convention.

An unknown symbol, wrong snapshot, invalid source selection or integrity failure
must not cause a name-based fallback or a read of the latest/live source.
The future P1-F03 convenience references must not replace this exact identity.

## 4. Approved pagination requirements

### P1-F02-R05 — Page a valid oversized selection

A valid symbol or explicit file-range request that exceeds one response allowance
returns a bounded first page with an explicit continuation. Size alone must not
turn a valid selection into an unexplained access error or a silently truncated
complete read. Genuine resource exhaustion and unavailable/unsupported content
still need honest outcomes; pagination does not bypass those conditions.

### P1-F02-R06 — Preserve the selection across continuation

The host-generated continuation identifies the same snapshot, file, original
selected range, next unread position and necessary selector/contract version.
Continuing must not drift past the selected symbol or range, skip source through
guessed offset arithmetic, or reinterpret the request against a different revision.

The agent follows a returned continuation rather than calculating the next offset.
The self-contained representation, integrity-protection requirement, same-review
cross-attempt use and replay behavior are agreed in R13-R16 below. Exact field
names, encoding, key-file format and exact provisioning protocol, size bounds and
explicit expiry/rotation behavior remain open. HMAC-SHA-256, project-local secret
ownership/storage, and the basic creation/restart/failure rules are agreed in
R18-R21 below.

### P1-F02-R07 — A cursor is not authorization

Recheck the current execution attempt, research permission, source integrity and
applicable limits on every page request. A previously valid cursor does not permit
an expired or superseded attempt to read. Neither guessed IDs nor cursor contents
can grant access to another project or source outside the permitted snapshot.

### P1-F02-R08 — Explicit partial and terminal pages

Each response identifies whether more of the selected range remains and supplies
a continuation when applicable. Exhausting the selected range on this response
is not proof that the current attempt read all earlier pages. Keep selection/page
completion separate from attempt-level read coverage.

### P1-F02-R09 — Prefer line boundaries; support long lines explicitly

Prefer pages containing complete lines where limits allow. For an exceptionally
long line, allow an explicitly marked partial-line page at a valid character
boundary for a supported encoding. Exact byte positions and hashes refer to the
original snapshot bytes. Line labels and continuation markers are metadata, not
source and not material that may be used to construct evidence hashes.

Do not normalize newlines, insert omission markers into evidence bytes or silently
replace undecodable characters to force success. The exact handling of encoding
edge cases needs verification and discussion before declaring the page algorithm
complete.

### P1-F02-R10 — Account only for source actually delivered

A request for a four-page function does not record a complete function read when
only one page was delivered. Associate actual returned source intervals with the
current attempt and preserve the existing actual-delivery accounting boundary.

Reaching the last page, possessing a cursor, or consuming a prior agent's summary
must not substitute for checking the current attempt's delivered interval union
when its result contract requires a complete/material source read. Interrupted
response-delivery and replay details must be reconciled with P1-F08/P1-F09 and the
runner's real delivery hooks rather than invented here.

### P1-F02-R11 — Agent-controlled continuation within limits

Return one bounded page; do not automatically fetch all remaining pages. The
analyst chooses whether to continue or inspect something else. A full-symbol
selection and repeated continuation requests do not reset cumulative limits,
increase a context window or multiply P1-F09's combined response allowance.

### P1-F02-R12 — Keep the mechanism within source retrieval

Use the existing source-reading infrastructure and suitable existing pagination
utilities where available. This capability does not need another worker, source
store, evidence system or mandatory per-page database record. The selected
mechanism is a self-contained, integrity-protected continuation. Resolve its
remaining encoding, key and lifecycle choices before coding; do not introduce a
cursor database or a process-local position registry as its backing mechanism.

### P1-F02-R13 — Self-contained, integrity-protected continuation

Use a host-generated opaque cursor containing sufficient metadata to resume the
selection without a separate database row per page or dependence on the original
worker's in-memory pagination state. The agent returns the cursor unchanged; it
does not construct its fields or calculate the next position.

The following are required meanings, not final serialized field names:

| Information | Required binding |
|---|---|
| Cursor contract/version | Identifies how the continuation is decoded and validated. |
| Review and snapshot identity | Binds the continuation to the originating review and immutable source state. |
| File identity and expected file hash | Identifies and verifies the same captured file. |
| Original selected source interval | Retains the original symbol or explicit file-range selection; paging cannot expand it. |
| Next unread byte position | Starts the next page at the recorded position within that selection. |
| Original symbol identity, when applicable | Retains which indexed symbol supplied the original selection. |
| Host-provided integrity protection | Detects modification of the selection, position and other bound metadata. |

The cursor contains navigation metadata, not source code, credentials or model
analysis. Integrity protection does not replace source-hash checks or current
execution authorization. R18-R21 record the subsequently approved authentication
algorithm and project-local storage boundary. The final wire encoding, exact file
location/format, token-size ceiling and any expiry/rotation policy remain open.
Authentication must not be described as encryption; this decision does not add an
encryption mechanism.

### P1-F02-R14 — Reusable within the same review across attempts

Bind cursor usability to the review, snapshot and selected source, not to the
original worker or agent attempt. A replacement or other independently authorized
attempt in that same review may continue from the cursor while it remains valid
under the eventual key/lifecycle contract. Recheck the new attempt's research
permissions and applicable limits. A cursor from another review must not be
silently rebound, even when that review uses identical source bytes.

Changing workers or ending the original attempt must not itself invalidate the
navigation reference. An expired original attempt is still denied under R07.
The new attempt receives read credit only for source actually delivered to it;
a cursor carries neither the original attempt's authorization nor its read history.
Checkpoint inclusion/transport is an integration requirement for P1-F04, not a
claim that the existing checkpoint schema already accepts cursors.

### P1-F02-R15 — Explicit continuation validation path

On a continuation request, validate the cursor's format, supported version and
integrity; bind it to the current execution's review/snapshot; resolve its file,
original selection and any symbol identity through the existing source/index
infrastructure; recheck the current attempt, source authorization and limits;
then verify and return the next bounded page through the same source reader.

Do not trust a decoded position merely because it looks like an integer. Validate
it against the original selected interval and exact source identity before use.
The details of the decoder and fail-fast error ordering must be agreed with the
final wire contract and P1-F07. An invalid or unverifiable cursor cannot trigger a
fallback to another symbol, current snapshot, or unprotected position. Unauthorized
requests must not disclose source or foreign-review metadata.

### P1-F02-R16 — Replay has no shared advancing position

Reusing a valid cursor starts from the same position in the same source selection.
It does not consume the cursor, advance a hidden shared pointer or modify another
reader's position. Concurrent reads of the same cursor must not cause either
reader to skip source.

Under unchanged relevant allowances, the source range and bytes should be
repeatable. A tighter current allowance may produce a smaller page, but its
starting position remains the one encoded in the cursor. Derive the next cursor
from the actual returned interval, not the originally intended page size.
This is a source-selection guarantee, not a requirement that all audit IDs or
other response metadata be byte-identical on replay. Usage/delivery accounting
continues through P1-F08/P1-F09; replay never grants free budget or inherited read
credit.

### P1-F02-R17 — Small codec with explicit restart support

Reuse a suitable host-owned cursor utility from the refactored code after checking
its contracts; otherwise use a narrow codec and validator within source retrieval.
Do not create another worker type, general pagination service, permission framework
or cursor-position store. Existing per-attempt audit and actual-read records remain
necessary; avoiding cursor rows does not remove those records.

The mechanism must not rely on an authentication secret that exists only in the
producing worker's memory. R18-R21 now establish persistent project-local secret
ownership, serialized initial creation, restart loading and failure behavior.
The precise key-file format/location and creation protocol still need to be mapped
to the refactored host. Rotation, explicit loss-repair procedure and expiry remain
open; do not infer indefinite validity, export host secrets or silently replace a
missing secret.

### P1-F02-R18 — Host-owned cursor-authentication secret

Use HMAC-SHA-256 to authenticate the complete cursor metadata, implemented through
Python's standard-library `hmac`/`hashlib` support. Verify the authentication tag
with `hmac.compare_digest()`. Reuse a compatible existing host utility where
available; do not introduce an external cryptography framework merely for this
capability.

"Host-owned" means SSR's host code manages and uses a secret that is not available
to the model. It does not mean a cursor ID, a worker ID or a mutable reading
position. The returned cursor contains the encoded selection metadata and its
authentication tag, never the secret. Authenticate all the selection and position
bindings in R13, not just an offset or file ID. The final canonical encoding and
wire fields remain to be agreed before implementation.

Illustrative mechanism, not a finalized wire representation:

```text
authentication_tag = HMAC-SHA-256(project_secret, encoded_cursor_metadata)
returned_cursor = encoded_cursor_metadata + authentication_tag
```

When a continuation returns, the host validates its bounded representation and
authentication before using its fields to serve source. A valid tag only establishes
integrity under this host secret; it does not authorize an attempt, prove source
integrity, or prove that any agent inspected the source. Preserve R07 and R15.

### P1-F02-R19 — Persistent project-local ownership and storage

Use one persistent host-owned cursor-authentication secret per SSR-managed
project, usable by that project's authorized workers. Store it in a dedicated,
owner-protected file in the project's SSR-managed private data area, outside both
the reviewed target and its immutable source snapshot.

Do not place the secret in `ssr.db`, model-visible configuration, source-read
results, cursors, transcripts, ordinary logs/errors, or analysis exports. This is
host infrastructure, not source evidence or an analytical record. Reuse the host's
existing private-file safety utilities where compatible. The exact filename,
file format, generation parameters, provisioning and recovery interfaces are not
fixed by this approval.

The shared secret authenticates many distinct cursors. It stores no current file,
current offset, active reader or cursor-consumption state.

### P1-F02-R20 — Create once through host initialization; load on restart

Initial provisioning must use a serialized host initialization path. Concurrent
workers must not independently generate different secrets or overwrite the same
project's established secret. Ordinary reads load the established secret through
a small host cursor component; individual workers do not manage its replacement.

A legitimate worker/controller restart loads the same stored secret. Restarting
or moving to another authorized attempt must not itself create a new secret or
invalidate an otherwise valid same-review cursor.

Before coding, identify the existing serialization and private-file utilities and
specify how genuine first initialization is distinguished from loss of a previously
provisioned secret. The agreed behavior requires that distinction; it does not
approve a new provisioning service or an arbitrary new database schema.

### P1-F02-R21 — Missing or unverifiable authentication fails explicitly

If the expected secret is unavailable, or a returned cursor cannot be authenticated,
return an explicit, safe continuation failure. Exact status names and model-facing
repair information must be reconciled with P1-F07. Never use unverified decoded
fields to serve source, silently generate a replacement secret, or pretend that a
cursor authenticated under a replaced secret still verifies.

After an explicitly handled host key repair, the analyst can start a fresh read
using its existing symbol/file reference under ordinary authorization. A fresh read
is not recovery of the old cursor. Do not invent an automatic old-key fallback,
rotation service, key history or expiry policy. Those lifecycle choices remain open.

### P1-F02-R22 — Independent readers share authentication, not positions

Each cursor contains its own source selection and continuation position. Two
workers reading different files can hold and use different cursors concurrently.
One worker can also hold multiple cursors, and two workers can independently read
the same function. Neither call advances or overwrites another cursor.

For example, A's cursor can select file X at byte 7,000 while B's selects file Y at
byte 4,500. Each request is authenticated and authorized independently, returns its
own bounded page, and produces a new immutable continuation for its actual end.
The numbers and file names in this example are illustrative, not contract limits.

The codec and project secret may be shared. Mutable authorization scopes, budgets
and delivered-source intervals must retain their correct attempt ownership. Do not
add a global reading position or a pool-wide pagination lock. Serialization of
initial secret creation is distinct from serializing source-page retrieval.

## 4A. Approved indexed symbol-lookup requirements

### P1-F02-R23 — Extend the existing listing and exact-get capabilities

Extend `symbol_list` to support indexed name lookup as well as listing the symbols
in a selected file. Keep `symbol_get(symbol_id)` for exact metadata retrieval and
`source_read` for explicitly requested source. An agent holding an existing symbol
ID does not have to perform a name search first.

Use the existing snapshot-bound symbol IDs in every result. A lookup returns
identifying metadata; it does not automatically read source into the model's
context, launch analysis, register a lead, or create another symbol identity.

### P1-F02-R24 — Exact name matching with optional narrowing filters

Support exact local-name and exact qualified-name lookup. Optionally narrow the
lookup by file ID, normalized relative file path, containing symbol, or symbol
kind. Supplied filters narrow the query; do not silently drop a restriction to
produce a result. Preserve file-scoped listing without a name predicate.

An unsuccessful exact lookup must not fall back to fuzzy/prefix/substring matching,
a similarly named file, a different snapshot, or a guessed declaration. A name
lookup remains a query over the inventory, not a model-based resolution step.
Other matching modes have not been agreed.

The final selector fields, permitted combinations, language-aware case and name
normalization, containing-symbol traversal semantics, and conflict errors still
need discussion. Qualified-name syntax must correspond to the actual index rather
than a newly invented cross-language naming convention.

### P1-F02-R25 — Return distinguishable declaration matches

Return enough indexed metadata for an analyst to distinguish matches: existing
symbol ID, local and qualified name, symbol kind, file identity/path, source
location, and containing-symbol identity where available. Preserve unavailable
metadata honestly; do not invent a containing type or a parser-derived signature.

A name shared by declarations in different files or classes returns alternatives.
The analyst may narrow its filters or inspect a selected ID. Do not choose a
preferred declaration and present it as the only match merely to simplify the
response. Exact response field names remain open.

### P1-F02-R26 — Declaration lookup does not resolve a callsite

A declaration matching a name is not proof that a call with that spelling reaches
it. Even one complete indexed match does not establish dynamic dispatch, alias
binding, a call edge, attacker influence, or a security path.

Do not create, modify, or upgrade a relationship from name-match uniqueness.
Existing relationship resolution information and further source analysis remain
the appropriate means of investigating a callsite. This lookup has no domain
publication side effects.

### P1-F02-R27 — Explicit query scope, completeness, and bounded pages

Bind the query to the current execution's snapshot. Apply P1-F01 research
permissions before pagination, not by removing unauthorized rows from a previously
limited page. Results must not reveal inaccessible subjects or return misleading
pages caused by post-pagination access filtering.

Use bounded, deterministic result ordering and make further results explicit.
A page with one item is not a unique match when other matches remain. Distinguish
no indexed matches, one complete match, multiple matches, and a partial result
whose complete match set has not been returned. Do not imply an exhaustive query
when it stopped because of a limit or unavailable inventory.

Expose relevant inventory limitations without turning them into fictional symbols.
No matches means no matches in the queried authorized inventory, not proof that
no corresponding behavior exists in all project source. Final status fields,
ordering keys, query-pagination representation, and bounds remain open; source-read
cursor approval does not automatically choose the symbol-list paging contract.

### P1-F02-R28 — Query the existing inventory through its owning component

Extend the existing/refactored inventory-query owner and tool adapter. Resolve
filters and query the existing symbol inventory with bounded selection; do not
load the entire project's symbol set into each worker to filter it in Python.
Reuse the existing research-policy authority and safe query construction.

Do not build a second symbol database, embeddings index, model-based resolver,
new worker type, or speculative navigation framework for exact lookup. This is a
read capability, not permission to change indexing semantics, fabricate bindings,
or publish analysis. Any genuinely necessary query index or schema change must
be justified separately; a new feature document alone does not require one.

## 4B. Approved analysis discovery and exact-result retrieval

The user approved this capability after its discussion. R29–R36 record that
agreement. R62-R67 now select H-bounded, position-based analysis-list continuation;
exact wire fields, status enums, and storage/query mapping remain open. This section
defines consumption of available results, not a new publication or knowledge-
acceptance authority.

### P1-F02-R29 — Discover analysis using existing indexed subjects

Allow an analytical agent to discover relevant analysis using an existing symbol
or file ID. Resolve the subject in the execution's bound snapshot and apply the
applicable review/context and research-access checks. Use existing subject/result
associations; do not ask another model to rediscover them or create a second
subject-identity system.

Return associated results only where their owning acceptance and visibility rules
permit. An association identifies what a result covers; it does not prove that the
result answers a new contextual question or applies under the same assumptions.

### P1-F02-R30 — Return a compact index of attributable results

The initial response identifies each existing document/result ID, covered
symbol/file IDs, analysis type, producer and source identity, recorded summary,
and applicable availability/limitations. Use summaries already recorded in the
result. Do not make a model call to summarize lookup results, invent a missing
summary, or load every complete document and source body automatically.

Keep list results bounded and pageable. Distinguish an unavailable summary from a
negative analytical conclusion. The precise supported artifact variants and
field names must be resolved against the owning result contracts before coding.

### P1-F02-R31 — Fetch the selected result by exact identity

After discovery returns result D18, a detail request for D18 selects D18, not a
moving "latest" alias. Where current permissions and visibility allow it, return
that result's documentation, controls, assumptions, unknowns, and evidence
references through its existing reader. Preserve its recorded identity and
provenance. Large results must be retrievable within bounded response limits.

If D19 becomes available after discovery, do not substitute it for D18. A new
lookup may expose D19 and its recorded relationship to D18. If D18 is no longer
accessible under the owning policy, explain the applicable unavailability rather
than return a different result. This does not grant historical-result access that
Phase 4 has not authorized or imply that D18 remains a current accepted conclusion.

### P1-F02-R32 — Preserve distinct analyses and assumptions

When several analyses concern the same subject, return their distinct IDs and
recorded relationships rather than merge them silently into an authoritative
answer. Different callers, questions, or assumptions may lead to different
conclusions. Reconciliation and applicability judgments remain with the owning
workflow; retrieval must not invent supersession, agreement, or semantic dedup.

### P1-F02-R33 — Report analysis availability separately from work status

A result's consumability and a review task's execution status are separate facts.
Where authorized and applicable, expose both using existing result and task
projections. Required scenarios are:

| Observed situation | Required meaning of response |
|---|---|
| No usable analysis and no matching scheduled review | Report both absences without claiming the subject is safe or needs no review. |
| Review queued or running with no usable result | Report that analysis is not yet available and identify permitted work references/status. Do not expose unfinished private content. |
| A task finished but required acceptance is pending | Report pending availability rather than treating `COMPLETED` as acceptance. Identify the permitted blocker information. |
| Usable prior analysis and supplementary work in progress | Return the available analysis and separately report outstanding work; neither fact erases the other. |
| Review failed | Report the recorded failure/unavailable outcome, not an empty successful analysis or "no issue found." |

These are behavioral meanings, not new status enums or lifecycle transitions.
When several matching tasks exist, preserve their distinct scopes and use bounded
work information rather than invent a single task that represents all analysis.
The exact work-summary schema and paging mechanism remain to be agreed.

### P1-F02-R34 — Delegate acceptance and visibility to their real owners

A completed task alone does not authorize returning its result. Consult the
result's existing acceptance/provenance authority and applicable visibility rules.
Conversely, unrelated unfinished work must not hide an otherwise usable result.
Broader source research under P1-F01 does not expose private child submissions,
unfinished conversations, sensitive transcripts, or other restricted artifacts.

Phase 4 decides which artifacts become shareable and at which boundary. P1-F02
consumes that decision; it does not choose a sealed-unit-only or general mid-review
publication policy. Reading another analyst's summary does not grant the current
attempt source-read credit or prove its own claim.

### P1-F02-R35 — Retrieval is not scheduling or a new knowledge system

Analysis lookup and detail retrieval must not wait for a reviewer, create a new
review task, register a lead, or create a blocking contextual-answer dependency.
The new approval in R37–R43 permits automatic subject-interest tracking and
lightweight freshness notices; this explicitly replaces the earlier blanket
prohibition on subscriptions. Do not make model calls to poll for updates.
The agent can choose source inspection, contextual review, or other work through
the corresponding capabilities. Preserve read audits and usage accounting; interest
tracking is not analysis publication, coverage acceptance, or a scheduling grant.

Extend `document_query` or its refactored equivalent for discovery and delegate
detail retrieval to suitable existing accepted-result readers. Do not copy their
validation logic, invent a parallel knowledge store, or replace all readers with
a speculative generic framework. Capability names are integration guidance; the
final provider-visible schema remains subject to review.

### P1-F02-R36 — Analysis-list consistency has its own contract

The source snapshot is immutable, but analysis availability can change while an
agent pages its result index. R62-R67 now define the separately approved contract:
retain the initial committed availability boundary H and continue by a stable
availability-based position, with current visibility/status checks on every page.
Newer publications require a fresh listing or exact-result retrieval; the agreed
notices advertise their availability without resetting the existing traversal.

This is not a frozen historical database view or permission snapshot. Do not reuse
a source-read cursor as an analysis-list cursor. Exact wire fields, ordering direction,
query mapping, expiry, and re-availability edge cases still require resolution.
Exact-result identity in R31 applies independently of list pagination.

## 4C. Approved automatic subject-specific freshness notices

This section records the user's proposal to advertise new records and the explicit
approval, after clarification, of automatic interest registration and next-normal-
interaction delivery. R44-R48 add durable work-scoped interests; R49-R55 now select
the committed availability marker and initial lookup/registration protocol.
R56-R61 select delivery acknowledgment; R62-R67 select H-bounded list continuation.
Exact storage schema and concrete query/request/response integration remain open.

### P1-F02-R37 — An analysis lookup registers interest automatically

When an authorized agent queries analysis for an indexed symbol or file, remember
that subject and the applicable lookup filters for its ongoing task or inquiry.
Do not require an additional subscribe tool call. Use existing subject identities;
do not infer interest through semantic similarity or subscribe to every project row.
Invalid or unauthorized lookups must not establish access to restricted subjects.

The interest belongs to the logical work, not a reusable worker slot. A slot that
later executes unrelated work must not inherit it. The behavior is intended to
support the ongoing analysis. Durable registration, same-work restoration and
logical-work lifecycle behavior are specified in R44-R46. R49-R55 select the
notification marker and initial registration sequence; exact owner/storage mapping
still requires implementation mapping; R56-R61 govern delivery acknowledgment.

### P1-F02-R38 — Announce only relevant, discoverable analysis

Advertise newly available results associated with the tracked subject/query only
when the current recipient is permitted to discover them. Consult the owning
acceptance and visibility rules. Creation of a private/provisional row or task
completion alone is insufficient. Check access again when a notice is delivered
and when its result is fetched; do not disclose restricted IDs or metadata.

A notice carries a compact subject identification and permitted result references
and types where available. Do not load full analysis or source merely to announce
availability, invent summaries, or use another model to assess notice relevance.
Exact notice fields, bounds and unavailable-detail behavior remain open.

### P1-F02-R39 — Deliver at the next ordinary interaction

Deliver pending relevant notices at the next ordinary tool-response or model-turn
boundary for the ongoing analysis. The next tool need not be another analysis
lookup. Do not interrupt an in-flight provider response, start another worker, or
make an extra provider call merely to advertise a publication.

When work is inactive, present applicable notices when it normally resumes; an
optional freshness notice does not itself schedule or reopen work. Waking an
analysis that is explicitly waiting for a contextual dependency remains Phase 3
behavior, not an implicit effect of this lookup capability. R56-R61 specify when
advertisement may be acknowledged. Exact attachment, ordering, response mapping and
budget composition still need implementation-level agreement.

### P1-F02-R40 — Retrieval and refresh remain optional

The agent may fetch an advertised result by exact ID, refresh its result listing,
read it later, or continue without fetching it. Advertising D20 must not replace
an explicitly selected D18, inject D20's body, reset the current listing cursor,
or automatically restart pagination. A request for D18 still selects D18 under R31.

Freshness notification and pagination consistency remain separate contracts.
The user's later approval in R62-R67 selects H-bounded position-based continuation;
notices alone did not establish that decision. Current access and status checks
still apply, and no frozen historical result set or permission snapshot is promised.

### P1-F02-R41 — Keep notices bounded and avoid repeated unchanged alerts

Coalesce relevant arrivals into a bounded notice rather than broadcasting each
publication to every worker. Do not repeat the same already advertised update on
every turn merely because the agent chose not to fetch it. Further relevant
updates may produce a new/coalesced notice. Explicitly represent omitted details
or offer an authorized refresh when the eventual response bound is reached; never
claim an exhaustive list when not all references are shown.

R49-R55 now select the committed availability marker and initial registration
ordering; R56-R61 govern interrupted delivery and acknowledgment. The exact
coalescing key, bounds, retention, marker storage/allocation and receipt schema
remain open. Do not invent numerical defaults,
silently drop unadvertised updates, or add a general message broker.

### P1-F02-R42 — Advertised is not retrieved, consumed or source-read

Distinguish the listing state observed by the work, update information advertised
to it, and results actually retrieved. A notice that D20 exists does not establish
that the agent read D20, adopted its conclusions, or inspected its source. Preserve
real authorship and current-attempt read accounting. No coverage, finding, or
requirement-completion credit follows from notification delivery.

These are distinct meanings, not a mandate for three database tables. The exact
state representation must be reconciled with P1-F04 and P1-F08; do not let a field
named 'seen' ambiguously substitute for all of these facts.

### P1-F02-R43 — Optional updates never override stale-input safeguards

Optional supplementary analysis is different from a material change that invalidates
bound inputs. A choice not to refresh does not permit acceptance of an obsolete
assessment or bypass current authorization, evidence or submission checks. Retain
the owning stale-input/invalidation rules; this feature does not create a new
invalidation policy or force a conclusion about the new analysis.

## 4D. Approved durable ownership of freshness interests

R44-R48 record durable work-scoped interests. R49-R55 add ordered availability and
race-safe lookup registration; R56-R61 add acknowledgment; R62-R67 add the separate
analysis-list continuation policy. Exact persistence and owner integration remain
open. These choices do not alter analysis acceptance or coverage ownership.

### P1-F02-R44 — Persist interest with a successful analysis lookup

Keep a small host-owned, source-free interest record when an authorized analysis
lookup establishes interest in a subject. Registration is part of completing the
successful lookup, not something deferred until the model next saves a checkpoint.
Worker memory may cache the record but must not be its only durable authority.

A process stopping after successful lookup but before an agent checkpoint must not
lose that work's interest. A normal authorized continuation of the same logical
work restores its interests without requiring another subscribe call. Do not claim
that registration succeeded when its persistence outcome is not established; the
exact failure/retry response must be settled with P1-F07/P1-F08 before implementation.

### P1-F02-R45 — One interest per equivalent work-subject query

Use the logical identity `(review, ongoing work, subject, normalized filters)` to
associate and deduplicate interests. Use existing indexed subject identities and
an existing durable task identity where it already represents the ongoing work.
Do not require a new inquiry subsystem merely to implement this capability. If a
continuation changes task identity, its same-work mapping must be explicit rather
than inferred from a worker slot, subject name or similar question text.

Repeated equivalent lookups reuse the interest instead of creating duplicate
listeners. Distinct work owners and materially different filters remain distinct.
Filter normalization and the exact key representation are still to be specified;
do not silently broaden filters or merge incompatible interests. Refreshing an
interest must not discard updates that were neither represented by the lookup nor
advertised under the eventual observation/delivery contract.

Retain only the metadata necessary to identify the review/work, subject, normalized
query, observed availability position, and notice-delivery progress. These are
logical fields, not prescribed database columns. Result retrieval remains distinct
from advertising: fetching D22 is not evidence that D20 and D21 were read. Reuse
existing consumption/read accounting instead of a blanket 'read through' marker.
Do not copy source, result bodies, conversation content or publication history into
each interest record.

### P1-F02-R46 — Restore and retire by logical-work lifecycle

A replacement attempt continuing the same logical work can use the durable
interests, with current recipient authorization and result visibility rechecked.
A reusable worker slot running unrelated work must not inherit those interests.
A failed or interrupted attempt does not by itself close still-continuable work.
Temporary waiting or a retryable interruption preserves interest for normal
resumption; a freshness notice does not itself resume, schedule or reopen work.

Stop advertising when the logical work is completed or cancelled under its owning
lifecycle. Do not use an individual attempt's terminal state as a substitute for
that decision. The exact closure mapping, physical retention/cleanup and restore
interfaces require reconciliation with the task/inquiry and checkpoint owners.
The record must not confer authority on a stale attempt or grant inherited source
or result-consumption credit.

### P1-F02-R47 — No publication gap between lookup and registration

The lookup's represented analysis and its initial observed availability position
must agree. A relevant result becoming available during lookup/registration must
be represented by that lookup or remain eligible for a later notice; it cannot be
lost between an earlier listing read and a later marker update. Only authorized,
consumable results qualify under the owning acceptance/visibility contract.

R49-R55 now select a committed review-local availability sequence and preserve the
lookup's position across separate short read and write transactions to satisfy
this invariant. This does not freeze later listing pages. Delivery acknowledgment
is now specified separately in R56-R61. Exact storage/allocation and failed-registration recovery details
remain subject to their owning contracts. Never keep a transaction open across a
model turn or mark a result advertised merely because a response was constructed.

### P1-F02-R48 — Reuse host state and keep persistence narrowly scoped

Inspect existing host-owned durable state for a compatible extension before adding
storage. If none fits, a small source-free persistence structure is acceptable;
it must have an explicit owner and fit the existing authorization, transaction and
migration practices. This approval does not allocate a table or migration number.

Register interests through the analysis-query owner and restore/check them through
the normal runtime-response/continuation integration. Derive bounded, coalesced
notices from authoritative availability information rather than creating a
notification task for every result or copying the publication history per agent.
Do not scan and summarize the entire project every turn. No general messaging
service, manager model, extra notification worker pool, new knowledge store or
copy of every query result is needed. Preserve the original query's result
identity, visibility, response bounds and ordinary audit/accounting.

## 4E. Approved availability sequence and lookup-registration ordering

R49-R55 govern the committed availability marker and initial lookup/registration
race. R62-R67 now separately govern subsequent analysis-list pagination; the shared
marker does not merge listing progress with notice delivery or result consumption.

### P1-F02-R49 — Order committed availability changes within each review

Use an ordered, committed availability sequence within the review. Each relevant
availability transition references its existing result and subject identities;
retain only the source-free metadata needed for ordering and lookup. Do not copy
result bodies or create one publication-history copy per worker or interest.

Reuse an existing ordered publication/event mechanism if it provides these
semantics. A timestamp, arbitrary result ID or prepublication row-creation order
is not a substitute. Gaps in sequence values are harmless; values exposed as the
observed position H must refer to committed availability. An allocation scheme
must not allow a later-visible transition to appear behind a previously observed
position and thereby become undiscoverable by an after-H query. The exact
counter/event allocation, schema and indexes are implementation details requiring
mapping and review, not permission to invent a new event platform.

### P1-F02-R50 — Record actual usability, independently of active interests

Record availability when the owning acceptance path makes the result usable, not
when a private draft, task or provisional row is created. Required runtime,
transcript and publication receipts continue to govern usability. A result created
earlier but made usable after H must enter the later availability stream.

Retain the transition even when no agent has yet registered interest. This permits
an interest created after a racing publication to recover that change from its
original observation position. Recording must not depend solely on delivering to
currently registered in-memory listeners.

Integrate the record with the owning accepted-availability transition. Do not
bypass the acceptance gate, infer usability from task completion, or claim atomic
transactions across ssr.db and transcript.db. The actual acceptance-owner hook and
recovery for multi-step sealing must be inspected and specified before enabling
notices. This feature does not redefine the result's publication policy.

### P1-F02-R51 — Observe H and the lookup through one short consistent read

For an initial analysis lookup, obtain the committed review availability position
H and the bounded authorized listing from the same short database read view.
Finish that read transaction before entering interest registration. Do not hold a
transaction across source/model I/O or a model turn.

H describes what availability existed in the lookup's view. It is not a statement
that every result at or below H fit in the returned page, was delivered, or was
read. Existing entries omitted by paging remain a listing-retrieval matter.
This initial-read requirement is not a frozen listing or permission snapshot.
The separately approved R62-R67 reuse H to bound subsequent position-based pages;
current visibility and result status remain authoritative.

### P1-F02-R52 — Register the interest with the originally observed H

In a separate short write transaction, validate the current work/attempt authority
and create the interest with H, or reuse an equivalent existing interest under
R45/R53. Complete durable registration before reporting the lookup-with-interest
operation as successful. Do not replace H with a later marker read during the
write transaction merely because newer results are now available.

For illustration, a lookup observes H=120; another worker publishes an associated
result at sequence 122 before registration commits. A new interest starts at 120,
so the transition at 122 remains eligible for a notice. A publication committing
while the consistent read is open is also later than that read view; it must not
be lost between listing and registration. The numbers are examples, not defaults.

If interest persistence fails or has an unknown outcome, do not claim complete
success or falsely claim that nothing was saved. Apply P1-F07/P1-F08's explicit
recovery path; recovering the original operation must not silently advance its
observation boundary past an unrepresented publication. Exact receipt/replay
fields remain open. Concurrent equivalent lookups must reuse one interest without
losing its earlier pending updates.

### P1-F02-R53 — Preserve existing progress and replay publication safely

Repeated equivalent lookups reuse their interest. They must not blindly replace
its pending/advertised progress with a newer H. A refresh is not evidence that all
earlier results were returned or read. Preserve the distinctions among observed,
advertised, retrieved and source-read information in R42/R45/R47.

Retrying bookkeeping for the same accepted availability transition must recover
that transition rather than create a second new-result event. Operational replay
is not the same as a genuine later availability transition; that distinction uses
the owning acceptance identity, not merely matching prose or file names. The exact
idempotency key and later-transition vocabulary remain to be specified with the
publication owner.

### P1-F02-R54 — Filter relevant changes and recheck current visibility

At the ongoing work's next ordinary interaction, query committed availability
changes after its relevant recorded position using exact subject associations and
normalized interest filters. Use a bounded indexed query, not a scan of every
analysis body or a broadcast to every worker. Unrelated subjects produce no notice.

An availability record proves that the transition was recorded, not that its
result is still visible or current. Recheck recipient authority and owning result
status before releasing notice metadata or content. Do not use a valid historical
sequence to disclose a now-restricted result. Handling later visibility changes
and retention gaps must be reconciled explicitly with the owning contracts; do
not silently claim those cases are solved by an increasing number alone.

Finding or composing a notice does not mark it advertised, consumed or read.
Advancing notice-delivery progress is governed by R56-R61 and its request-bound
acknowledgment condition, not by successful detection. Bounded notice pages must not silently skip unadvertised
changes by jumping progress to the latest review sequence.

### P1-F02-R55 — Reuse existing owners and keep open contracts explicit

The implementation needs authoritative ordered availability, an indexed association
to existing subjects, and the durable interests from R44-R48. Reuse compatible
host event/query/state components. Do not add a separate database, message broker,
notification worker pool, manager model or duplicated knowledge store.

Approved transaction direction: observe H and listing in one short consistent
read; close it; durably register/reuse interest in a separate short write using
that observed H; discover later eligible changes at normal interactions. This is
a behavioral/transaction contract, not final SQL or a claim that the current
implementation already supports it.

Final sequence storage/allocation, initial/empty-state representation, filters,
acceptance integration, exact acknowledgment records and retention remain open.
R56-R61 select acknowledgment/replay; R62-R67 select H-bounded position-based list
continuation without finalizing their schemas. Ask about consequential choices;
do not supply new numerical bounds or assume a new publication policy.

## 4F. Approved notice-delivery acknowledgment and recovery

These requirements record the approved host-managed delivery condition. They do
not establish that a model understood a notice or consumed its referenced analysis.
Exact persistence fields and provider-outcome mapping still need code verification
and agreement; no new messaging service or model-facing acknowledgment tool is needed.

### P1-F02-R56 — Acknowledge after a valid response is durably recorded

Mark a notice advertised only after an ordinary model request containing it has
produced a valid response durably associated with that exact request. Preparation,
queueing, request construction, or an inconclusive send alone is insufficient.
The model need not call a separate acknowledgment tool or mention the notice.

A valid response requesting another tool is sufficient; do not wait for the
analyst's terminal submission. Invalid arguments in that returned tool call are a
separate validation issue, not by themselves evidence of failed notice delivery.
Map 'valid response' to the actual runner/protocol outcome contracts before coding;
this document does not silently classify every refusal or partial-stream outcome.
Advertisement is an observable exchange condition, not comprehension, adoption,
result retrieval, evidence consumption, source inspection, or coverage credit.

### P1-F02-R57 — Bind acknowledgment to the exact included notice set

Record the association between logical work, notice identity, represented
availability changes/results, actual attempt, and the final outgoing request.
Use existing request/turn identities where suitable. The association must reflect
what remains after final context selection and budgeting, not an earlier draft.
A notice omitted from the model-bound request stays pending.

Acknowledge only the exact notices represented in that request. If Q53 advertises
D20 and D21 becomes available while Q53 runs, acknowledging Q53 cannot suppress
D21. Never set advertised progress to the latest review sequence at response time.
Neither omitted references nor gaps in advertisement become delivered by inference.
How bounded coalescing represents omitted detail remains an explicit open contract.

### P1-F02-R58 — Recover acknowledgment; repeat only at ordinary interactions

When the request has no conclusive recorded response, retain uncertain/pending
delivery and permit replay at the next normal interaction under current authority
and resource limits. Prefer a safe occasional repeat over silently losing an update.
Do not advance a shared reading position, duplicate a result/lead/task, or charge
an acknowledgment as a new analysis operation.

When the response was recorded but acknowledgment was interrupted, recover the
acknowledgment from the durable request/response and notice association. No new
model exchange is needed just to settle that bookkeeping. Repeating settlement
for the same outcome is idempotent and must not reset newer progress.

Do not claim exactly-once presentation to the remote model. Interrupted delivery
can be uncertain. Never launch a notice-only model request, resume waiting work,
or reopen completed/cancelled work solely to deliver or retry an optional notice.

### P1-F02-R59 — Preserve current visibility and prior-attempt isolation

Recheck recipient authority and current result visibility before presentation or
replay; a pending notice never authorizes disclosure of a now-restricted result.
Apply the existing logical-work lifecycle and owner-controlled finalization rules.

A late response from an earlier attempt can settle only the exact work/request/
notice association permitted by those rules. It cannot acknowledge a notice only
its successor received, overwrite successor progress, or make the stale attempt
eligible for fresh tools. Use attempt-bound durable identities, not whichever
attempt currently occupies the task or worker slot. Replacement attempts inherit
no source-read credit from recovered advertisement acknowledgments.

### P1-F02-R60 — Source-free bookkeeping independent of full transcripts

Keep only the necessary notice/result/change references, owning work and attempt,
request/turn linkage, and outcome/acknowledgment metadata. Reuse existing durable
execution records when they prove the required association. Record no extra copy
of prompts, source, result bodies or provider payloads for this feature.

Reliable notice acknowledgment must not depend on enabling optional full sensitive
transcript capture. A request hash alone does not enumerate its included notices;
the recoverable association must identify them. Do not invent a second transcript
store, new provider protocol, messaging service or notification worker pool.

### P1-F02-R61 — Make crash boundaries explicit in the implementation

Map request construction, final context selection, dispatch, response acceptance,
durable response recording and acknowledgment to the existing runner owners.
Persist the necessary association at a recoverable dispatch boundary; do not claim
recoverability when it exists only in an in-memory pending response. No database
transaction may remain open across the model exchange.

A response-recording or acknowledgment failure is not successful delivery merely
because network bytes were received. Apply P1-F08 outcome recovery without asking
the model to reconstruct unchanged metadata. The physical storage, exact response
predicate, write/receipt ordering and recovery API remain prerequisites before
implementation readiness; this approval fixes the observable semantics, not DDL.

## 4G. Approved H-bounded analysis-list continuation

This approval applies to the changing list of available analyses. It does not
silently choose pagination for symbol lookup, source search, relationship queries,
work-status lists, or a selected result's detailed body.

### P1-F02-R62 — Retain the original availability boundary

An initial analysis listing uses the committed availability position H observed
with that listing under R51. Continue the same query using that original H; include
only results whose qualifying availability lies within that boundary. Do not move
H forward during continuation or insert later publications into the old traversal.
A result created before H but made consumable after H is a later arrival under R50.

H bounds availability, not historical permissions, analysis correctness, or actual
consumption. Exact results, relevant subject associations and the qualifying
availability position must come from the owning records, not guessed timestamps.

### P1-F02-R63 — Continue by a stable position, not a row offset

Use a stable availability-based order, with an existing result identity as a
tie-breaker, and continue after the last returned position. Do not implement
continuation as a numeric offset into the current mutable list. Mutable status,
relevance score or last-edit time must not reorder this traversal.

The continuation preserves the original review/snapshot, subject, filters, H,
ordering position and contract identity. It must not silently become a different
lookup. Reuse a compatible cursor codec, but give analysis-list and source-read
cursors distinct types and validation semantics; they are not interchangeable.
Final field names, ordering direction and storage mapping are not selected here.

### P1-F02-R64 — New results remain independently accessible

A publication after H remains eligible for the approved freshness-notice mechanism.
The analyst can fetch an advertised result by exact identity immediately, even
while its older listing is unfinished. That fetch does not advance or reset the
old listing. The agent can also refresh explicitly: a fresh lookup observes a new
boundary and can include later results, subject to current access and acceptance.

Refreshing is not proof that earlier results were returned or read, and must not
overwrite pending interest/notice progress under R53. No forced refresh, automatic
body loading, or implicit task/worker creation follows from pagination or a notice.

### P1-F02-R65 — Apply current visibility and status on every page

H does not preserve access to a result that is now restricted or unavailable.
Recheck current execution authority, result visibility, acceptance and the query's
status filters before returning every page or exact-result detail. A superseded
result must not be labeled current. If the query excludes its current status, it
may disappear from later pages rather than retain eligibility from the initial read.

The guarantee is bounded traversal of earlier availability without reordering from
new publications, not an immutable historical database snapshot. A final page means
no further currently eligible entries remain within that query and H. It does not
mean there are no newer results, or that the agent consumed every earlier entry.
If evaluation stops on a resource/operational limit, expose the partial outcome;
do not falsely report exhaustion of the selected listing.

### P1-F02-R66 — Keep list, notice and consumption progress separate

Advancing or exhausting a list cursor must not acknowledge a notice, advance its
advertised position, or award result-consumption/source-read credit. A notice's
acknowledgment still depends on the exact included request and recorded response
under R56-R61. An independently fetched result changes neither an old traversal's
H nor its saved position. Separate queries/readers retain independent cursors.

### P1-F02-R67 — Use bounded queries within existing owners

Implement list continuation through the existing analysis-query owner and the
committed availability mechanism. Each page uses a short database read operation;
never hold a transaction open across model turns. Do not persist a complete result-
list copy per agent, introduce another database, or add a pagination/notification
service. Existing durable interest and delivery bookkeeping remain separate.

The agreed continuation rule still needs mapping to actual result/availability
records. Explicitly resolve how multiple subject associations or later availability
transitions for one result affect its stable listing identity. Do not substitute
an event feed for a result listing or silently choose those Phase 4 integration
semantics. Exact schema, index design, cursor encoding/expiry and release enablement
remain open; do not describe this feature as implementation-ready yet.

## 4H. Approved direct-relationship navigation

The user approved extending the existing `relationship_query` for bounded direct
connections around a known symbol. This approval preserves indexed identities,
actual edge direction, callsites, resolution uncertainty and provenance. It does
not authorize a new resolver, graph store, automatic transitive traversal, or
changes to graph/publication/scheduling authority. Exact wire fields and paging of
changing relationship records still require discussion.

### P1-F02-R68 — Reuse relationship queries over known subjects

Use the existing relationship-query capability, or its refactored owner, with a
known symbol ID, requested relationship kinds and incoming/outgoing/both direction.
Resolve the subject within the current attempt's bound snapshot and P1-F01 research
policy. Return only supported kinds actually recorded; requesting a kind does not
establish parser or framework support that the inventory lacks.

Return direct connections, not an automatic traversal of the whole connected
component. The analyst may follow returned subject IDs through further queries.
One-hop response scope is not a cap on the analyst's investigative route.

### P1-F02-R69 — Preserve the recorded edge direction

For outgoing call retrieval, select calls originating in the requested symbol,
including recorded unresolved calls. For incoming call retrieval, select recorded
calls whose resolved target is the requested symbol. In a both-direction query,
retain each relationship's source and target orientation: an incoming caller-to-S42
edge must not be rewritten as S42-to-caller.

Self-calls remain identifiable through their existing edge and endpoint identities.
The final contract must settle how both-direction output represents a self-edge
without inventing a second logical relationship or losing a callsite. A choice of
wire grouping or duplicate presentation is not selected by this amendment.

### P1-F02-R70 — Return attributable connections, not inferred paths

A permitted relationship result needs its existing ID and kind, originating symbol,
resolved target identity where available or recorded unresolved name/locator,
originating source location, provenance and available supporting references.
Include the recorded resolution state and basis where available. Preserve the
meaning of definite, ambiguous, unresolved and ignored resolver outcomes rather
than relabeling all stored records as confirmed connections.

Return resolver-produced alternatives only when they actually exist and identify
what produced them. A declaration-name search is not a source of confirmed binding
alternatives. Missing resolution metadata is not grounds to manufacture a status,
confidence value or proof. The exact mapping of absent/inapplicable information
and per-kind result shapes remains a wire-contract decision.

Distinguish extractor observations, resolver decisions and permitted analyst-
authored relationship claims. A target ID does not transform an analyst claim into
a deterministic fact. Structural retrieval does not prove attacker influence,
reachability under particular conditions, or a complete security path.

### P1-F02-R71 — Do not guess incoming callers

A recorded unresolved call with the same spelling as the selected declaration is
not a resolved incoming edge to that declaration. Do not attach it by name-match
uniqueness or silently promote a possible target to a definite target. Preserve
uncertain information separately where the eventual interface supports it.

An empty incoming-call result means no matching resolved incoming records were
found within the queried scope and its reported limits. It must not assert no
callers, unreachability, or safety. Expose relevant inventory/resolution limitations
without inventing global completeness guarantees.

### P1-F02-R72 — Keep distinct callsites inspectable

Do not collapse different callsites into an indistinguishable source/target pair.
Two calls to the same helper can occur under different controls or branches. Where
the existing representation has separate relationship records, retain their IDs
and locations. Where it groups occurrences, retain its bounded occurrence
information and enough references to inspect the separate locations.

Presentation grouping may reduce repetition but must not erase occurrence
identity, supporting locations or reported omissions. No occurrence table or new
relationship identity algorithm is mandated by this requirement.

### P1-F02-R73 — Apply visibility without hiding authorized unresolved origins

A recorded unresolved outgoing relationship remains discoverable when its
originating subject and callsite are authorized under the applicable policy.
The lack of a resolved target alone is not a reason to silently drop it.

An authorized origin does not grant access to protected target metadata, private
analyst results, or another snapshot. Recheck relevant execution, research and
record-visibility rules before returning IDs, alternatives or source references.
Do not expose protected target details in diagnostics or completeness metadata.
The safe representation of a restricted target must follow the agreed final
result/error contract; do not add a new cross-project disclosure policy here.

### P1-F02-R74 — Retrieval does not mutate the graph or schedule work

Query existing records and compatible resolution information through their owners.
Do not equate the canonical relationship collection with the coverage scheduler's
same-file dependency graph. Use a verified association when composing information
from them, not a guessed join by display name or a silent replacement of one graph
with the other.

A relationship query must not create or upgrade edges, run a model to resolve a
call, change candidate or coverage state, create scheduling dependencies, or spawn
analysis work. Ordinary read audit and resource accounting remain permitted.
Do not automatically load connected source bodies; return references that the
analyst may inspect with `source_read`. Relationship metadata grants no source-read
credit. This amendment does not add automatic freshness interests to relationship
queries; the existing automatic-interest decision concerns analysis lookup.

### P1-F02-R75 — Bound results and state their limitations

Use bounded queries and explicit partial/completeness information. Respect the
actual supported relationship kinds, resolution coverage, authorized scope and
resource limits. Do not load the full project graph into each worker merely to
answer a local relationship query. A page is not proof of whole-graph completeness.

The precise stable ordering, occurrence-page representation and continuation
consistency for changing relationship records remain open. Do not silently apply
the analysis-result H-boundary to relationship records without an agreed mapping.
Likewise, the immutable source cursor does not define relationship paging. These
open choices block claims of a final executable relationship-tool contract.

## 4I. Approved manifest-backed file discovery and directory browsing

The user approved one catalogue capability for directory browsing and filtered file
lookup, based on the existing immutable-snapshot manifest. This extends navigation
without exposing the live filesystem, adding another inventory, or conflating
metadata discovery with source access or analysis-update subscriptions. The final
tool name, request/response schema, filter normalization and paging encoding remain
open; this section does not choose them implicitly.

### P1-F02-R76 — Reuse the snapshot catalogue as the authority

Browse and find files through the existing manifest and associated inventory records
for the current attempt's bound snapshot. Reuse existing file identities and the
owning catalogue/query implementation or its refactored equivalent. Do not walk the
live target, expose an arbitrary host-filesystem browser, run another indexing pass,
or create a second file store to answer discovery requests.

The two uses are directory browsing and filtered file discovery. They share the
catalogue and authorization path; this is not a requirement for two tools or a new
service. A symbol ID is not required to locate a manifest-recorded file.

### P1-F02-R77 — Browse explicit directories without shared working-directory state

Directory browsing returns visible immediate child files and subdirectories by
default, in bounded pages. Do not automatically dump the entire descendant tree.
Each request identifies its intended directory or query; one worker must not alter
another worker's selection through shared mutable current-directory state.

Directory entries describe groups of recorded snapshot paths. They do not imply
access to a physical host directory or require a new persistent directory-identity
system. The root representation and exact directory-selector syntax remain to be
specified in the final contract.

### P1-F02-R78 — Support exact file lookup with explicit narrowing

Initial name-based discovery supports exact filenames and exact normalized relative
file paths, with optional narrowing by directory, recorded language, or
classification. File finding can include descendants when requested. Honor the
requested directory boundary and matching mode; do not silently widen an exact
lookup into fuzzy/pattern matching or discard filters to produce a result.

Return distinguishable records when the same filename exists in several directories.
Do not select the first match as a unique answer. Exact case/normalization rules,
filter combinations and descendant-selection fields still require agreement;
pattern matching needs its own supported contract rather than an implicit fallback.

### P1-F02-R79 — Return metadata and existing references, not implicit content

For each permitted file, return its existing file reference, normalized relative
path, recorded byte size, classification, and recorded language/inventory information
where available. Preserve missing information as missing; do not invent a language
or a successfully completed inventory. The exact result fields remain open.

The discovered reference should support the applicable existing symbol-list,
source-read and analysis-query paths. Discovery itself must not read source bodies,
start reviews, register leads, or automatically register freshness interests. The
approved automatic-interest behavior applies to analysis lookup, not filename
browsing. Ordinary audit and resource accounting remain permitted.

A file reference is a locator, not an access grant or evidence that its source was
read. An explicit later source read rechecks current authority and source integrity;
metadata discovery grants neither source-read credit nor coverage completion.

### P1-F02-R80 — Derive directory groups safely before paging

Apply metadata visibility to eligible manifest records before deriving directory
entries. Do not reveal a restricted filename, file ID or hidden directory merely
because an unfiltered grouping or count exposes it. Follow the existing visibility
owner; this requirement does not grant a new right to inspect excluded metadata.

Use path-component boundaries. A selection for `src/api/` must not include
`src/api_old/` through a naive textual-prefix match. Deduplicate derived immediate
child directory entries before pagination so a directory containing several files
is not repeated as several catalogue entries. Deterministic ordering and query-bound
continuations are required; the concrete query/index and cursor contract remain
implementation choices to discuss.

### P1-F02-R81 — Distinguish discoverability, readability and inventory availability

A permitted context-only file without callable symbols remains discoverable. A parse
error or unsupported inventory must not silently remove a file whose metadata is
otherwise permitted. Expose the recorded limitation instead of representing it as a
successfully indexed file with no symbols.

Metadata visibility does not imply readable captured content. A discoverable file
whose content is unavailable under the source policy must not be presented as
readable. Conversely, restrictions on metadata itself apply to names, IDs and derived
directories. Consult the existing classification, metadata-visibility and
source-access owners rather than implementing a competing policy in this tool.

An empty response means no matching visible entries in the queried snapshot
catalogue, subject to the reported limits. It is not proof that the live target
folder is empty, that the project contains no such behavior, or that review has
completed.

### P1-F02-R82 — Enforce current execution and snapshot boundaries

Validate the actual running attempt and resolve catalogue selections within its
bound snapshot under P1-F01. Recheck current authorization on subsequent page or
reference operations; neither a displayed relative path nor a continuation permits
reading another snapshot, project, or host location. Fail with the applicable safe
outcome instead of falling back to live filesystem discovery.

Do not leak protected catalogue entries through errors, result counts or directory
summaries. Use P1-F07 for actionable outcomes and preserve explicit distinctions
between invalid requests, empty matches, restricted metadata, unavailable content,
inventory limitations and bounded partial results.

### P1-F02-R83 — Bound queries and reuse infrastructure

Use bounded manifest/inventory queries and explicit completeness/continuation
information. Do not load a complete manifest into each worker or rescan the target
for each lookup. Inspect existing query services, indexes and reference factories
first; any necessary optimization should extend that infrastructure rather than
introduce a parallel catalogue or preemptively add directory tables.

The final contract must settle ordering, root/descendant and filter semantics,
metadata-visibility projection, page limits and query-bound cursor representation.
Do not import analysis-list availability sequencing into the file catalogue merely
because both capabilities paginate. No schema, table, additional model call, or new
worker type is selected by this approval.

## 4J. Approved source-text search direction

This section records approval of explicit literal/regex matching, manifest-backed
scope selection, match-centered previews and honest search completeness. It does
not itself select the regex library or a complete search-continuation algorithm.
R91-R95 below settle per-file cross-line behavior; R96-R101 subsequently settle
occurrence ordering, non-overlap and complete-match-based progress. Precise dialect,
newline/anchor flags, encoding and search-cursor details remain open. Source
reading and search pagination are different contracts.

### P1-F02-R84 — Extend the existing source-search capability

Extend `source_search` rather than add a second source store or model-driven search
system. Search is navigation over permitted immutable source. A textual occurrence
is not a resolved call, security classification, candidate or proof of vulnerability.
Keep direct indexed navigation available without requiring a preceding text search.

The historical `_source_search()` in `src/ssr/tools.py` at harness commit
`8b7ed0e335d4f4fb5ae53ef6e059334661279f20` requires explicit file IDs, performs
literal per-line matching, clips previews to the line prefix, and continues past
decoding failures. Those observed behaviors identify extension points, not the
required destination modules after refactoring. Reinspect their current owners.

### P1-F02-R85 — Explicit matching modes and case behavior

Literal matching is the default; punctuation is literal. Support an explicitly
requested regular-expression mode under R86. Matching is case-sensitive by default
with an explicit case-insensitive option. Never silently change a failed literal
search into regex, fuzzy or semantic matching, or drop a supplied restriction.

Examples of intended inputs are literal `shell=True`, `build_command` and a route
string, or a regex alternative matching several operation names. These examples
are not a finalized regex dialect or a vulnerability detector. Final fields,
Unicode/case semantics and exact newline/anchor flags remain open. Cross-line
matching follows the subsequently approved R91-R95.

### P1-F02-R86 — Bound regex compilation and execution

Use an explicitly supported, restricted non-backtracking regex implementation with
bounded compilation, scanned input and generated output. Select a compatible
existing dependency or discuss the required dependency before installing one.
RE2 was an illustrative implementation approach, not an approved library choice.

Reject unsupported syntax with a useful explanation when the matcher can identify
it. Do not fall back silently to an unrestricted engine, execute a target-owned
search tool, or expose general shell execution to obtain pattern matching. Exact
resource limits, pattern dialect and engine identity remain implementation blockers.

### P1-F02-R87 — Resolve search scope through the snapshot catalogue

Support explicit file-ID selection and permitted directory/filter selections;
whole-authorized-snapshot search is also an explicit selection. Agents must not
have to enumerate every permitted file ID merely to search a directory. Resolve
scope through existing manifest and P1-F01 research authority in the attempt's
bound snapshot. Search readable content, not the live target or host filesystem.

Apply supported restrictions consistently and report the actual selected scope.
Do not expand it after zero matches. Exact selector combinations, descendant rules
and normalization must agree with the catalogue contract before implementation.
Content-only search creates no review task, lead or new analysis subscription.

### P1-F02-R88 — Return exact occurrences with match-centered previews

Return the existing file reference, relative path, exact match location and a
bounded preview around the occurrence. Include a containing symbol only where the
inventory association is unambiguous. A textual match must not invent a containing
symbol or resolve an ambiguous callsite.

Keep the exact matched byte range separate from the preview range actually
returned. Preserve original source coordinates and hashes. For a late match on a
long line, show the matching region rather than an unrelated line prefix. Mark
omitted context or an oversized match explicitly; do not insert presentation
markers into source bytes used for hashes. Exact preview fields, clipping limits,
multiline preview representation remain open. R91-R95 require the complete match
to be independent of that preview; R96-R101 specify separate occurrences, stable
ordering and progress that never derives from preview clipping.

### P1-F02-R89 — Report real search progress and omissions

Distinguish a completed search with no matches, a filled result page with remaining
work, a resource-interrupted incomplete search, and omitted/unsearchable content.
Offer continuation when the eventual search contract supports it; otherwise give
an honest narrowing/retry action. Pagination must not reset cumulative limits.

Report files/ranges actually examined, not merely the number selected. Decoding
failures must not be silently counted as successful no-match content. Preserve
integrity and authorization errors as their own failures. Do not claim exhaustive
results after an early stop or conflate output truncation with scan completeness.
The precise counters, stopping positions and continuation mechanism are still open.

### P1-F02-R90 — Separate host scanning from delivered source and coverage

Only preview source actually delivered belongs to the current attempt's delivered-
source accounting. Host examination of a file to search it does not mean the model
read the entire file or completed its symbol review. A search hit, graph lookup or
partial preview cannot automatically satisfy full-inspection or coverage gates.

Reuse the existing verifier, broker/accounting and index-query owners. Source
search requires no summarization inference, second source index/store, new manager
role or automatic candidate creation. Wire/resource changes need explicit version
and compatibility handling; do not smuggle them into the structural refactor.

## 4K. Approved per-file and cross-line search semantics

This section records the user's approval of the immediately preceding per-file
matching proposal. Occurrence ordering, non-overlap, empty-match handling and
complete-match-based progress are subsequently approved in R96-R101. Search-cursor
encoding, regex library/dialect and newline/anchor flags remain open.

### P1-F02-R91 — One file is the matching input

Treat each selected file's supported text as one matching input, not independent
display lines or source-response pages. Permit an occurrence to span line breaks
within that file when the requested query can match them. Never concatenate
separate files into one matching input. A cross-line textual occurrence is still
navigation, not a resolved binding or a vulnerability conclusion.

### P1-F02-R92 — Follow the requested literal or regex semantics

A literal without a newline matches its actual text; do not ignore intervening
whitespace or line breaks. Permit a literal containing a newline to match across
lines within one file. An explicitly requested regex may match across lines only
as its supported syntax and selected flags permit. Do not silently enable flags,
normalize source newlines, or reinterpret unsupported syntax. Final newline,
anchor, Unicode and encoding behavior must be specified with the chosen matcher.

### P1-F02-R93 — Output boundaries do not truncate the matching input

A result or preview limit must not cause a match crossing that boundary to be
missed or shortened. Preserve the complete match coordinates separately from the
preview actually delivered. Mark a clipped oversized preview explicitly and let
`source_read` reopen the selected source. The end of a clipped preview is not a
search-resumption position. Match enumeration and response formatting have
separate responsibilities; the exact continuation algorithm remains open.

### P1-F02-R94 — Reuse the verified reader and match one file at a time

Start with the existing verified file-reading path and approved bounded matcher,
one file at a time. This does not approve unbounded memory, a custom streaming
regex engine, persistent search jobs or another source index. Any later chunked
implementation must demonstrate the same matching semantics; a fixed overlap
alone cannot establish equivalence for all supported queries.

If a file cannot be processed under supported memory/scan limits, report the
limitation. Do not silently fall back to line-by-line matching and report no
matches as a completed search. Exact bounds, oversized-input handling and safe
continuation after a resource interruption require their own agreed contracts.

### P1-F02-R95 — Preserve occurrence identity across presentation sizes

For the same snapshot, query and supported matching contract, changing only the
result/preview page size must not change the complete occurrence sequence when
search is allowed to finish. Apply the occurrence and progress policy in R96-R101;
exact cursor representation and matcher dialect remain separate prerequisites.
Only source actually returned in previews or explicit reads contributes to current-
attempt delivered-source accounting; host matching of a whole file does not grant
whole-file read or coverage credit.

## 4L. Approved occurrence enumeration and matching progress

This section records the user's approval of individual, non-overlapping textual
occurrences in deterministic file/byte order, progress after complete matches,
original-file matching context and explicit rejection of zero-length occurrences.
It specifies behavior; it does not choose a regex library or finalize the search
cursor, timeout-recovery, encoding or resource-limit contracts.

### P1-F02-R96 — Return a result per occurrence, not per matching line

Represent each enumerated textual occurrence with its own exact match range.
Several occurrences on one source line remain distinguishable even when their
bounded previews overlap or have identical text. A shared line, symbol, endpoint
pair or preview is not a duplicate-occurrence key. Retain the existing file
reference and original-byte coordinates; do not create persistent evidence or
candidate records merely to identify search hits.

For example, searching literal `path` in the illustrative text
`validate(path); write_file(path); record_action(path)` produces three separate
match ranges. This is a navigation result, not three confirmed security issues.

### P1-F02-R97 — Use deterministic file and match ordering

Order enumerated results by the existing canonical normalized relative file path,
then increasing original match start-byte position, then match end-byte position
as a tie-breaker. Reuse the manifest's path representation without changing
filename case or normalizing source bytes. Do not order this initial search by
mutable relevance, worker completion time, discovery arrival or model-generated
scores. The final path comparison/collation contract must be explicit and
consistent across initial queries and continuations; this amendment does not
invent a platform-specific comparator.

This orders occurrences emitted by the supported matching contract. It does not
select among competing regex alternatives or redefine the chosen engine's declared
match-selection semantics. Those dialect details remain prerequisites.

### P1-F02-R98 — Enumerate non-overlapping occurrences initially

After a non-empty match, continue looking at or after that complete match's end.
The next enumerated match cannot start inside the preceding match. For example,
literal `ana` in `banana` returns the first occurrence at the zero-based half-open
byte range [1, 4), not the overlapping occurrence at [3, 6).

Do not add an overlapping-results mode implicitly. Identify the supported
occurrence policy in the eventual tool contract/response so completeness means
complete under that policy. If a future requirement needs overlaps, discuss and
version that extension rather than silently changing existing query results.

### P1-F02-R99 — Resume after the complete match, not the preview

A complete match's end controls progress following that returned occurrence.
If the match spans bytes [500, 800) while the preview exposes only [500, 650),
preview clipping must not resume searching at 650, shorten the match or cause part
of it to be enumerated again. Page/preview formatting and occurrence selection
remain separate responsibilities.

When the next occurrence does not fit the response allowance, do not advance the
agent-visible continuation beyond it as though it were returned. Keep it available
on continuation, or explicitly explain that it cannot be represented under the
supported contract. Inspecting a match to test whether a page is full is not proof
that the model received it. The exact continuation representation, interrupted-
response replay and safe scan-checkpoint positions remain to be specified with
P1-F08; this rule does not allocate a per-match persistence table.

### P1-F02-R100 — Preserve original-file context on continuation

Resuming at a match position must preserve the original file as the matching
input. Do not slice the suffix and treat its first character as the beginning of
a new file: that can alter supported anchors, boundaries and other context-sensitive
matching behavior. Use the selected matcher's positioned-search facility only
when its behavior has been verified to satisfy this contract. Byte positions must
be mapped through the agreed encoding rules, not passed blindly to a text API
that expects character indexes.

Test continuation against a complete search of the same original input, using the
finally supported anchor/boundary syntax and flags. If the engine/adapter cannot
preserve those semantics, report the integration blocker rather than silently
accepting divergent results. No custom streaming engine is authorized by this
requirement.

### P1-F02-R101 — Treat produced zero-length matches as unsupported

For the initial contract, when a regex produces an empty source match, return an
explicit, actionable unsupported-occurrence error explaining that the query must
include the text to locate. Do not enter a no-progress loop, silently skip empty
matches, advance by an invented character rule, or claim a complete search that
omits them. This addresses an actually produced empty match; it does not require
building a separate static analyzer to classify every potentially empty regex.

If ordinary matches have already been returned before this case occurs, mark the
search incomplete with the reason. Those earlier locations remain attributable
navigation results, but the search is not exhaustive. Exact status/field names
and partial-result envelopes belong to the agreed P1-F07 integration and final
wire contract. Do not label a supported-but-empty-producing pattern a syntax error
or switch engines/patterns to manufacture a non-empty result.

## 5. Illustrative interaction — not a final tool schema

```text
Agent requests source for known symbol S42.
Host resolves S42 in the bound snapshot and selects its indexed full range.
Host checks the attempt and research policy, then reads verified source.
Response identifies the source actually returned and whether more remains.
If more remains, it supplies a continuation for this exact selection.

Agent optionally requests continuation.
Host rechecks authority, validates the continuation and reads the next page.
The last page reports that no more of the selection remains.
Any full-read claim is evaluated from this attempt's delivered intervals,
not from receiving that last page alone.
```

S42 is illustrative, not an implementation symbol or a new ID format.
This example does not establish the serialized request/response schema.


Analysis retrieval example (D18/D19/T42 are illustrative, not new ID formats):

```text
Agent: What analysis is available for known symbol S42?
Host: Return compact, authorized result references including D18 and its provenance.
      Separately report that supplementary review task T42 is running.

Agent: Retrieve result D18.
Host: Recheck current access and the owning result's visibility/acceptance rules.
      Return D18's permitted detail, bounded and pageable.
      Do not substitute D19 if it was published after the discovery response.

Agent: Choose whether to inspect source, query another result, or request context.
Host: No task is created and no automatic waiting occurs merely from the lookup.
      Remember the current work's interest in S42 and the applicable query.

Another worker publishes a result D20 that this agent may discover for S42.
Agent: Read a different function during its normal work.
Host: Return that read plus a bounded notice that new analysis D20 exists for S42.
      Do not fetch D20's body or reset the existing analysis listing.
Agent: Decide whether to retrieve D20, refresh the listing, or continue unchanged.
```

## 6. Implementation guidance for the agreed portions

The sequence below elaborates the approved mechanism. It does not authorize
implementation until required open contracts are resolved and the feature is
reviewed as ready.

### 6.1 Source reads and continuations

| Step | Required developer action and verification |
|---|---|
| 1. Map and characterize | Locate current owners of `symbol_get`, `source_read`, symbol ranges, research authorization, output limits and actual-read accounting. Record legacy behavior, configured limits, exposed roles, callers and tests before changes. |
| 2. Resolve a single selection | Add the symbol selector through the existing index. Normalize either initial selector to a snapshot/file and bounded source interval. Validate selector exclusivity. Do not make the model copy hashes or coordinates. |
| 3. Reuse source authority | Apply P1-F01 checks and send the selected file/range through the existing verified reader. Keep coverage ownership and final-result authorization separate. |
| 4a. Map the private-key owner | Locate the refactored host's private-file and serialized initialization utilities. Keep one persistent project-local cursor secret outside target/snapshot data. Propose its exact file format/location and first-initialization-versus-loss behavior before coding. Do not add a key service or per-worker keys. |
| 4a.1. Implement the narrow codec | After agreeing the wire encoding, authenticate the complete cursor metadata with HMAC-SHA-256 using standard-library support and verify with `compare_digest`. Keep encode/verify separate from current-attempt authorization and source reading. Do not store per-page position rows. |
| 4a.2. Connect initialization and reload | Provision only through the serialized initialization path; ordinary workers load the established secret. Test concurrent initialization, process restart, missing/unreadable secret and mismatched authentication without silent replacement. No rotation/expiry implementation is implied. |
| 4b. Implement the page contract | Once encoding and remaining cursor choices are settled, return a bounded page that fits source and serialized-result limits, reserving space for identities/status/continuation. Preserve the selected range and advance only by source actually returned. Do not solve overflow by raising global limits. |
| 4c. Validate continuation and replay | Run the R15 validation path for every continuation; accept same-review independently authorized replacement attempts, deny foreign/stale access, and keep replay free of a shared advancing pointer. Use the current response allowance without shifting the encoded start. |
| 5. Connect delivery accounting | Bind each successfully delivered source interval to the executing attempt. Ensure partial pages and last-page retrieval cannot satisfy an unfulfilled full-read prerequisite. Use actual runner hooks; do not assume an internal successful read equals model delivery. |
| 6. Integrate exposure and errors | Keep `symbol_get` metadata-only and expose the revised `source_read` consistently to the agreed analytical roles. Return actionable selector/cursor/authorization/range errors without leaking unauthorized source. No mandatory lookup sequence is introduced. |
| 7. Verify compatibility | Exercise initial file-range reads and the new symbol mode, continuations, failure cases and related runtime accounting. Assess tool-schema/execution-receipt version impacts; do not reuse incompatible historical execution identities. |

No per-page cursor row is required: pagination state is self-contained. The
existing manifest, symbol index, snapshots and configured policies remain
authority; audit and read-accounting persistence stay intact. The approved
cursor-authentication secret is persistent host state in a project-local private
file, not pagination position state. Exact provisioning details, rotation/expiry,
version negotiation and P1-F03 convenience-reference persistence remain unresolved.
Do not make a schema migration merely because a feature file exists.

### 6.2 Exact indexed symbol lookup

This sequence elaborates R23–R28; it does not settle the remaining wire, ordering,
normalization, or query-pagination choices.

| Step | Required developer action and verification |
|---|---|
| L1. Map existing query behavior | Locate the refactored owners of `symbol_list`, `symbol_get`, inventory records, file-ID/path resolution, authorization filters, and paging. Record current consumers, output contracts and tests. Preserve exact-ID retrieval and file-scoped listing. |
| L2. Agree and validate query inputs | Define explicit local-name/qualified-name lookup and permitted file/parent/kind filters in the existing tool contract. Resolve filter references inside the execution-bound snapshot. Validate conflicts and unsupported modes; never repair an empty result by dropping a filter. |
| L3. Apply research scope in the query | Reuse P1-F01's authority and query the existing inventory. Access predicates must constrain the eligible rows before page selection. Use the project's validated, parameterized query mechanisms rather than interpolating model input or materializing the full inventory in a worker. |
| L4. Produce a deterministic bounded result | Apply the agreed stable ordering and page limit, returning existing identities and distinguishing metadata. Determine whether more matches exist using a bounded query where practical; do not require a costly full-project count merely to avoid a false uniqueness claim. Final paging mechanics still need agreement. |
| L5. Project completeness and limitations | Distinguish the number of items in this page from query completeness and inventory coverage. Surface relevant parse/unsupported limitations from existing records. Do not infer a call binding from a single match or attach another subject's private analysis to a metadata response. |
| L6. Integrate and validate the tool | Add focused lookup tests and rerun affected source/index/authorization/tool-contract tests. Confirm that returned IDs work with `symbol_get` and `source_read`, but lookup itself does not expose source automatically or create domain records. Assess tool-schema and execution-receipt compatibility through the existing owners. |

Illustrative processing path, not a second implementation authority:

```text
Validate current execution and the agreed lookup arguments.
Use the execution's bound snapshot.
Resolve supplied file/parent identities inside that snapshot.
Apply exact indexed name predicates and all supplied narrowing filters.
Apply research authorization before bounded page selection.
Return existing symbol identities, distinguishing metadata and page completeness.
Report relevant inventory limitations; do not infer a callsite binding.
```

No new durable symbol/lead/task record is needed for this read-only lookup. Retain
existing tool audit and usage accounting. Separate query-pagination state decisions
from the already agreed source-reading cursor; sharing a codec is not authority
to silently share different pagination semantics.

### 6.3 Analysis discovery, exact retrieval, and work availability

This sequence elaborates R29–R36. R62-R67 now govern analysis-list pagination;
publication policy remains with its owner. Historical components include
`document_query` and the dedicated
symbol-result readers inspected earlier in this conversation; verify the actual
modular-refactor owners, field availability, role filters, callers, and tests.
Do not infer that all proposed result types already share one schema.

| Step | Required developer action and verification |
|---|---|
| A1. Map result and work authorities | Identify existing document/result-to-subject associations, accepted-result readers, provenance/receipt checks, role visibility, task projections, and summary fields. Record which proposed artifact variants can actually be consumed. Do not broaden a restricted reader by bypassing its owning publication contract. |
| A2. Define the lookup boundary | Resolve symbol/file references within the execution-bound snapshot and applicable review context. Define supported result filters and safe work-status fields before coding. Extend the existing query owner rather than perform repository-wide model search or a full per-worker document scan. |
| A3. Build compact discovery | Return permitted existing IDs, subjects, types, recorded summaries, producer/source identities, and availability/limitations. Apply relevant visibility rules before releasing identities or content. Keep distinct results distinct; do not run summarization inference or infer a missing relationship. |
| A4. Add exact detail dispatch | Dispatch a selected result reference to its owning reader. Recheck access and acceptance; preserve identity, provenance, content, evidence references and bounded detail paging. If unavailable, return that outcome without replacing it with a newer result. Keep per-type validation with its owner. |
| A5. Compose independent work availability | Obtain relevant authorized task state through its owning projection. An available result may coexist with queued, running, failed, or supplementary work. Do not use task completion as the acceptance predicate or expose private provisional content through a status response. |
| A6. Implement the agreed list consistency and common outcomes | Apply R62-R67 and section 6.8: retain H, continue by stable position, and recheck current visibility/status. Resolve exact schema and availability-to-result mapping before coding. Integrate P1-F07 outcomes and P1-F09 combined-response limits; source cursor semantics are not interchangeable. No transaction spans model turns. |
| A7. Test callers and preserve read-only behavior | Run accepted/private/pending/failure combinations, exact-ID races, bounded retrieval and cross-snapshot/unauthorized cases. Confirm no provider inference, new lead/review task, acceptance write, or source-read credit is produced merely by consuming summaries. Assess tool-schema, execution-receipt and public-query compatibility through the existing owners. |

Transient response composition and existing query projections should be sufficient
unless inspection identifies a concrete missing association or indexing need.
Do not add a new knowledge store, task scheduler, per-query worker, or result
publication lifecycle to implement discovery. Any necessary persistence extension
must be justified and agreed rather than inferred from this feature's existence.
The final interface must identify which result kinds are supported and distinguish
"not visible," "not available," and "not supported" without leaking private data.

### 6.4 Freshness notices: integration guidance and unresolved mechanisms

The following steps implement the agreed interaction without choosing unapproved
storage or pagination algorithms. Verify actual refactored owners; this save does
not claim a new code inspection or an existing ready-made notice subsystem.

| Step | Required developer action and verification |
|---|---|
| N1. Map the boundaries | Identify the logical task/inquiry owner, accepted subject/result associations, availability transitions, result visibility checks, and the runner's ordinary response-composition boundary. Determine whether an existing event/query mechanism can supply the needed change information. |
| N2. Capture interest with lookup | Observe the bounded listing and committed availability H in one short consistent read, then register/reuse the interest in a separate short write using that original H (R44-R45/R51-R53). Preserve existing pending progress and recheck work authority. Do not rely on worker memory or a model checkpoint; exact failure/receipt fields remain open. |
| N3. Detect relevant availability | Use the review-local committed availability sequence in R49-R50 and exact subject associations. Record actual usability even with no active interests, recheck current recipient visibility, and query later changes through existing owners. Map the smallest compatible storage/allocation and acceptance integration; do not scan or summarize all project results each turn. |
| N4. Compose at a normal boundary | Attach a bounded notice through a defined response/turn hook without replacing the requested tool result, inventing a tool call, corrupting provider call/result pairing, or scheduling an extra model exchange. Integrate the total context/result allowance with P1-F09. Exact notice placement remains an open wire-contract decision. |
| N5. Separate delivery and consumption | Apply R56-R61: bind final included notices to the actual request/attempt, acknowledge after a valid durably recorded response, and recover or repeat only at normal interactions when uncertain. Retrieval is separate. Map the exact records to P1-F08 and continuation to P1-F04. |
| N6. Test isolation and optionality | Verify subject/work isolation, accepted-versus-private results, late visibility changes, no per-turn duplicate alerts, coalescing, exact-ID fetch, unchanged listing selection, and zero notice-only model calls or review tasks. Mark tests depending on unsettled delivery/restart contracts as blocked rather than inventing those contracts. |

Keep this a small host capability integrated with existing retrieval and execution.
No separate manager model, messaging service, notification worker, full query-result
copy or new knowledge store is authorized. R44-R48 now require durable, work-scoped interests; section 6.5 describes their
implementation boundary. R49-R55 and section 6.6 add the approved notification
marker and registration ordering. Exact storage/allocation, subject-to-file
aggregation, lifecycle/retention limits and the concrete delivery-record mapping
still require discussion. The acknowledgment behavior is approved in R56-R61. Do not describe the complete notice subsystem as
restart-safe until its remaining contracts are specified and tested.

### 6.5 Durable interests: approved implementation direction

Map these steps to the refactored owners before changing code. The sequence gives
the approved mechanism and its boundaries, not permission to invent the remaining
publication, receipt, retention or schema choices.

| Step | Required developer action and verification |
|---|---|
| I1. Resolve work ownership | Identify the durable task/inquiry identity and how successive attempts refer to the same logical work. Reuse the current task identity where sufficient. Document any continuation that changes tasks and obtain agreement on that mapping; never key interests by worker slot. |
| I2. Map minimal durable state | Inspect existing host persistence and its transaction owner. Model the review/work, subject, normalized filters, initial/observed availability and advertised-progress meanings without copying documents. Choose the smallest compatible extension; exact schema, normalization, migration and retention are not selected here. |
| I3. Integrate successful lookup registration | Implement R51-R53: observe listing and H consistently, end the read, then durably register/reuse the interest without replacing H or erasing pending progress. Do not require a checkpoint or subscribe call. Specify the exact failure/replay outcome with P1-F07/P1-F08 before enabling the final protocol. |
| I4. Restore at normal continuation | Load the same work's interests for an authorized replacement attempt through existing continuation/runtime hooks. Recheck visibility before notices. Preserve waiting/retryable work; stop active advertising only under the logical-work closure authority. |
| I5. Keep progress meanings separate | Coalesce pending information with the existing normal-turn notice hook. Do not equate queued/composed notice, delivered notice, retrieved result or source inspection. Do not suppress unseen lower-position updates merely because a later result was fetched. R56-R61 select acknowledgment behavior; exact P1-F08 receipt/storage integration remains open. |
| I6. Verify lifecycle and races | Add deterministic cases T62-T69 and T70-T79 at existing query/state/runtime seams. The notification marker and two-transaction direction are now agreed; map them to actual storage/acceptance owners. Simulate replacement/interleavings with disposable state, not live model calls. R56-R61 and T80-T88 now define delivery expectations; bind their concrete fixtures to the runner records before implementation. |

The persistent state change is intentional host bookkeeping even though the
analysis content is retrieved read-only. It does not create review work, grant
result acceptance, change canonical coverage, or reopen a completed inquiry.

### 6.6 Availability sequence and race-safe registration

This sequence applies the approved R49-R55 mechanism. It does not import the older
proposal's scheduling modes or prescribe new schema tables. Use the refactored
owners once their actual contracts have been verified.

| Step | Required developer action and verification |
|---|---|
| V1. Map ordered availability | Inspect existing committed publication/event order, subject associations and acceptance predicates. Determine whether they distinguish actual usability from provisional creation and can be queried by review/subject/sequence. Identify any missing storage/indexing; propose only the necessary extension. |
| V2. Connect the acceptance owner | Record each relevant availability transition using its real accepted-result identity after required receipts permit use, independently of active listeners. Keep the marker coherent with the owner's transition and retry semantics. Verify no pending transaction or late lower sequence can hide an event behind an exposed H. Do not claim cross-database atomicity. |
| V3. Compose the consistent read | Within one short read view obtain H and the authorized bounded listing. Carry H as host metadata through response preparation. Close the transaction before the separate write; no provider call, target-source scan or long-held read snapshot belongs inside it. |
| V4. Commit interest registration | Recheck work/attempt authority, create an absent interest at the original H or reuse the equivalent record, and preserve pending delivery state. Handle competing registrations through the owning transaction/uniqueness authority. Persistence failure must not become complete lookup success. Map original-operation replay to P1-F08. |
| V5. Query changes without acknowledging them | At the normal interaction hook, retrieve bounded later changes for the work's subjects/filters and apply current visibility. Keep detected changes separate from advertised/retrieved progress. Do not advance delivery state merely because a query or response composition succeeded. Use the R56-R61 acknowledgment condition; final record and adapter mapping remain prerequisites for implementation. |
| V6. Verify the interleavings | Test publication before, during and after the lookup read and before/after interest commit, including no prior listener, concurrent publishers, rollback, equivalent-query replay, delayed usability, changed permissions and failed registration. Assert listing-or-notice eligibility without claiming optional summaries were read. |

Illustrative host processing, not final signatures or executable SQL:

```text
validate current lookup authority and query
with short consistent read view:
    H = committed availability position for this review
    page = authorized bounded result listing from that same view
close read view

with separate short write transaction:
    recheck current work and attempt authority
    create interest at H if absent, otherwise preserve equivalent interest progress
commit registration

return page under the tool-result delivery contract
# Merely composing this response does not acknowledge a notice or prove delivery.

at next normal interaction:
    look up relevant later availability changes for the work's interests
    filter by current visibility and response bounds
    offer notice through the separately specified delivery path
```

H is not reused as a universal 'read through' value. Do not reset an existing
interest to H as a shortcut, make all later listing pages frozen by implication,
or require a live listener at publication time. Sequence schema and allocation,
empty-history initialization, historical bootstrap and multi-step acceptance
reconciliation require explicit implementation mapping. No application code or
migration is supplied by this document.

### 6.7 Notice acknowledgment: approved implementation sequence

| Step | Required developer action and verification |
|---|---|
| Acknowledge-1. Locate real exchange boundaries | Trace final context selection, dispatch, valid-response normalization and durable response recording. Identify existing attempt/request IDs and source-free lifecycle records. Document the supported outcome predicate; do not treat 'response prepared' or any partial stream as completed delivery. |
| Acknowledge-2. Bind final inclusion | After budgeting, associate only actually included notice identities and represented changes with the outgoing work/attempt/request. Establish recoverability before dispatch without holding a transaction during inference. Excluded notices remain pending. No new body or transcript copy. |
| Acknowledge-3. Settle the exact outcome | After the associated valid response is durably recorded, acknowledge that request's notices through the existing state owner. Replays return the existing outcome. Never read the latest availability counter and use it as a replacement for the request's included set. |
| Acknowledge-4. Recover or replay | Recover a missing acknowledgment from the recorded response and inclusion association. Without conclusive response evidence, permit a bounded repeat at a later normal interaction after visibility checks. Do not create work or an extra provider call for delivery alone. |
| Acknowledge-5. Verify ownership and failures | Test omitted notices, later publications, late prior-attempt responses, double settlement, revoked visibility, interrupted streams and optional transcript capture disabled. Verify no inherited read credit and no writes to another attempt's unrelated state. |

Illustrative sequence, not a new tool schema or mandatory module layout:

```text
pending = eligible notices for this logical work under current visibility
request = ordinary request after final context selection and response budgeting
included = exact pending notices present in request
record recoverable association(included, work, attempt, request)
perform ordinary model exchange without a database transaction held

if the associated valid response is durably recorded:
    idempotently acknowledge exactly included
else:
    keep uncertain/pending; reconcile before later normal presentation
```

No current record name or transport outcome is assumed. Any necessary persistence
extension must be minimal and integrated with the existing runtime owner. Test
the actual model-bound payload and durable linkage, not only a notice composer.

### 6.8 H-bounded analysis listing: implementation sequence

Use the R51 read-view boundary already needed for gap-free interest registration.
This is a feature extension, not a second publication or notification mechanism.

| Step | Developer action | Verification before proceeding |
|---|---|---|
| Q1. Map stable result positions | Identify accepted result identities, subject associations, committed availability records and current visibility/status predicates. Reuse their owners. Propose the concrete immutable ordering tuple, tie-breaker and direction; resolve repeat availability/multiple associations rather than infer a new lifecycle. | Later publications cannot move an earlier entry's listing position; one result is not accidentally multiplied by association joins. Unsettled transition semantics remain an explicit blocker. |
| Q2. Compose the initial bounded query | In the existing short consistent read, obtain H and query eligible results within H, with authorization and filters applied before bounded output. Return existing result references and the last returned ordering position. Register interest using the original H as already specified. | The first page and H agree. Partial pages do not claim unique/exhaustive matches or mark all results through H consumed. |
| Q3. Validate and continue | Resolve a typed analysis-list cursor, check review/snapshot and query identity, preserve H, and query after its stable position using the same ordering. Apply current acceptance/visibility and response limits. Reuse compatible index/query and authentication utilities; do not use mutable-list offsets. | A new publication between pages never enters/rearranges the old traversal; a foreign query/source cursor cannot be silently accepted. |
| Q4. Integrate refresh and exact retrieval | Leave old cursors valid under their own checks when an explicit new lookup observes a new H or an advertised result is fetched by ID. Reuse equivalent interests without discarding pending updates. | Old continuation, fresh lookup and exact-result read can be interleaved independently. None acknowledges unrelated notices or transfers read credit. |
| Q5. Handle shrinking eligibility honestly | Recheck current status/permissions for each page and detail fetch. Use a short read per page; report actual exhaustion within H separately from partial evaluation or the existence of later publications. | Removing access or superseding an entry cannot leak it or label it current; limits cannot be misreported as no more results. |
| Q6. Integrate and test the boundaries | Exercise T49 and T89-T96 through actual query/broker/result consumers, not only cursor decoding. Verify request-schema and SDK/receipt compatibility before enabling changed semantics. | Same result IDs and owning acceptance gates are reused; no per-agent list snapshots, new notification workers, schema guessing or provider calls solely for paging. |

Processing outline (not final SQL or a wire schema):

```text
Initial lookup:
    within one short consistent read:
        observe committed boundary H
        query currently permitted matching result positions within H
        return a bounded page and its last returned position
    durably register/reuse the interest using that original H

Continuation:
    validate current attempt and the typed query-bound cursor
    within a short read:
        query currently eligible result positions after the saved position,
        within the unchanged H and original subject/filters/order
    return the actual page, completeness and next continuation where applicable

Fresh lookup or exact-result fetch:
    execute independently; do not mutate an older cursor or notice acknowledgment
```

The storage of availability positions, filtering of repeated transitions, direction
of ordering, maximum page bounds, cursor bytes and exact failure statuses remain
implementation prerequisites to resolve. Existing result-detail pagination, source
pagination and notice-delivery receipts retain their separate contracts.

### 6.9 Direct-relationship queries: approved implementation direction

Implement R68-R75 through the existing relationship-query owner. Historical
navigation pointers are `indexing.py`, `symbol_graph.py` and the broker query
handlers at the previously inspected harness baseline; locate their actual owners
in the delivered refactor. The same-file resolver's outcomes must not be assumed
to exist for every canonical relationship or every language.

| Step | Required developer action and verification |
|---|---|
| G1. Map existing records and associations | Inspect canonical relationship fields, occurrence/callsite representation, resolver outputs, subject associations, provenance/visibility owners, indexes and callers. Record which relationship kinds and resolutions are actually available. Verify any cross-record join by durable identity; do not infer bindings from names. |
| G2. Specify the local query contract before wiring it | Define subject selection, supported kind filters, direction values, per-kind result shapes, absent resolution metadata, restricted targets, self-edge/both-direction behavior and paging. Discuss remaining choices rather than treating them as approved defaults. Do not add a second graph store or new general resolver. |
| G3. Implement directional selection | Resolve the subject in the current snapshot. Select outgoing records by originating subject and incoming calls by resolved target; preserve edge direction. Include authorized unresolved outgoing records and keep possible targets separate from resolved incoming edges. Apply existing authorization/visibility at the query/projection boundary before releasing page contents. |
| G4. Compose bounded provenance and callsite metadata | Return existing IDs, actual recorded resolution/basis, authorized endpoints or locators, callsite references and permitted evidence/provenance. Preserve distinct occurrences. Use the source reader only when explicitly requested through that tool; do not load bodies or generate summaries inside this lookup. |
| G5. Integrate completeness and tool exposure | Use the agreed common error/result conventions and eventual relationship pagination contract. Do not silently drop unresolved edges, treat one returned page as complete, or reuse source/list cursor semantics without their own relationship contract. Check role exposure, provider-visible definitions and execution-receipt/schema compatibility through their existing owners. |
| G6. Verify read-only behavior across the boundary | Test directional results, ambiguous/unresolved outcomes, repeated callsites, self-calls, protected targets, stale attempts, missing metadata and bounded results. Assert that retrieval changes no canonical relationship, candidate, task dependency or coverage state; ordinary read audit remains allowed. Check existing navigation and scheduler regressions separately. |

The intended flow is:

```text
Validate current attempt and supported query inputs.
Resolve the existing subject ID in its bound snapshot.
Query direct records through the existing directional relationship owner.
Attach only recorded, correctly associated resolution/provenance information.
Apply visibility and bounded output/continuation behavior.
Return attributable metadata, source references and honest limitations.
```

This sequence is implementation guidance, not a new wire schema. It neither
requires one service per step nor a mandatory folder layout. A focused extension
and small query/projection helpers are sufficient where the refactor provides the
needed components. Any missing persisted association or index must be demonstrated
against the actual code before proposing a schema change. A model call, second
graph database, background resolver, automatic dependency scheduler and per-worker
copy of the graph are outside this approved retrieval feature.

### 6.10 File catalogue: approved implementation direction

Implement R76-R83 by extending the existing manifest/catalogue and inventory-query
owners. The historical `read_verified_file()` path in `source.py` reads recorded
path, hash, size, classification and available inventory metadata from
`snapshot_files` and `file_inventories`; it is a reuse pointer, not a requirement to
call the source reader or read source bytes during file discovery. Verify the
actual refactored owners and file-reference integration before coding.

| Step | Required developer action and verification |
|---|---|
| F1. Map existing catalogue ownership | Locate manifest records, file-reference factories, metadata visibility/classification rules, inventory projections, query indexes and consumers. Identify how the discovered reference is resolved by symbol, source and analysis tools. Do not invent another file identity or assume every existing reference type has interchangeable semantics. |
| F2. Specify the two selection forms | Define directory browsing and exact filename/relative-path lookup, optional directory/language/classification restrictions, explicit descendant search and conflicting-input errors. Set root, case/normalization, ordering and cursor fields through the remaining design discussion, not developer defaults. Keep selection request-local. |
| F3. Build bounded directory projection | Restrict records to the execution-bound snapshot and permitted metadata before grouping. Derive visible immediate children using proper directory-component boundaries, deduplicate child directories before paging, and avoid retrieving the entire manifest into each worker. Reuse/extend the owning query infrastructure. |
| F4. Build filtered file discovery | Apply every supported filter without silent broadening. Return distinguishable existing file references and recorded metadata, with honest parse/unsupported/missing-inventory information. Do not read source, compute new analytical summaries, infer safety, or treat file lookup as a coverage action. |
| F5. Integrate reference and outcome paths | Verify that a discovered context-only file can be read without a symbol ID when the source policy permits it. Ensure explicit source reads recheck access/integrity and analysis lookups, not browsing, register freshness interests. Keep page selection stable and use the common bounded outcome/accounting owners. |
| F6. Exercise behavior and regressions | Test immediate-child and descendant behavior, duplicate names, component-prefix collisions, hidden metadata, missing/failed inventory, independent worker queries, page deduplication and stale/foreign selections. Inspect side effects: no target filesystem scan, source-read credit, implicit task/lead/interest creation, or coverage completion. |

Approved processing sequence, not a finalized tool schema:

```text
Catalogue request with an explicit directory or file query
    validate the current attempt and supported arguments
    take the snapshot from the execution context
    constrain existing manifest/inventory records by query and metadata visibility
    for directory browsing, derive and deduplicate immediate children
    return a deterministic bounded page of recorded metadata and existing references
    include limitations and a query-bound continuation where applicable

Later explicit operation on a discovered file reference
    use the existing symbol, source or analysis owner
    revalidate its own access and result rules
    never treat catalogue discovery as content delivery or coverage
```

For the approved illustrative manifest `src/api/routes.py`,
`src/api/auth/permissions.py` and `src/api/auth/session.py`, browsing `src/api/`
returns the visible `routes.py` file and one `auth/` directory entry, not three
recursive file bodies. This is a test example, not a prescribed response encoding.
A directory entry may be derived only from metadata the recipient can discover.

No new persistence is required solely to remember an agent's current directory.
Keep ordinary tool audit and resource accounting, but do not add another source
store, per-worker manifest copy, filesystem-access service, or model-based file
finder. Exact metadata/result fields, limits and continuation details remain
prerequisites for a final executable interface.

### 6.11 Source-text search: approved implementation direction

Implement R84-R90 through the refactored equivalents of the existing search handler,
manifest selection, source verifier, matcher and response/accounting boundaries.
Replace the current line-by-line matching assumption with R91-R95. Final matcher
dialect/flags and remaining continuation decisions must precede enabling this
capability. Apply R96-R101 occurrence/progress rules rather than infer them from
response-page boundaries.

| Step | Required developer action and verification |
|---|---|
| S1. Map current search owners | Inspect `_source_search` or its refactored equivalent, selector validation, catalogue policy, decoding/byte-coordinate helpers, result limits and model-visible error projection. Record current dependencies and which tests assert the old per-line/prefix behavior. |
| S2. Finalize matcher and selectors | Specify literal/explicit-regex modes, case semantics, supported regex dialect, compile/input/output bounds, file/directory/snapshot selectors and valid combinations. Confirm the chosen engine and dependency approval. Apply R91-R95 per-file/cross-line semantics; exact newline/anchor flags and search continuation remain open. |
| S3. Resolve and verify scope | Reuse manifest-backed selection and current attempt/research checks. Read only verified permitted snapshot content, keep supplied filters, and account for actual scan progress and decoding limitations. Avoid copying the whole manifest into every worker. |
| S4. Produce precise navigation hits | Obtain exact occurrence coordinates in original bytes and build bounded match-centered previews. Associate a containing symbol only through an unambiguous inventory relation. Keep match and preview ranges separate and make truncation explicit. |
| S5. Integrate limits and outcomes | Distinguish full scan, filled result page, interrupted scan, decoding omission and authorization/integrity failure. Preserve P1-F07 actionable outcomes and P1-F09 aggregate limits. Credit only delivered preview intervals; search scanning is not source-read coverage. |
| S6. Verify before enabling | Run literal punctuation/case, regex alternatives/unsupported syntax, scope filtering, long-line previews, repeated occurrences, encoding failure, exact byte/hash and resource-stop scenarios. Verify no fallback engine, model call, task creation, target execution or automatic analysis interest. Full search traversal tests depend on the remaining continuation contract. |

The implementation flow to preserve is:

```text
explicit source-search request
    validate current execution and supported query/mode/scope
    resolve selection from the existing authorized snapshot catalogue
    obtain verified content and explicit decoding status
    apply the agreed bounded literal/regex matcher
    return exact occurrences and match-centered bounded preview source
    report actual scan/output completeness, omissions and supported continuation
    record ordinary host cost plus only source actually delivered to the attempt
```

No new persistent search job, stored full result set, per-page row or streaming
matcher state is selected here. Any such addition requires a demonstrated need
and an agreed contract. The developer must not label the feature ready while
exact matcher flags, case-to-byte mapping or remaining search pagination
consistency is undefined. Cross-line behavior is specified by R91-R95; occurrence
ordering, non-overlap and complete-match-based progress are specified by R96-R101.

### 6.12 Per-file cross-line search: approved implementation guidance

Extend section 6.11; do not add another source-search service. The following steps
implement R91-R95 only. Concrete internal helper names remain developer discretion
within the agreed owners; matcher flags and continuation semantics do not.

| Step | Required developer action and verification |
|---|---|
| M1. Trace matching and formatting separately | Locate the refactored file verifier, decoder, matcher and preview formatter. Identify any per-line or response-page slicing that currently changes the matcher's input. Preserve original-byte coordinate conversion. |
| M2. Establish the per-file input boundary | Supply one verified file's supported text as the matching input. Accept explicit newline-containing literals and supported cross-line regex queries. Never concatenate files or silently normalize newlines; finalize the dialect/flag contract before enabling it. |
| M3. Separate complete matches from output | Obtain the full occurrence range independently of preview clipping. Build bounded previews afterward, with explicit partial status; do not use preview length as matching progress or a search-cursor offset. |
| M4. Enforce honest processing limits | Process one file at a time within approved limits. When the supported strategy cannot process an input, report that limitation rather than substituting line-by-line semantics. Do not build custom streaming infrastructure as an incidental optimization. |
| M5. Compare presentation-independent outcomes | Specify tests below against the eventual matcher. Compare complete occurrence ranges across different response sizes and any actual processing boundaries. Treat continuation-dependent assertions as blocked until the search-continuation contract is agreed, not as passing tests. |

### 6.13 Occurrence enumeration: approved implementation guidance

Implement R96-R101 within the existing/refactored search handler, selected bounded
matcher and preview/accounting components. Do not create an occurrence service,
second index or persistent result set just to paginate textual matches.

| Step | Required developer action and verification |
|---|---|
| E1. Map the matcher contract | Verify how the selected bounded matcher enumerates matches over original per-file input, reports spans and supports a start position. Record anchor, boundary, alternative-selection and text/byte-index semantics. Unsettled dialect and encoding behavior remain blockers, not inferred defaults. |
| E2. Enumerate explicit occurrences | Produce one record per non-empty, non-overlapping match. Preserve multiple hits on one line and distinguish full match coordinates from preview coordinates. Reject actually produced zero-length matches with the R101 outcome instead of inventing an advancement rule. |
| E3. Establish deterministic order | Traverse the authorized manifest using its canonical relative paths and the final documented comparator, then emit matches in original start/end-byte order. Never rely on filesystem listing order, asynchronous completion order or a relevance score. |
| E4. Separate progress from formatting | Track complete-match boundaries independently of preview windows. Use the complete returned match end for subsequent matching. When a candidate hit cannot fit, retain it for the next response or report the explicit representability limitation; do not advertise a position beyond an omitted hit. Exact cursor fields stay open. |
| E5. Preserve original context and accounting | Resume matching against the original verified file with the agreed positioned semantics; do not change file-boundary or word/line-boundary behavior by slicing. Preserve current authority, scan limits, actual delivered-source accounting and P1-F08 response-recovery requirements. Replay cannot reset budgets or claim unreturned preview/source was read. |
| E6. Verify end-to-end enumeration | Compare full occurrence identities across different preview and result allowances after complete traversal is available. Include multiple same-line matches, overlap exclusion, empty matches, anchored continuation and a next hit omitted by the response bound. Keep cursor-dependent tests pending until its contract is finalized. |

Illustrative processing outline, not a final tool signature or cursor schema:

```text
resolve the authorized query and original file input
    obtain the next occurrence under the declared matcher/occurrence policy
    if the occurrence is empty: return the explicit incomplete/error outcome
    map the complete match to original-byte coordinates
    prepare its bounded, separately identified preview
    if it cannot be represented: preserve that hit or report the limitation
    otherwise return the hit and account only for delivered preview source
    resume subsequent matching at/after the complete match end in original context
```

Do not equate internal scanning progress, formatter lookahead, agent-visible
continuation, and source delivered to the model. The full cursor and interruption
protocol must define their relationship without losing an unreturned occurrence.
This amendment does not prescribe per-hit storage, a new matching engine or new
numeric limits.

## 7. Acceptance scenarios derived from approved behavior

These are expected tests, not tests run during this documentation save. Map them
to the refactored test suite before implementation; use the approved local test
setup and do not activate paid/live model work implicitly.

| Test | Fixture / action | Expected result |
|---|---|---|
| P1-F02-T01 | Retrieve metadata for a known function. | `symbol_get` returns indexed metadata without implicitly returning function source. |
| P1-F02-T02 | Read a known function directly by symbol ID. | No preceding metadata lookup is required; returned source is from the exact indexed full range, or its first clearly partial page. |
| P1-F02-T03 | Read that same range by explicit file ID and lines. | Both modes use the same verifier/authorization; compare byte identity where selections coincide. |
| P1-F02-T04 | Supply conflicting symbol and file selectors. | Reject the conflict; do not choose either selector or read unrelated source. |
| P1-F02-T05 | Select an unknown or foreign-snapshot symbol. | Fail with the relevant safe error; no name-match/latest-revision fallback. |
| P1-F02-T06 | Read an authorized helper outside the assignment. | Source is readable under P1-F01; assignment and coverage ownership remain unchanged. |
| P1-F02-T07 | Select a symbol larger than one response. | Return bounded pages with explicit partial status and continuation; concatenated returned source matches the selected bytes without accidental gaps or range escape. |
| P1-F02-T08 | Request an oversized but valid explicit file range. | Same page behavior; source size alone is not an unexplained invalid-range failure. |
| P1-F02-T09 | Page source containing long lines and multibyte characters. | Prefer full lines; mark necessary partial lines; preserve valid character boundaries and original byte/hash identities for supported encoding cases. |
| P1-F02-T10 | Obtain a cursor, then expire or supersede the attempt. | Continuation cannot bypass current execution checks. |
| P1-F02-T11 | Continue with an invalid/unsupported cursor or changed snapshot bytes. | Reject the appropriate problem without silently restarting or changing selection. |
| P1-F02-T12 | Deliver only the first page; separately test last-page access without earlier delivery. | Neither is incorrectly counted as a full-symbol read. |
| P1-F02-T13 | Stop after one page and perform another lookup. | No automatic background pagination or hidden model-context expansion occurs. |
| P1-F02-T14 | Make paginated reads near configured cumulative limits. | Pagination preserves source/result/context and combined-response limits; continuation does not grant new budget. |
| P1-F02-T15 | Continue a saved cursor from a fresh independently authorized attempt in the same review, with the eventual key contract satisfied. | Continue the exact selection without the original broker's in-memory position map or a per-page cursor row. Only the new page is credited to the new attempt. |
| P1-F02-T16 | Use that cursor in a different review sharing the same immutable snapshot. | Reject review mismatch; do not silently rebind the cursor or disclose the other review's context. |
| P1-F02-T17 | Replay a cursor sequentially and concurrently with unchanged allowances. | Each call begins at the same position and returns the same selected source page; no shared pointer advances and no caller skips bytes because another used the cursor. |
| P1-F02-T18 | Replay a cursor under a tighter permitted response allowance. | Preserve its starting position and original selection; return a smaller valid page where feasible and derive continuation from the actual end. Genuine insufficient capacity is reported explicitly. |
| P1-F02-T19 | Alter cursor-bound review, snapshot, file, hash, selection, position or symbol metadata without valid host integrity protection. | Reject before serving source; never accept the modified position or reconstruct a convenient replacement. |
| P1-F02-T20 | A valid same-review cursor is presented by an attempt that lacks current permission for its source. | Current authorization denies access despite valid cursor integrity. |
| P1-F02-T21 | Restart the host/worker and reload the established project-local secret, then present an otherwise valid saved cursor. | Continue the same review/source selection; do not generate a new secret, depend on the original worker's memory, or transfer read credit. Validate against the eventual agreed key-file/provisioning implementation. |
| P1-F02-T22 | Authenticate a cursor, then modify each independently bound metadata field without producing a valid new tag. | HMAC verification rejects the change before serving source. Test the full payload, not only its offset; a syntactically valid altered selection is still invalid. |
| P1-F02-T23 | Run worker A's continuation on file X alongside worker B's continuation on file Y using the same project secret; also interleave two cursors in one worker. | Every response uses its own selection/position and returns its own new cursor. Read accounting remains attempt-owned; no global offset or mutable cursor pointer is involved. |
| P1-F02-T24 | Exercise concurrent first-initialization callers and subsequent worker loads in isolated project data. | The serialized host path establishes one secret without competing overwrites. All loads use that established secret; ordinary reads cannot reinitialize it. |
| P1-F02-T25 | Remove, make unavailable, or replace the secret in a disposable test project, then submit an old cursor. | Missing/unreadable secret or failed authentication is explicit. No source is served from unverified fields; no automatic secret replacement or old-cursor rebinding occurs. |
| P1-F02-T26 | Use a known fixture secret and inspect returned cursors, model-bound messages/configuration, ordinary state/logs/errors, transcripts and normal exports. | The secret remains only in its authorized host storage/memory. Authentication tags may appear in cursors, but the secret itself must not leak; source/inference fixture data does not become a production secret. |
| P1-F02-T27 | After an explicitly simulated host key repair, request source afresh by a permitted symbol/file reference. | A new ordinary read can return source and a new cursor without pretending the old cursor recovered. Current authorization and source integrity still apply. |
| P1-F02-T28 | List a permitted file's symbols without supplying a name. | Existing file-scoped listing remains supported, with indexed IDs, bounded results and no automatic source bodies. |
| P1-F02-T29 | Search an exact local name shared by declarations in several files/classes. | Return distinguishable alternatives with existing IDs and completeness information; no guessed winner or new identities. |
| P1-F02-T30 | Search an exact qualified name with and without a file restriction. | Apply the supplied restrictions to the existing inventory. A qualified spelling is not assumed globally unique where multiple indexed declarations match. |
| P1-F02-T31 | Combine an exact name with file, containing-symbol and kind restrictions using the eventually agreed combinations. | Results satisfy every supplied restriction; no restriction is silently removed to manufacture a match. Verify containing-symbol semantics against the agreed final contract. |
| P1-F02-T32 | Request an exact name absent from the queried index while similar names and inventory gaps exist. | No fuzzy/latest-snapshot fallback. Report no indexed matches and relevant limitations without claiming the behavior does not exist anywhere in source. |
| P1-F02-T33 | Use a page allowance of one with two or more eligible matching declarations. | Return one item with more-results information; never label this a unique complete match. Verify traversal across the agreed stable page order. |
| P1-F02-T34 | Return one complete declaration match for a spelling used by an unresolved callsite. | Report declaration match completeness only; relationship resolution and candidate/coverage state remain unchanged. |
| P1-F02-T35 | Query permitted symbols outside the assignment, with inaccessible or foreign-snapshot subjects interleaved in storage order. | Broader research lookup succeeds only within the permitted snapshot. Authorization constrains pagination; no inaccessible identities/source leak and no assignment/coverage ownership change. |
| P1-F02-T36 | Use an existing symbol ID with `symbol_get` and then `source_read` without a preceding name search. | Direct retrieval works through the existing ID paths; `symbol_get` stays metadata-only and source is returned only by the explicit read. |
| P1-F02-T37 | Execute repeated exact lookups in a project whose inventory exceeds the context-item budget. | Bounded inventory queries do not require a full per-worker symbol catalogue. No new symbol, relationship, lead, task, or coverage rows are created; ordinary audit/accounting may still occur. |
| P1-F02-T38 | Query available analysis for a known symbol or file with one permitted recorded result. | Return compact existing identities, covered subjects, recorded summary, producer/source identity and limitations without loading the full result or source automatically. |
| P1-F02-T39 | Run discovery where an available artifact has no recorded summary. | Do not create prose or invoke a model to fill it; represent absent summary information under the agreed final schema. |
| P1-F02-T40 | Discover D18, then make D19 available before requesting D18's details. | Return D18 where still authorized; never substitute D19 or silently merge the results. |
| P1-F02-T41 | Discover a result, then make it unavailable under the owning visibility policy before detail retrieval. | Recheck access and return the explicit safe outcome; exact selection does not override policy or permit a latest-result fallback. |
| P1-F02-T42 | Store several permitted analyses for one subject with different assumptions or questions. | Return distinct records/provenance and only recorded relations. Do not choose an authoritative winner or manufacture a merged conclusion. |
| P1-F02-T43 | Query a subject without a usable result, with no matching review, queued review, running review, and failed review in separate fixtures. | Distinguish each analysis/work-availability combination and permitted work references; no empty-success safety conclusion. |
| P1-F02-T44 | Mark a review task complete while its required result acceptance is pending. | Result detail remains subject to its real acceptance gate; report pending availability instead of trusting task status. No private provisional content leaks. |
| P1-F02-T45 | Keep usable prior analysis while supplementary review is queued, running, or failed. | Expose the usable analysis and separately report outstanding/failed work; do not hide the result solely due to that work. |
| P1-F02-T46 | Request foreign-snapshot, unauthorized, or private analysis, and repeat a permitted request with a stale attempt. | Reject according to current identity/visibility rules without returning protected content or treating project-wide source access as publication permission. |
| P1-F02-T47 | Retrieve a large permitted result and consume a bounded detail page. | Identify the exact result and actual content returned with explicit completeness/continuation. Do not credit this as source inspection or automatically load the rest. Final detail-page contract remains a prerequisite for execution of this test. |
| P1-F02-T48 | Repeat discovery/detail reads while a relevant reviewer is still working. | Reads complete without waiting for that reviewer, auto-polling, task creation, lead registration or domain acceptance writes. Ordinary read audit/accounting remains allowed. |
| P1-F02-T49 | Add results or change acceptance between discovery pages. | Follow R62-R67: retain the initial H and stable continuation position, exclude later availability, and recheck current visibility/status. New-result notices and explicit refresh remain independent. Concrete execution still requires the agreed query/schema mapping. |

| P1-F02-T50 | Work A queries analysis for S42, then an associated consumable result D20 appears. | A receives a bounded availability notice at its next ordinary interaction without a separate subscribe request. |
| P1-F02-T51 | After the lookup, A next requests source from an unrelated function rather than querying analysis again. | The normal source response/turn can carry the S42 notice; no polling lookup is required and source contents remain unchanged. |
| P1-F02-T52 | Publish D20 during an in-flight model response, or while A is inactive. | No interruption, additional model call, new task, or automatic reopening occurs. The notice is eligible at the next normal interaction/resumption under the agreed work lifecycle. |
| P1-F02-T53 | Worker slot W moves from work A to unrelated work B; another slot continues A under its authorized continuation. | Interests are keyed to logical work, not W. B inherits no A notices. Same-work durable restoration is required by R44-R46; exact continuation mapping and delivery assertions remain dependent on their final contracts. |
| P1-F02-T54 | Publish a result for an untracked subject and a private/pending-acceptance result for S42. | Neither creates a misleading new-available-result notice for A. No restricted record metadata leaks. |
| P1-F02-T55 | D20 was eligible when detected but is no longer visible at delivery or fetch. | Apply current visibility and owning availability rules; do not disclose restricted content or substitute a different result. |
| P1-F02-T56 | Advertise D20 while A holds a cursor and has selected D18. | Neither selection nor cursor is silently replaced or reset. A may fetch D20 directly, refresh, or continue without retrieving it. The exact listing-membership behavior remains governed by the still-open pagination contract. |
| P1-F02-T57 | A ignores an advertised update across several normal turns. | No identical repeated notice solely because D20 remains unread. A later relevant update can generate another/coalesced notice. |
| P1-F02-T58 | Several relevant results arrive before the next ordinary interaction. | Coalesce under the agreed response allowance; identify non-exhaustive information and preserve exact authorized result identities. Numerical limits and omission representation remain open. |
| P1-F02-T59 | A receives a notice but never fetches its result. | Do not record result consumption, new source-read intervals, coverage, or a satisfied analytical requirement. |
| P1-F02-T60 | An accepted update makes a bound required input stale, and A ignores the notice. | Owning stale-input/submission checks still apply. Optional refresh is not an override or a finding-validity policy. |
| P1-F02-T61 | Publication races the first lookup, or notice response delivery fails. | The race portion now follows R49-R55 and T70-T79: preserve eligibility after the observed H. Notice-delivery failure follows R56-R61 and T80-T88; detection alone cannot establish advertised or consumed state. Concrete record/outcome mapping remains to be verified. |
| P1-F02-T62 | Successfully query S42, stop the process before any agent checkpoint, publish a newly consumable result, and resume the same logical work in a replacement attempt. | Durable interest is restored and the update remains eligible for notice at a normal interaction, subject to current visibility. No repeat subscribe request or worker-local state is required. |
| P1-F02-T63 | Repeat equivalent lookups from the same logical work, including a replacement attempt. | One equivalent interest is reused; no duplicate listeners or per-turn duplicate alerts. The final filter-normalization and observation rules must not discard unadvertised updates. |
| P1-F02-T64 | Query the same subject under different work owners and materially different filters. Reassign a used worker slot to unrelated work. | Ownership/filter isolation is preserved. The unrelated work inherits no prior interests; no implicit cross-work merge occurs. |
| P1-F02-T65 | Compare attempt failure followed by authorized continuation, temporary waiting, logical-work completion and logical-work cancellation. | Continuable/waiting work retains its interests; logically completed/cancelled work receives no further advertising or automatic reopening. Map assertions to real lifecycle states rather than inferring closure from an attempt alone. |
| P1-F02-T66 | Interleave accepted availability with the listing read and durable interest registration. | Apply R51-R52's consistent read plus original-H write sequence. A later publication remains eligible after H even when committed before registration; refine executable fixtures against the actual storage/acceptance mapping. Notice acknowledgment remains separate. |
| P1-F02-T67 | Retrieve D22 directly while D20/D21 were not retrieved; also construct a notice whose delivery is interrupted. | Retrieval/advertising/source-read meanings remain separate; D22 does not mark earlier results read, and a constructed response is not proof of delivery. Use R56-R61/T80-T88 for acknowledgment and replay behavior; map fixtures to the actual durable runtime records. |
| P1-F02-T68 | Inspect durable interest state and normal resume behavior using disposable fixtures. | State contains only allowed ownership/query/progress metadata, not source, result bodies, conversations or a per-agent publication-history copy. No notification worker, extra model call, review task or coverage write is created. |
| P1-F02-T69 | Inject interest persistence failure or an uncertain outcome during lookup completion. | The tool must not falsely report durable registration. Reconciliation/retry follows the eventual P1-F07/P1-F08 contract without duplicate equivalent interests. Exact error and acknowledgment behavior remains to be agreed. |


| P1-F02-T70 | Publish relevant results concurrently in one review and inspect committed availability positions, including a transaction that rolls back. | Committed ordering is unambiguous; sequence gaps are harmless. No phantom availability from rollback, and no later-visible transition falls behind a previously exposed H. Test the actual chosen allocation mechanism. |
| P1-F02-T71 | Create a private result before H, then complete its required acceptance after H. | Creation produces no premature consumable notice; the actual usability transition receives a later availability position, retaining the owning receipt/visibility gates. |
| P1-F02-T72 | Commit a result before the initial read view begins; use a page too small for every preexisting result. | H and the listing are consistent. Preexisting eligible results remain discoverable through the listing; an omitted page entry is not recorded as delivered/read, and H is not an all-results consumption receipt. |
| P1-F02-T73 | Hold the consistent lookup read open at H=120 while another connection commits a relevant transition at 122. | The lookup view remains coherent; registration uses 120 and the transition at 122 remains eligible for notice. End both host transactions before any model turn. |
| P1-F02-T74 | Commit a relevant transition after the lookup read closes but before a new interest is written. | Registration retains the original H rather than the latest marker. The transition is recoverable even though no interest/listener existed at publication time. |
| P1-F02-T75 | Commit a relevant transition just after interest registration; include an unrelated-subject transition between two relevant ones. | A later bounded subject/filter query can discover the relevant changes without a broadcast or body scan. The unrelated subject produces no notice; detection does not itself advance advertisement progress. |
| P1-F02-T76 | Repeat an equivalent lookup while its interest has pending changes; also run competing equivalent registrations. | Reuse one interest under the existing uniqueness/transaction authority. A newer H must not erase earlier pending changes; no duplicate listener or inherited read/consumption credit. |
| P1-F02-T77 | Replay bookkeeping for the same accepted availability transition after an interrupted acknowledgment. | Recover the same recorded transition instead of emitting a duplicate new-result event. This is operational idempotency, not semantic merging of distinct leads/results. |
| P1-F02-T78 | Detect a recorded transition, then revoke recipient visibility or make the result unavailable before composing the notice. | Recheck current authority/status; no protected result identifiers or contents leak. Availability history does not override acceptance or count as delivery. |
| P1-F02-T79 | Fail or interrupt durable interest registration after the listing read; exercise recovery of that original operation. | Do not report complete lookup-with-interest success or invent a noncommit outcome. Preserve the original observation boundary for recovery so later publications cannot be silently skipped. Exact failure/receipt assertions depend on P1-F07/P1-F08; no notice acknowledgment is inferred. |

| P1-F02-T80 | Construct N17 but omit it from the final budgeted request; separately stop before dispatch. | N17 is not acknowledged as advertised. Preparation is insufficient, and later normal delivery remains possible. |
| P1-F02-T81 | Include N17 in Q53 and durably record a valid response containing another tool call; separately make that returned call's arguments invalid. | Acknowledge N17 under the response predicate without waiting for final analysis or successful execution of the returned tool. Tool-argument errors remain separate. |
| P1-F02-T82 | Include a D20 notice in Q53, then publish D21 while Q53 runs. | Acknowledge only Q53's represented notice set; D21 remains pending. No jump to the newest sequence or implied delivery of omitted updates. |
| P1-F02-T83 | Time out or break a stream without a conclusive recorded response. | Keep delivery uncertain and permit a safe repeated notice at the next ordinary interaction. No notice-only inference, new task, lead, or result. |
| P1-F02-T84 | Record the valid response, then interrupt before acknowledgment; replay recovery twice. | Recover one idempotent acknowledgment from the durable inclusion/response association, preserving newer progress and requiring no extra inference. |
| P1-F02-T85 | Deliver a late earlier-attempt response while its successor has a different notice pending. | Settle only the original association under existing finalization authority. The successor's notice/progress is not falsely acknowledged; no new authority or read credit is granted. |
| P1-F02-T86 | Restrict result visibility before repeat delivery; separately close or cancel the logical work. | Do not disclose protected metadata and do not reopen work for an optional notice. Temporary waiting alone is not closure. |
| P1-F02-T87 | Run delivery and acknowledgment recovery with full transcript capture disabled using deterministic runner fixtures. | Source-free inclusion/outcome records suffice; no dependency on sensitive transcript bodies or another body store. Concrete assertions use the agreed actual durable-record mapping. |
| P1-F02-T88 | Receive response bytes but fail durable response recording; separately fail acknowledgment persistence. | Do not claim advertised success without the required recorded outcome. Distinguish uncertain response evidence from recoverable post-response settlement through P1-F08. No model reconstruction of unchanged notice metadata. |


| Test | Fixture / action | Expected result |
|---|---|---|
| P1-F02-T89 | Start a listing with D18-D20 within H; return a partial page, then publish D21 after H before continuation. | Continue only the original H-bounded query without duplicates/skips caused by D21's arrival; D21 is eligible for the independent notice path. Exact order uses the subsequently agreed stable direction. |
| P1-F02-T90 | Retrieve a newly advertised D21 by exact ID while the older listing remains unfinished, then continue that listing. | D21's permitted details are returned independently; the old H and saved position remain unchanged. No forced completion or refresh of the old listing. |
| P1-F02-T91 | Explicitly refresh after later availability, retaining an older continuation as well. | The fresh lookup observes a newer H and can include new eligible results. The old continuation retains its original H; neither traversal erases pending interest/notice progress. |
| P1-F02-T92 | Remove a listed result's visibility or supersede it before a subsequent page/detail request. | Current access/status rules govern. Do not expose restricted content, label a superseded result current, or substitute a newer result. A status-filtered entry may disappear. |
| P1-F02-T93 | Exhaust an H-bounded listing while later results exist; separately stop evaluation at a resource limit. | Exhaustion describes only currently eligible entries within H and the original filters. Later results can still be advertised. Resource-limited evaluation is explicitly partial, not false exhaustion. |
| P1-F02-T94 | Change a mutable relevance score/last-edit field or remove an earlier eligible entry between pages. | Continuation uses the approved stable availability-based position and existing-ID tie-breaker, not row offsets or mutable ranking. Apply current status filters without repositioning unrelated results. |
| P1-F02-T95 | Interleave two query cursors and attempt to use an analysis-list cursor for source reading or for another review/subject/filter selection. | Valid traversals remain independent. Reject mismatched cursor kinds or query identity rather than reinterpret them; current execution/access checks remain mandatory. |
| P1-F02-T96 | Page, exhaust, refresh, and directly fetch results while a distinct pending notice exists. | List progress never acknowledges the pending notice or grants retrieval/source-read credit for unreturned bodies; delivery acknowledgment still follows R56-R61. |


| Test | Fixture / action | Expected result |
|---|---|---|
| P1-F02-T97 | Query outgoing calls from a known permitted symbol with both resolved and unresolved recorded targets. | Return the direct recorded calls with existing IDs and actual resolution information; lack of a target ID alone does not suppress the authorized unresolved origin. |
| P1-F02-T98 | Query incoming calls to S42 with recorded resolved callers plus unresolved calls sharing S42's local name. | Return the resolved-target calls in caller-to-S42 direction; name-only records are not promoted to confirmed incoming edges. |
| P1-F02-T99 | Query an ambiguous relationship with recorded resolver alternatives; separately provide similarly named declarations that are not alternatives in the resolver output. | Preserve the recorded ambiguity, alternatives and their basis. Do not turn declaration lookup matches into resolver conclusions. |
| P1-F02-T100 | Query incoming calls where no matching resolved records exist and indexing/resolution limitations are present. | Return an appropriately bounded empty result with limitations; do not claim no callers, no reachability or no vulnerability. |
| P1-F02-T101 | Record two calls from one handler to the same helper under different branches or controls. | Both callsites remain inspectable through their existing IDs/occurrence representation and references. Presentation grouping must not erase either site. |
| P1-F02-T102 | Query a self-call with outgoing, incoming and both-direction selections. | Preserve the original self-edge identity and actual endpoints. Assert the separately agreed both-direction presentation once specified; do not fabricate another edge or silently lose the occurrence. |
| P1-F02-T103 | Query an authorized origin with an unresolved locator; separately query an origin whose target metadata or analyst contribution is restricted. | The permitted unresolved origin remains visible; protected target/result metadata is not leaked. Safe restricted-target representation uses the final approved contract. |
| P1-F02-T104 | Use a foreign-snapshot/unauthorized subject or expire the current attempt before the query. | Reject through the existing identity/access owners without a name fallback or protected source/metadata disclosure. |
| P1-F02-T105 | Retrieve relations repeatedly and inspect state changes and provider invocations. | No model resolver, implicit source-body read, graph mutation, candidate change, task creation or coverage dependency is caused by retrieval. No source-read credit; ordinary audit/accounting may occur. |
| P1-F02-T106 | Query a subject with more direct relationships/occurrences than fit a response, in a much larger project graph. | Return bounded attributable metadata and explicit continuation/omissions under the eventual relationship-page contract; do not load the whole graph per worker or claim the first page is exhaustive. |
| P1-F02-T107 | Return extractor-, resolver- and permitted analyst-originated records; include a record lacking a resolution basis. | Preserve each origin and actual supporting references. No target ID or missing metadata is converted into a deterministic proof or invented confidence value. |
| P1-F02-T108 | Canonical relationship records and the coverage dependency graph contain different supported connections. | Retrieve through the correct owners and verified associations without replacing one graph with the other. Record kinds not modeled by the resolver remain explicit; scheduler and acceptance state remain unchanged. |


| Test | Fixture / action | Expected result |
|---|---|---|
| P1-F02-T109 | Browse `src/api/` where the visible manifest contains `routes.py`, `auth/permissions.py` and `auth/session.py` beneath it. | Return the immediate `routes.py` file and one derived `auth/` directory entry, in bounded pages. No automatic recursive tree or source bodies. |
| P1-F02-T110 | Perform exact filename lookup for two permitted files named `settings.toml`; then narrow to one exact relative path. | Filename lookup returns distinguishable existing file references; the exact path selects only its matching record. No guessed unique winner or dropped restriction. |
| P1-F02-T111 | Find descendants beneath `src/jobs/` with supported recorded-language and classification filters; perform a nonmatching exact lookup with similar names present. | Apply every supported filter and explicit descendant scope. A miss does not silently become a fuzzy/pattern search. Exact field/case combinations use the final agreed schema. |
| P1-F02-T112 | Browse/find within `src/api/` while `src/api_old/` also contains files. | Directory-component matching excludes `src/api_old/`; no textual-prefix collision widens the query. |
| P1-F02-T113 | Discover a permitted context-only file without symbol inventory, then request a permitted source range explicitly. | Discovery returns its file reference and accurate metadata; source reading does not require a symbol ID and independently verifies permission and bytes. Discovery alone receives no source-read credit. |
| P1-F02-T114 | Discover files with parse errors, unsupported inventory, or absent recorded language, where metadata is permitted. | Keep the files discoverable with the actual limitations/missing fields. Do not claim successful empty symbol inventories or infer readability from metadata alone. |
| P1-F02-T115 | Catalogue records include a directory containing only restricted metadata and another with both visible and restricted entries. | Group/paginate only permitted metadata; no protected names, IDs or hidden directory information leak through entries, counts or diagnostics. |
| P1-F02-T116 | Discover a file whose metadata is permitted but whose source content is unavailable under the owning policy; separately request an unknown or foreign-snapshot reference. | Metadata does not grant content access. Explicit reads/lookups return the applicable safe outcome with no live/latest-source fallback. |
| P1-F02-T117 | Browse a directory with many descendants that share immediate child directories and a page smaller than the number of distinct visible children. | Deduplicate child directory entries before paging. Continuation follows the final deterministic query-bound order; no duplicate entries solely because several files share a directory. |
| P1-F02-T118 | Interleave worker A browsing `src/api/` and worker B finding files under `src/jobs/`, including their continuations. | Each selection remains request/cursor-bound. No shared current directory, cross-query results, or inherited authorization. |
| P1-F02-T119 | Repeat file discovery in a manifest larger than the context-item budget, including an empty result, then inspect provider calls, filesystem access and durable state. | Bounded catalogue lookup needs no full per-worker manifest copy or live-target scan. Empty results do not claim a live directory is empty. No inference, source bodies/read credit, review task, lead, freshness interest or coverage mutation; existing audit/accounting may occur. |
| P1-F02-T120 | Obtain a permitted catalogue continuation, then expire/supersede the attempt or remove relevant metadata access before the next request. | Current execution/visibility checks prevent unauthorized output. A previously returned file reference/cursor does not grant independent authority; verify detailed cursor errors against the final contract. |


| Test | Fixture / action | Expected result |
|---|---|---|
| P1-F02-T121 | Search literal text containing regex punctuation, then explicitly select regex mode on the same permitted source. | Literal mode does not interpret punctuation; explicit regex uses only the agreed dialect. No silent change of mode. |
| P1-F02-T122 | Search mixed-case text with the default and explicit case-insensitive option. | Default is case-sensitive; explicit insensitive matching preserves exact original-byte locations. Detailed Unicode cases require the final case/encoding contract. |
| P1-F02-T123 | Use a supported regex alternative, malformed syntax and a construct unsupported by the selected bounded matcher. | Match valid syntax; reject invalid/unsupported syntax with actionable detail where known. No fallback to an unrestricted matcher or model inference. |
| P1-F02-T124 | Search explicit file IDs, a permitted directory/language selection, and the explicit authorized snapshot. | Scope uses the existing manifest and permissions. No manual enumeration is required for directory search; filters are never silently broadened. |
| P1-F02-T125 | Place a match far beyond the start of a long source line. | Preview includes the actual match region or explicitly marks an oversized match; exact match and returned-preview coordinates/hashes stay distinct. |
| P1-F02-T126 | Put several occurrences on one line and an inventory ambiguity around the containing symbol. | Returned hits retain precise locations and do not invent symbol association. Occurrence count/order expectations are blocked until that contract is settled. |
| P1-F02-T127 | Include selected content that cannot be decoded under the supported encoding policy. | Explicitly report omitted/unsearchable content; no silently completed no-match claim. Unsupported input does not become replacement-decoded evidence. |
| P1-F02-T128 | Separately fill the output page and stop a scan through host resource limits before all selected content is examined. | Distinguish result pagination from an interrupted scan. Report real progress and supported next action without inventing complete counts or resetting budgets. |
| P1-F02-T129 | Scan several files but deliver only two small previews; inspect attempt-read accounting and side effects. | Only actual preview intervals are credited as delivered. No full-file/symbol coverage, lead/task/interest creation or analytical conclusion follows from internal scanning. |
| P1-F02-T130 | Request excluded/foreign-snapshot content, expire the attempt, or alter snapshot bytes in separate fixtures. | Current source/identity/integrity controls fail with appropriate safe outcomes. No live-source fallback, protected preview, or ordinary empty success. |

| P1-F02-T131 | In one permitted file, place a call spelling on one line and its opening parenthesis on a later line; compare it with a single-line form using an explicitly supported whitespace-tolerant regex. | Both occurrences are found under the chosen cross-line-capable pattern; exact match ranges refer to the original file bytes. A literal requiring adjacent characters does not silently gain whitespace tolerance. |
| P1-F02-T132 | Search for a literal containing an actual newline, and compare it with a literal lacking that newline. | Each matches only according to its actual literal content. No newline removal, insertion or normalization manufactures a match; exact encoding/newline cases await the finalized matcher contract. |
| P1-F02-T133 | Place an occurrence across a boundary that would separate source-response pages; vary preview/result allowances. | The complete occurrence is preserved regardless of output boundaries. Preview clipping cannot shorten the match or determine search progress. |
| P1-F02-T134 | Use a supported match larger than the preview allowance. | Return the complete match location and an explicitly partial bounded preview. A separate authorized source read can inspect the source; no full-match read credit is granted for unreturned bytes. |
| P1-F02-T135 | Put the first part of a potential match at the end of one file and the remaining part at the beginning of another. | No cross-file occurrence is produced. Each file is an independent matching input even when processed sequentially. |
| P1-F02-T136 | Repeat a complete permitted search with different output-page sizes; separately exercise an input exceeding the supported processing strategy and any implemented chunk boundary. | Once occurrence/cursor contracts are settled, complete runs yield the same occurrences. Oversized inputs produce explicit limitations, not silent per-line no-match success. Any chunked optimization must demonstrate equivalent semantics rather than assume a fixed overlap suffices. |

| P1-F02-T137 | Search literal `path` in the ASCII fixture `validate(path); write_file(path); record_action(path)`. | Return three separately located occurrences on that line; overlapping previews do not collapse the distinct match ranges or create evidence/candidates. |
| P1-F02-T138 | Place several matches in multiple permitted files; randomize input discovery/worker order while keeping the snapshot and query fixed. | Return canonical relative-file order, then original match start/end-byte order. Do not fold path case or let completion order/relevance change result order. Final path comparator and matcher alternative semantics must be fixed before asserting full cross-platform equivalence. |
| P1-F02-T139 | Search literal `ana` in `banana`, with both a single response and the eventual supported continuation. | Enumerate [1, 4) only; do not also return overlapping [3, 6). Completeness is reported under the non-overlapping policy. |
| P1-F02-T140 | Use a complete non-empty match longer than its preview allowance, followed by a second match; vary preview and result sizes and finish each permitted traversal. | Complete match identities remain unchanged. Resume after the complete first match, not after its clipped preview. Credit only preview bytes actually delivered. Cursor-dependent traversal remains pending until its exact contract is settled. |
| P1-F02-T141 | Fill a response so the next discovered occurrence cannot be represented in that page. | Do not advance the advertised continuation beyond the unreturned occurrence. It remains available on continuation, or a specific representability failure makes the incomplete outcome explicit. A lookahead scan is not delivery. |
| P1-F02-T142 | Resume within an original file using supported anchor/boundary patterns whose behavior would differ if a suffix became a new input. | Positioned continuation agrees with enumeration on the original full file. No false file-start or boundary match appears from slicing. Use only the final supported syntax/flags; the concrete matcher/cursor implementation is required to execute this test. |
| P1-F02-T143 | Supply a syntactically supported regex that actually produces a zero-length occurrence before any non-empty result. | Return actionable unsupported-occurrence failure; no infinite loop, silent skipping, fabricated non-empty match or completed-no-match claim. Do not call this a pattern syntax error when compilation succeeded. |
| P1-F02-T144 | Under the final supported dialect, encounter a zero-length match after ordinary matches have already been delivered. | Identify the search as incomplete and explain the unsupported empty occurrence. Preserve earlier exact navigation results without claiming exhaustive coverage or silently advancing by a character. |

## 8. Required remaining discussions

| Open item | What is not yet approved |
|---|---|
| Indexed symbol-lookup details | Extending `symbol_list`, exact local/qualified lookup, optional file/parent/kind filters, alternatives, no inferred bindings and scope-before-paging are agreed. Final fields/combinations, case/name normalization, parent traversal, ordering, query-pagination shape/bounds and exact statuses remain open. |
| File-catalogue interface details | R76-R83 approve one manifest-backed capability for immediate-child directory browsing, explicit descendant finding, exact filename/path lookup and optional directory/recorded-language/classification filters. Preserve file references, metadata visibility, inventory limitations and separation from source reads/interests. Final tool name/schema, filter combinations, root/case/normalization, ordering, reference integration and directory/file pagination encoding/bounds remain open. |
| Relationship-query implementation details | R68-R75 approve bounded direct retrieval through existing owners, original edge direction, strict resolved incoming calls, authorized unresolved origins, attributable resolution/provenance and distinct callsites without graph mutations. Final selector/filter/status fields, self-edge/both-direction presentation, restricted-target representation, occurrence paging, stable order/continuation consistency and exact resolver-to-record associations remain open. |
| Source-search implementation details | R84-R90 approve default literal/case-sensitive matching, explicit bounded non-backtracking regex, manifest-backed scope, exact match-centered previews and honest scan/output limitations. R91-R95 now require per-file matching, explicit cross-line behavior and presentation-independent complete occurrences. R96-R101 settle individual non-overlapping hits, canonical path/start/end-byte order, complete-match-based progress, original-file context and explicit produced-zero-length errors. Exact engine/dialect/dependency, alternative-selection semantics, newline/anchor flags, selector fields, Unicode/case-to-byte mapping, path comparator, scan limits and resumable search cursor remain open. Source-read pagination does not finalize search pagination. |
| Analysis-retrieval contracts | Compact subject-based discovery, exact-result detail retrieval, separate work availability and no auto-wait/task creation are agreed in R29–R36. Exact artifact variants, role visibility, selector/response fields, paging of details/work references, and result-specific acceptance integration remain open; Phase 4 still owns publication. |
| Analysis-list implementation details | R62-R67 approve original-H availability bounds, stable availability-based continuation with existing-result-ID tie-breaking, explicit refresh/exact fetch, and current visibility/status rechecks. Exact ordering direction, concrete query tuple, re-availability/multiple-subject mapping, wire encoding/bounds and expiry remain open. This does not select pagination for symbol/search/relationship or work-status lists. |
| Freshness-notice mechanics | R37-R48 establish automatic notices and durable work/subject/query interests. R49-R55 now select committed review-local availability sequencing and a consistent lookup read followed by a separate original-H registration write. Exact event/counter storage/allocation, acceptance-owner hook, empty/history initialization, task/inquiry mapping, filter normalization, response fields/limits, exact R56-R61 response/receipt mapping and coalesced-delivery representation, later visibility transitions, retention/cleanup and file-symbol relevance remain open. Do not invent a table or general messaging service. |
| Read wire contract | Final selectors, mutually exclusive request variants, response fields, continuation fields and allowed defaults. |
| Cursor wire contract | Self-contained cursors, HMAC-SHA-256, validation, replay and same-review cross-attempt use are agreed. Exact encoding, canonical authenticated bytes, field/size/version bounds and error contract still need decisions. |
| Secret provisioning details | Persistent project-local owner-protected storage, serialized first creation, worker loading/restart and no silent replacement are agreed. Exact filename/format, generation parameters, atomic initialization protocol and how prior provisioning is distinguished from loss remain open. |
| Rotation, repair and expiry | Key identifiers or generations if needed, rotation, the explicit loss-repair procedure and whether/when cursors expire remain open. Do not build a general key-management service or assume indefinite validity. |
| Encoding and delivery | Supported encoding edge cases, partial-line display contract, delivery interruption and replay accounting. |
| Integration and release | Actual refactored owners/tests; tool schema, SDK and execution-receipt compatibility; how new behavior is enabled. |

Do not treat these as developer-discretion decisions. Private helper names and
small local decompositions may be chosen within an agreed interface; the unresolved
authority, lifecycle, public-contract and persistence choices require discussion.

## 9. Dependencies and completion

P1-F01 owns research access and assignment separation. P1-F03 owns new source-read
reference handling and evidence normalization. P1-F07 owns common actionable tool
outcomes. P1-F08/P1-F09 must agree on delivered-result/replay and grouped-response
accounting. Phase 4 owns analysis acceptance and visibility; Phase 7 reconciles
cross-feature identities and compatibility, not missing local specifications.
Freshness notices additionally depend on logical work ownership, P1-F04 continuation,
P1-F08 actual-delivery/recovery handling, and the existing acceptance/availability
owner. Optional notices do not create Phase 3's blocking answer subscriptions.

Source selection, pagination, independent cross-attempt cursors, HMAC-SHA-256,
persistent project-local host-secret ownership, exact indexed symbol lookup,
and subject-based analysis discovery followed by exact-result retrieval are now
saved as agreed portions of P1-F02. R37–R43 add automatic subject-specific freshness
notices and optional retrieval, while amending R35's subscription prohibition.
R44-R48 add durable interest registration, equivalent-query reuse, same-work
restoration, logical-work closure and gap-free lookup/registration requirements.
R49-R55 now select the committed review-local availability marker and the original-H
read/write registration sequence. R56-R61 add request-bound acknowledgment after a
valid durably recorded response, recovery and safe uncertain repeats. R62-R67 now
select H-bounded stable-position analysis-list continuation alongside notices and
independent exact retrieval/refresh. Exact query tuple/order direction, storage/
allocation, response/receipt mapping, final wire contracts and Phase 4 acceptance
remain open.
R68-R75 add direct-relationship retrieval; section 6.9 (G1-G6) and T97-T108
capture its implementation work and acceptance scenarios. Final relationship
wire/visibility projection, occurrence/page mechanics and refactored owner mapping
remain explicit prerequisites, not developer-invented defaults.
R76-R83 add manifest-backed file discovery and directory browsing; section 6.10
(F1-F6) and T109-T120 capture the implementation direction and acceptance scenarios.
Final catalogue fields, filtering/normalization, paging and reference mapping remain
explicit prerequisites. Metadata visibility and source readability keep their
existing owners; this approval creates no new classification or publication policy.
R84-R90 add source-text search; section 6.11 (S1-S6) and T121-T130 specify its
implementation work and acceptance scenarios. R91-R95, section 6.12 (M1-M5) and
T131-T136 add per-file cross-line matching independent of output boundaries.
R96-R101, section 6.13 (E1-E6) and T137-T144 add individual non-overlapping
occurrences, deterministic file/byte order, original-context matching progress and
explicit zero-length failure. Matcher selection, exact flags/alternative semantics,
path comparison, byte mapping, scan/response limits, full cursor/recovery behavior
and exact wire fields remain prerequisites, not implicit defaults.
The feature is not implementation-ready until its remaining required contracts,
code mapping, tests and dependencies are discussed and reviewed. No code, migration,
application test or benchmark has been produced by this documentation update.

## 10. Approval and save record

- The user approved keeping `symbol_get` metadata-only and extending `source_read`
  with known-symbol and explicit-file-range selection through one reader.
- The user approved full-symbol defaults and host-managed bounded pagination,
  including selection-preserving continuations, explicit long-line fragments,
  agent-controlled paging and actual-delivered-source accounting.
- The user approved self-contained, integrity-protected cursors bound to the
  review and source selection rather than the original worker; same-review
  authorized replacement attempts can continue without inheriting read credit.
- The user approved replay from a fixed position without a shared advancing
  pointer, using the current limits and deriving continuation from actual bytes.
- The user asked that approved feature progress be saved to GitHub or local files.
  Earlier local-only checkpoints are historical. The v0.7 baseline was published
  in `JennieXLisa/ssr-redesign` before this amendment; Git history preserves it.
- The user approved HMAC-SHA-256 with a project-local persistent host secret after
  clarifying that the secret authenticates cursors and is not their reading
  position. The approved storage boundary is an owner-protected host file; creation
  is serialized, workers reuse it, restarts reload it, and missing/unverifiable
  authentication never triggers silent replacement or acceptance.
- The simultaneous-reader clarification is retained: a shared project secret
  authenticates independent cursors and does not connect their positions or
  transfer one attempt's read history to another.
- Version 0.1 remains in `history/before-p1-f02-source-read/`; version 0.2 in
  `history/before-p1-f02-self-contained-cursors/`; version 0.3 and its accompanying
  indexes/register are preserved in `history/before-p1-f02-cursor-authentication/`.
  Exact encoding/provisioning, rotation/expiry, and other open feature choices are
  not silently approved by this revision.

- The user approved extending `symbol_list` with exact local-name and qualified-name
  lookup, optional file/location/containing-symbol/kind filters, explicit alternative
  matches and query completeness. Known IDs remain directly usable; matching one
  declaration never automatically resolves a call or upgrades a relationship.
- This v0.5 save adds R23–R28, implementation guidance L1–L6 and test scenarios
  T28–T37 derived from that approval. It does not finalize the listed remaining
  schema, normalization, ordering, query-pagination or navigation decisions.
- The complete preceding v0.4 feature text, v1.4 decision register and affected
  indexes are retained unchanged in `history/before-p1-f02-indexed-symbol-lookup/`.

- The user approved compact analysis discovery by existing subject IDs, exact-result
  retrieval, separately reported review availability, and no automatic waiting or
  task creation. Existing acceptance/visibility owners remain authoritative.
- This v0.6 save adds R29–R36, implementation guidance A1–A7 and scenarios
  T38–T49. These scenarios are requirements, not executed application tests. At
  that checkpoint dynamic-list consistency awaited a decision; v0.11 now updates T49.
- The prior v0.5 feature, v1.5 register and affected indexes are preserved unchanged
  in `history/before-p1-f02-analysis-retrieval/`. Other feature requirements and
  phases are not expanded by this save. Relationship-query details remain open.

- The user proposed advertising newly created records so the agent could choose
  whether to reload. After clarification, the user explicitly approved automatic
  subject-interest tracking from an analysis lookup and delivery at the ongoing
  work's next normal interaction, without forced retrieval or a separate subscribe
  call. Interests must not follow a reusable worker slot into unrelated work.
- This v0.7 save adds R37–R43, implementation guidance N1–N6 and scenarios
  T50–T61. R35 is explicitly amended to permit freshness interests while retaining
  the prohibitions on implicit tasks, waiting and blocking contextual dependencies.
  The v0.6 high-water/keyset proposal was not approved at that checkpoint. Its
  previously open status is superseded by the explicit v0.11 approval below.
- The preceding v0.6 feature, v1.6 register and affected indexes are retained
  unchanged in `history/before-p1-f02-freshness-notices/`. This is documentation
  only; no implementation, application test, or GitHub publication is claimed.


- The user approved durable interests stored per ongoing task/inquiry as part of
  successful analysis lookup, rather than relying on worker memory or the next
  agent checkpoint. Equivalent work/subject/filter queries reuse one interest;
  normal same-work continuation restores it and logical closure stops advertising.
- This v0.8 amendment adds R44-R48, implementation steps I1-I6 and acceptance
  scenarios T62-T69. It narrows the earlier persistence open item but leaves
  exact schema, marker/registration ordering, notice delivery acknowledgment,
  physical retention and continuation mapping open. T66/T67/T69 explicitly retain
  those implementation dependencies. No application tests or code changes are
  claimed. The prior text remains in Git history and the preceding local package.


- The user approved committed availability changes within a review and a
  lookup-consistent starting position: observe H and the bounded listing in one
  short read transaction, close it, then register/reuse interest in a separate
  short write using that original H. Record actual usability independently of
  active listeners so a publication between lookup and registration remains
  discoverable. Preserve existing pending progress and idempotent transition replay.
- This v0.9 amendment adds R49-R55, implementation steps V1-V6 and scenarios
  T70-T79. It updates the earlier open-marker statements and the race portions of
  T61/T66. It does not approve changing-list pagination, delivery acknowledgment,
  exact schema/allocation, or new publication/visibility policy. These are
  specified tests and implementation guidance, not executed application tests.
- Save status for this amendment: LOCAL ONLY; GitHub write actions were not
  available in this session. The pre-edit files match the blobs at remote commit
  `017bde3f0c1f59a01ca9d8b11273f5000676a7be`. The previous versions are preserved in
  the local `history/before-p1-f02-availability-sequence/` directory and in Git
  history. Publication must reconcile the current remote head before applying
  this two-file change; no implementation repository was modified.

- The user approved host-managed advertisement acknowledgment after the ordinary
  request containing a notice produces a valid, durably recorded response. The
  exact included set controls acknowledgment; later or omitted updates remain
  pending. Recovery settles a known response or permits safe repeat at a normal
  interaction when uncertain, without a model acknowledgment call or extra task.
- Version 0.10 adds R56-R61, implementation section 6.7 and T80-T88. It narrows
  earlier open-delivery statements without selecting changing-list pagination,
  coalescing representation, physical schemas or provider-outcome mapping. These
  are specified tests, not executed application tests.
- This amendment is LOCAL ONLY. GitHub read access was checked, but this session
  exposes no repository-write action. The remote checkpoint was observed at
  `017bde3f0c1f59a01ca9d8b11273f5000676a7be`; v0.9 and v0.10 are not claimed pushed.
  The pre-edit v0.9/v1.9 files are preserved under
  `history/before-p1-f02-notice-delivery-acknowledgment/`. No application code,
  release, deployment, original specification, or other feature was changed.


- The user explicitly approved the combination of an analysis listing bounded to
  its original availability position H, stable availability-based continuation
  after the last returned position with an existing-result-ID tie-breaker, and
  independent freshness notices/exact retrieval/refresh for later results.
- Version 0.11 adds R62-R67, implementation section 6.8 (Q1-Q6), and T89-T96; it
  updates R36/T49 and earlier current-status statements so the chosen paging rule
  is no longer described as wholly open. Current permissions/status are never
  frozen, and listing progress cannot acknowledge notices or grant source-read credit.
- This amendment is saved locally only; no GitHub files were written during this
  save. The last remote checkpoint recorded earlier in the conversation was
  `017bde3f0c1f59a01ca9d8b11273f5000676a7be`; it was not reverified here. Preserve and
  reconcile later remote work before publication. The exact preceding v0.10/v1.10
  local files are retained in `history/before-p1-f02-bounded-analysis-listing/`.
  No application code or other feature changed; added tests are specified, not run.

- The user explicitly approved bounded direct-relationship queries that preserve
  actual direction, separate callsites, recorded resolution/basis and provenance,
  including authorized unresolved origins and no guessed incoming bindings.
- Version 0.12 adds R68-R75, section 6.9 (G1-G6), and T97-T108. It narrows the
  relationship-retrieval open item without choosing its final wire schema, paging
  contract, restricted-target projection or self-edge presentation. Earlier
  approval-history statements about unresolved relationship behavior describe
  their earlier checkpoints and are superseded by this explicit approval.
- This amendment is saved locally. No GitHub write was performed. The remote
  `main` ref was checked in this session and still pointed to
  `017bde3f0c1f59a01ca9d8b11273f5000676a7be`; do not describe the later local
  amendments as published. Exact pre-edit v0.11/v1.11 documents are preserved in
  `history/before-p1-f02-direct-relationships/`. No other feature or application
  code was modified. Acceptance scenarios are specified, not executed tests.

- The user explicitly approved one manifest-backed catalogue for bounded
  immediate-child directory browsing and filtered exact filename/path discovery,
  with explicit descendant searches and existing file references. Discovery must
  preserve metadata/readability/inventory distinctions, safe path boundaries and
  visibility-before-grouping/pagination; it must not read the live filesystem or
  automatically read source, create tasks/leads or subscribe to analysis updates.
- Version 0.13 adds R76-R83, section 6.10 (F1-F6), and T109-T120. It narrows the
  file-discovery open item without inventing final tool names, wire fields, root or
  matching-normalization rules, cursor encoding, visibility classifications or new
  storage. Previously approved requirements and test scenarios are unchanged.
- This amendment is LOCAL ONLY. GitHub create/update discovery returned no matching
  actions in this session; no remote write was attempted or claimed. Remote branch
  state was not rechecked for this save. The incremental patch applies to the exact
  local v0.12/v1.12 preimages, not an assumed current GitHub checkout. Those preimages
  are preserved in `history/before-p1-f02-file-discovery/`. Only this feature and the
  decision register changed. Added acceptance scenarios are specified tests, not
  executed application tests.

See the [phase specification](../SPECIFICATION.md),
[phase implementation plan](../IMPLEMENTATION_PLAN.md), and
[decision register](../../DECISION_REGISTER.md).

- The user approved the source-search direction: default literal and case-sensitive
  matching, explicit bounded non-backtracking regex, manifest-backed scope selection,
  exact match-centered previews and honest scan/output completeness. The approval
  does not choose the regex dependency or resolve multiline/search-continuation
  semantics.
- This v0.14 amendment adds R84-R90, section 6.11 (S1-S6), and T121-T130. Earlier
  requirements and test scenarios are retained. Exact implementation questions
  remain open and the feature is not implementation-ready.
- This save is LOCAL ONLY. No GitHub write or remote-head verification was performed
  for this amendment, and no application code/test or dependency installation ran.
  The incremental patch uses the local v0.13/v1.13 preimages preserved in
  `history/before-p1-f02-source-search/`, not an assumed current remote version.

- The user approved per-file matching with explicitly requested cross-line queries,
  independent matching/preview boundaries, one-file-at-a-time verified processing,
  and explicit limitations rather than silent line-by-line fallback.
- Version 0.15 adds R91-R95, section 6.12 (M1-M5), and T131-T136. It updates current
  statements that cross-line behavior was wholly open; earlier approval history
  remains unchanged. Exact dialect/flags, overlap/zero-length matches and source-
  search continuation are still to be discussed. No proposed next decision is saved
  as approved.
- Saved locally only. No GitHub access/write, application-code change, dependency
  installation or application-test run was performed during this amendment. Exact
  local v0.14/v1.14 preimages are preserved in
  `history/before-p1-f02-cross-line-search/`; the incremental patch uses those
  preimages, not the older remote checkpoint.


- The user approved one result per textual occurrence, deterministic canonical
  relative-file/start/end-byte order, non-overlapping enumeration, continuation
  after complete matches rather than clipped previews, preserved original-file
  matching context, and explicit failure on produced zero-length matches. Partial
  results cannot be represented as an exhaustive search after that failure.
- Version 0.16 adds R96-R101, section 6.13 (E1-E6), and T137-T144. Earlier rules
  remain intact; current open-item descriptions now distinguish settled occurrence
  behavior from the still-open matcher, encoding, comparator and cursor mechanics.
  No unapproved next design choice is recorded as a requirement.
- This update is LOCAL ONLY. No GitHub call or write, application-code change,
  dependency installation or application-test execution was performed for this
  amendment. Exact v0.15/v1.15 preimages are preserved in
  `history/before-p1-f02-occurrence-enumeration/`. Its incremental patch uses those
  local preimages, not an assumed current GitHub checkout. These acceptance cases
  are specified tests, not executed harness tests.
