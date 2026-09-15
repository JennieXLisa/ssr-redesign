# Navigation API, search, pagination and errors

Refines S1-NV-R01–R23 and S1-ER-R01–R06. All operations use the same navigation/source owners, not one set of implementations for the CLI and another for agents. The executable models in `contracts/v1/models.py` define field types; production adopts those types rather than creating an unrelated DTO family.

## Operations

| Operation | Exact arguments after required `index_run_id` | Result |
|---|---|---|
| find_functions | `pattern, mode, *, case_sensitive=True, path_glob=None, language=None, limit=50, cursor=None` | FunctionSearchPage |
| read_function | `symbol_id, occurrence_id, *, max_bytes=None` | SourcePage |
| continue_read | Only `continuation`; no index_run_id or new budget | SourcePage |
| read_file | `path, start_line=1, end_line=None, *, max_bytes=None` | SourcePage |
| search_text | `pattern, *, case_sensitive=True, multiline=False, path_glob=None, language=None, limit=50, cursor=None` | TextSearchPage |
| get_callers / get_callees | `symbol_id, *, limit=50, cursor=None` | ReferencePage |
| get_references | `symbol_id, *, usage=None, limit=50, cursor=None` | ReferencePage |
| get_file_outline | `path, *, limit=50, cursor=None` | OutlinePage |
| list_directory | `path='', *, limit=50, cursor=None` | FilePage |
| find_files | `path_glob, *, language=None, limit=50, cursor=None` | FilePage |
| find_flags | `*, categories=None, path_glob=None, symbol_id=None, limit=50, cursor=None` | FlagPage |
| list_occurrences | `symbol_id, kind, *, limit=50, cursor=None` | OccurrencePage |
| get_call_arguments / get_binding_targets | `reference_id, *, limit=50, cursor=None` | ArgumentPage / TargetPage |
| get_progress / list_diagnostics | `*` or `*, component=None, file_id=None, limit=50, cursor=None` | Progress / DiagnosticPage |

All public page limits are 1–200, default 50. Common page envelope: index_run_id, snapshot_id, items, next_cursor and run-wide coverage. A source page uses next_continuation rather than search cursor. `find_flags` and `get_progress` additionally report `rule_mode` and `rule_manifest_digest` from the run's frozen flagging selection, including incomplete, paused, failed and completed runs. The completion report uses that same Progress record; it does not reconstruct the selected rules from mutable configuration. Return null next_cursor only when no further current matching item exists after the returned position. Page exhaustion never means whole-index completion.

Navigation starts after the run's frozen applicability plan is ready; INDEX_INITIALIZING identifies a pending metadata plan without claiming complete or zero-file coverage. Ordinary extraction/resolution/scanning may still be partial. Source readers use the selected extraction profile's metadata, not mutable snapshot-wide overrides.

## Function results and direct reads

Retain symbol_id, local_name, qualified_name, kind, language, signature, definitions and declarations as approved. Each occurrence reference has occurrence_id, path, start_byte, end_byte, start_line and end_line. Definitions select signature plus body. Return at most eight initial references of each kind per item, with `definitions_cursor`/`declarations_cursor` for the corresponding list_occurrences operation and `occurrences_complete` describing whether those lists are fully presented. No hidden truncation. Additional references retain direct read IDs; no repeated name search is required.

Limit inline signature metadata to 1024 serialized UTF-8 bytes at a character boundary, with `signature_complete=false` when abbreviated. A null signature means unavailable, not truncated. The occurrence reference opens the full exact declaration/definition. This explicit abbreviation prevents a generated enormous signature from defeating the metadata page budget; the canonical extracted signature/source is retained.

Anonymous callables have null local_name and a generated qualified/display label. Function-name matching ignores null local names; outlines expose all anonymous IDs. Qualified scope names never become another matching field. Proven declaration/definition groups use resolution.md's representative and retain original identity aliases for reads.

## Files, outlines and text search

list_directory returns immediate children only. A caller explicitly descends; the tool does not dump the recursive tree. find_files matches project-relative paths using wcmatch glob with GLOBSTAR and DOTMATCH, no brace/extglob expansion, and case-sensitive matching independent of host filesystem. `**` spans zero or more path components; `*` does not cross `/`. An empty directory argument denotes snapshot root. Literal input paths are normalized project-relative paths; reject absolute paths, NUL and `..` traversal. Store raw Git path bytes separately. For the reversible display/API path, decode UTF-8 with surrogateescape, represent invalid byte surrogates as uppercase `%HH`, and encode every literal percent as `%25`; leave valid Unicode characters and `/` separators readable. The inverse decoder must reject noncanonical encodings and traversal after decoding. Do not conflate paths by replacement decoding. Globs match this canonical display form; ordering uses decoded original path bytes.

FilePage items include file_id where applicable, path, entry_type, language or null, size_bytes, and per-file processing states. Directory entries have no invented file-language state. Symlinks are links, not imported external contents. A failed/unavailable parser does not hide captured files. Outline items include symbol/occurrence identity, scope parent, nesting depth, kind, display name, available signature and exact occurrence reference, never bodies. Preserve ancestry by parent IDs even when pagination splits a subtree.

search_text uses the same `regex` VERSION1 dialect/case semantics as regex name matching, but searches captured text including comments and strings. Default is per-line matching; multiline=True searches the decoded complete file. Store nothing permanently merely because a query runs. Return file_id/path, exact match range, an excerpt of at most 512 UTF-8 bytes with explicit excerpt_truncated, and nullable enclosing symbol/occurrence references. Missing extraction only removes optional owner enrichment, never the textual match.

