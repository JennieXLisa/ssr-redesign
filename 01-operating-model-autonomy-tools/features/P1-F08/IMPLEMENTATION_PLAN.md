# P1-F08 — Reliable tool actions and outcome recovery: implementation plan

Updated: 2026-09-09. Documentation only. Read the [feature](../P1-F08-tool-action-recovery.md), [state contract](../../../contracts/STATE.md) and [tool envelope](../../../contracts/TOOLS.md). This feature makes a repeated host action recoverable; it does not promise exactly-once external model execution.

## Contract-hardening integration — Prefix/fragment/yield replay boundaries

Expand operation recovery fixtures across runtime-prefix insertion, transcript-prefix seal, semantic publication, synthesis entry/head CAS, yield preparation and settled continuation publication. Receipt IDs and exact input hashes must be recovered; no replay calls another model solely to reconstruct accepted effects.

An operation COMMITTED receipt for yield identifies only the prepared intent until the separate finalizer seals publication. A stage COMMITTED receipt identifies a journal root/revision, not whole-file completion. Exact stage replay after newer revisions returns its old receipt; altered arguments are a new operation subject to CAS. Count metadata quotas once per semantic operation, and retain unknown provider usage instead of refunding it during recovery.

Normative source: [hardening contract index](../../../CONTRACT_HARDENING.md). Preserve the existing feature procedure below except where this explicit correction replaces it; implement the linked exact schemas, not a local incompatible approximation.

## 1. Inventory action owners and effect boundaries

List every state-changing collaborative operation: checkpoint save, independent lead registration, contextual request, contextual answer publication, yield and terminal role submission. Also include analysis lookups that register interests. For each record which owner validates, which owner begins the authoritative transaction, which rows are effects, and what immutable receipt can reconstruct success. Existing `ToolPersistenceError`/prepared persistence recovery is a reuse point, not a reason to add a second commit system.

Never wrap arbitrary callbacks in a generic retry loop without knowing whether they committed. Navigation/source reads remain replayable reads with real usage accounting; provider calls have independent uncertain-delivery rules. Do not retry target side effects because SSR is static-only.

## 2. Derive a semantic operation identity

Canonicalize only the operation's meaning: review, logical work, operation kind, contract version, bound input revision and canonical semantic arguments. Exclude ephemeral provider call IDs and transport formatting. Preserve ordered lists when order changes meaning; sort only explicitly set-valued fields under the declared normalization. Reject duplicate/invalid keys before hashing.

Map each provider call ID and request/attempt to the derived operation ID for audit. A retransmitted call with changed arguments under the same provider correlation is an error. An exact semantic replay returns its original result even if the provider assigned a new call ID. This prevents duplicate leads after lost acknowledgments.

Different claims about one file produce different identities. Same subject or title is not sufficient deduplication. Expected checkpoint sequence and context-request revision participate in identity. Intentionally repeatable distinct actions require a host-issued action ticket under their own contract; do not add random model IDs to evade idempotency.

Store only allowed source-free normalized content and hashes. Search queries and provider bodies can be sensitive; an operation ledger is not permission to copy every raw tool argument into ordinary state.

## 3. Prepare outside the transaction

Parse, validate prose/refs and verify immutable source through the existing owners. Produce a typed prepared artifact carrying input digest/revision and the owning domain's validated values. Bind the completed provider exchange/turn provenance before a model-authored effect can become accepted. A pending incomplete stream cannot be treated as a valid prepared result.

If PREPARED is durable, its record must contain enough safe information and an owner tag to resume that exact action. Do not persist an unexplained PENDING row that no component can reconcile. Expensive parsing/source reads occur outside the short database write transaction. Any mutable assumptions are rechecked during commit.

## 4. Atomic effect and receipt commit

```text
execute(prepared, execution):
    require_current_access(execution)
    existing = operations.lookup(prepared.id)
    if existing is COMMITTED:
        verify_same_input_digest(existing, prepared)
        return authorized_projection(existing.receipt)
    with owning_domain_transaction():
        existing = operations.lookup_for_update(prepared.id)
        if existing is COMMITTED:
            return existing.receipt
        require_current_lease_control_and_input(execution, prepared)
        effect = owner.commit_prepared(prepared, connection)
        receipt = owner.immutable_receipt(effect)
        operations.mark_committed(prepared.id, receipt, connection)
    return receipt
```

