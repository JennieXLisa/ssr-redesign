# P1-F02 — Indexed navigation and information retrieval

Version: 0.8  
Updated: 2026-09-09  
Feature status: IN DISCUSSION  
Approved detail saved: source selection, pagination, authenticated cursors, indexed lookup, exact analysis retrieval, automatic freshness notices, and durable work-scoped interests  
Detailed specification: PARTIAL — further interfaces and navigation choices remain open  
Implementation readiness: NOT READY  
Implementation and application tests: NOT PERFORMED

This feature file records explicit approvals from the design conversation. The
source-reading, pagination, cursor-design, authentication and indexed-lookup
requirements below record approved choices; their written formulation is available for review.
The user has approved HMAC-SHA-256 and a persistent project-local host secret.
The latest approval adds automatic interest tracking when an agent queries a
subject's analysis, followed by lightweight notices at the ongoing work's next
ordinary interaction when relevant new analysis is available. Retrieval and refresh
remain the agent's choice. This amends R35's previous blanket prohibition on
subscriptions; it does not add contextual dependencies, task creation or waiting.
The latest approval also requires durable, source-free interests registered with
successful lookups, independently of worker memory or model checkpoints. Restore
interests for the same ongoing work; do not transfer them to unrelated work.
The feature remains partial. Final wire/key-file formats, rotation/expiry, other
matching modes, changing-list pagination, exact interest schema/change markers,
delivery acknowledgment, new publication rules, and rollout remain open.
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
agreement; exact wire fields, status enums, and changing-list pagination mechanics
remain open. This section defines consumption of available results, not a new
publication or knowledge-acceptance authority.

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

### P1-F02-R36 — Specify changing-list consistency before implementation

The source snapshot is immutable, but new analysis results and acceptance updates
can appear while an agent pages a result index. The consistency behavior must be
explicit. Do not reuse the source-reading cursor's immutable-range assumptions
without a separate result-list contract.

The user has approved the need for explicit consistency, not a particular
high-water mark, keyset, snapshot-list, offset, cache, or expiry mechanism.
Those implementation choices remain open. Exact-result identity in R31 applies
regardless of which list-pagination mechanism is subsequently agreed.

## 4C. Approved automatic subject-specific freshness notices

This section records the user's proposal to advertise new records and the explicit
approval, after clarification, of automatic interest registration and next-normal-
interaction delivery. R44-R48 below now add the approved durable work-scoped
interest mechanism. The exact change-marker, result-list pagination, storage
schema and delivery-acknowledgment protocol remain undecided.

### P1-F02-R37 — An analysis lookup registers interest automatically

When an authorized agent queries analysis for an indexed symbol or file, remember
that subject and the applicable lookup filters for its ongoing task or inquiry.
Do not require an additional subscribe tool call. Use existing subject identities;
do not infer interest through semantic similarity or subscribe to every project row.
Invalid or unauthorized lookups must not establish access to restricted subjects.

The interest belongs to the logical work, not a reusable worker slot. A slot that
later executes unrelated work must not inherit it. The behavior is intended to
support the ongoing analysis. Durable registration, same-work restoration and
logical-work lifecycle behavior are now specified in R44-R46; exact owner mapping,
marker and acknowledgment contracts still require implementation-level agreement.

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
behavior, not an implicit effect of this lookup capability. Exact attachment,
ordering, delivery acknowledgment and budget composition need implementation-level
agreement before this feature is considered ready.

### P1-F02-R40 — Retrieval and refresh remain optional

The agent may fetch an advertised result by exact ID, refresh its result listing,
read it later, or continue without fetching it. Advertising D20 must not replace
an explicitly selected D18, inject D20's body, reset the current listing cursor,
or automatically restart pagination. A request for D18 still selects D18 under R31.

Freshness notification and pagination consistency are separate contracts. A notice
does not by itself approve a high-water mark, keyset algorithm, cached listing or
frozen-result snapshot. R36 remains open on those implementation details. Current
access and status checks apply irrespective of the eventual paging mechanism.

### P1-F02-R41 — Keep notices bounded and avoid repeated unchanged alerts

Coalesce relevant arrivals into a bounded notice rather than broadcasting each
publication to every worker. Do not repeat the same already advertised update on
every turn merely because the agent chose not to fetch it. Further relevant
updates may produce a new/coalesced notice. Explicitly represent omitted details
or offer an authorized refresh when the eventual response bound is reached; never
claim an exhaustive list when not all references are shown.

The exact coalescing key, change marker, limit, retention and interrupted-delivery
policy remain open. Do not invent numerical defaults, silently drop unadvertised
updates, or add a general message broker to implement this interaction.

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

This section records the explicit approval of durable interests attached to ongoing
work. It narrows the earlier persistence open item; it does not choose an SQL schema,
a publication sequence, a list-pagination algorithm or a delivery receipt protocol.

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

