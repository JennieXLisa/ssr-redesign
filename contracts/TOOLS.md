# Agent-facing tools and common contracts

Version: collaborative-v1. This is a normative host contract, not a claim that these surfaces are implemented. Agent schemas are a provider-supported projection of it. The host always enforces the full discriminated input variants, unknown-field rejection and semantic checks. The new runtime exposes only the frozen collaborative-v1 projection; old stored schemas remain historical records, not a fallback execution route.

## 1. Common values and outcome envelope

IDs are existing opaque identifiers, nonempty strings bounded to 200 characters. A `Subject` is exactly `{kind: "symbol"|"file"|"candidate"|"artifact"|"relationship", id}`. Every supplied subject resolves within the current execution's bound review/snapshot; no agent-facing override selects another snapshot. Relative paths are exact manifest spellings; root directory input is `""`, not `/`. Path comparisons and ordering use UTF-8 byte ordering of the canonical manifest path, matching database BINARY ordering; no case folding or normalization.

`SourceRef` is a host-authenticated reference to exact snapshot/file/byte/hash metadata, not an evidence ID. `EvidenceRef` is an existing evidence ID with its original analytical claim/provenance. `ArtifactRef` selects an exact immutable accepted-result body. Do not interchange these reference kinds by guessing.

Every result uses:

```json
{
  "contract": "collaborative-v1",
  "status": "OK",
  "data": {},
  "issues": [],
  "page": {"next_cursor": null, "exhausted": true},
  "completeness": {"scope_complete": true, "omitted_count": 0, "reason": null},
  "effect": {"state": "NONE", "operation_id": null, "receipt_id": null}
}
```

`status`: OK, PARTIAL, REJECTED, UNAVAILABLE, RETRYABLE, OUTCOME_UNKNOWN. `effect.state`: NONE, PREPARED, COMMITTED, UNKNOWN. Only bounded source-free semantic operation receipts enter ordinary persistence. Tool-read data containing source belongs only to the normal model context and separately governed transcript, not this envelope copied wholesale into ssr.db.

Each issue: `{code, location, message, retry_kind, repair_action, details}`. Location is a JSON pointer. Issue/IssueDetails and repair_action are closed shapes in hardening-v1.schema.json; details expose only expected type/maximum, observed integer, expected contract and reference kind. Per-code disclosure still applies; no raw exception, SQL, secret, protected identifier or arbitrary source echo. `retry_kind`: FIX_INPUT, MORE_ANALYSIS, RETRY_SAME_OPERATION, HOST_RECOVERY, NONE. Return independent errors together up to 16 plus omitted count; stop on bad identity/authorization/integrity or missing prerequisites. Unknown/unavailable protected subjects use nondisclosing errors.

Freshness notices are an explicit host-context attachment at the next normal turn, not fields injected into a source string or fake provider tool call. Their budget counts toward the actual outgoing request. Payload: `{batch_id, subject, new_result_refs, observed_through, count, omitted_count, action:"FETCH_EXACT_OR_REFRESH"}`. The internal batch ID/sequence is not a result-consumption receipt.

## 2. Navigation inputs

All queries accept optional `limit` where applicable. Continuation is a distinct input variant: never combine a cursor with a changed selector. For source search only, repeat `query`, `mode`, `flags`, and `selection` with the cursor so its digest can be checked without embedding search text in the token.