A content query timeout is an explicit QUERY_TIMEOUT, not a complete empty result. The default per-request query timeout is 30 seconds, configurable by the researcher; work already captured/indexed is unaffected. Do not skip expensive files to get a successful answer. Text search operates on a verified snapshot materialization or blob iterator, never the working tree. Large file processing may use a worker process; cancellation must not leave a claimed indexing job or corrupt its progress.

## References and flags

ReferencePage items retain reference/callsite ID, usage, `owner_symbol_id` and `owner_name`, exact source occurrence/argument spans, target/candidate references and binding status/basis. For incoming calls, the owner ID/name identifies the caller; `targets` identifies the called function or candidates, not the caller. Resolve `owner_name` from the same published owner record used for `owner_symbol_id` in the query transaction; use its qualified display name (including the anonymous-callable label). Both owner fields are null only when no owner is established, and both are present otherwise. No extra name lookup by the consumer is required. get_callers and get_callees are one-hop only. Multiple callsites between the same functions remain separate items. Initial reference items include at most eight arguments and eight targets; arguments_cursor and targets_cursor continue through get_call_arguments/get_binding_targets with the same reference ID. A single resolved target needs no target continuation. This bounds nested collections without hiding remaining records. get_references includes supported non-call uses; passing a function argument is not an invocation. Outgoing unresolved calls remain visible without invented target IDs. Incoming ambiguous candidates are labeled candidates, never confirmed calls.

FlagPage items have flag_id, category, signal_kind, reason, source range, owner or null, engine/rule identity and immutable manifest digest. Grouping in the human renderer is presentation only. Filtering does not run rules or remove unflagged code from other navigation. Multi-category matches may appear as distinct category associations without claiming multiple vulnerabilities.

## Live keyset pagination

Sort functions by the representative group's earliest visible source path, source start byte and representative ID. Sort references/flags/text matches by their own captured path, start byte and stable ID; text IDs are deterministic from file/match range/ordinal. Sort file entries by path and stable identity. Outline order is file position then occurrence ID, with parent relationships retained. Use C/byte ordering, not user-locale collation.

A navigation cursor is `ssr1.` base64url canonical JSON with v=1, type='query', operation, index_run_id, query_digest, and last_key. query_digest covers the effective pattern/mode/case/filter/usage/category/symbol settings, not limit. Continuation requests repeat the same query arguments; reject differing effective settings or operation/run with CURSOR_MISMATCH. A different valid limit is allowed because keyset position does not depend on page size. Tokens have the same strict 4096-byte decode limit and duplicate-key rejection as source tokens, but the payload type must not be confused with a source-read token.

Query after last_key and return only current committed matches. Fetch limit+1 matching results to determine continuation, not merely limit+1 unfiltered rows. Application-side regex filtering may scan multiple ordered database batches; do not emit next_cursor pointing before the last returned match or a fake terminal page because one internal batch had no matches. If the actual serialized metadata response would exceed its 50,000-byte default, return fewer complete items with a valid next_cursor. An individually oversized item produces RESPONSE_ITEM_TOO_LARGE with configuration remediation, not truncated IDs/locations.

During indexing, new records before a cursor position require refreshing from cursor=None. A cursor replay is a new live query and may differ. After a completed unchanged run, a fresh full traversal must return every recorded match exactly once. Proven symbol association can change grouping during processing; do not promise frozen live enumeration.

## Error contract

Envelope is always `{'errors': [...]}` for failures. Every entry contains code, operation, field_path or null, component or null, position or null, message, expected or null, received or null, remediation, retryable and diagnostic_id or null. Positions identify units explicitly: input pattern Unicode scalar offset is zero-based; source bytes/lines follow source-reading.md. Do not populate a field_path for a storage fault to blame a valid argument.

Closed codes: INDEX_INITIALIZING, INVALID_ARGUMENT, INVALID_PATTERN, UNKNOWN_LANGUAGE, RUN_NOT_FOUND, SYMBOL_NOT_FOUND, OCCURRENCE_NOT_FOUND, OCCURRENCE_MISMATCH, PATH_NOT_FOUND, PATH_OUTSIDE_SNAPSHOT, SOURCE_NOT_TEXT, SOURCE_RANGE_INVALID, INVALID_CONTINUATION, CURSOR_MISMATCH, RESPONSE_BUDGET_TOO_SMALL, RESPONSE_ITEM_TOO_LARGE, QUERY_TIMEOUT, STORAGE_UNAVAILABLE, STORAGE_INTEGRITY_ERROR and INTERNAL_ERROR. Domain capture/index commands add their separately documented operational codes; they do not rename navigation meanings.

Collect independent syntactic/type/bounds errors in request-field order. Then validate prerequisites in order: run, snapshot/files, symbol, occurrence association, token/range/source. Do not invent dependent mismatches when the run/symbol could not be loaded. Malformed regex plus invalid limit returns both. A failed query is never items=[]. Only established transient storage failures are retryable without argument changes; all diagnostic guidance states what is known and the next action, not speculative repairs.

Error responses have an independent 65,536-byte ceiling. Bound echoed input to 256 characters, message to 768 and remediation to 1024, with safe truncation indicators when necessary. Do not include source bodies, DSNs/tokens or raw stacks. Navigation request shape has bounded field counts, so all independent argument errors fit; rule-file validation diagnostics use their separate paged inspection operation when a large selected catalogue is invalid. Persist a correlation record for operator diagnostics, not an automatic repair instruction.