This is an acceptance invariant, not selection of a high-water mark, event counter,
timestamp or frozen listing. The concrete ordering, registration failure handling
and race-safe transaction/replay protocol remain required design decisions. Use
short host operations; never keep a transaction open across a model turn. Do not
mark a result advertised merely because an outgoing response has been constructed.

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

This sequence elaborates R29–R36 without selecting open publication or dynamic-list
pagination rules. Historical components include `document_query` and the dedicated
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
| A6. Resolve list consistency and common outcomes | Before implementation readiness, agree how discovery pages behave as results arrive or acceptance changes. Integrate P1-F07 outcomes and P1-F09 combined-response limits. Reusing a cursor codec must not silently import the immutable-source paging semantics. Do not hold a transaction open across model turns. |
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
| N2. Capture interest with lookup | After validating/resolving the subject, durably register/reuse the interest for its ongoing work and normalized query as part of the successful lookup (R44-R45). Do not rely on the next model checkpoint or worker-local memory. Specify success/failure and initial observed-marker ordering before implementation. |
| N3. Detect relevant availability | Use the owning accepted-publication information and exact subject associations; distinguish 'became consumable' from provisional creation. Check recipient visibility. Propose the smallest compatible change-marker/event integration before adding persistence; do not scan and summarize all project results for every worker turn. |
| N4. Compose at a normal boundary | Attach a bounded notice through a defined response/turn hook without replacing the requested tool result, inventing a tool call, corrupting provider call/result pairing, or scheduling an extra model exchange. Integrate the total context/result allowance with P1-F09. Exact notice placement remains an open wire-contract decision. |
| N5. Separate delivery and consumption | Record only the actual notice-delivery state supported by the runner's evidence. Retrieval of a result is a different action. Reconcile lost acknowledgments/replay with P1-F08 and work continuation with P1-F04; do not mark an update advertised merely because a pending response was constructed. |
| N6. Test isolation and optionality | Verify subject/work isolation, accepted-versus-private results, late visibility changes, no per-turn duplicate alerts, coalescing, exact-ID fetch, unchanged listing selection, and zero notice-only model calls or review tasks. Mark tests depending on unsettled delivery/restart contracts as blocked rather than inventing those contracts. |

Keep this a small host capability integrated with existing retrieval and execution.
No separate manager model, messaging service, notification worker, full query-result
copy or new knowledge store is authorized. R44-R48 now require durable, work-scoped interests; section 6.5 describes their
implementation boundary. The exact storage representation, subject-to-file
aggregation, lifecycle/retention limits, publication-marker and delivery protocol
still require discussion. Do not describe the complete notice subsystem as
restart-safe until its remaining contracts are specified and tested.

### 6.5 Durable interests: approved implementation direction

Map these steps to the refactored owners before changing code. The sequence gives
the approved mechanism and its boundaries, not permission to invent the remaining
publication, receipt, retention or schema choices.

| Step | Required developer action and verification |
|---|---|
| I1. Resolve work ownership | Identify the durable task/inquiry identity and how successive attempts refer to the same logical work. Reuse the current task identity where sufficient. Document any continuation that changes tasks and obtain agreement on that mapping; never key interests by worker slot. |
| I2. Map minimal durable state | Inspect existing host persistence and its transaction owner. Model the review/work, subject, normalized filters, initial/observed availability and advertised-progress meanings without copying documents. Choose the smallest compatible extension; exact schema, normalization, migration and retention are not selected here. |
| I3. Integrate successful lookup registration | Resolve and authorize the query, then durably create or reuse its equivalent interest as part of lookup completion. Do not require a model checkpoint or a second subscribe tool. Specify how the listing and observation position satisfy R47 and how persistence failure is surfaced before coding the final protocol. |
| I4. Restore at normal continuation | Load the same work's interests for an authorized replacement attempt through existing continuation/runtime hooks. Recheck visibility before notices. Preserve waiting/retryable work; stop active advertising only under the logical-work closure authority. |
| I5. Keep progress meanings separate | Coalesce pending information with the existing normal-turn notice hook. Do not equate queued/composed notice, delivered notice, retrieved result or source inspection. Do not suppress unseen lower-position updates merely because a later result was fetched. The actual delivery acknowledgment is still an open P1-F08 integration contract. |
| I6. Verify lifecycle and races | Add deterministic cases T62-T69 below at existing query/state/runtime seams. Simulate process replacement using disposable state; use no live model calls. Keep tests requiring the exact marker/receipt protocol explicitly blocked until that protocol is agreed. |