| Tool | Initial input / exact selection | Data returned |
|---|---|---|
| `review_context` | optional section: ASSIGNMENT, CAPABILITIES, WORK_PROGRESS, RESOURCE_STATUS | Owned task/revision, authorized capabilities, bounded progress and accounting; never the whole project graph. |
| `symbol_get` | `{symbol_id}` | Indexed identity, names, kind, parent and ranges; no source body. |
| `symbol_list` | optional `file_id` OR `path`; optional `local_name` OR `qualified_name`; optional `parent_symbol_id`, `kinds`, `limit` | All filters conjunctive, parent means direct indexed parent, exact case-sensitive names; default no name lists permitted symbols. Stable `(path,start_byte,symbol_id)` pages. No inferred call binding. |
| `file_list` | `mode:BROWSE` + `directory`; or `mode:FIND` + optional `filename` OR `path`, `directory`, `recursive`, `languages`, `classifications` | BROWSE immediate visible children; FIND `recursive:false` default, explicit true for descendants. Root `""`. Sort directory entries before files then exact path; directories derived from visible manifest entries, dedup before paging. |
| `source_stat` | `{file_id}` | Manifest/inventory metadata, permitted readability and exact line count when verified; no content. |
| `source_read` | `{symbol_id}` OR `{file_id,start_line,end_line}` OR `{cursor}` | Original selection, exact returned original-byte range/hash, content, encoding, partial-line indicators, SourceRef and next cursor. Symbol default full indexed range; lines 1-based inclusive with canonical byte conversion. Empty files return NO_READABLE_LINES with authoritative line count zero and no SourceRef; do not invent a readable line or evidence interval. |
| `relationship_query` | `{symbol_id,kinds,direction:IN\|OUT\|BOTH,limit?}` | One-hop existing edges; real orientation; resolved targets, authorized unresolved locators and attributed alternatives; original occurrences. Self edge appears once in BOTH with `directions:[IN,OUT]`. |
| `source_search` | `{query,mode:LITERAL\|REGEX,flags:{case_sensitive,multiline,dotall},selection,limit?}` | Separate match/preview ranges, file and optional unambiguous containing symbol, original-byte hashes, per-page/cumulative scan limitations and search cursor. |
| `document_query` | `{subject,result_kinds?,include_superseded:false,limit?}` | Compact available-artifact index and separate work status. Registers equivalent durable interest; initial listing H in same read view. Default available current results; no automatic source/body. |
| `analysis_get` | `{artifact_id,section?,cursor?}` | Exact immutable accepted artifact via owning reader; no substitution or merge. Detail pages bind artifact hash + section + byte/field position. |
| `knowledge_query` | existing typed scope/kind filters, bounded | Existing accepted FACT/HYPOTHESIS/QUESTION records with provenance and uncertainty; never promote model prose to source. |
| `analysis_interest_release` | `{subject,filters}` | Retire only the current work's matching interest; idempotent bookkeeping, not cancellation of producer/review work. |

Relationship result pages use original review-change H for model/material relationship publications. Immutable extractor edges are generation zero. Stable `(source_path,callsite_start,relationship_id,occurrence_id)` order, target visibility rechecked. A restricted target becomes `{resolution:"RESTRICTED"}` with no ID/name, while an authorized origin remains available. Absence of resolution metadata is NOT_RECORDED, not UNRESOLVED proof. Incoming confirmed CALLS require recorded target equality; resolver alternatives are outgoing attributed context, not confirmed inbound matches.

`selection` for search is exactly one of `{kind:"FILES",file_ids:[...]}`, `{kind:"DIRECTORY",directory,recursive,languages?,classifications?}`, `{kind:"SNAPSHOT",languages?,classifications?}`. Metadata visibility and readable classification filter before bytes are fetched. An explicit invalid file fails selection rather than silently disappearing. Pattern in LITERAL mode treats punctuation literally; multiline/dotall flags are invalid there because exact embedded newlines already work.

## 3. Source/search cursor format and matching

Token: `c1.<base64url(canonical_json_payload)>.<base64url(hmac_sha256)>`. No padding. Authenticate `b"ssr:collaborative-v1:" + kind + b":" + exact_payload_bytes`; verify before using decoded coordinates. Bounded parsing rejects duplicate keys, floats for positions, unknown fields, malformed UTF-8, unsupported versions and out-of-order positions. HMAC key generation is in CONFIGURATION.md. No credentials or source text in tokens. Reuse codec, not semantics, across kinds.

All payloads bind key_id/generation, review_id, snapshot_id, kind, policy/contract digest and original selection identity. SOURCE adds file_id/hash, original start/end, next_byte and optional symbol ID. Metadata list kinds add canonical query digest, manifest/graph identity, stable last tuple and H when mutable. SEARCH binds query/flags digest, selection digest, matcher artifact/options digest, last file path/hash, next_match_start, optional pending_match range and cumulative omission counters. The query/selection must be supplied unchanged on continuation. Cursors are replayable across authorized attempts in the same review, never mutable shared offsets.

