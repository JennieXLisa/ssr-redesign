# P1-F06 — Independent lead registration: implementation plan

Updated: 2026-09-09. Documentation only. Read the [feature](../P1-F06-independent-lead-registration.md), [tools](../../../contracts/TOOLS.md), [state](../../../contracts/STATE.md) and P1-F03/P1-F08. The original agent reports a suspicion and continues. It does not supervise or await the investigation.

## Contract-hardening integration — Nonterminal prefix proof and bounded lead registration

Before seed/effect execution, record the accepted requesting response with the exact call tuple and observed input binding. Obtain runtime-prefix-v1 and required transcript-prefix-v1 according to PREFIX_RECEIPTS PR-R06. Prefix sealing ends before this tool's own effects/ACK; never wait for AGENT_TERMINAL or use a fabricated terminal capture. A source read requested in the same response cannot retroactively support the reported lead.

Inside the existing candidate/task transaction, recover exact operation first, then reserve root128/review10000 lead counters with domain writes. A full execution pool still creates queued independent work; a metadata quota failure explicitly returns LIMIT_REACHED with no false ID. Pending required receipt uses a bounded durable pending proposal and is not runnable until proof passes. Test capture-seal→project-link crash, proposer later failure, duplicate operation at full quota, second-counter rollback and immediate follow-up with a live proposer.

Normative source: [hardening contract index](../../../CONTRACT_HARDENING.md). Preserve the existing feature procedure below except where this explicit correction replaces it; implement the linked exact schemas, not a local incompatible approximation.

## 1. Tool and ownership boundary

Expose `report_lead` as a nonterminal collaborative tool to analytical roles, including synthesis when it discovers a separate interaction. Inputs are hypothesis, observations, subject_refs, evidence_refs/source_refs, unknowns, requested_check and optional category. Derive review/snapshot/work/attempt from the broker. A category is organization metadata, not an eligibility whitelist. A grounded unknown-category report is valid.

Route the call to a small registration service using the existing CandidateService, evidence preparation and task/coordinator authority. Do not write a new lead database beside candidates or directly mutate candidate SQL in the tool handler. An additional suspicion becomes a SEEDED candidate/follow-up record, not FINAL_READY. The tool response carries original operation/receipt identity and the resulting candidate/task or association, plus truthful queued/deferred status.

A complete exploit path, reachability proof, severity verdict or falsification is not a registration prerequisite. Required minimum is a concrete observed behavior, resolvable permitted source/subject references and a meaningful question that another analyst can check. A malformed or entirely ungrounded payload is a field-specific correction, not a silently discarded lead.

## 2. Self-contained handoff preparation

Validate source-free prose and typed reference identity through P1-F03. Resolve the indexed subjects and exact bytes that motivate the suspicion. Preserve which facts are observed, which assumptions are unestablished and what the requested reviewer should test. Do not scrape private free-form notes from the proposing conversation to fill missing fields.

Prepare a task descriptor containing the lead/candidate identity, source-backed observations, question, accepted input references and explicit unknowns. The next worker reopens material source independently; the descriptor is not inherited source-read credit. It must remain usable if the proposer fails immediately after registration.

Record the completed provider exchange that requested the action before effect execution. When required transcripts apply, seal that completed prefix/turn through the real transcript owner. The lead's acceptance must not depend on sending its own success ACK in a future provider request, or on finalizing the proposer's whole attempt. If a required producer receipt is unavailable, return explicit pending/recovery status rather than pretend independent registration succeeded.

## 3. Registration transaction

Prepare source verification outside the short authoritative transaction. Inside it recheck execution/input authority, look up exact operation replay, and call caller-transaction variants of existing domain operations. Where CandidateService currently owns its own transaction, extract a narrow prepared/caller-connection primitive instead of copying business rules into the broker.

