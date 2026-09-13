# Stage 1 — Function lookup and source retrieval

Status: approved behavior from the researcher discussion. This records the agreed lookup, reading, captured-text search, one-hop caller/callee navigation, file-outline, file-discovery, direct function-read reference, and repeatable-continuation requirements; it is not a complete executable API schema, implementation plan, or test-results report.

Read with [function-records.md](function-records.md), [reference-records.md](reference-records.md), [indexing-progress.md](indexing-progress.md), [flag-records.md](flag-records.md), and [source-intake.md](source-intake.md). PostgreSQL holds searchable records; Git retains the immutable source. Existing snapshot/run identity and partial-query requirements apply.

## Approved requirements

**S1-NV-R01 — Shared navigation operations.** Provide one lookup and source-retrieval interface for the initial researcher CLI and later model-tool adapters. Both use the same owning operations and source identities, rather than maintaining separate lookup implementations. Stage 1 proves these operations without connecting a model or starting investigations. Exact method names, signatures, response schemas, and package ownership remain to be specified.

**S1-NV-R02 — Find functions by local name.** Support wildcard and regular-expression matching against indexed local function names, with optional path and language filters. Return bounded results containing symbol IDs, qualified names, available signatures, and source locations, not every matching function's complete body. Qualified names provide identifying context; do not introduce a local/qualified-name matching selector. Preserve the wildcard/regex distinction already agreed for name matching. Include directly usable source-read references under S1-NV-R12. Exact query options, filter syntax, case handling, ordering, and pattern-engine details remain to be specified; this does not create or run a flagging rule merely because a search was requested.

**S1-NV-R03 — Preserve distinct matches.** Return same-name functions in different files or scopes, and same-name overloads, as distinct entries with their own identities and identifying context. Do not select the first match implicitly or collapse entries by name. The researcher or later model selects a returned symbol ID and source occurrence for the subsequent read under S1-NV-R12. Retain the selected snapshot and indexing-run association; a lookup must not silently switch to a different run or a newer source revision. Anonymous callables remain individually retrievable by their identities under S1-FN-R09; generated navigation labels are not fabricated declared function names.

**S1-NV-R04 — Read exact function source.** Given the selected function identity and occurrence under S1-NV-R12, retrieve its corresponding captured source with line numbers and file/location context, including the signature and body when reading a definition. Use the recorded source locations and managed Git snapshot, not the original working directory or a moving remote branch. Preserve the distinction between available declarations and definitions under S1-FN-R04/R07; do not fabricate a body for a declaration-only entry. Detailed response-field and multiple-occurrence pagination conventions remain part of the interface design.

**S1-NV-R05 — Explicit continuation for large functions.** Support reading a large function through explicit continuation rather than silently truncating its source. Identify which portion was returned and whether more of the selected source remains, with a usable way to continue that same read. Continuation must remain bound to the same selected source identity and snapshot. Completing a sequence of reads must make the entire selected source available without silently omitting intermediate content. A bounded response does not reduce capture or indexing scope. Repeatability and reader independence follow S1-NV-R13. The response budget, continuation representation, and precise range conventions remain to be agreed; no cursor implementation is selected here.

**S1-NV-R06 — Read captured text by file range.** Allow the researcher to request selected lines from any captured text file, including documentation, configuration, unsupported text source, and code outside function bodies. A function record or security flag is not a prerequisite for this operation. Preserve the selected file's snapshot identity, line positions, and applicable capture/retrieval limitations. Existing symbolic-link boundaries and LFS exclusions still apply; do not expose external targets or present an LFS pointer as the missing underlying source. Exact encoding, range-validation, and non-text error behavior remain to be specified.

**S1-NV-R07 — Navigation is independent of flags.** Unflagged functions and captured text remain searchable/readable through the same operations as flagged source. Flags help identify research starting points; they are not an eligibility or access filter. Searches and reads must retain the partial-processing indicators required by S1-IN-R22 and S1-IX-R05. An empty function search while extraction is unfinished means no match is currently available, not proof that none exists. A successful read does not claim complete reference resolution, flagging, or whole-run indexing.

**S1-NV-R08 — Regex search across captured text.** Provide regular-expression text search across captured text files, with optional path and language filters. Include source code, documentation, configuration, and captured text without extracted functions, including unsupported or unparseable text source. Search the selected immutable snapshot, not the original working directory or a moving remote revision. Function records and security flags are not prerequisites for finding text. Unlike local-name matching, content search may find text within comments and strings; a text match does not establish executable behavior.

