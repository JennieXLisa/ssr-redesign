# P1-F04 — Agent-initiated checkpoints: implementation plan

Updated: 2026-09-09. Documentation only. Read the [feature](../P1-F04-progress-checkpoints.md), [STATE.md](../../../contracts/STATE.md), [TOOLS.md](../../../contracts/TOOLS.md) and [configuration](../../../contracts/CONFIGURATION.md). The design reuses checkpoint storage and recovery; it does not make model reasoning a trusted memory store.

## Contract-hardening integration — 170k checkpoint and dossier algorithm

Implement E/O/M and I_max at the actual ssr.agent.runtime composition boundary. With E=170000, O=16384, M=4096, checkpoint threshold is127092 and maximum input149520. Count system/tool/protocol overhead, not only history. Use a checkpoint-only exchange above the soft threshold with output4096 and at most two attempts, consuming real budgets.

The dossier builder must return measured tokens/UTF-8 bytes and included mandatory-delta manifest. Enforce8192tokens/32768bytes total and4096tokens/16384bytes core. Use exact host manifest references for large mechanical sets. Preserve incomplete tool groups and material contradictions in the defined eviction order. Test 365000 constructed input→zero dispatch, immutable request hash after counting, tokens-only/bytes-only dossier overflow, failed checkpoint retaining its prior head, and three no-progress resumptions stopping.

Normative source: [hardening contract index](../../../CONTRACT_HARDENING.md). Preserve the existing feature procedure below except where this explicit correction replaces it; implement the linked exact schemas, not a local incompatible approximation.

## 1. Locate the existing save and restore boundaries

Map `CheckpointState`, `save_checkpoint`, `load_latest_checkpoint`, the broker's `_checkpoint_state`, ordinary tool filtering, host-checkpoint messages, and `ssr.worker.context_recovery` to the actual checkout. Identify the existing checkpoint sequence, body hash, author and task/attempt binding. Preserve old parsers so legacy checkpoints remain readable under their original contracts.

Currently checkpoint exposure and checkpoint storage are separate decisions. In collaborative mode remove the host-only exposure restriction, but call the same schema/validator/save owner from ordinary and host-requested turns. Do not create `save_agent_memory` beside `checkpoint_state`. A normal save must return `terminal:false`; `yield_work` remains an explicit P6-F02 action.

## 2. Parse a typed, bounded portable state

The input includes `expected_sequence` and the state fields in TOOLS.md: facts, hypotheses, unknowns, typed next_action, subject/evidence/source/artifact references, source/search cursors, answer references and request references. Reject unknown fields. Facts remain analyst assertions with evidence references, not host-certified truth. Keep hypotheses and counterevidence distinct rather than flattening everything into a narrative summary.

Validate the encoded size after field validation. A collection of individually small values can still exceed the total checkpoint limit. Resolve referenced subjects within the bound review/snapshot and check current metadata visibility. Authenticate convenience tokens, but do not convert authentication into read credit. Preserve unavailable/stale references with explicit status only where the checkpoint contract permits; do not silently replace them with latest artifacts.

Search queries may contain source or credentials. Store query digest, mode/flags, selection and cursor; only retain query text if the ordinary safe-prose policy accepts it. Otherwise save `query_omitted_reason: SOURCE_SENSITIVE`. A future attempt is told to supply the exact query again or start a new search. It cannot reconstruct it from a digest. Do not add a second sensitive store for checkpoint convenience.

## 3. Compare-and-swap save transaction

Prepare/validate outside the write lock. Derive the semantic operation identity from work, contract, bound input revision, expected_sequence and canonical safe state. Check P1-F08's exact committed operation before rejecting a now-old expected sequence: a retry of a previously successful save returns that save's original receipt.

```text
prepared = validate_checkpoint(call, execution)
with immediate_transaction():
    require_current_attempt_and_input(execution)
    if exact_operation_is_committed(prepared.operation_id):
        return original_receipt
    current = load_work_checkpoint_head(execution.work_id)
    require(current.sequence == call.expected_sequence)
    next = current.sequence + 1
    insert_checkpoint(next, safe_state, hash, author_attempt, input_revision)
    compare_and_swap_head(current.sequence, next)
    commit_operation_receipt(checkpoint_id, next, state_hash)
return checkpoint_receipt
```

