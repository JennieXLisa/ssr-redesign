# P1-F02 — Detailed implementation plan

Updated: 2026-09-09. Status: developer implementation guidance; runtime implementation and application tests have not been performed.

Read with the [feature specification](../P1-F02-indexed-navigation-and-retrieval.md), [approved requirements](APPROVED_REQUIREMENTS.md), [approved test scenarios](APPROVED_TESTS.md), [baseline map](../../../BASELINE.md), and shared [tools](../../../contracts/TOOLS.md), [state](../../../contracts/STATE.md) and [configuration](../../../contracts/CONFIGURATION.md). This is the feature's build plan, not an instruction to reconstruct an implementation from the five-step overview. Helper names below are proposed private interfaces, not existing public SDK methods.

## 1. Change map and implementation slices

The inspected refactor keeps execution authorization and dispatch in `ssr.tools`; result construction in `ssr.tooling.source_handlers`, `metadata_handlers` and `distributed_handlers`; source integrity in `ssr.source`; and final model-request composition in `ssr.agent` with policy/event helpers. Verify these locations in the actual authorized checkout. Preserve existing facade class identities and legacy contract hashes.

Implement four slices in this order: A, source selectors and byte-accurate pagination; B, index/catalogue/relationship queries and text search; C, exact artifacts and publication-bounded discovery; D, durable interests and notice delivery. A/B can be tested independently. Do not enable a successful C lookup-with-interest until its registration transaction exists. D requires completed-exchange metadata from the runner and availability ownership from P4-F01; missing prerequisites are release blockers, not permission to simulate reliable delivery.

Before changing scope checks, enumerate callers of `_file_ids`, `allowed_paths`, `allowed_symbol_ids`, assigned-range callbacks and `_source_read_ranges`. Label each call RESEARCH, SUBMISSION or EXECUTION. Remove assignment clipping only from research. Keep owned-unit read-completeness and canonical contribution membership checks.

## 2. Normalize source selections into one internal value

Use an immutable internal selection with `snapshot_id`, existing `file_id`, canonical path, expected file hash, original half-open byte range, next byte, selector kind and optional symbol ID. Obtain execution snapshot/policy from the broker, never a model-supplied override.

For `{symbol_id}`, query symbol ID AND bound snapshot; obtain the indexed full range and file locator, not only its body. For `{file_id,start_line,end_line}`, resolve the file and convert inclusive line numbers against verified original bytes. For `{cursor}`, decode the SOURCE continuation, restore the original selection, and recheck all bound identities. Reject mixed variants before reading source. An unknown ID must not fall back to a name search. Empty files yield the documented no-readable-lines outcome.

Apply P1-F01 research policy to the resolved file. Pass a narrowly constructed internal single-file `SourceScope` to the existing resolver where needed; this does not alter assignment ownership. Keep canonical path validation, classification checks, safe regular-file handling, file-size/hash verification and range bounds in the existing source authority. Never read the mutable original checkout as a fallback.

```text
selection = normalize_selector(execution, arguments)
require_current_attempt(execution)
research_policy.authorize(selection.file, execution.bound_policy)
verified = verify_snapshot_file(selection)
page = build_page(verified, selection, remaining_allowances)
return page, actual_delivery_descriptor(page)
```

The descriptor is a proposed result of preparation, not immediate source-read credit.

## 3. Fit source pages to the serialized response

Compute the maximum candidate span from configured source-page size and remaining per-call, combined-tool and context allowances. Reserve metadata/cursor overhead first. Do not equate original source bytes, Unicode characters, JSON bytes and provider tokens.

Prefer a complete line ending within the allowed cut. If the first line is longer, use a valid encoded-character boundary and mark a partial line. Preserve CRLF and original byte coordinates. Display line numbers, truncation markers and labels must remain outside the source string used for hashing. Hash exactly the original returned span. If no character plus required metadata fits, return a bounded representation/resource failure, not a cursor that makes no progress.

Serialize the candidate envelope and measure it. If too large, shrink the text on a valid boundary, rebuild coordinates/hash/cursor and measure again. Do not let downstream context trimming cut a content string while retaining its old hash. When a prepared page is omitted from the final model request, it grants no delivered-source interval. Retain the final request-to-delivery association through the existing accounting owner.

`page.exhausted` means the selected range is exhausted from this cursor. A full-symbol-read predicate independently checks the union of original-byte intervals delivered to this attempt. Receiving first and last pages does not cover the missing middle. A replacement attempt inherits references/checkpoints, not read credit.

## 4. Implement cursor encoding once, with typed payloads

Use the contract's `c1.payload.tag` encoding, canonical UTF-8 JSON, unpadded base64url and HMAC-SHA-256. Include cursor kind/version, review, snapshot, policy and original selection in the authenticated payload. Bound token length before decoding. Reject duplicate JSON keys, noncanonical representation, booleans where integers are required, invalid ranges and unsupported kinds. Verify the tag with `compare_digest` before trusting bound coordinates. SOURCE, SEARCH and list cursors are distinct variants even though they share a codec.