Return bounded results identifying the file, source line/location, a short matching excerpt, and the enclosing function when known from the selected index. Do not return entire files by default, discard a match because function metadata is unavailable, or invent a function owner for text outside a known callable. The returned location must support reading surrounding captured text through S1-NV-R06. Preserve the existing snapshot-only link boundary, LFS exclusions, and applicable completeness indicators. Search results are navigation observations, not newly generated security flags or automatic investigation tasks.

Use the shared navigation owner under S1-NV-R01. Exact regex engine/dialect, case and multiline behavior, filter syntax, excerpt bounds, pagination, search-coverage reporting, and implementation backend remain to be specified with the researcher. This requirement does not select a new search service or duplicate the canonical source store.

**S1-NV-R09 — One-hop caller and callee navigation by default.** Given a selected function identity, return its immediate recorded callers or callees through the shared navigation owner. A default lookup covers one relationship hop, not recursive expansion of the repository's call graph. For a recorded chain A -> B -> C, a caller lookup for C identifies B, not A as an immediate caller; a callee lookup for A identifies B, not C as an immediate callee. The researcher or later model can explicitly follow another returned function identity to continue exploring.

Return bounded results with the related function's identity and name where established, file context, the exact callsite location, and the recorded resolution status. Locations must allow the individual callsite and its argument expressions to be read from the same immutable snapshot. Multiple calls from one function to another remain individually accessible; grouping by function must not discard their distinct occurrences. Do not return every related function body or recursively expand neighbors merely because the lookup was requested.

Derive both directions from the same call occurrences and resolution records under S1-RF-R06. Preserve pending, ambiguous, and unresolved information rather than inventing a target identity or treating a candidate as an established caller/callee. Non-call references remain distinguishable; passing a function as an argument does not by itself make the enclosing function its caller. Apply the existing snapshot/run association and partial-coverage indicators, including when other files can still contribute callers. This requirement settles the default traversal behavior, not exact response schemas, candidate presentation, grouping, pagination, or an optional recursive-query API.

**S1-NV-R10 — File outlines without source bodies.** Given a captured file path within the selected snapshot and indexing run, return its indexed classes, functions/methods, and anonymous callables through the shared navigation owner. Include their recorded identities, names or anonymous navigation labels, available signatures, nesting/enclosing-scope relationships, and exact source locations. Preserve distinct entries for overloads, same-name members, and multiple lambdas; do not flatten away ownership or present generated labels as declared names. The outline describes the selected file's indexed structure, not inferred application behavior.

Return bounded metadata rather than loading or returning the outlined bodies or generating model summaries. The researcher or later model can select an entry or source location and read it through the existing function/file-range operations. Keep those selections bound to the same source identities and snapshot. Outline access must not depend on a security flag or completion of unrelated reference resolution or scanning.

When extraction is unfinished, clearly mark the available outline as partial. An empty partial outline does not establish that the file contains no classes or functions. Preserve reported extraction failures and unsupported-language limitations rather than presenting them as a successful empty outline; captured text remains readable under S1-NV-R06. A complete file outline does not imply complete caller lists, flagging, or whole-run indexing. Exact response fields, ordering, hierarchy representation, and pagination remain to be specified with the researcher.

**S1-NV-R11 — Directory listing and wildcard file-path discovery.** Provide directory listing and wildcard file-path search within the selected completed snapshot through the shared navigation owner. Support finding captured paths such as README files, files under routes directories, or C++ source files without first knowing a function name or locating a security flag. Search project-relative paths, not the researcher's live filesystem. Discovery includes captured documentation, configuration, unsupported source, and binary-file metadata as well as supported source. Do not omit an included file merely because structural extraction is unfinished, failed, or inapplicable.

Return bounded entries containing paths, entry/file types, and available language and processing status, not file contents or an automatic dump of the entire repository tree. Preserve unknown or pending metadata as such. A discovered file does not imply successful extraction, resolution, or flagging. Selecting a path must support the existing outline or applicable source-reading operations against the same snapshot; no model calls, source execution, or additional capture is triggered by discovery.

Apply the existing snapshot-only symbolic-link boundary and exclusions. Listing a captured link or an excluded-content diagnostic must not traverse outside the snapshot or imply that an absent submodule/LFS target was captured. Exact wildcard path grammar, directory-listing depth, case handling, ordering, response fields, and pagination remain to be specified with the researcher. This adds navigation over the existing snapshot, not a second filesystem index or a file-watching service.

**S1-NV-R12 — Search results carry direct function-read references.** Function-search results must contain the information needed to read a selected function immediately, without another name lookup or reconstructing a source location. Return `index_run_id` in the response context and each item's `symbol_id`, local and qualified names, available signature, and available definition references. Each definition reference includes its `occurrence_id`, captured project-relative `path`, and `start_line`/`end_line` location. A definition reference identifies a concrete source occurrence, not just the enclosing file or a function name.

