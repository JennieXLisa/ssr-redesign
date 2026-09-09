# P1-F09 — Grouped read-only retrieval: implementation plan

Updated: 2026-09-09. Documentation only. Read the [feature](../P1-F09-grouped-read-only-retrieval.md), [TOOLS.md](../../../contracts/TOOLS.md) and [CONFIGURATION.md](../../../contracts/CONFIGURATION.md). Grouping is a transport/execution convenience, not a second tool implementation or a transaction across unrelated reads.

## Contract-hardening integration — Aggregate context and receipt accounting

Reserve one combined output/context allowance across the final formatted batch, including error envelopes and notices. Every returned subresult retains its identity and actual delivered range; a subresult omitted by the final budget stays explicitly unreturned. Never multiply I_max or tools.max_input_bytes by batch size.

Only the current final request/response observation may grant delivery credit. Batch reading source and reporting a lead in the same model response is not a proof shortcut; state-changing tools remain outside read_batch. Test at170k boundary with one failing read and a pending notice, cancelled undispatched items, and a request changed after the tokenizer count.

Normative source: [hardening contract index](../../../CONTRACT_HARDENING.md). Preserve the existing feature procedure below except where this explicit correction replaces it; implement the linked exact schemas, not a local incompatible approximation.

## 1. Broker interface and whitelist

Expose `read_batch` with `items:[{key,tool,arguments}]`. Keys are unique bounded caller labels used only to associate responses. Validate the batch count, key types/uniqueness and permitted tool names before dispatch. Reject nested read_batch and any write/control operation: checkpoint, report_lead, contextual request/publication, yield, terminal submission and operator recovery are excluded.

The allowed read-like set includes source/file/symbol/stat/relationship/knowledge/detail queries and document_query. Document_query's durable interest registration is an explicitly permitted bookkeeping effect, not permission to batch arbitrary writes. Reuse each ordinary tool's complete parser, authorization, implementation and output checks; do not fork separate batch versions of source verification or artifact visibility.

References for later items must be already known. No variable substitution such as 'use item 1's first symbol ID' is supported. A dependent sequence requires a later model decision/tool call. Reject unresolved templates rather than guess their values.

## 2. Plan total response allowance before dispatch

Reserve the batch envelope, item keys, per-item outcome metadata and minimal error space from the existing combined result/context allowance. Allocate the remaining payload deterministically in input order, bounded by each tool's configured allowance. Unused budget can flow to later items; no item is entitled to a full max_tool_result_bytes multiplied by item count.

Distinguish response bytes, original source bytes, scanned bytes, rows, provider tokens and wall time. A metadata item can be cheap in source bytes but large in encoded output. A regex search can scan substantial input while returning a small preview. Account actual work in its owning dimensions.

If minimal outcomes for all items cannot fit, reject the batch before execution or reduce accepted batch size through an explicit caller correction. Do not execute items whose results cannot be represented and then omit their identities silently. Full semantic results can be paginated/truncated only through their ordinary contracts.

## 3. Execution model

Start with sequential calls through existing handlers, with optional bounded concurrency only for truly independent readers using isolated connections. Parallel provider tool support does not make a SQLite connection thread-safe. Each concurrent item owns its connection/transaction and source read resources, or execution remains sequential. The batch coordinator must not hold one read transaction while waiting for all items or model turns.

```text
validate_batch_envelope(items)
plan = allocate_combined_budget(items, remaining_allowance)
for item in planned_input_order:
    if cancellation_or_authority_expired():
        result[item.key] = NOT_EXECUTED(reason)
        continue
    result[item.key] = ordinary_tool_dispatch(item, plan.allowance(item))
    charge_actual_cost_and_release_unused_allowance(item)
return results_in_original_input_order
```

For a concurrent implementation, keep deterministic output order even when completion order differs. Do not make returned order encode unpredictable thread scheduling. Internal worker count for grouped reads stays within host resource limits; it is not a new pool of analytical model workers.

## 4. Per-item error and cancellation behavior

A recoverable lookup failure can coexist with successful independent items. Return each item's normal envelope, identity and continuation. The batch-level summary states counts of successful/partial/rejected/not-executed items; it never asserts atomic success when one failed.

A global stale lease, cancellation or snapshot integrity failure stops undispatched work. Already executed successful reads retain their actual outcomes/accounting. Do not roll back unrelated already committed document-query interests or claim that no effects occurred. Check current authority before each dispatch, and inside any permitted interest-registration transaction.

Use an explicit NOT_EXECUTED item disposition for undispatched calls rather than pretending an empty result. Do not retry the whole batch automatically when one item fails. P1-F08 recovers an exact completed bookkeeping operation, and the analyst can retry only the failed/narrowed item.

## 5. Source delivery and notices

Aggregate per-item source delivery descriptors into the final model request. Record only ranges whose content survives final composition. Do not credit a requested whole function, a skipped item or a removed result. When a page is shortened by its ordinary fitter, its range/hash/cursor must match the shortened content. Never crop JSON/source text afterward without rebuilding metadata.

Freshness notices are selected once at the final ordinary request boundary under the remaining common allowance. Do not attach an independent full notice allowance to every subresult. If a notice is omitted, keep it pending. Item-specific source hashes must exclude notices, display labels and sibling results.

Repeatedly fetching the same source is still actual transport/work cost; maintain interval union only for read-completeness proofs, not as a reason to hide usage. A new attempt receives no previous batch's source-read credit.

## 6. Document-query bookkeeping isolation

When two batch items ask for equivalent analysis, canonical interest keys allow one durable interest. Do not create duplicate listeners from item keys. Each successful lookup's original H/receipt remains coherent under P1-F02; concurrent registration cannot overwrite pending notice progress with a later marker.

One item can return available artifact metadata while another observes a newer publication. The batch is not a global frozen database snapshot. Each item's explicit query boundary/result identity describes its view. Do not imply that all items share one simultaneous acceptance state.

## 7. Tests and measurable assertions

Compare sequential ordinary calls with a batch of the same known symbol/source/detail requests: data identities, hashes and authorized results match within the explicitly shared budget. Use out-of-order completion to verify stable key association/output order. Duplicate keys, forbidden tools, nested batches and dependent placeholders fail before dispatch.

Set the aggregate allowance below the sum of individual maxima. Assert final serialized bytes fit and each shortened page has correct source coordinates/hash/continuation. Include an item whose minimal result cannot fit and verify explicit not-executed/repair behavior rather than lost output.

Fail one metadata lookup among two valid reads: other results survive with accurate partial summary. Cancel between items: executed outcomes retained, undispatched marked. Exercise simultaneous document-query interests and a publication during lookup; pending notices are not lost. Verify no concurrent use of one SQLite connection with a test guard that rejects cross-thread access.

Inspect final provider-bound request and delivery records after context trimming. A removed item contributes no source-read credit. Batch calls must not create candidates, canonical coverage or extra analytical tasks. Permitted interest/operation metadata is the documented exception.

## 8. Build sequence and limits

Implement a sequential dispatcher first, shared budgeting second, cancellation/error aggregation third, then optional isolated read concurrency only if measured useful. The feature is valid without parallel host I/O. Reuse ordinary handler tests and add integration tests for grouping boundaries. No generic task DAG engine, multi-action transaction, hidden dependency resolver or per-item model call belongs here.
