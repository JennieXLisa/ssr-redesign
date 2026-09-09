# P4-F04 — Evidence and sensitive-data boundaries: implementation plan

Updated: 2026-09-09. Documentation only. Read the [feature](../P4-F04-evidence-and-sensitive-data.md), [STATE.md](../../../contracts/STATE.md), P1-F03 references and the implementation repositories' existing content policy. Preserve exact permitted source/transcript behavior; do not invent blanket redaction or a copied-source knowledge database.

## Contract-hardening integration — Evidence closure across input and prefix manifests

Bind source/evidence references to actual earlier delivery records and immutable snapshot ranges. The runtime prefix's delivery_manifest_hash references a paged host closure; it does not assert that all files scanned internally were read by the model. Revalidate both provenance and current visibility before consuming it.

Prefix bodies and input/manifest metadata in ssr.db remain source-free; sensitive arguments/query strings and capture records never migrate there for convenience. Hash mismatch, missing required prefix and foreign snapshot must deny consumption. Test UTF-8/long-line evidence, absent capture proof, same-response requested read, historical producer identity and staged reference-set closure without unbounded payload copies.

Normative source: [hardening contract index](../../../CONTRACT_HARDENING.md). Preserve the existing feature procedure below except where this explicit correction replaces it; implement the linked exact schemas, not a local incompatible approximation.

## 1. Trace data by type and destination

Build a concrete flow map for SourceSegment/VerifiedFile bytes, source tool previews, provider messages, tool arguments, checkpoint state, knowledge/artifact prose, operation receipts, notices, SDK DTOs, logs and exports. Label each destination as ordinary source-free state, model context, explicitly enabled sensitive transcript/content, or private host secret storage.

Audit generic serialization points: dataclass-as-dict, exception repr, structured logger fields, operation prepared payloads and API response conversion. A SourceSegment contains raw content; serializing the entire object into ordinary metadata is prohibited even if most fields are harmless. Use explicit allowlisted projections per destination, not name-based removal of any field containing the word 'source'.

## 2. Original-byte evidence path

All material anchors resolve against the assigned immutable snapshot. Keep canonical path, half-open original-byte interval, file hash and span hash authoritative. Display line/column values derive from the original encoding; labels, normalization, CRLF changes and preview omission markers are not source bytes.

Prepare evidence through the existing SourceResolver/EvidenceRepository and source-free prose guard. Preserve symbol containment where supplied. A range spanning more than one symbol must not be falsely attached to one symbol to pass schema validation. Read-only navigation may reopen broader authorized source, but accepted evidence still needs exact verified coordinates.

Do not substitute the live checkout when snapshot bytes are missing or changed. Integrity failure remains distinct from unsupported encoding or no search match. Cursor/SourceRef authentication proves token integrity, not source availability or analytical truth.

## 3. Delivery versus scanning

Source returned by a tool carries an exact delivery descriptor. At final model-request composition, record only descriptors whose content was actually retained. A host search may scan a whole file but return one preview: only the preview's bytes were delivered. A metadata lookup or accepted summary gives no source-read interval.

Keep attempt ownership in delivery_records. New attempts can reuse immutable refs but cannot inherit a predecessor's inspection claim. Candidate/unit validators query actual current-attempt intervals when their role requires direct reading. Repeated transport remains real cost even when interval union avoids double-counting completeness.

## 4. Safe ordinary persistence

Before saving checkpoint, lead, contextual answer, summary, result, operation record or notice, run the existing safe-prose/credential and source-copy guards at the owning acceptance boundary. Retain their documented narrow allowance for technical identifiers or verified short expressions rather than globally stripping all useful terminology. Do not relax the guard for a new tool just to get its schema accepted.

Search query strings are especially sensitive. Store query digest and structural selection, and only save text when the guard permits it. Otherwise record omission reason and require resupply/fresh query on continuation. Never put a raw query into cursor metadata or error logs automatically.

Ordinary records keep exact IDs, hashes, source-free analysis, field-specific codes and real producer/consumer/acceptor associations. Key material, authorization headers, raw provider bodies and opaque provider reasoning are not portable ordinary state. A convenience reference is not a second source store.

## 5. Preserve governed sensitive capture separately

When full transcript/content capture is enabled and required, the transcript owner records the exact permitted payload bytes and seals them through its existing contract. Do not mutate or redact those required content bytes merely to make an ordinary-storage leakage test pass. Transport credentials and the cursor-authentication secret remain excluded even in full capture.

Model-authored mid-review artifacts use real completed-turn/prefix receipts from this store. Project state receives only source-free receipt links/digests. If a required transcript is missing/corrupt, the artifact remains pending; no ATTACH-database shortcut or fabricated receipt resolves the gap.

Recovery preserves original captures and adds any explicitly allowed attestation separately. Later attempts do not rewrite the previous transcript to make its request/result IDs match newer state.

## 6. Producer and consumption provenance

Evidence content identity, original creator, current user and accepting artifact are separate. An exact evidence reuse keeps original created_by and adds current usage provenance. A changed claim produces another immutable evidence item. Host/analyzer producers have real host operation/tool identities, not invented model runs.

A notice is an advertisement only. Its delivery receipt does not imply artifact retrieval, adoption, source inspection, coverage completion or candidate validity. Keep these facts separate in API/metrics projections; a generic field named 'seen' must not conflate them.

## 7. Public SDK and export boundaries

Normal query DTOs remain source-free. Explicit source/transcript reads use their existing sensitive APIs, opaque handles, policy checks and byte limits. The controller projects these through supported SDK services; it does not open harness databases or filesystem content directly.

A new current finding does not automatically export source, change retention or enable transcript capture. Export is a separately authorized operation using current candidate validity and recorded source/evidence refs. Historical package bytes remain immutable. Error handling must not disclose protected paths/IDs merely to explain why an export failed.

## 8. Sentinel-driven tests

Create disposable synthetic fixtures with unique source snippets, credentials, a cursor secret, provider body markers and source-derived search queries. Run source read/search, checkpoint, lead/answer publication, diagnostic failures, notice delivery, batch composition and export projections. Inspect ordinary database text/JSON columns, logs, events and normal SDK responses for disallowed sentinels.

With full capture enabled, verify exact permitted source/tool/provider bytes remain in the separate transcript store and their hashes match. Verify transport keys/cursor secret remain absent from both ordinary output and sensitive content captures. With capture disabled, required receipt policy must either permit source-free exchange evidence or block the feature explicitly; never pretend a full transcript exists.

Test UTF-8, CRLF, long-line preview labels, cross-symbol ranges and changed snapshot bytes. Compare hashes to original source, not rendered text. Reuse evidence from another attempt and assert original creator plus new use, with no inherited read credit. A normal lookup or new finding event must not create an export file.

## 9. Implementation commits and exit

Add explicit safe projection helpers/types at existing owners; wire source-delivery descriptors; apply guards to every new persistence path; integrate real turn receipts; test controller/export projections. Keep target execution prohibited while allowing SSR's own isolated test suite. Completion evidence includes a field/destination matrix, exact-byte assertions and sentinel scans, not a general statement that data is 'sanitized'. No new source filesystem, universal regex redactor, direct-SQL agent tool or implicit retention change belongs here.
