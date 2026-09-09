# P3-F01 — Contextual requests and routing: implementation plan

Updated: 2026-09-09. Documentation only. Read the [feature](../P3-F01-contextual-requests-and-routing.md), [TOOLS.md](../../../contracts/TOOLS.md), [STATE.md](../../../contracts/STATE.md), and P3-F04 for blocking-edge checks.

## Contract-hardening integration — Exact routing and consumer quota transactions

Resolve a request to its immutable question/facet revision and subject/assumption/input digests before equivalence lookup. Join only exact compatible work or accepted answers; a similar filename/name is not equivalence. Reserve the live consumer count64 and root request total256 in the same transaction that registers the association.

Cycle/depth checks operate on the resulting graph with the actual producer task and depth8 limit under the same writer. An edge that would exceed a cap is not implemented by spawning a duplicate producer. A request becoming ANSWER_AVAILABLE is backed by a ContextAnswer artifact and RuntimePrefix proof, never a producer's unfinished private notes. Test last-consumer-slot races, opposite concurrent edges and answer revision changes between lookup and association.

Normative source: [hardening contract index](../../../CONTRACT_HARDENING.md). Preserve the existing feature procedure below except where this explicit correction replaces it; implement the linked exact schemas, not a local incompatible approximation.

## 1. Normalize the question and its context

`request_context_review` accepts question, explicit subjects/locators, assumptions, requested facets, evidence/source references and blocking intent. Bind caller task/inquiry, review, snapshot, input revision and actual producer operation from execution. Validate bounded source-free prose and P1-F03 references. A question must identify a missing fact, but need not establish a vulnerability.

Create a canonical equivalence key from snapshot, governing policy/contract, exact subject set, question/facet revision and assumptions. Sort only explicitly set-valued subject/facet fields; preserve meaningful argument order and text. Do not use filename/CWE equality or embedding similarity as automatic reuse authority. Unknown locators create NEEDS_MAPPING, not guessed symbols.

A caller gets an attributable request/consumer link even when its producer is shared. Keep the distinction between caller request identity, shared production equivalence and actual producer task. Do not erase the second caller's rationale when joining.

## 2. Routing order and decisive predicates

Use one collaboration router, not a manager model. Check host deterministic capability before allocating model work. Then apply the feature's routing order:

1. Exact compatible available answer: snapshot, subject coverage, requested facets, question revision, assumptions and policy all match. Recheck real acceptance/visibility and retain the exact artifact ID.
2. Equivalent in-flight request: same canonical equivalence, compatible producer state, and no forbidden dependency cycle. Add a consumer, not another producer.
3. Queued canonical unit owning the relevant subject: attach question/context and request a priority boost through task/scheduler APIs. Keep canonical unit membership and callee prerequisites intact.
4. Active canonical reviewer: create a work-scoped inbox delta through P3-F02; never edit its original admitted request or steal its lease.
5. Targeted CONTEXT_REVIEW: create bounded supplementary work for the specific missing facets when no usable route exists or a reviewer declines/finishes without answering.

A generic accepted function summary is not compatible merely because it mentions the same symbol. Check explicit answered facets and conditions. Missing metadata cannot be treated as a successful equivalence proof.

## 3. Separate routing preparation from authoritative commit

Read candidate routes and prepare normalized descriptors outside the write transaction. Inside a short serialized project transaction recheck caller authority/input, exact operation replay, producer state/equivalence, request limits and blocking-edge safety. If a candidate producer finished meanwhile, recompute a valid route; do not attach an orphaned request to a terminal task.

```text
prepared = normalize_request(call, execution)
route_candidates = inspect_existing_answers_and_work(prepared)
with collaboration_transaction():
    require_current_caller_and_revision(prepared)
    if exact_operation_committed(prepared): return original_receipt
    route = revalidate_or_choose_route(route_candidates, prepared)
    request, consumer = create_or_join_request(prepared, route)
    check_and_insert_blocking_edge_if_requested(consumer, route)
    attach_inbox_or_create_targeted_task(route, request)
    record_operation_receipt(request, consumer, route)
return nonterminal_routing_receipt
```

Use unique equivalence/producer-intent constraints to serialize two concurrent identical requests. Task creation and request-to-producer association must commit together, or use a unique durable outbox intent with explicit pending materialization. No provider call or source parsing occurs under the write lock.

## 4. Route to existing canonical work without changing ownership

Resolve subjects through existing review-unit membership, including recursive components. A question spanning several units can route targeted facets to their owners without declaring a whole file newly assigned. Definite same-file dependencies remain coverage prerequisites; a priority boost cannot bypass them.

For an active unit, record pending inbox delivery and return ROUTED/WAITING_FOR_ANSWER as appropriate. The caller does not automatically yield. It may continue independent research, or explicitly yield through P6-F02 against registered blocking requests. A nonblocking question is never added to its readiness predicate accidentally.

When an active large reviewer reports NEEDS_DIFFERENT_SCOPE, expires or completes without the answer, preserve the same request/revision and route supplementary work. Do not duplicate full-file review by default. A targeted helper receives the concrete question, known facts, explicit unknowns and source references, not another worker's raw conversation.

## 5. Shared consumers and revision handling

Each consumer records required question revision, blocking intent and disposition. An answer usable by one consumer may be incompatible with another whose assumptions changed. Superseding a consumer request creates a new revision; do not retroactively retarget accepted answer history.

Cancelling one consumer removes only its active demand/blocking relation. Keep a shared producer while another consumer needs it or canonical coverage requires it. Exclusive optional producer cancellation goes through the task owner; the router never deletes shared work rows. Whole-review cancellation uses the review control path separately.

Source/analysis visibility is checked for the receiving caller, not merely the producer. Do not leak a private answer ID through 'we already have an answer' notices. Routing to permitted source does not grant access to another review's accepted artifacts.

## 6. Failures and finite limits

At request/depth/revision limits, retain a visible unresolved question/limitation and return actionable REQUEST_LIMIT/DEPTH_LIMIT outcomes. Do not record ANSWER_AVAILABLE or candidate dismissal. Rewording a question without new evidence cannot reset logical-work no-progress accounting.

A failed canonical task is visible and may cause supplementary routing or a named blocker. Unrelated requests continue. A routing transaction retry reuses the original operation/request identity; it does not allocate another worker. An accepted answer found during a retry is returned as exact reuse with the new routing decision recorded, not silently pasted into the original context.

## 7. Integration fixtures

Create caller A querying subject S42 with a queued canonical owner: assert one owner, one request association and a priority proposal, not another file task. Repeat with an active owner and verify an inbox delta rather than mutation of its original request hash. Finish the owner immediately before routing commit and verify supplementary work remains available.

Run concurrent equal requests from A and B: one producer with two consumer links and independently attributable receipts. Change assumptions or requested facets and prove no join. Cancel A and prove B/canonical demand keeps the producer active. Supply an exact accepted answer with complete metadata and verify no model task; remove one required facet and verify reuse is not accepted.

Add cyclic/depth-limit fixtures through P3-F04. Crash after request creation/task intent/commit and verify idempotent recovery. No lookup or routing ACK should change caller RUNNING status; only explicit yield does.

## 8. Build sequence and acceptance evidence

Implement normalization/equivalence tests; add exact accepted-answer lookup; add join/consumer transactions; wire queued canonical context/priority; wire active inbox and completion fallback; finally enable targeted task creation and mixed-pool admission. Completion requires routing reason records and race/consumer-cancellation tests. No natural-language manager router, private transcript sharing, automatic waiting or permanent task-per-file duplication belongs here.