```text
prepared = validate_and_prepare_lead(call, execution)
with project_transaction():
    require_current_attempt_and_revision(execution)
    if operations.committed(prepared.operation_id):
        return operations.original_receipt(prepared.operation_id)
    candidate = candidates.seed_prepared(prepared, connection)
    origin = record_exact_origin(candidate, prepared.operation_id, producer_turn)
    task = tasks.create_followup_if_absent(candidate, prepared.descriptor, connection)
    operations.commit(candidate.id, task.id, origin.id, connection)
return nonterminal_registration_receipt
```

Candidate, origin/evidence associations, follow-up task or durable work intent, and operation outcome must not partially commit. If task creation must be routed through a coordinator outbox, commit the unique intent atomically with the candidate and report that the task is pending materialization. Never return a fabricated task ID. The outbox consumer creates one task per origin/revision and remains an explicit completion obligation.

## 4. Queueing is independent of the proposer

The follow-up may be eligible before original unit/file completion. Do not add a dependency on the proposer's terminal result or canonical parent synthesis. Enable this only with the mixed prerequisite scheduler in P6-F01; legacy phase filtering must not silently leave accepted leads permanently unschedulable.

When capacity is free, the normal scheduler may admit the work. When the pool is full, retain the queued task. Do not preempt a healthy worker or allocate beyond provider/project limits. Budget exhaustion records an unfunded/deferred obligation with a reason; it does not delete the lead or report the review complete.

The original attempt stays RUNNING with the same assignment and remaining budgets. No polling, answer retrieval or dependency is created for it merely by reporting a separate issue. Context needed to complete its current analysis uses `request_context_review`, not a hidden blocking flag on report_lead.

## 5. Replay versus semantic deduplication

P1-F08 exact-operation replay returns the same candidate/task/receipt. Two reports about the same file are not automatically duplicates. Same source with different claims or assumptions remains distinct unless an explicit reconciliation establishes equivalence.

For an exact already-registered origin that later appears in the proposer's canonical submission, record/reference its origin ID and avoid recreating the same seed. Preserve every legitimate producer's observation. Do not overwrite a candidate hypothesis because another agent used a similar title. Compatible-work association belongs to the collaboration/candidate owner and must return its actual target and reason.

A changed analytical proposal is a new semantic operation. Repeating a provider call ID with altered arguments is invalid correlation, not permission to update an old committed result.

## 6. Failure cases and visible outcomes

Invalid source reference: REJECTED, no domain effects, exact correction pointer. Candidate insert failure: transaction rolls back including any work intent. Crash after commit/before ACK: recover original receipt, no new model judgment. Outbox materialization delayed: report durable intent/task-pending state, not running. Proposer later fails: lead remains a valid registered suspicion; no automatic dismissal. Follow-up investigator refutes it: candidate gets the proper independent disposition without changing proposer's coverage result.

Current access still applies when recovering receipts. An expired agent cannot initiate a new write through a recovery route; the host may settle its exact precommitted operation. Diagnostic responses must not expose hidden candidates merely to explain duplicate handling.

## 7. Acceptance fixtures

Script A to report a deletion-path suspicion halfway through reviewing a command builder, then continue its assigned source read and submit its ordinary result. Run B on the follow-up before A terminates. Verify A's attempt did not end, B has a self-contained descriptor, and original file coverage remains unfinished until its own contract passes.

Repeat with all slots occupied: lead and queued work survive; no extra active worker or forced cancellation. Repeat with budget exhausted: obligation remains visible and review completion is false. Kill A after registration; B still runs from persisted inputs.

Inject crashes after candidate preparation, before transaction commit, after commit, and during outbox consumption. Assert either no committed effect or one candidate/origin/work intent and one follow-up task. Retry identical calls concurrently and compare receipt IDs. Submit distinct same-file hypotheses and prove both survive. Verify canonical pass-through of the original lead origin does not duplicate it.

## 8. Implementation order and exit

Implement safe prepared-lead validation first; add caller-owned candidate/task transaction and operation receipt; wire nonterminal broker exposure and turn provenance; integrate scheduler eligibility; test canonical-origin reconciliation and full-pool recovery. Do not expose the tool as complete until its durable registration and independent follow-up path both work. No separate lead manager model, duplicate candidate store, automatic exploit generation or final-finding bypass is part of this feature.