Provision the 32-byte project secret only through the serialized coordinator initialization/repair path specified in CONFIGURATION.md. Use exclusive creation, restricted permissions, safe-path checks, durable file publication and a provisioning record. Workers load the established secret; missing state after provisioning is an error, not a reason to generate a replacement. Rotation changes the generation and invalidates convenience cursors, not durable evidence coordinates. Never put the key in prompt configuration, logs, transcripts, ordinary database fields or exports.

Cursors are immutable positions. Replay starts at the same position; no server pointer advances. Another authorized attempt in the same review may use one. A different review, stale attempt or newly disallowed file cannot. A current tighter allowance may produce a smaller page. Returned continuation derives from the actual page end.

## 5. Implement metadata queries without per-worker catalogues

`symbol_get` stays metadata-only. `symbol_list` supports exact local OR qualified name, file ID OR canonical path, direct parent and kind filters. Apply every supplied filter conjunctively in parameterized SQL. Sort by `(path,start_byte,symbol_id)` using canonical path order and fetch a lookahead row. One visible result with lookahead is not uniqueness. An unfiltered listing is paginated, not loaded fully into Python.

Resolve file IDs through existing locator authority. A deterministic UUID/hash cannot be decoded into a path: if no inverse index exists, populate the small manifest association specified in STATE.md at indexing, rather than recompute every file's hash per call.

`file_list` BROWSE derives immediate visible children under a component-bounded directory; root is `""`. Apply visibility before grouping, deduplicate directories before pagination, and use directory/file plus canonical path ordering. FIND respects explicit recursion, exact filename/path and classification/language filters. `src/api/` must not select `src/api_old/`. A parse error or context-only file remains discoverable where metadata is permitted, but missing inventory is not an empty successful parse. No live filesystem walk, source read, task creation or interest registration occurs in catalogue browsing.

## 6. Relationship query implementation

Preserve original source-to-target orientation for IN, OUT and BOTH. IN confirmed calls require resolved target equality. A target-name match, unique declaration name or resolver alternative does not satisfy that predicate. OUT retains authorized unresolved originating calls and their recorded locators. Join resolver decisions through compatible relationship/occurrence identity and resolver version; missing resolution metadata is NOT_RECORDED, not fabricated certainty.

Return each recorded occurrence/callsite. Distinct calls between the same functions cannot collapse into one unexplained edge. BOTH returns a self-edge once. Filter protected endpoint metadata without converting an inaccessible endpoint into a public guessed declaration. Accepted model-authored relationships retain their provenance and visibility gates. The query does not modify canonical relationships or the same-file scheduling dependency graph.

Use the relationship ordering/revision in TOOLS.md. Reuse public query plan construction where compatible, but keep model-facing scope enforcement at the broker boundary. Test against a fixture containing a resolved call, two repeated callsites, an unresolved callback, self-recursion and an inaccessible endpoint.

## 7. Per-file text matching and original-byte mapping

Compile literal or the explicitly enabled pinned RE2 mode once per tool call. Literal is available without the optional regex adapter. Validate mode/flags/pattern size before scanning. Unsupported regex constructs cannot fall back to Python backtracking regex. Run the matcher within the selected process/resource boundary; return structured failure if the capability is absent.

Enumerate permitted manifest files in canonical path order. Read and verify one file at a time. Decode only supported encodings strictly. Preserve a mapping from matcher positions to original byte offsets; validate it with multibyte characters, BOMs and CRLF. Never apply offsets from case-folded or normalized text to original bytes. Follow TOOLS.md's case-matching policy and report unsupported encodings explicitly rather than replace characters.

The entire file is the matching context. Do not split on display lines or source-response pages. Use positioned search on the original buffer, so `^`, word boundaries and multiline constructs see original surrounding text. Repeated suffix slicing can incorrectly make a continuation look like a new file start. A custom streaming matcher is not required; unsupported large input is an explicit omission/progress blocker, not a switch to weaker line-by-line semantics.

Emit non-overlapping, non-empty occurrences in `(path,start_byte,end_byte)` order. Two occurrences on one line stay separate. On a zero-length occurrence, return the specified incomplete/unsupported-occurrence outcome and retain already returned ordinary matches. Never loop or silently claim exhaustion.

## 8. Match previews and safe search continuation

Compute the complete match range first. Build a bounded preview around that match, not the first characters of its line. Hash preview bytes separately from match coordinates. Mark clipping and partial-line boundaries. Do not hash omission labels. An enclosing symbol may be attached only from an unambiguous inventory association.

Bind SEARCH cursors to query digest, exact manifest selection/filter digest, mode/flags, matcher contract/version, review/snapshot/policy, current file identity/hash and last safe match progress. Query text is resupplied on continuation; it is not reconstructible from its digest and must not be copied into ordinary metadata when source-sensitive.

If a discovered occurrence cannot fit this response, retain it as pending at its match start; do not advance past it. Continue after the full emitted match end, never the clipped preview end. A fully exhausted file advances to the next path. Re-verifying the one partially searched file is permitted and charged. Re-scanning all earlier files for each page is not the normal implementation.

