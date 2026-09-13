# Stage 1 — Function lookup and source retrieval

Status: approved behavior from the researcher discussion. This records the agreed lookup, reading, and captured-text search requirements; it is not an executable API schema, implementation plan, or test-results report.

Read with [function-records.md](function-records.md), [reference-records.md](reference-records.md), [indexing-progress.md](indexing-progress.md), [flag-records.md](flag-records.md), and [source-intake.md](source-intake.md). PostgreSQL holds searchable records; Git retains the immutable source. Existing snapshot/run identity and partial-query requirements apply.

## Approved requirements

**S1-NV-R01 — Shared navigation operations.** Provide one lookup and source-retrieval interface for the initial researcher CLI and later model-tool adapters. Both use the same owning operations and source identities, rather than maintaining separate lookup implementations. Stage 1 proves these operations without connecting a model or starting investigations. Exact method names, signatures, response schemas, and package ownership remain to be specified.

**S1-NV-R02 — Find functions by local name.** Support wildcard and regular-expression matching against indexed local function names, with optional path and language filters. Return bounded results containing symbol IDs, qualified names, available signatures, and source locations, not every matching function's complete body. Qualified names provide identifying context; do not introduce a local/qualified-name matching selector. Preserve the wildcard/regex distinction already agreed for name matching. Exact query options, filter syntax, case handling, ordering, and pattern-engine details remain to be specified; this does not create or run a flagging rule merely because a search was requested.

**S1-NV-R03 — Preserve distinct matches.** Return same-name functions in different files or scopes, and same-name overloads, as distinct entries with their own identities and identifying context. Do not select the first match implicitly or collapse entries by name. The researcher or later model selects a returned symbol ID for the subsequent read. Retain the selected snapshot and indexing-run association; a lookup must not silently switch to a different run or a newer source revision. Anonymous callables remain individually retrievable by their identities under S1-FN-R09; generated navigation labels are not fabricated declared function names.

**S1-NV-R04 — Read exact function source.** Given the selected function identity, retrieve its corresponding captured source with line numbers and file/location context. Use the recorded source locations and managed Git snapshot, not the original working directory or a moving remote branch. Preserve the distinction between available declarations and definitions under S1-FN-R04/R07; do not fabricate a body for a declaration-only entry. Exact occurrence-selection and response-field conventions remain part of the interface design.

**S1-NV-R05 — Explicit continuation for large functions.** Support reading a large function through explicit continuation rather than silently truncating its source. Identify which portion was returned and whether more of the selected source remains, with a usable way to continue that same read. Continuation must remain bound to the same selected source identity and snapshot. Completing a sequence of reads must make the entire selected source available without silently omitting intermediate content. A bounded response does not reduce capture or indexing scope. The response budget, continuation representation, and precise range conventions remain to be agreed; no cursor implementation is selected here.

**S1-NV-R06 — Read captured text by file range.** Allow the researcher to request selected lines from any captured text file, including documentation, configuration, unsupported text source, and code outside function bodies. A function record or security flag is not a prerequisite for this operation. Preserve the selected file's snapshot identity, line positions, and applicable capture/retrieval limitations. Existing symbolic-link boundaries and LFS exclusions still apply; do not expose external targets or present an LFS pointer as the missing underlying source. Exact encoding, range-validation, and non-text error behavior remain to be specified.

**S1-NV-R07 — Navigation is independent of flags.** Unflagged functions and captured text remain searchable/readable through the same operations as flagged source. Flags help identify research starting points; they are not an eligibility or access filter. Searches and reads must retain the partial-processing indicators required by S1-IN-R22 and S1-IX-R05. An empty function search while extraction is unfinished means no match is currently available, not proof that none exists. A successful read does not claim complete reference resolution, flagging, or whole-run indexing.

**S1-NV-R08 — Regex search across captured text.** Provide regular-expression text search across captured text files, with optional path and language filters. Include source code, documentation, configuration, and captured text without extracted functions, including unsupported or unparseable text source. Search the selected immutable snapshot, not the original working directory or a moving remote revision. Function records and security flags are not prerequisites for finding text. Unlike local-name matching, content search may find text within comments and strings; a text match does not establish executable behavior.

