# Source-reading, positions and response budgeting

This is the concrete refinement of S1-NV-R04–R06/R12–R16/R20–R23. It preserves the approved signatures `read_function(index_run_id, symbol_id, occurrence_id, *, max_bytes=None)` and `continue_read(continuation)`.

## Original bytes and decoding

Git is authoritative. Use a persistent `git cat-file --batch` reader or a verified content-addressed blob spool. Validate object type and size, consume exactly the advertised byte count plus framing, and never interpret target bytes as a Git command. The spool may be deleted; it is not a replacement source store. Original-byte slicing occurs before display formatting. [S9]

Supported text decoding is UTF-8, UTF-8 with BOM, BOM-declared UTF-16 LE/BE, and explicit path-configured Latin-1 or Windows-1252. Detect BOM before binary-NUL heuristics. Python encoding cookies are honored through `tokenize`; other declared codecs must be in the configured supported codec list. For non-NUL text not valid UTF-8 and without a declaration, use a recorded Latin-1 byte-preserving fallback and disclose that decoding is a fallback, not a guessed semantic encoding. Binary heuristics never remove captured bytes. Invalid explicitly selected decoding is a diagnostic, not replacement-character corruption.

Source text is decoded without newline normalization. Retain CRLF, lone CR and LF exactly in `source`. Line boundaries treat CRLF as one newline, LF as one and lone CR as one. A BOM consumes original bytes but is not counted as a visible column. Metadata records its size and codec. For a selection containing the BOM, the source string retains U+FEFF so the captured prefix is not silently hidden. Adapters may omit the BOM in their parser buffer only with the corresponding original-byte offset mapping.

Use zero-based byte offsets `[start_byte,end_byte)`. Lines and within-line columns are one-based. Page boundaries do not split a CRLF pair; count its combined escaped size when calculating a progressing fragment. Columns count decoded Unicode scalar values, not UTF-8 bytes, UTF-16 units, grapheme clusters or tab-expanded screen cells. The end position is the exclusive boundary; an interval ending immediately after a newline has end_line on the next line and end_column 1. Adjacent intervals share a boundary without duplicating bytes. Function searches return the same endpoint convention.

## SourcePage and read selection

SourcePage uses the approved fields plus `subject_kind` (`function` or `file`) to distinguish file-range reads. Function reads have non-null symbol/occurrence IDs; file reads have both null. `range` contains `start_byte`, `end_byte`, `start_line`, `end_line`, `start_column`, `end_column`. `source` has no inserted line-number prefixes. The CLI renders positions alongside the text; JSON/model adapters keep source unchanged.

`read_file(index_run_id, path, start_line=1, end_line=None, *, max_bytes=None)` selects inclusive one-based requested lines. `end_line=None` selects through EOF. Validate requested bounds; do not silently clamp an invalid range. Reading an empty text file with start_line 1 and no end_line returns an empty source page with range `[0,0)` and no continuation. This is not a non-progressing page because the selection is exhausted. File reads do not require function extraction or flags. Resolve symbolic links only in the approved virtual snapshot namespace.

A function read validates the occurrence belongs to the selected symbol or proven association in that run, then selects its full declaration/definition span. No signature/body recomputation, line-based guessing or new name search. Continuations keep the same selection and exact upcoming page interval. A new read can use another budget; continuing an existing token cannot.

## Canonical serialization and numeric limits

Count the complete compact UTF-8 JSON SourcePage using `json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode('utf-8')`. Include all required keys, quoted/escaped source, IDs, path, range, coverage and continuation. Do not include the CLI's terminal newline or an external provider's unrelated envelope in the claimed payload limit. Later adapters must independently account for their envelopes.

Default effective budget is exactly 50,000 bytes; valid initial overrides are positive integers at most 1,000,000. Reject booleans as integers. An initial budget must also pass the calculated minimum below. Bounds constrain responses, not source size, file size, parser scope or total pages. Numeric positions/counts are integers from zero through 2^63-1 (one-based coordinates start at 1).

## Stateless token

Token format is `ssr1.` followed by unpadded base64url of canonical JSON. Enforce a maximum encoded token length of 4096 bytes; reject duplicate JSON keys and unknown fields before interpreting it. Payload keys: `v=1`, `type='source'`, `subject_kind`, `index_run_id`, `snapshot_id`, `file_id`, nullable `symbol_id`/`occurrence_id`, `selection_start`, `selection_end`, `page_start`, `page_end`, `budget`, `reader_profile='source-v1'`.