Initial matcher selection is official google-re2 in non-POSIX, leftmost-first mode. `case_sensitive:true`, `multiline:false`, `dotall:false` defaults; explicit inline RE2 flags follow the supplied pattern and are part of its digest. Pattern alternatives preserve engine semantics. No look-around, backreferences, zero-length occurrence skipping, fuzzy fallback or implicit whole-word rules. Literal case-sensitive uses exact text search; literal insensitive uses RE2 literal mode for Unicode simple case behavior without transformed-string offsets.

Decode using the verified recorded encoding with strict errors. Initial supported codecs: UTF-8 (including BOM as the U+FEFF code point), ASCII, ISO-8859-1. Preserve LF/CRLF bytes; no universal-newline translation, NFC or full casefold replacement. RE2 Python string indexes must be converted through a tested character-to-original-byte map. Build one bounded map per current file, not per match; ASCII/Latin-1 use direct offsets. Codecs outside this set are explicit search omissions, not inventory or coverage success.

Search operates on the full original decoded file with a positioned search call. Resume position is the end of the last returned nonempty match, or the exact start of a pending unreturned match. Do not slice the prefix and create false ^/\A/word boundaries. Prefer line-aligned previews centered on the match; long matches expose full match identity and a clipped preview. Returned previews count only their actual source bytes. All selected data examined internally is separate host scanning work, not model source credit.

Search continuation algorithm:

1. Validate current execution, token if any, query/selection/contract digests and remaining scan budget.
2. Enumerate visible readable manifest files in canonical path order starting at the current file, never before completed files.
3. Verify the current file, decode/map once, and run bounded positioned matching with original file context. Use the host matcher pool; its jobs execute only the trusted matcher, never target code.
4. Accumulate individual non-overlapping occurrences until output allowance is reached. Keep the first unreturned occurrence at its start in the next token; lookahead is not delivered progress.
5. If a full file completes without another hit, advance to the next file. Reopening the one partially searched file may reverify/decode it; account that work, and do not promise resumable internal regex automata.
6. Timeout/interruption without a matcher-certified safe position returns PARTIAL and a cursor at the last emitted-match boundary or current file start. Explicit persistent file-size/encoding limitations may advance past that file while accumulating a named omission; final scope_complete stays false. An oversized query/zero-length occurrence fails the query and supplies no same-query continuation.
7. Repeated no-progress at the same boundary returns SEARCH_PROGRESS_BLOCKED, with narrower-scope/changed-query guidance. Do not spin through the same file indefinitely or silently skip an unexamined region.
8. Only issue a next token when it fits the response. If even a minimal hit+cursor cannot fit, return RESULT_UNREPRESENTABLE without consuming that hit. Response replay starts at the same query position, but every actual provider/host operation retains real resource accounting.

The native matcher runs in a fixed host-owned process pool (default two). Kill/recreate only a timed-out matcher child, never another analytical worker; no per-search durable job subsystem. Verification/decoding may still consume bounded memory and I/O. Shared admission must enforce pool, file-size and memory bounds before starting.

## 4. Nonterminal proposals and final submissions