SQLite serialization/unique constraints implement the compare-and-reuse boundary; no distributed lock service is needed. Helpers receive the caller connection and must not commit independently. A uniqueness conflict is followed by exact identity comparison, never INSERT OR REPLACE. The operation COMMITTED record and domain effect IDs must share the authoritative transaction.

When another database is involved, do not claim atomicity across stores. Transcript or artifact publication uses explicit staged receipts and reconciliation owned by P4-F01. A work-creation outbox intent is itself a durable domain effect; its receipt must say pending materialization until an actual task exists.

## 5. Determine outcomes before retrying

Before commit: validation failure means NONE; safely prepared transient failure can be retried as the same operation. After commit: lost acknowledgment returns the original receipt, never reruns the model to reconstruct the result. Unknown commit outcome: query the authoritative operation/owner using exact identity, then either recover COMMITTED, prove no commit and safely retry, or retain OUTCOME_UNKNOWN with a named recovery path.

Do not return RETRYABLE as though nothing happened when the commit outcome is unknown. Do not assume a thrown exception means rollback occurred. Domain code must expose the exact commit boundary and receipt-recovery lookup. An unrelated newest candidate/task row is not evidence about this operation.

A cancelled or expired original attempt cannot initiate new effects. Coordinator recovery can settle an already committed original operation under explicit recovery authority and original identities. It must not adopt the successor's lease or attribute old evidence to that successor.

## 6. Avoid receipt dependency cycles

For report_lead/publish_context_answer, the required producer receipt authenticates the completed model response that requested the action. Record/seal it before effect execution. The action's acceptance cannot wait for its own success response to be consumed by a later model call: that creates a cycle.

Tool effect receipts, provider exchange receipts, runtime finalization and full-attempt transcript sealing are distinct. Mid-review contributions may use an accepted immutable prefix/turn seal; never label the whole active transcript complete. External provider retries remain chargeable uncertain exchanges, even when host effect replay is idempotent.

## 7. Recovery executor and error budget

Reuse the existing bounded host retry/backoff path for known retryable storage contention. Keep prepared objects across those retries, with cancellation checks before new writes. Stop at the configured host retry boundary and expose the real pending/unknown result; do not invoke extra inference solely to retry SQLite.

On restart, enumerate recoverable operations by status/owner and bounded keyset pages. Dispatch each to its owning reconciliation function. Do not scan all result prose, guess operations by timestamps, or create a general distributed transaction framework. Each owner documents which states can be replayed and which require manual integrity recovery.

Receipt reads recheck current recipient visibility. A stable operation ID is not a bearer credential. Safe acknowledgments can contain effect IDs/statuses only when authorized.

## 8. Failure-injection tests

For each action, inject failure after prepare, immediately before commit, inside the domain transaction, after commit/before response, and after response recording. Compare domain rows and operation receipt. Expected outcomes are either zero committed effect or exactly one effect with one recoverable receipt.

Execute two identical report_lead calls concurrently with different provider call IDs: one candidate/task origin, same receipt. Execute two distinct claims about the same source: separate valid proposals. Reuse a provider call ID with altered content: reject correlation mismatch. Replay checkpoint save after a newer checkpoint exists: return original save receipt without creating another revision.

Create a predecessor/successor attempt race and settle the old receipt late. Only original operation/finalization rows may change. Test missing/invalid receipt hashes, unsupported owner tags and sensitive raw input; no guessed recovery or leakage. Check outbox duplicate delivery separately from semantic lead deduplication.

## 9. Commit and acceptance gates

Implement identity normalization fixtures first; add owner-specific prepared/commit/recovery interfaces; integrate domain transactions one action at a time; then wire runner error behavior and restart reconciliation. Every newly supported action needs its own crash matrix. Do not enable an action merely because the generic operation table exists. Completion evidence includes row-count/identity assertions, concurrency barriers and exact outcomes, not only successful sequential calls.