A timeout only advances to a certified safe boundary. If the matcher provides no certified progress, retain the previous boundary. Count repeated no-progress attempts through the work/operation owner, not a mutable cursor; a replayed token cannot reset the limit. Eventually return SEARCH_PROGRESS_BLOCKED with narrowing guidance, not an endless retry or hidden skip. Maintain scan cost separately from source-preview delivery. Any skipped file keeps `scope_complete:false`, even on the last page.

## 9. Exact analysis retrieval and availability ordering

`document_query` resolves the requested subject inside the execution's review/snapshot and uses existing subject-to-result associations. Project recorded summaries only; no summarization inference. Separate usable results from work status: queued supplementary work can coexist with accepted analysis, and COMPLETED tasks can still lack required receipts.

`analysis_get` dispatches an exact artifact/result ID to its owning reader. Recheck visibility, acceptance and payload hash. D18 must not become D19 because D19 was published after discovery. Detail cursors bind exact artifact, payload hash and section. Analysis consumption is not source-read credit.

The acceptance owner creates an availability event/epoch in the short transaction exposing a consumable artifact. Allocate sequence inside that serialized commit; do not reserve sequence blocks in workers. A unique transition key makes replay idempotent. Transcript storage remains independent: verified prefix/attempt receipts are prerequisites, not a distributed transaction claim.

For the initial lookup, read H and the bounded result page through one short consistent read view. Close it. Revalidate work and insert/reuse its interest at original H in a short write. Do not substitute the newer counter. A publication between these steps remains after H. Preserve an existing interest's pending progress. A failed registration is not successful lookup-with-interest.

Analysis continuation considers active availability epochs `sequence <= H`, then keys after `(sequence,artifact_id)` in ascending order. Recheck current visibility. An artifact restored after H cannot reenter through an obsolete epoch. Refresh opens a new traversal without resetting old cursors or acknowledging notices. No transaction remains open across model turns.

## 10. Durable interests and request-bound delivery

Key interest by review, logical work, exact subject and normalized filters. Register even for an empty authorized lookup. Restore it for another attempt of the same work, not another task in the same slot. Waiting preserves it; logical completion/cancellation closes it. Persist metadata only.

Inspect interests in bounded round-robin order. Read availability changes after the processed position; filter currently permitted, relevant results. Irrelevant checked events may advance processed state without claiming advertisement. Do not pass an unrepresented eligible event because the response budget filled. A bounded coalesced batch records the exact inspected span, included IDs and explicit omitted-detail count. Keep one ordered outstanding batch per interest.

Attach notices at final ordinary request composition, not by altering source strings or forging tool-call IDs. Record batch-to-request-to-attempt identity and digest only when the batch survived final trimming. After a valid corresponding response is durable, acknowledge exactly those batches. A malformed subsequent tool call does not undo delivery of the earlier notice. A new D21 arriving while a D20 notice is in flight remains pending.

Crash after response recording but before ACK: reconcile the exact ACK without inference. Partial/uncertain delivery remains eligible for safe repeat at a later ordinary interaction. Duplicate ACK is a no-op; a late old attempt cannot acknowledge a successor's batch or overwrite its work revision. This bookkeeping must work without full sensitive-transcript capture. It proves advertisement, not comprehension, artifact retrieval or source inspection.

## 11. Required integration tests and exit gates

Slice A: a four-page symbol, long UTF-8 line, CRLF, empty file, excluded/foreign ID, conflicting selectors, tampered cursor, lost key, cross-worker replay and changed allowances. Concatenated pages equal original selected bytes; only final-delivered intervals count. Cross-file research succeeds while foreign coverage submission fails.

Slice B: repeated names, direct parent filters, directory prefix collisions, deduplicated directories, unresolved incoming name ambiguity, repeated callsites, multiline regex, zero-length match, pending oversized occurrence, encoding omissions and timeout without progress. Compare the full occurrence tuple sequence with page sizes 1, 7 and 25. Use test strings as inert source; do not execute reviewed target code.

Slice C: D18 exact retrieval after D19 publication; private result denial; completed-task/pending-receipt state; pause lookup after H, publish D20, finish registration; fail registration and retry at original H; withdrawal/restoration after H; independent refresh and old-list continuation.

Slice D: worker restart before checkpoint, unrelated slot reuse, notices trimmed from the final request, response-recorded/ACK crash, uncertain stream, newer event during inference and duplicate/late ACK with transcripts disabled. Assert no candidate, review task or coverage effects arise merely from browsing. Interest/operation bookkeeping is the documented exception.

For each slice record exact test IDs, collection, command, exit status and fixture input hashes. Preserve the earlier T01–T144 and CT01–CT08 behavior in the companion ledgers. The documentation validator cannot certify runtime concurrency or source accounting.

## 12. Explicit non-goals and handoff evidence

No second symbol index, graph database, semantic search model, live filesystem browser, per-page database session, notification daemon, generic shell or custom streaming-regex engine. Do not pass the whole mutable broker into extracted handlers. Public capability enablement waits for truthful module mapping, paired contract tests and the required receipt paths. Missing integration is a named build gate, not justification to drop source verification or claim complete search.
