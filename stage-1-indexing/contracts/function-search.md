# Stage 1 — Function-search API

Status: signature, result fields, direct read references, and page-size bounds approved by the researcher. The `coverage` object and the remaining details listed below are not yet frozen. This document is a partial API contract, not a claim of implemented or tested functionality.

## Scope and traceability

**S1-NV-R18 — Concrete function-search interface.** Implement the signature and result shape below through the shared navigation owner. This specializes the approved requirements; it does not introduce another search engine or a separate CLI implementation.

Read with:

- [Source retrieval](../requirements/source-retrieval.md): S1-NV-R01–R04, R07, R12, and R16.
- [Live pagination](../requirements/live-pagination.md): S1-NV-R17.
- [Function records](../requirements/function-records.md): identities, signatures, declarations/definitions, and overloads.
- [Indexing progress](../requirements/indexing-progress.md): partial results and per-step completion.
- [Tool errors](../requirements/tool-errors.md): actionable errors and the shared `errors` array.

## Operation signature

```python
from typing import Literal


def find_functions(
    index_run_id: str,
    pattern: str,
    mode: Literal["wildcard", "regex"],
    *,
    case_sensitive: bool = True,
    path_glob: str | None = None,
    language: str | None = None,
    limit: int = 50,
    cursor: str | None = None,
) -> FunctionSearchPage:
    ...
```

The signature describes the shared operation; it is not an implemented stub or a new requirement to expose an HTTP endpoint.

| Input | Contract |
|---|---|
| `index_run_id` | Select the index run and its associated snapshot. No redundant project/snapshot input is required for this operation. |
| `pattern` | Apply the pattern to indexed local function names only. Qualified names remain display context, not another matching field. |
| `mode` | Required explicit `wildcard` or `regex`; do not infer a mode from punctuation or fall back on invalid input. |
| `case_sensitive` | Boolean; defaults to `True`. |
| `path_glob` | Optional path filter; `None` means no path restriction. Exact path-glob grammar remains to be fixed. |
| `language` | Optional language filter; `None` means no language restriction. The exact language-code vocabulary remains to be fixed. |
| `limit` | Integer from **1 through 200**, inclusive; defaults to **50**. Reject out-of-range limits with an actionable error rather than silently adjusting them. |
| `cursor` | Optional continuation for live pagination. `None` starts a fresh search; continuation retains the selected run, query/filter settings, and ordering position under S1-NV-R17. Exact token encoding and validation are still open. |

The page limit bounds the number of function items in one response, not the total number of matches that may be retrieved or the included indexing scope. Returning fewer than `limit` items does not by itself establish that indexing is complete.

## Successful response: `FunctionSearchPage`

| Field | Required content |
|---|---|
| `index_run_id` | The selected index-run identity. |
| `snapshot_id` | The snapshot associated with that run. |
| `items` | This page's function results, no more than `limit`. |
| `next_cursor` | A continuation string, or `null` when no further matching results are currently available after this page. |
| `coverage` | Relevant extraction/resolution progress and failures. Its exact fields, status values, and calculation are the next design decision; an unspecified object is not an implementation-ready contract. |

`next_cursor: null` reports the end of currently available pagination, not the end of indexing. Apply the live-refresh behavior in S1-NV-R17: a newly indexed match before the last ordering position may require a fresh search to be seen. For exhaustive enumeration of recorded matches, start a fresh search after the selected run is complete and unchanged.

### Function item

| Field | Required content |
|---|---|
| `symbol_id` | The function's recorded identity in the selected run. Names alone are not identities. |
| `local_name` | The indexed local name used for matching. |
| `qualified_name` | The indexed qualified name used for identifying scope/context. |
| `kind` | The recorded callable kind. The complete enum remains to be fixed with the language mappings. |
| `language` | The recorded source language. |
| `signature` | Available signature text, or `null` when unavailable. |
| `definitions` | Read references for available definition occurrences. |
| `declarations` | Read references for available declaration occurrences, including declaration-only entries. |