The persistent state change is intentional host bookkeeping even though the
analysis content is retrieved read-only. It does not create review work, grant
result acceptance, change canonical coverage, or reopen a completed inquiry.

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
| P1-F02-T49 | Add results or change acceptance between discovery pages. | Verify the explicitly agreed list-consistency contract once settled; immutable source-cursor behavior alone cannot satisfy this test. This scenario remains blocked on the open consistency decision, not an implied high-water-mark design. |

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
| P1-F02-T61 | Publication races the first lookup, or notice response delivery fails. | Verify the later-agreed marker/acknowledgment protocol prevents skipped unadvertised updates or false consumption. Exact race assertions are blocked on those explicit remaining decisions. |
| P1-F02-T62 | Successfully query S42, stop the process before any agent checkpoint, publish a newly consumable result, and resume the same logical work in a replacement attempt. | Durable interest is restored and the update remains eligible for notice at a normal interaction, subject to current visibility. No repeat subscribe request or worker-local state is required. |
| P1-F02-T63 | Repeat equivalent lookups from the same logical work, including a replacement attempt. | One equivalent interest is reused; no duplicate listeners or per-turn duplicate alerts. The final filter-normalization and observation rules must not discard unadvertised updates. |
| P1-F02-T64 | Query the same subject under different work owners and materially different filters. Reassign a used worker slot to unrelated work. | Ownership/filter isolation is preserved. The unrelated work inherits no prior interests; no implicit cross-work merge occurs. |
| P1-F02-T65 | Compare attempt failure followed by authorized continuation, temporary waiting, logical-work completion and logical-work cancellation. | Continuable/waiting work retains its interests; logically completed/cancelled work receives no further advertising or automatic reopening. Map assertions to real lifecycle states rather than inferring closure from an attempt alone. |
| P1-F02-T66 | Interleave accepted availability with the listing read and durable interest registration. | Each relevant result is represented by the lookup or remains eligible for notice; no observation gap. Exact interleavings and assertions are blocked on the still-open marker/transaction protocol. |
| P1-F02-T67 | Retrieve D22 directly while D20/D21 were not retrieved; also construct a notice whose delivery is interrupted. | Retrieval/advertising/source-read meanings remain separate; D22 does not mark earlier results read, and a constructed response is not proof of delivery. Exact acknowledgment/replay tests require the agreed delivery protocol. |
| P1-F02-T68 | Inspect durable interest state and normal resume behavior using disposable fixtures. | State contains only allowed ownership/query/progress metadata, not source, result bodies, conversations or a per-agent publication-history copy. No notification worker, extra model call, review task or coverage write is created. |
| P1-F02-T69 | Inject interest persistence failure or an uncertain outcome during lookup completion. | The tool must not falsely report durable registration. Reconciliation/retry follows the eventual P1-F07/P1-F08 contract without duplicate equivalent interests. Exact error and acknowledgment behavior remains to be agreed. |

## 8. Required remaining discussions

| Open item | What is not yet approved |
|---|---|
| Indexed symbol-lookup details | Extending `symbol_list`, exact local/qualified lookup, optional file/parent/kind filters, alternatives, no inferred bindings and scope-before-paging are agreed. Final fields/combinations, case/name normalization, parent traversal, ordering, query-pagination shape/bounds and exact statuses remain open. |
| File discovery | Project-tree/path browsing and file-discovery interfaces remain open. A relative-file-path filter for symbol lookup does not finalize a separate file-search capability. |
| Relationship retrieval | Detailed result shape and navigation for resolved/ambiguous/unresolved edges, including gaps and provenance. |
| Source search | Exact search modes, filters, match previews and search-limit/continuation semantics. Source-read pagination approval does not finalize search pagination. |
| Analysis-retrieval contracts | Compact subject-based discovery, exact-result detail retrieval, separate work availability and no auto-wait/task creation are agreed in R29–R36. Exact artifact variants, role visibility, selector/response fields, paging of details/work references, and result-specific acceptance integration remain open; Phase 4 still owns publication. |
| Changing analysis lists | Ordering, continuation identity, membership under new arrivals, changing acceptance/visibility, consistency markers and expiry remain open. Automatic update notices are approved separately; they do not finalize the dynamic-list pagination algorithm. |
| Freshness-notice mechanics | Automatic notices and durable interest per review/work/subject/normalized query are agreed in R37–R48, including lookup-time registration, restoration, work isolation, and a no-publication-gap invariant. Exact task/inquiry mapping, filter normalization, schema, marker/transaction protocol, response fields/limits, delivery acknowledgment/replay, retention/cleanup and nested file-symbol relevance remain open. Do not invent a table or general messaging service. |
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
They do not settle changing-list pagination, exact interest schema/change markers,
delivery acknowledgment, final wire contracts, or Phase 4 acceptance.
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
  T38–T49. These scenarios are requirements, not executed application tests. The
  dynamic-list consistency scenario is explicitly blocked on a further decision.
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
  The v0.6 high-water/keyset proposal was discussed but not separately approved as
  the final pagination algorithm; it remains an open implementation decision.
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

See the [phase specification](../SPECIFICATION.md),
[phase implementation plan](../IMPLEMENTATION_PLAN.md), and
[decision register](../../DECISION_REGISTER.md).
