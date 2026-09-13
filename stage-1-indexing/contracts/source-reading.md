# Stage 1 — Source-reading API

Status: operation signatures, the SourcePage fields, and whole-response byte budgeting below are approved. Numeric budgets, detailed range fields, token encoding, and other remaining items are not yet frozen. This is a partial API contract, not implemented functionality or an executed test report.

## Scope and traceability

**S1-NV-R20 — Concrete function-read and continuation interface.** Expose the two operations below through the shared source reader. The initial CLI and later model-tool adapters use that same owner; do not create a separate source-reading implementation for each adapter.

Read with [source-retrieval.md](../requirements/source-retrieval.md), especially S1-NV-R04–R06 and R12–R16; [function-search.md](function-search.md) for direct read references and the S1-NV-R19 coverage object; and [tool-errors.md](../requirements/tool-errors.md) for actionable, batched errors. Search-result pagination remains separate under [live-pagination.md](../requirements/live-pagination.md).

## Operation signatures

```python
def read_function(
    index_run_id: str,
    symbol_id: str,
    occurrence_id: str,
    *,
    max_bytes: int | None = None,
) -> SourcePage:
    ...


def continue_read(
    continuation: str,
) -> SourcePage:
    ...
```

These signatures specify shared operations, not HTTP endpoints or production stubs.

| Input | Contract |
|---|---|
| `index_run_id` | Identifies the selected index run and its associated immutable snapshot. |
| `symbol_id` | Identifies the function selected from that run. |
| `occurrence_id` | Identifies the particular declaration or definition to read. Validate its association with the supplied symbol and run; do not choose a different occurrence implicitly. |
| `max_bytes` | Optional initial whole-response byte budget under S1-NV-R21. `None` uses the configured source-response budget. Numeric defaults, permitted bounds, and the exact serialization profile remain to be agreed. |
| `continuation` | Self-contained token returned by the reader. It supplies the pinned source identities, specific next section, and read budget needed to continue. No additional IDs, caller-computed offsets, or reader session are required. |

The initial read selects the occurrence's full recorded source. For a definition, that includes its signature and body; for a declaration, it is the available declaration text, without an invented body. A response budget controls how much of that selected source fits in a page, not the total source available to read.

Resolve the effective budget for the initial read and retain the required budget information in its continuations. `continue_read` accepts no new size override. An issued token identifies a fixed section: repeating it must not resize that section based on another reader's settings or a newly selected default. A separate initial read can use another valid budget without changing earlier tokens.

## Successful response: SourcePage

Every successful response from either operation has the following fields:

| Field | Type and meaning |
|---|---|
| `index_run_id` | String identifying the selected run. |
| `snapshot_id` | String identifying the run's immutable source snapshot. |
| `symbol_id` | String identifying the selected function. |
| `occurrence_id` | String identifying the selected declaration or definition. |
| `path` | Captured project-relative file path. |
| `source` | Returned source text, without inserted line-number prefixes. |
| `range` | Object describing the actual returned source interval: zero-based inclusive start byte, exclusive end byte, and readable line/within-line positions. Exact nested field names and column units remain to be specified. |
| `next_continuation` | String token for the next section, or `null` when this page reaches the end of the selected occurrence. |
| `coverage` | The compact, whole-run coverage object specified by S1-NV-R19 in function-search.md. Reuse its fields and meanings rather than defining another progress format. |

The `range` describes this page's actual source, not the entire occurrence when only a fragment was returned. Byte offsets refer to original captured-file bytes under S1-NV-R16, not character indexes or positions in formatted output.

Line numbers are presentation metadata. A CLI or model-tool formatter may display them beside the code, but must not insert them into the `source` value. Within-line fragments must remain identifiable under S1-NV-R15. Encoding and newline rules must preserve the connection between the returned text and its recorded original-byte range.

`next_continuation: null` means the selected occurrence has been fully returned by this read sequence; it does not mean the index is complete. Coverage may change as indexing advances. Such progress changes do not alter the source section or source positions returned for an existing token.

## Whole-response byte budgeting

**S1-NV-R21 — Budget the complete serialized source response.** Apply the effective byte budget to the entire serialized SourcePage returned by `read_function` or `continue_read`, not just its `source` value or the captured-byte interval. Include the serialized field names, source representation, identifiers, path, range metadata, coverage, continuation token or null value, and enclosing response syntax. Account for encoding and serialization escaping; a character count or the length of the original source slice is not the serialized response size.

When choosing a new source section, account for the required metadata and continuation overhead before deciding how much source fits. Check the complete serialized response size before returning it. Preserve whole lines and valid character boundaries under S1-NV-R15. Do not satisfy the budget by dropping required fields, hiding coverage, omitting a needed continuation, or silently discarding source. Successive pages must still expose the entire selected source under the existing continuation rules. The budget does not reduce capture or indexing scope.

