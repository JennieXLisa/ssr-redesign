# Stage 1 — Live navigation pagination

Status: approved pagination behavior from the researcher discussion. This is not a frozen API schema or an executed test report.

This companion to [source-retrieval.md](source-retrieval.md) continues its navigation requirements. Read with [indexing-progress.md](indexing-progress.md) and [tool-errors.md](tool-errors.md). It settles the live-search pagination policy previously left open, without changing immutable source-read continuation behavior.

## Approved requirement

**S1-NV-R17 — Stateless live pagination with explicit refresh.** Paginate available committed index results in a stable order by captured file path, source offset, and unique record ID. A continuation identifies the selected indexing run, operation/query and filter settings, and last returned ordering position. Continue after that position without maintaining a server-side cursor session or mutable per-reader position. Preserve the selected run's snapshot association; a continuation must not silently change the query, filters, or run.

While indexing continues, each page reflects available committed results and clearly indicates incomplete coverage. A newly published match that sorts before the current position may not appear on subsequent pages. Explain that restarting the same search without a cursor refreshes the result set and can reveal those earlier matches. Reaching the last currently available page does not imply that indexing finished or that all eventual matches were returned. Live result pages are not frozen historical result sets, and replaying a search cursor during indexing need not return identical items.

For a completed, unchanged index run, a fresh search followed through all pages must enumerate its complete matching result set without pagination-induced gaps or duplicates. A traversal begun while indexing was incomplete does not become exhaustive merely because indexing completes before its final page; restart from the beginning after completion when full enumeration is required. This is completeness of the recorded matching results, not proof that static analysis found every possible runtime relationship.

Implement this over the existing canonical records. Do not introduce stored search sessions, retained database cursors, or historical copies of every result set solely to freeze pagination. Source reading remains separate: an issued source-read continuation still returns its fixed captured section under S1-NV-R13/R14, regardless of changes in searchable index records. Partial-query access does not reduce full-scope indexing obligations.

## Derived acceptance scenarios

These are observations required of future tests, not tests executed here.

| ID | Scenario | Required observation |
|---|---|---|
| S1-NV-T33 | During indexing, read a result page; publish matching records sorting before and after its last position; continue and then restart the search. | Continuation advances after the recorded position and can include the later-position match. A fresh search reveals the earlier-position match. Pages disclose incomplete coverage and refresh semantics rather than promising exhaustive live enumeration. |
| S1-NV-T34 | Finish a run after a search has already passed some newly populated positions; start a fresh search over the completed unchanged run and follow every page. | Do not label the earlier live traversal exhaustive. The fresh completed-run traversal enumerates every recorded match once in the agreed order, including distinct records sharing a path and offset. |
| S1-NV-T35 | Continue an index query through a newly constructed reader without a stored session; interleave another reader and replay an existing source-read token while indexing advances. | Index pagination uses its own run/query/filter/position context and no shared mutable position. Search pages may reflect newly committed records; the source-read token continues to return its original fixed section. Neither operation changes source identity. |

## Design details still to specify

Exact cursor fields and encoding, validation/error mapping, page-size bounds, ordering keys for each result shape, handling of enrichment or symbol association changes, and coverage/refresh response fields remain to be specified. Source-read and search-pagination tokens must not be conflated. No numeric defaults, frozen-result service, or automatic refresh loop is approved here.