Do not load or return matching function bodies in search responses. Keep same-name functions, different scopes, and overloads distinct. Anonymous-callable identity and retrieval remain governed by S1-FN-R09; generated navigation labels are not fabricated declared names.

### Definition/declaration read reference

Each returned occurrence reference contains:

| Field | Required content |
|---|---|
| `occurrence_id` | Identity of the concrete declaration or definition occurrence associated with the returned symbol. |
| `path` | Captured project-relative file path. |
| `start_byte` | Zero-based inclusive start in the original captured file bytes. |
| `end_byte` | Zero-based exclusive end in those bytes. |
| `start_line` | One-based readable start-line location. |
| `end_line` | One-based readable end-line location; the exact display convention at an exclusive byte endpoint on a line boundary remains part of the source-position contract. |

Byte intervals follow S1-NV-R16. A definition reference identifies the source to read, including its signature and body, not only the body or the enclosing file. A declaration reference identifies its available declaration source without claiming a body exists.

Use the returned values directly:

```python
read_function(
    index_run_id=page.index_run_id,
    symbol_id=item.symbol_id,
    occurrence_id=selected_occurrence.occurrence_id,
)
```

No second name search or caller-computed offset is required. The shared reader checks that the occurrence belongs to the selected symbol/run before reading its captured bytes. Search results must not silently choose the first definition or substitute a same-name function.

A declaration-only item has no fabricated definition: `definitions` is empty and available declarations retain their read references. During partial processing, an empty definitions list means no definition is available in the returned view, not proof that none exists elsewhere. Multiple-occurrence bounding/continuation remains open; the implementation must not silently truncate these lists or expand them without respecting the agreed bounded-response requirement.

## Error behavior

Use the shared `errors` array, including for single errors. Invalid patterns, invalid page limits, or invalid/mismatched cursors do not become successful empty searches. Return all independently detectable input errors with the affected field, explanation, and known correction. Preserve completed indexing; a navigation-input error must not change source or index records.

A valid search with zero matches returns `items: []` with its coverage information. A storage/query failure is an error, not a successful no-match result. Detailed error codes and cursor checks remain part of the shared error/API design.

## Acceptance scenarios

These are required future tests, not executed test results.

| ID | Scenario | Required observation |
|---|---|---|
| S1-NV-T36 | Omit optional arguments, then repeat using explicit valid filters and options. | Defaults are case-sensitive matching, no path/language filter, a fresh search, and at most 50 function items. Explicit valid options are honored without qualified-name matching or body dumps. |
| S1-NV-T37 | Request limits 1 and 200, then 0, -1, and 201 through the CLI/shared owner. | Accept the inclusive boundaries; reject the out-of-range values with actionable errors without silently clamping them. Omitted limit uses 50. |
| S1-NV-T38 | Search same-name overloads and declaration-only entries; use a returned definition or declaration reference to read source. | All approved item and occurrence fields are present, unavailable signatures are null, identities remain distinct, and direct reads return the selected captured source without another search or fabricated bodies. |
| S1-NV-T39 | Reach the final currently available page while indexing is unfinished, then restart after processing completes. | Keep `next_cursor` distinct from coverage. Live pagination discloses incomplete results; the fresh completed-run traversal enumerates the recorded matches under S1-NV-R17. |
| S1-NV-T40 | Submit an invalid regex with an out-of-range limit. | Return both independent problems in `errors[]` with correction guidance; do not execute the invalid search or return an empty successful page. |

## Details still requiring agreement

- Exact `coverage` fields, states, counts, and scope relative to query filters.
- Closed kind/language vocabularies, remaining field constraints, and complete machine-readable schemas.
- Pattern engine/dialect, path-glob semantics, and exact live-pagination ordering keys for a symbol with multiple occurrences.
- Cursor payload/validation and behavior when continuation arguments differ from the recorded query.
- Bounds and continuation for multiple declaration/definition references and overall response size.
- Source-location display details and the complete shared error-code catalogue.

Do not choose these remaining behaviors silently or start a separate implementation of navigation to work around an unfinished contract. No other Stage 1 requirement is changed by this approval.
