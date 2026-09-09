# P1-F02 — Indexed navigation and information retrieval

Version: 1.1 · Updated: 2026-09-09

**Implementation entry point: [Detailed feature implementation plan](P1-F02/IMPLEMENTATION_PLAN.md).** It contains the concrete selector, paging, cursor, search, query, transaction, notification and test procedures. The former five-step overview was insufficient as a developer handoff; use the detailed plan, not that overview, to implement this feature.

Document status: specified design, not implemented or application-tested behavior. Decision basis: prior explicit agreements plus [delegated engineering choices](../../ENGINEERING_DECISIONS.md). Dependencies: P1-F01, P1-F03, P1-F07, P1-F08, P1-F09, and the artifact-availability owners identified in the detailed plan.

## Purpose and concrete outcome

Provide a path from known or discoverable indexed subjects to exact source and accepted analysis. Implement the agreed source/search cursors, fresh-result notices and relationship/catalogue queries without creating another knowledge or source system.

## Existing implementation and ownership

Reuse the inspected `tooling.source_handlers`, `metadata_handlers`, `distributed_handlers`, `query.analysis_records`, accepted-result readers, `SourceResolver`, manifest/index and conservative graph resolution. These are baseline observations, not proof of the developer's installed package. Consult [BASELINE.md](../../BASELINE.md) and map actual call sites before editing. Keep public facades and historical results intact.

The complete earlier requirements and acceptance scenarios remain active companion records, not optional archival reading: [approved requirements](P1-F02/APPROVED_REQUIREMENTS.md) and [approved tests](P1-F02/APPROVED_TESTS.md). This guide does not waive them.

## Detailed requirements

**P1-F02-C01.** Use the exact tool variants, ordering, text codecs and continuation payloads in [TOOLS.md](../../contracts/TOOLS.md). Known IDs never require name rediscovery; exact name/path filters remain conjunctive; no lookup creates a binding or vulnerability conclusion.

**P1-F02-C02.** Source pages use the full indexed symbol or requested file range and original byte/hash coordinates. Long lines may split at valid characters. Cursors are HMAC-authenticated navigation, independently authorized, replayable and work-slot independent.

**P1-F02-C03.** Search continuation authenticates query/selection/matcher digests and last safe file/match position, not preview progress. Repeat the same query/selection on continuation. Preserve original-file anchors, nonoverlap, individual occurrences and explicit zero-length failure.

**P1-F02-C04.** Use the selected pinned google-re2 capability with strict supported decoding. Timeouts return a safe progress boundary and an incomplete result; persistent size/encoding omissions remain visible across pages. Repeated no-progress returns an actionable stopping error instead of endless rescanning. Literal mode remains available without the optional regex dependency.

**P1-F02-C05.** Analysis discovery registers durable exact-subject/filter interests using original lookup H; listings are H-bounded, availability-ordered and independently refreshed. Exact detail reads never substitute new results. Notices bind to actual model requests and durable response outcomes.

**P1-F02-C06.** File browsing is manifest-backed and has no side-effect subscription. Relationship queries preserve direction, occurrences and resolution provenance; self edges appear once for BOTH, restricted target metadata remains hidden, and incoming confirmed calls require resolved target equality.

## Inputs, outputs, and state

The [tool contract](../../contracts/TOOLS.md) owns serialized variants; the [state contract](../../contracts/STATE.md) owns publication/interests/notice records and transaction rules; [configuration](../../contracts/CONFIGURATION.md) owns bounds and key provisioning. The detailed plan explains their integration and safe processing order. A missing field in an adapter or a refactor mismatch is a concrete implementation gate, not permission to invent weaker behavior.

Source cursor, search cursor, artifact identity, evidence identity, logical work, worker slot and execution attempt are distinct concepts. No page-specific persistence is required solely to remember source positions. Durable interests, operation outcomes and delivery evidence have their own explicit owners.

## Ordered implementation

Follow the [detailed implementation plan](P1-F02/IMPLEMENTATION_PLAN.md), in four slices:

1. Source selectors, authorization and byte-accurate pages, including typed cursor provisioning and actual delivery accounting.
2. Symbol/file/relationship query adapters and per-file positioned search, including encoding maps, bounded previews, safe continuation and no-progress recovery.
3. Exact artifact retrieval, accepted availability sequencing, H-bounded pages and lookup-to-interest registration without a lost-publication race.
4. Work-scoped interests, bounded change scans, final-request notice attachment and response-bound acknowledgment/recovery.

Each slice has explicit algorithms and exit tests in that plan. Do not enable an incomplete composite capability simply because its individual schema validates. Existing legacy attempts keep their original policy and tool/schema hashes.

## Failure, concurrency, and recovery

Reject cross-review, wrong-kind, wrong-policy or wrong-matcher cursors. Missing established keys require explicit host repair, not silent regeneration. Registration failure after reading a lookup page is not successful lookup-with-interest; recovery preserves original H. H does not freeze current permissions. A skipped/undecodable input prevents complete-search claims. An unreturned occurrence remains pending even if its preview would overflow the current page.

A prepared result or notice that was trimmed out of the final request is not delivered. Response-recorded/ACK-not-recorded recovery settles only the exact exchange. A successor inherits navigation references and durable interests for the same work, not another attempt's source-read credit.

## Acceptance tests

These are tests to implement and run, not test results from authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P1-F02-CT01 | Same query resumed on a different worker | Same match start; no inherited source-read credit. |
| P1-F02-CT02 | Match discovered but preview does not fit | Next cursor retains that occurrence. |
| P1-F02-CT03 | Regex anchors/boundaries after cursor | Original file context is preserved. |
| P1-F02-CT04 | D20 published between H read and interest write | D20 appears in the lookup or a later notice, never lost. |
| P1-F02-CT05 | Response recorded before notice ACK crash | Recover ACK without additional inference. |
| P1-F02-CT06 | Artifact withdrawn then restored after H | Old listing excludes the new epoch; refresh/notices may expose it. |
| P1-F02-CT07 | Two cursors and two parallel readers | No shared mutable position or authority. |
| P1-F02-CT08 | Matcher repeatedly times out at the same position | Explicit progress blocker; no hidden skip or infinite retry. |

The detailed plan adds fixture construction, race barriers, expected database non-effects, page-size comparisons and per-slice verification. Retain the original T01–T144 scenarios in [APPROVED_TESTS.md](P1-F02/APPROVED_TESTS.md).

## Do not overengineer or expand scope

No streaming-regex implementation, per-page database session, second search/index store, semantic lookup model, live filesystem browser, notification service, unbounded result copy or mutable whole-broker dependency injected into every handler.

## Definition of done

Produce an actual call-site/module map, implement each slice through the owning components, execute its positive/negative/race cases, and record test collection plus tool/prompt/schema compatibility evidence. Documentation/schema validation cannot establish source-delivery correctness or concurrent publication safety. No live installation, provider spend, target execution or deployment is authorized by this documentation update.