The initial read uses `read_function(index_run_id=..., symbol_id=..., occurrence_id=...)`. The shared reader validates that the occurrence belongs to that symbol and run, resolves its stored exact ranges in the associated snapshot, and returns the selected function's captured source, including signature and body, with line numbers and explicit continuation when needed. The caller does not need another search, a newly resolved Git revision, or guessed body boundaries. When multiple definition occurrences are recorded, their distinct IDs and locations allow explicit selection; do not silently pick the first occurrence or switch to another function with the same name.

For declaration-only entries, return an empty `definitions` list and retain usable references to available declarations so their source can still be read without fabricating a body. During incomplete indexing, no available definition means none is recorded in the returned view, not proof that no definition exists elsewhere. Preserve the existing coverage indicators and bounded-response requirements. The complete response schema, declaration-reference representation, limits, pagination of multiple occurrences, and continuation format remain to be specified; this requirement approves the search-to-read linkage, not unrelated API defaults.

**S1-NV-R13 — Independent, repeatable source-read continuations.** Each returned continuation identifies a specific next source section of the same selected captured function occurrence. Repeating that continuation returns the same section and source ranges rather than advancing a shared mutable cursor. Preserve the index-run, symbol, occurrence, and snapshot association established by the initial read under S1-NV-R12. Retrying after a lost response must not silently skip the section that was requested.

Separate readers must not move each other's read positions, whether they read the same function or different functions/files. Interleaved requests and replays must leave each reader able to follow the returned continuations through the entire selected source without gaps under S1-NV-R05. Ongoing indexing or changes to the original working directory must not redirect an issued continuation to another source section or revision. This fixes the returned source section and its ranges, not byte-for-byte equality of unrelated progress metadata that may change while indexing continues.

The token representation, stateful versus self-contained implementation, lifetime/error behavior, and response-size policy remain to be specified with the researcher. This agreement does not introduce a global read-position store or settle pagination over changing search results.

## Intended researcher workflow

```text
Search local function names with *command*
    -> Inspect matching IDs, paths, qualified names, signatures, and definition references
    -> Select a symbol ID and occurrence ID from the returned index-run context
    -> Read exact snapshot source directly, continuing explicitly when necessary
    -> Follow recorded references or open recorded callsites
```

The following abbreviated example illustrates S1-NV-R12; it omits pagination, coverage, and other response fields, and the example IDs do not specify their production format:

```json
{
  "index_run_id": "idx_12",
  "items": [
    {
      "symbol_id": "fn_42",
      "local_name": "execute_command",
      "qualified_name": "Admin::execute_command",
      "signature": "int execute_command(const char* command)",
      "definitions": [
        {
          "occurrence_id": "def_7",
          "path": "src/admin.cpp",
          "start_line": 42,
          "end_line": 68
        }
      ]
    }
  ]
}
```

Those returned identifiers feed directly into the reader:

```python
read_function(
    index_run_id="idx_12",
    symbol_id="fn_42",
    occurrence_id="def_7",
)
```

Reference/callsite information is governed by reference-records.md. Default caller/callee navigation is one hop under S1-NV-R09; further exploration requires another explicit lookup. This workflow does not select ranking or automatic recursive exploration behavior.

Text search provides another entry point: search for a route string, configuration key, or SQL fragment; inspect matching excerpts and locations; then read surrounding source or navigate to a known enclosing function. It does not require a function-name match or an existing flag.

A file outline provides a structural entry point: select a captured file, inspect its indexed classes and callables without their bodies, then read a selected entry or source range under S1-NV-R10.