Use the existing sequence convention for an initial checkpoint and document it in the adapter; do not invent a second counter. The head and immutable checkpoint row must be consistent after crash. Do not overwrite the old checkpoint body. The receipt includes checkpoint ID, sequence and digest, not the entire saved analysis repeated back to the model.

A genuine CAS conflict returns the current sequence and a safe retrieval/merge action. The model must not automatically retry with the new sequence while discarding newer state. If two different states raced, keep both original inputs in their respective operation provenance, but only the CAS winner becomes current.

## 4. Save does not yield or reset accounting

A successful ordinary save leaves the task RUNNING, the current attempt active and its lease/budget unchanged. It must not release a reservation, create another worker, increment operational retries or satisfy file coverage. The host may ask for a save before context exhaustion, but it uses the same persistence path and operation semantics.

Reserve context/output margin through the existing runner policy before actual exhaustion. A failed save preserves the last valid checkpoint and reports the failure. If neither saving nor further work fits, stop with the real incomplete/resource outcome. Never synthesize a successful terminal review simply because a checkpoint is available.

Checkpoint text is guidance. The host does not execute `next_action.objective` as a shell command, tool call or scheduler instruction. Typed next_action can orient a resumed analyst without granting authority.

## 5. Build a continuation dossier

On new attempt admission, verify same logical task/inquiry, review/snapshot and execution contract. Load the latest valid compatible checkpoint through the existing recovery owner. Add current assignment and input-token identity, unresolved durable context requests, permitted accepted answers, and explicit material-input deltas. Interests and requests are durable host records already; do not duplicate them inside a separate checkpoint subscription database.

The dossier identifies original checkpoint author/sequence and states which referenced artifacts changed or became unavailable. It must not silently reinterpret the old hypothesis against a new candidate revision. Limit dossier size using recorded summaries and exact references; do not inline whole documents or the previous conversation. Provider-opaque continuation state is not portable memory across attempts.

Initialize source-delivery accounting empty for the new attempt. References/cursors still help navigation, but required material source must be reopened. Restore interests for the same work, not for the reusable worker slot. Pending notifications and accepted answer references are context, not proof that the new agent consumed them.

## 6. Failure and lifecycle matrix

Crash before checkpoint commit: old head remains authoritative; replay the validated save through P1-F08. Crash after commit but before ACK: return the original checkpoint receipt without another sequence. Expired predecessor: cannot write a new checkpoint over its successor. Unsupported schema/hash mismatch: explicit compatibility/integrity error; no prose-based reconstruction. Cancelled logical work: normal writes stop; host recovery may settle an earlier committed operation only.

Yield references an exact checkpoint digest in P6-F02. Recheck that association and input revision in the task transition transaction. The checkpoint save itself does not create a WAITING state. A dependency request made after the last model checkpoint still survives because its own registration is durable.

## 7. Required tests

Use a scripted model that saves, performs another read, then saves changed state. Assert two distinct sequences, continued RUNNING status and unchanged budget allocations except actual usage. Repeat the first save's operation after the second is current: it returns the first receipt, not a third checkpoint or a CAS overwrite.

Pause two saves at validation and commit them with equal expected_sequence. One wins; the other receives a conflict. Expire the losing attempt and verify it cannot merge into a successor by manipulating the sequence. Crash after insertion/head/operation boundary using transaction rollback injection and prove no partial head is visible.

Resume after a context request was registered but before model checkpointing. The request/interest survives. Supply an old SourceRef and search cursor with omitted sensitive query; the dossier preserves allowed locators, marks the query unavailable and gives no inherited read credit. Test oversized state, invalid reference kind, safe-prose rejection and unsupported versions.

## 8. Delivery sequence

Characterize old save/restore behavior first. Add collaborative state parsing and schema fixtures. Implement exact replay plus CAS transaction. Expose the same save owner to ordinary turns. Integrate bounded continuation dossiers and P6-F02 yield. Run tests both at the save function and through broker→runner→new-attempt flow. Completion requires actual collected regression results and checkpoint hash/author assertions, not merely a new state dataclass.