Return bounded results identifying the file, source line/location, a short matching excerpt, and the enclosing function when known from the selected index. Do not return entire files by default, discard a match because function metadata is unavailable, or invent a function owner for text outside a known callable. The returned location must support reading surrounding captured text through S1-NV-R06. Preserve the existing snapshot-only link boundary, LFS exclusions, and applicable completeness indicators. Search results are navigation observations, not newly generated security flags or automatic investigation tasks.

Use the shared navigation owner under S1-NV-R01. Exact regex engine/dialect, case and multiline behavior, filter syntax, excerpt bounds, pagination, search-coverage reporting, and implementation backend remain to be specified with the researcher. This requirement does not select a new search service or duplicate the canonical source store.

## Intended researcher workflow

```text
Search local function names with *command*
    -> Inspect matching IDs, paths, qualified names, and signatures
    -> Select a function ID
    -> Read exact snapshot source, continuing explicitly when necessary
    -> Follow recorded references or open recorded callsites
```

Reference/callsite information is governed by reference-records.md. This workflow does not define additional traversal depth, ranking, or automatic exploration behavior.

Text search provides another entry point: search for a route string, configuration key, or SQL fragment; inspect matching excerpts and locations; then read surrounding source or navigate to a known enclosing function. It does not require a function-name match or an existing flag.

## Derived acceptance scenarios

These are required observations for future tests, not executed test results.

| ID | Scenario | Required observation |
|---|---|---|
| S1-NV-T01 | Search indexed local names with wildcard and regex patterns, with and without path/language filters. | Return the matching IDs, qualified-name context, available signatures, and locations through bounded results; do not include every function body or match solely through a qualified-name prefix. |
| S1-NV-T02 | Search a name shared by different scopes/files and overloads, then select a specific result. | Keep distinct identities; do not choose the first match. The read uses the selected function, file, snapshot, and run. |
| S1-NV-T03 | Read a function after modifying or removing the original working source. | Return the captured source with line numbers and locations; never fall back to live source or a newly resolved branch. Declaration-only entries do not gain fabricated bodies. |
| S1-NV-T04 | Read a function larger than one response and follow its continuations. | Each response identifies its returned portion and remaining content; successive reads cover the entire selected source without silent truncation, gaps, or changes of source identity. |
| S1-NV-T05 | Request line ranges from captured configuration, documentation, unsupported text source, and code outside functions. | Read the requested captured text without requiring a function entry or flag; preserve locations and existing link/LFS restrictions. |
| S1-NV-T06 | Find and read an unflagged function while unrelated extraction/resolution/flagging remains unfinished. | Navigation remains available; processing limitations stay explicit. Empty partial searches and successful reads do not imply complete indexing or absence of other matches. |
| S1-NV-T07 | Exercise the initial CLI lookup/read workflow through the shared navigation owner using disposable captured source and index records. | Verify the real entry-point-to-owner path without LLM calls. No separate CLI-only lookup or source-reading policy is introduced; later adapters are specified to use the same owner. |
| S1-NV-T08 | Search for a route string, configuration key, and SQL fragment across captured code, documentation, and configuration, with and without path/language filters. | Return bounded matching excerpts with file and line locations, respecting the selected filters rather than returning whole files; locations open the matching captured text through the shared reader. |
| S1-NV-T09 | Search captured text containing matches inside a known function, at module level, in comments/strings, and in a file without successful structural extraction. | Keep text matches regardless of flags or available function metadata. Attach the enclosing function only when known; do not fabricate owners or treat comment/string matches as executable behavior. Disclose relevant incomplete indexing. |
| S1-NV-T10 | After capture, modify or remove the working directory, then search and read matching text while link/LFS exclusions are present. | Results and follow-up reads use the same captured bytes; no live-source or external-link fallback and no LFS-pointer substitution for missing content. The query neither creates flags nor starts a model investigation. |

## Decisions still requiring discussion

- Exact operation signatures, response fields, error forms, range conventions, and encoding behavior.
- Search filters, case handling, pattern engines, ordering, pagination, and partial-result consistency. Captured-text regex search is approved under S1-NV-R08; its multiline behavior, excerpt bounds, and coverage reporting remain to be specified.
- Large-source response budgets, continuation mechanics, and declaration/definition selection.
- PostgreSQL query/index design, source-reader and text-search interfaces, and modular ownership.

Specify these mechanisms with the researcher before assigning implementation. Do not add automatic model analysis, restrict navigation to flagged functions, or use large-source limits to silently omit required source.