Issued continuations retain their fixed section and effective budget under S1-NV-R13/R14/R20; whole-response accounting does not authorize resizing an already-issued section. The concrete serialization/encoding profile, framing boundary for each adapter, numeric defaults/bounds, overhead reservation for changing coverage metadata, and too-small-budget/error-response behavior remain to be specified before implementation. Both the byte bound and repeatable source-section requirements must be preserved by that design.

## Reader implementation obligations

1. Validate the inputs through the shared error contract, including the selected run/symbol/occurrence association. A continuation must also identify an allowed section of that same occurrence; possession of a token does not replace source-access checks.
2. Select the recorded interval from the pinned Git file contents. Do not read the original working directory, resolve a moving branch, guess a body boundary, or perform another name search.
3. For an initial read, apply the effective whole-response byte budget under S1-NV-R21, allowing for required metadata and serialization while retaining whole lines where possible. Split an oversized line only at valid character boundaries and report the fragment's position. For continuation, honor its already-fixed section and validate it against the canonical records.
4. Return SourcePage and a self-contained next continuation when source remains, checking the complete serialized size against the effective budget. Do not maintain a mutable shared read position or PostgreSQL cursor session. Replays must not advance another reader or skip code.

Source-read failures use `errors[]` under S1-ER-R01–R06, with the known failure location, explanation, correction or diagnostic action, and retry classification. Do not turn an invalid reference or missing source object into an empty successful page. Exact error codes, validation constraints, and too-small-budget handling remain part of the unfinished API details.

## Intended usage

```python
page = read_function(
    index_run_id=search_page.index_run_id,
    symbol_id=item.symbol_id,
    occurrence_id=selected_occurrence.occurrence_id,
)

# On an explicit request to read the next section:
if page.next_continuation is not None:
    next_page = continue_read(continuation=page.next_continuation)
```

This illustrates separate caller-directed reads, not automatic draining of every page into a model's context. Stage 1 introduces no model calls or investigation workflow.

## Acceptance scenarios

These are required future tests, not executed test results.

| ID | Scenario | Required observation |
|---|---|---|
| S1-NV-T43 | Search for a function through the CLI/shared owner and read a selected definition; repeat with a declaration-only entry. | Returned IDs are sufficient. SourcePage identifies the exact run, snapshot, symbol, occurrence, and path. A definition read selects signature and body; a declaration read selects declaration text without fabricating a body or making another name lookup. |
| S1-NV-T44 | Omit max_bytes, then start a separate read with another valid explicit budget; follow returned tokens. | The first read uses the configured budget; the second uses the supplied budget. Each sequence makes its entire selected source available without gaps. Continuations require only their token, not repeated IDs or manual offsets. |
| S1-NV-T45 | Read multiline source and an oversized line with multibyte characters; render line numbers in the CLI. | SourcePage.source has no added line-number prefixes. Range metadata identifies the actual original-byte interval and readable positions. Whole lines are retained where possible; fragments remain character-safe and are not presented as complete lines. |
| S1-NV-T46 | Issue a continuation, lose its response, change the configured default budget, and replay it through a new reader while other reads are interleaved. | The issued token still returns its fixed section and retains the original read-budget context. No per-reader session is required; another request or updated default cannot advance or resize that token's section. Unrelated coverage metadata may change. |
| S1-NV-T47 | Supply a mismatched occurrence or malformed/out-of-occurrence continuation, then simulate a missing captured source object. | Return actionable errors under the shared errors[] contract. Do not substitute another occurrence, guess an ID, return unrelated/live source, or treat a storage failure as an empty successful page. |
| S1-NV-T48 | Reach the last page of a function while unrelated extraction, resolution, or flagging remains unfinished. | next_continuation is null for the finished source read, while coverage retains the selected run's actual incomplete status and per-step counts. Reading source does not change indexing completion. |
| S1-NV-T49 | Read source containing multibyte characters and characters requiring serialization escaping, with metadata and a continuation large enough that counting source bytes alone would exceed a valid response budget. | The complete serialized SourcePage fits the effective budget, including source, metadata, coverage, continuation, and enclosing syntax. Select less source as needed without breaking characters, dropping required fields, or losing the continuation. |
| S1-NV-T50 | Follow all source pages under a valid whole-response budget, then replay an issued continuation while indexing coverage changes. | Every successful serialized page respects its effective budget. The read sequence exposes all selected source without gaps; replay returns the same issued source section and ranges rather than resizing it to accommodate metadata changes. The final page reports no continuation only when its selected source is exhausted. |

## Details still requiring agreement

- Numeric response-budget defaults and permitted bounds; concrete serialization/encoding and adapter-framing boundaries under S1-NV-R21; overhead reservation for repeatable sections with changing metadata; too-small-budget and error-response behavior.
- Exact range-object fields, within-line units, encoding behavior, and line-end display conventions under the agreed original-byte coordinates.
- Token payload/encoding, integrity validation, lifetime/error behavior, and complete machine-readable request/response schemas.
- Closed operation/error mappings and the concrete package, Git-reader, and database interfaces.

The operation shape and whole-response budgeting boundary are settled. Do not add a continuation size override, stored cursor sessions, automatic source draining, or unrelated navigation features while filling in these remaining details.
