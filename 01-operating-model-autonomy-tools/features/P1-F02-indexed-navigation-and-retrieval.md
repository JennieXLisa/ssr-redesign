# P1-F02 — Indexed navigation and information retrieval

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P1-F01`, `P1-F03`, `P1-F07`, `P1-F08`, `P1-F09`

## Purpose and concrete outcome

Provide a complete path from known or discoverable indexed subjects to exact source and accepted analysis. Finish the previously approved source/search cursors, fresh-result notices and relationship/catalogue queries without introducing another knowledge or source system.

## Existing implementation and ownership

Reuse tooling source_handlers/metadata_handlers/distributed_handlers, query.analysis_records and accepted-result readers, SourceResolver, manifest/index and conservative symbol_graph resolution. The current contracts in contracts/TOOLS.md close every formerly open interface and cursor choice; the original 101 approved requirements and 144 scenarios are preserved in this feature’s companion ledger.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P1-F02-C01.** Use the exact tool variants, ordering, text codecs and continuation payloads in TOOLS.md. Known IDs never require name rediscovery; exact name/path filters remain conjunctive; no lookup creates a binding or vulnerability conclusion.

**P1-F02-C02.** Source pages use the full indexed symbol or requested file range and original byte/hash coordinates. Long lines may split at valid characters. Cursors are HMAC-authenticated navigation, independently authorized, replayable and work-slot independent.

**P1-F02-C03.** Search continuation authenticates query/selection/matcher digests and last safe file/match position, not preview progress. Repeat the same query/selection on continuation. Preserve original-file anchors, nonoverlap, individual occurrences and explicit zero-length failure.

**P1-F02-C04.** Use the official pinned google-re2 capability with strict supported decoding. Timeouts return a safe progress boundary and an incomplete result; persistent size/encoding omissions stay visible across all pages. Repeated no-progress returns a repairable stopping error instead of endless rescanning.

**P1-F02-C05.** Analysis discovery registers durable exact-subject/filter interests using original lookup H; listings are H-bounded, availability-ordered and independently refreshed. Exact detail reads never substitute new results. Notices bind to actual model requests and durable response outcomes.

**P1-F02-C06.** File browsing is manifest-backed and has no side-effect subscription. Relationship queries preserve direction, occurrences and resolution provenance; self edges appear once for BOTH, restricted target metadata stays hidden, incoming calls require resolved target equality.

## Inputs, outputs, and state

Normative field tables and cursor algorithms are in TOOLS.md; publication/interests/notice transactions are in STATE.md; initial bounds and atomic persistent-key provisioning are in CONFIGURATION.md. These documents jointly resolve former open questions, not new alternatives left to the implementer. No page-specific persistence is required except existing accounting/operation receipts and durable query interests.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Implement selectors and indexes

Resolve file_id, symbol_id, exact names and manifest directories with parameterized bounded queries. Keep authorized filtering before grouping/paging, direct-parent semantics, canonical path order and existing ID generation.

### Step 2: Implement one cursor codec and typed payloads

Create the single project key via the serialized provisioning path. Domain-separate SOURCE, SEARCH, SYMBOL_LIST, FILE_LIST, RELATIONSHIP_LIST and ANALYSIS_LIST payloads. Enforce length and canonical form before accepting positions. Do not import controller-private token utilities.

### Step 3: Build source and search adapters

Use the same verified reader. Create bounded source pages; create the isolated RE2 adapter and byte map; implement positioned search and pending-match continuation. Literal exact mode must function without optional regex capability.

### Step 4: Integrate artifact availability and notices

Implement registry/sequence/interest transactions through their owners, then request-bound batches and acknowledgments in the runner. Attach notices only after final request composition, not by mutating source strings or inventing provider tool IDs.

### Step 5: Run cross-page and cross-attempt contracts

Use preserved T01–T144 plus completion tests below. Compare full occurrence sets under page sizes 1/7/25, UTF-8/CRLF, same-file multi-worker replay and interrupted acknowledgment. Record actual transport hashes and installed matcher identity.

## Failure, concurrency, and recovery

A cursor from another review, policy generation or matcher digest fails explicitly. Lost key requires explicit repair, never automatic regeneration. A lookup that reads a page but fails interest persistence is not successful lookup-with-interest; replay uses its original H. H does not freeze current permissions. Search cannot claim completeness for a skipped file or failed decoding.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P1-F02-CT01 | Same query resumed on a different worker | Same match start; no inherited source-read credit. |
| P1-F02-CT02 | Match discovered but preview does not fit | Next cursor retains that occurrence. |
| P1-F02-CT03 | Regex ^/word-boundary after cursor | Original file context preserved. |
| P1-F02-CT04 | D20 published between H read and interest write | Appears in lookup or later notice, never lost. |
| P1-F02-CT05 | Response recorded before notice ACK crash | Recover ACK without inference. |
| P1-F02-CT06 | Artifact withdrawn then restored after H | Old listing excludes new epoch; notice/refresh can expose it. |
| P1-F02-CT07 | Two cursors and two parallel readers | No shared mutable position or authority. |
| P1-F02-CT08 | Matcher repeatedly times out on same position | Explicit progress blocker; no hidden skip or infinite retry. |

## Do not overengineer or expand scope

No streaming-regex implementation, per-page database session, search indexing rewrite, semantic lookup model, live filesystem browser, notification service, or unbounded result-set copy.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.

## Earlier approvals

Retain the [original approved requirements](P1-F02/APPROVED_REQUIREMENTS.md) and [original acceptance scenarios](P1-F02/APPROVED_TESTS.md). The complete source documents and checksums remain in the historical checkpoint.