Directory listing and wildcard path search under S1-NV-R11 let the researcher find the captured file before requesting its outline or reading its text. Examples of the intended searches are `README*`, `**/routes/*`, and `**/*.cpp`; the precise wildcard grammar remains an interface-design decision.

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
| S1-NV-T11 | Through the initial CLI and shared owner, query callers/callees for a recorded cross-file chain A -> B -> C, then explicitly follow B. | Each default lookup returns only immediate neighbors with IDs/names, file/callsite locations, and resolution status. Reaching the next hop requires another lookup; no transitive neighbor is mislabeled as immediate and no graph/body dump occurs. |
| S1-NV-T12 | Record two calls from B to C at different locations, query in both directions, and open each callsite after the original working source changes. | Both views derive from the same occurrences. Each distinct call and its argument expressions remain accessible from the pinned snapshot even if the display groups them under one function. |
| S1-NV-T13 | Query during unfinished cross-file resolution with ambiguous/unresolved call occurrences and a function passed as a callback argument. | Results retain their resolution and partial-coverage distinctions; no candidate becomes an established target and no argument reference alone becomes a call edge. Empty partial caller lists do not imply that no callers exist. |
| S1-NV-T14 | Through the CLI and shared owner, request an outline for a file containing classes, methods, nested functions, overloads, and multiple lambdas. | Return bounded identities, names/labels, available signatures, nesting, and exact locations without loading or returning their bodies or making model calls. Distinct entries and enclosing scopes remain navigable. |
| S1-NV-T15 | Select an unflagged callable from a file outline after the original working source changes or disappears. | The existing reader opens that entry's exact captured source using the outline's identity and location; no live-source fallback, implicit first-match selection, or flag prerequisite occurs. |
| S1-NV-T16 | Query outlines during unfinished extraction, after successful extraction with no callable entries, and for failed or unsupported extraction. | Distinguish partial, completed-empty, failed, and unsupported outcomes. Keep captured text accessible; neither a partial empty outline nor a complete file outline implies complete relationships, flags, or whole-run processing. |
| S1-NV-T17 | Through the CLI and shared owner, list a captured directory and use wildcard path searches to find README, route, and C++ files. | Return bounded paths, entry/file types, and available language/processing status without file contents, a flag prerequisite, model calls, or an automatic whole-tree dump. Selected paths support the existing outline or applicable source reader. |
| S1-NV-T18 | Discover captured files with pending, failed, or unsupported extraction, alongside documentation, configuration, and binary files. | Files remain discoverable with honest available metadata and processing status; lack of symbols does not hide a file or become an implied successful index. |
| S1-NV-T19 | After capture, change or remove the original checkout, then list/search paths while external links, missing submodules, and LFS exclusions exist. | Discovery remains bound to the selected snapshot; do not consult live paths, traverse external link targets, or report uncaptured/excluded contents as captured files. Follow-up reads preserve the same boundaries. |
| S1-NV-T20 | Through the CLI and shared owner, search for a function and pass only returned index-run, symbol, and definition-occurrence identifiers into read_function after the original checkout changes. | The result supplies the path and line context plus all identifiers needed for an immediate read. No second search or guessed range is required; the reader returns the exact captured signature and body with line numbers and continuation when necessary. |
| S1-NV-T21 | Search symbols with multiple recorded definitions and same-name overloads; read a selected occurrence, then supply an occurrence from another symbol or run. | Each available definition has its own occurrence reference. The valid read opens exactly the selected occurrence, while a mismatched association is rejected rather than selecting another definition, the first name match, or a different snapshot. |
| S1-NV-T22 | Search a declaration-only entry and an entry whose definition has not yet become available during indexing. | Return no fabricated definition/body. Available declarations retain usable read references. An empty definitions list during partial processing is not presented as proof that no definition exists, and search still returns metadata rather than bodies. |
| S1-NV-T23 | Through the CLI and shared reader, request a continuation, lose its response, retry the same continuation, and then follow the returned next continuation. | The retry returns the same source section and ranges rather than advancing to another section; subsequent continuation covers the remaining source without skipping the retried section or changing the selected occurrence. |
| S1-NV-T24 | Interleave two readers of different functions/files, then two readers of the same function, including repeated continuation requests. | Each reader retains its own progression. No request or replay advances another reader's position; identical continuations identify identical source sections regardless of interleaving. |
| S1-NV-T25 | Issue a continuation while indexing is incomplete, then finish more indexing and change or remove the original working source before replaying it. | The continuation still returns the same captured function section and ranges. Updated processing metadata does not redirect the read to a different occurrence, snapshot, or live file. |

## Decisions still requiring discussion

- Exact operation signatures, response fields, error forms, range conventions, and encoding behavior. S1-NV-R12 fixes the direct search-to-read identity linkage; complete schemas remain to be specified.
- Search filters, case handling, pattern engines, ordering, pagination, and partial-result consistency. Captured-text regex search is approved under S1-NV-R08; its multiline behavior, excerpt bounds, and coverage reporting remain to be specified.
- Caller/callee response fields, grouping, and candidate/unresolved presentation under S1-NV-R09. One-hop default navigation is settled; no recursive-query feature is approved here.
- File-outline response fields, ordering, hierarchy representation, and pagination under S1-NV-R10.
- Directory-listing depth, wildcard path grammar, case handling, ordering, response fields, and pagination under S1-NV-R11.
- Large-source response budgets, continuation representation, storage, and lifetime/error behavior. Repeatability and reader independence are settled by S1-NV-R13. S1-NV-R12 requires explicit occurrence references; declaration-reference representation and pagination for multiple occurrences remain to be specified.
- PostgreSQL query/index design, source-reader and text-search interfaces, and modular ownership.

Specify these mechanisms with the researcher before assigning implementation. Do not add automatic model analysis, restrict navigation to flagged functions, or use large-source limits to silently omit required source.