Validate every identity against canonical records and every interval against the selection/file/occurrence. Validate codec boundaries, page_start < page_end for nonempty continuation, and stored snapshot association. Do not accept arbitrary filesystem paths or unvalidated Git OIDs from a token. The token is an untrusted request representation, not an authorization capability; no signature/key service is required. A modified but otherwise valid in-scope request does not acquire additional source permissions. Invalid tokens return structured errors, never guessed replacements.

## Fixed sections with changing coverage

Do not size a token's section using only today's compact counters: their decimal lengths can grow. Before selecting source, calculate a reserved metadata size by serializing a SourcePage template with the actual immutable IDs/path, maximum-width permitted numeric range/coverage values, the longer Boolean value, and a placeholder next token whose length is computed from the maximum-width source-v1 payload (including the maximum allowed budget width, not the requested budget's digit count). Include empty source quotes. This produces a deterministic upper bound from the contract, not an arbitrary guessed padding constant. Use the same reader profile/reservation for the whole selection.

For a selected source string, partition decoding output into **paging atoms**: a CRLF pair is one atom; every other Unicode scalar is one atom. The exact JSON contribution of an atom is `len(compact_json(atom)) - 2`, removing only the enclosing string quotes. A CRLF contributes four escaped bytes (`\r\n`), not the two bytes of either scalar alone. Calculate the largest atom contribution in the entire selected source; use this same atom iterator for minimum calculation, page selection, and one-page lookahead. Never split a CRLF pair to satisfy the budget. `minimum_required_bytes` is reserved metadata size plus that contribution, or just the final-page metadata size for a genuinely empty selection. This is the minimum accepted by the safe-paging policy, not a claim that no smaller first-page serialization could fit. It guarantees progress throughout the chosen selection, including later escaped or multibyte characters.

When the requested/configured budget is smaller, return RESPONSE_BUDGET_TOO_SMALL with requested_bytes and this calculated minimum, explaining the safe-paging reserve. Do not issue an empty page with a continuation. Error responses obey navigation.md's independent error policy (a 65,536-byte target without dropping independent errors), not the invalid source budget. Preserve the original read references in correction guidance.

## Page algorithm

1. Validate the initial identity or token. Resolve codec and original-byte/character boundary map from the selected immutable file. Obtain current run coverage separately from source selection.
2. For a new initial read, compute the fixed reservation and minimum; choose the longest prefix of complete paging atoms whose escaped source contribution fits `budget - reservation`. Prefer the last whole-line boundary within that prefix. If no complete line fits, use the character boundary rather than dropping the oversized line. A nonempty selection must advance at least one complete paging atom, including both characters when that atom is CRLF.
3. For continue_read, select exactly token.page_start:page_end. Never reslice it because coverage/defaults changed. Check the token range against the source-v1 algorithm and canonical selection; a token cannot bypass maximum-size validation.
4. If more source remains, calculate the next page interval with the same fixed reservation and effective budget. Encode that next interval in a new token. This needs only one-page lookahead; the metadata reserve bounds token size independently of later pages, so no recursive construction of the entire page sequence is necessary.
5. Build SourcePage with the actual returned range/current coverage and the next token or null. Serialize and verify the whole payload fits. A failure of this assertion is a contract implementation bug, not permission to silently shorten an already-issued page or drop metadata.

For raw decoding boundaries that cannot represent a character-safe selected interval, return SOURCE_RANGE_INVALID with exact bounds; do not insert replacement characters to make it fit. Initial function ranges are validated during publication, so such an error normally indicates a corrupted index or malformed explicit request.

## Required proof cases

Test ASCII, multibyte UTF-8, UTF-16 BOM, CRLF, lone CR, an oversized line, escaped quotes/backslashes/control characters, empty file, declaration-only occurrence, and many pages. Concatenated source pages must equal the selected decoded source with no missing/duplicated content. Original byte intervals must be adjacent and cover the complete selection. Replaying a token returns the same source/range after process restart, default-budget change and coverage growth from 9 to 10 or 99 to 100 completed files. Both source identity and serialized-byte bound must hold.

## CRLF minimum regression

Run `python -m unittest discover -s stage-1-indexing/validation/regressions -p "test_source_budget.py" -v`. At the calculated minimum, CRLF remains intact and paging progresses. One byte less is rejected. Quotes, controls, multibyte scalars, and CRLF must use the same atom calculation. This is a reference/prose regression, not proof of production codec or Git integration.
