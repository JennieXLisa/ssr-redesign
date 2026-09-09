# P4-F01 — Accepted artifacts and publication: implementation plan

Updated: 2026-09-09. Documentation only. Read the [feature](../P4-F01-accepted-artifacts-and-publication.md), [STATE.md](../../../contracts/STATE.md), P1-F03 normalization and P1-F08 operation recovery. This is the common acceptance boundary for early collaboration, not a second knowledge database.

## Contract-hardening integration — Real prefix publication contract

Implement the closed runtime and transcript prefix receipt bodies, canonical chain framing, unique parent/end boundaries and input-observation checks in PREFIX_RECEIPTS.md. Main-ledger runtime events stay source-free; captured provider/source bytes stay in transcript.db. A completed response may seal a prefix while its attempt remains active; capture status remains appendable.

The publish transaction consumes a verified prefix or stores a bounded ACCEPTANCE_PENDING artifact. It commits artifact availability, review sequence, exact subject associations and wake intents together only after proof. Required capture failure never becomes an available answer. Later unrelated timeout preserves earlier valid prefix-backed artifacts; covered-prefix corruption withdraws dependent material. Test every crash boundary and same-response source-read non-credit.

Normative source: [hardening contract index](../../../CONTRACT_HARDENING.md). Preserve the existing feature procedure below except where this explicit correction replaces it; implement the linked exact schemas, not a local incompatible approximation.

## 1. Producer and artifact matrix

Map existing symbol/file/link/investigation/falsification payload stores and validators. Add registry adapters for canonical unit results, contextual answers, host query answers, analyzer observations and independent lead registrations. Each artifact points at one existing typed payload/result identity and hash. Do not copy source or result bodies into the registry.

MODEL_ATTEMPT producer: actual task, agent run, attempt, completed provider exchange, input digest and relevant delivery receipts. HOST_QUERY producer: real host operation, capability/version, input/output digests and narrow supported assertion. STATIC_ANALYZER producer: actual invocation, executable/rule digests, selected source and scan disposition. No fake agent or zero-token inference is created for host artifacts.

Acceptance prerequisites are variant-specific. SEMANTIC_RESULT, SOURCE_DELIVERY where required, EXECUTION_EXCHANGE and required TRANSCRIPT_TURN are not interchangeable. A host declaration query does not need a fabricated model transcript, but also cannot claim authorization sufficiency outside its capability.

## 2. Prepare immutable payloads

Run typed parsing, safe-prose validation, source/evidence reference verification, producer authorization and role-specific semantic completeness before final publication. Capture exact input revision, payload digest, explicitly associated subjects and limitations. Preparation does not make a result discoverable and cannot create half of its evidence graph.

States are PREPARED, ACCEPTANCE_PENDING, AVAILABLE or REJECTED as in the shared contract. Body identity is immutable. A correction or changed interpretation creates a successor artifact with explicit relation, not an UPDATE of content under the same artifact ID. Source and provider content obey the existing separate storage policy.

Associate explicitly covered symbols and their inventory-resolved containing file. File association means analysis exists about that file; it is not complete-file coverage. Do not infer subject associations through semantic similarity.

## 3. Seal the producing exchange without a cycle

The model-authored tool action originates in a completed provider response. Record its request/input digest, accepted response/tool arguments and source-delivery descriptors before executing the publication action. When transcript mode requires exact capture, seal the immutable completed turn/prefix in transcript storage. The remaining attempt can continue appending later turns.

The seal must not claim the whole attempt is complete. The publication must not wait for the tool's own success ACK to appear in a future model request: that ACK is produced only after publication, so making it a prerequisite is circular.

A partial stream or malformed unaccepted tool call cannot establish a producer contribution. An unrelated later failure in the same attempt does not retroactively erase a properly accepted earlier contribution. Preserve separate identities for the exchange, tool effect, runtime finalization and transcript receipt.

## 4. Cross-store sequence

Do not open an ATTACH transaction and claim ssr.db plus transcript.db are one atomic authority. Use staged durable transitions:

1. Commit the validated source-free semantic payload/registry entry as ACCEPTANCE_PENDING in the project store, with required receipt identities.
2. The transcript owner commits/verifies the completed producer-turn seal in its own store where required.
3. Record its source-free verified receipt link in the project store through the receipt owner.
4. In one short project transaction recheck every acceptance prerequisite, current generation and exact payload/producer digests; make the artifact AVAILABLE, allocate availability sequence and insert the unique event.

When all receipts already exist, the owner can prepare and publish in a single short project transaction, but it must execute the same checks. A missing receipt is an explicit pending blocker; it must not be replaced by task COMPLETED or a synthetic attestation.

## 5. Availability transaction

```text
with publication_transaction():
    artifact = load_exact_pending_artifact(id)
    verify_payload_and_current_producer_receipts(artifact)
    if transition_key_already_committed(artifact, generation):
        return original_availability_receipt
    require_current_acceptance_policy(artifact)
    sequence = increment_review_counter_inside_transaction()
    mark_available(artifact, generation)
    insert_review_change(sequence, exact_transition_key, artifact, subjects)
    record_request_answer_associations_and_wake_intents_if_applicable()
    commit_operation_outcome()
```

Allocate sequence only inside this serialized commit. Do not reserve worker sequence blocks that can commit out of order behind a lookup's H. Gaps are acceptable; an accepted change cannot appear later below an already observed committed boundary. Duplicate publish/recovery returns the same transition rather than another 'new result' event.

Withdrawals and re-availability have explicit new transitions/generations. Historical events remain immutable. Queries, notices, dependency wake and candidate gates all consult the same current availability predicate. No consumer gets a private-result shortcut merely because source access is broad.

## 6. Receipt and publication recovery

Crash before semantic commit: rerun validated preparation under operation identity. Crash after semantic commit before transcript seal: pending artifact remains unavailable and reconciliation requests/locates the exact missing seal. Crash after seal before cross-store link: verify and link the existing seal. Crash after AVAILABLE/event commit before ACK: recover original receipt without another event or model judgment.

Never edit captured transcript bytes to manufacture a passing receipt. A legitimate historical recovery attestation is a separate, narrowly authorized record with its own provenance. A required integrity failure remains a blocker until that explicit recovery contract permits resolution.

Recovery scans bounded pending records by owner/state, not every document body. Recheck current source/artifact visibility before exposing recovered results. Late predecessor settlement cannot mutate a successor attempt's task or input state.

## 7. Acceptance tests

Publish a contextual answer while its canonical parent remains RUNNING. With a valid own-turn receipt, query/notice/dependency consumers may use it; file coverage remains incomplete. Remove each required receipt in turn and assert all consumers consistently report pending/unavailable.

Inject crashes at every cross-store boundary above. Reconcile twice and assert one immutable payload, one valid receipt link and one availability event per generation. Change the body under an existing ID and require an integrity conflict. Use a HOST_QUERY artifact and verify real capability provenance without fake agent metadata.

Publish, withdraw and restore an artifact after a listing's H: old pages exclude the new epoch, fresh discovery can see it, and history is retained. Crash after a valid answer then fail unrelated later work in its producer attempt: the accepted answer persists. A producer receipt from the wrong task/turn/input digest must fail.

## 8. Implementation order and exit

Implement producer-union parsing and registry adapters; factor the single acceptance predicate; add real turn/prefix receipts; wire staged pending/available transitions; integrate availability events and request wake intents; then update all readers/gates. Completion evidence must show identical acceptance decisions across query, notice, dependency, candidate and export paths plus cross-store crash fixtures. No publication manager model, copied source store, fake terminal receipts or task-completed shortcut is permitted.