| Tool | Model-authored input | Host action / result |
|---|---|---|
| `checkpoint_state` | `{expected_sequence,state:{facts,hypotheses,unknowns,next_action,subject_refs,evidence_refs,source_refs,artifact_refs,source_cursors,search_cursors,answer_refs,request_refs}}` | Same owner for host-requested and ordinary saves. Revision CAS, source-free validation, checkpoint ID/sequence. No automatic yield. |
| `report_lead` | `{hypothesis,observations,subject_refs,evidence_refs,source_refs,unknowns,requested_check,category?}` | Validate and atomically record SEEDED candidate + independent work intent; return lead/candidate/task refs and queued/associated/budget reason. No wait for parent completion. |
| `request_context_review` | `{question,subjects,assumptions,evidence_refs,source_refs,requested_facets,blocking}` | Register/join/routable request; return exact request ID, routing disposition and available answer if exact compatible reuse. No automatic yield or finalization. |
| `publish_context_answer` | `$defs.ContextAnswer` in hardening-v1.schema.json | Independent prefix-backed answer artifact; exact request/facets, no canonical task completion. |
| `yield_work` | `{checkpoint_id,reason,request_ids}`; current input bound by request receipt | Commit preparation only while RUNNING; stop inference, settle predecessor, then guarded WAITING/PENDING publication. Never clear lease early. |
| `submit_focused_analysis` | `$defs.FocusedResult` | Exact question, checked subjects, observations/counterevidence, registered leads and explicit disposition. |
| `submit_context_review` | `$defs.ContextResult` | Seal the exact accepted answer artifact for the assigned request/revision. |
| `record_investigation_progress` | `$defs.InvestigationProgress` | Nonterminal NEED_CONTEXT; requires real checkpoint/requests, followed by explicit yield. |
| `stage_file_synthesis` | `$defs.SynthesisStage` | Prefix-backed bounded journal append with manifest hash and revision CAS. |
| `submit_file_synthesis` | `$defs.SynthesisSeal` | Small final identity seal, full host validation/publication; never full-unit arrays in model arguments. |
| Other role-specific `submit_*` | Mechanically projected exact existing semantic contract under ROLE_PROJECTIONS.md | Preserve required analytical fields and validators; no generic analysis dictionary. |
| `read_batch` | `{items:[{key,tool,arguments}]}` | Up to configured bound; known independent read-like tools only. Individually identified outcomes, aggregate budget and authorization. |

`input_token` is a host-issued revision/digest reference, not authority. Each exact submission tool retains its full role-specific analysis fields (file/symbol coverage, path, controls, impact, falsifier verdict). The smaller envelope removes only mechanically known identity and metadata. It does not flatten all result kinds into a generic unrestricted object.

Answer outcomes: ANSWERED, CONTRADICTED_ASSUMPTION, INCONCLUSIVE, NEEDS_DIFFERENT_SCOPE. These describe the response to a question, not candidate validity. Negative answers are useful completion. A malformed answer is not an INCONCLUSIVE analytical result.

## 5. Operational rules

Read-like batch whitelist: source/symbol/file/relationship/stat/detail/knowledge queries and document_query. document_query may create host interest bookkeeping, but not analysis work. Each subrequest uses its own database read connection or runs sequentially; never concurrent use of one SQLite connection. Submission, checkpoint, lead, context request, yield and operator actions are excluded. Preserve key order in results regardless of execution completion order. Stop undispatched items on cancellation with explicit NOT_EXECUTED; do not pretend batch atomicity.

The final provider request includes source/result notices only within the combined context ceiling. Record what actually remained after trimming. Remove safe obsolete content only with durable references/checkpoints. A prepared tool result not sent to the model grants no read credit; all actual processing/delivery resources remain accounted. Candidate gates inspect host delivery records, never model assertions that it read a whole file.

Error/repair does not reset resources or force accepted success. Recoverable schema errors permit repair, analytical gaps permit ordinary research, stale inputs require explicit refreshed material, authorization/integrity issues stop the unauthorized operation, and transient persistence failure replays the validated host operation.


Checkpoint `next_action` is `{kind: READ|QUERY|REQUEST_CONTEXT|INVESTIGATE|SUBMIT|WAIT, objective: string}`. Reference fields remain separate and typed. Saved search query text is optional and subject to the source-free guard described in STATE.md; raw query text is never automatically durable. SourceRef/cursor tokens have the bounded token length, not the shorter existing-ID limit. Whole input/checkpoint encoded-byte bounds still apply after per-field validation.

## Hardening contract binding

The combined executable tool variants in `schemas/tool-inputs.schema.json` and `schemas/hardening-v1.schema.json` must agree. INPUT_REVISIONS.md governs actual delivered input tokens; PREFIX_RECEIPTS.md governs nonterminal producer proof; FILE_SYNTHESIS.md governs all canonical synthesis stages/seals; CONTEXT_BUDGET.md governs final dispatch and RESOURCE_BOUNDS.md governs finite work. A source cursor remains cross-attempt navigation; an input token is bound to one exact attempt/request-observed revision.
