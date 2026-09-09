# P6-F03 — Budgets, backpressure and finite work: implementation plan

Updated: 2026-09-09. Documentation only; no provider spend or throughput test was performed. Read the [feature](../P6-F03-budgets-backpressure-and-limits.md), [configuration](../../../contracts/CONFIGURATION.md), [state](../../../contracts/STATE.md), P6-F01 admission and P1-F08 recovery.

## Contract-hardening integration — Enforceable final-request and metadata budgets

Implement CONTEXT_BUDGET.md at the single actual dispatch point: E170000, O16384 including reasoning, M4096, I_max149520 and checkpoint threshold127092 on the named profile. Counter identity and exact serialized request hash are mandatory; unknown count or changed post-count request denies dispatch. The same gate covers ordinary, repair, checkpoint, resume and batch follow-up requests.

Implement RESOURCE_BOUNDS.md's root/review/consumer/pending quotas with operation receipts, multi-dimension rollback and no-progress settlement. Lifetime lead/request counts are not refunded by dismissal; live counters release only on unique terminal association transitions. Existing receipt recovery stays admissible at full pending quota. Test boundary counts,365k constructed input, second-quota rollback, unchanged retries, unknown usage reservations and full-pool queued leads.

Normative source: [hardening contract index](../../../CONTRACT_HARDENING.md). Preserve the existing feature procedure below except where this explicit correction replaces it; implement the linked exact schemas, not a local incompatible approximation.

## 1. Inventory dimensions and existing owners

Trace model concurrency, backend/shared-resource capacity, per-file limits, request/attempt wall deadlines, command/review/work token and currency limits, tool rows/result bytes, source-delivery bytes, search-scanned bytes, and host matcher/analyzer memory/process limits. Record the existing owner and unit for each dimension. A byte counter cannot substitute for a token budget, and a model slot cannot substitute for a host-memory reservation.

Reuse backend_pressure, existing provider usage/event accounting, worker guards/finalization and controller admission. Keep one authoritative ledger per enforced balance. The controller's global admission store and harness project store remain distinct; do not imply a cross-database atomic reservation.

Configuration remains pinned to the review/attempt. New focused/context work inherits the appropriate existing profile unless explicitly configured. Do not shorten long investigation limits or reset limits on yield, repair, checkpoint, source continuation or child request.

## 2. Reservation representation

Bind each reservation to review, logical root/work, task, exact attempt/provider request or host job, resource group, budget dimension, reserved amount, actual/estimated amount, status and settlement identity. Monetary values use fixed units/Decimal at boundaries rather than binary floating point. Preserve pricing identity and whether reported amounts are actual, upper bounds, estimates or unknown.

Do not persist two mutable balances that can disagree. A materialized balance/cache must be reconstructible from the authoritative ledger and tested against it. The same request may reserve several dimensions, but its consumption is charged once per dimension—not once again for every consumer of shared context work.

A shared producer retains one execution-cost owner. Consumer/root attribution is a reporting allocation, not duplicate billing. Record the selected owner/allocation at admission; cancelling one consumer cannot refund already incurred shared work or shift costs silently to another root.

## 3. Reserve before dispatch

Compute the next real request's reservation from its final input estimate, maximum allowed output and any documented billable dimensions. Reuse actual tokenizer/provider estimation where available, retain uncertainty, and include hidden/reasoning/cache pricing only when the provider's contract supports a sound bound. Unsupported strict currency enforcement must fail preflight or require an explicitly configured token-only policy; never advertise a hard currency cap using unknown prices.

```text
prepared = estimate_next_request(final_request, pricing_contract)
controller_grant = global_admission.try_reserve(prepared.resource_vector)
with project_admission_transaction():
    require_current_plan_control_and_task_revision()
    require_all_local_balances_fit(prepared.reservations)
    claim_exact_task_or_bind_existing_attempt()
    insert_local_reservations_with_unique_request_identity()
if local_claim_failed:
    release_exact_unused_controller_grant()
else:
    recheck_dispatch_authority()
    invoke_provider_outside_transaction()
```

Every enforced dimension must fit. Do not accept a request because concurrency fits while money, wall time or host-memory does not. A lost task-claim race releases the exact provisional global grant; it must not leave a leaked slot or repurpose it for an unauthorized task/provider.

Before each additional model turn, repeat incremental reservation against remaining cumulative limits. Reservations are not a new budget. A tool retry that performs no new provider call creates no provider usage, but actual repeated host scans still consume host resources.

## 4. Settle by request identity, not semantic result

Record the completed exchange and provider usage before releasing its financial reservation. Settlement is idempotent on the actual request/exchange identity. Two model calls returning the same analytical result still cost two real calls. A replayed committed host operation with no new model call costs no fictitious additional model request.

On valid usage, convert held to actual consumed and release only the unused portion. On timeout/cancellation with uncertain server processing, keep unknown or conservatively held usage until the provider protocol or explicit reconciliation establishes a defensible amount. Do not treat a network exception as zero tokens or guaranteed request cancellation.

Physical connection/model-slot release and money uncertainty are distinct: a safely terminated local execution can free physical concurrency while retaining a financial uncertainty hold. If remote execution may still consume a provider-specific concurrency entitlement, honor that provider's pressure/recovery contract rather than assuming a free slot.

A settlement below a strict reserved ceiling is ordinary; reported usage exceeding the modeled ceiling is a metering/contract fault. Record actual usage, stop further admissions under the affected strict policy and surface the discrepancy. Do not clamp actual cost to the reservation to make the ledger balance.

## 5. Required-work estimate and optional admission

In addition to hard balances and protected dispatch opportunities, maintain a versioned remaining canonical-work estimate. Before sufficient accepted samples, use the configured conservative startup estimate. After the selected minimum sample count, derive the declared estimate from committed comparable unit/role cost observations and retain sample size, policy version and uncertainty.

Estimate only remaining canonical obligations, including necessary synthesis and known dependency work; avoid double-counting shared units or counting completed/adopted units again. Separate spent cost, held reservations, uncertain usage, estimated remaining required work and available uncommitted balance in projections.

Admit optional discovery only when its reservation leaves the selected required-work estimate allowance intact. If the estimate already exceeds remaining budget, pause optional work and show the shortfall. Required work may proceed while hard limits permit; the estimate is not an additional infinite entitlement. Reaching an estimate never proves full coverage is funded.

Valid report_lead registration still records a suspicion and queued/deferred required work when funds are unavailable. Do not delete the candidate, call it investigated or mark review completion because execution cannot be funded.

## 6. Finite expansion and host-resource admission

Enforce open contextual requests, depth, revisions, optional focused backlog and no-progress continuation at the durable work/root owner. Rewording or spawning another attempt must not reset these counters. A bound returns an explicit unresolved/deferred outcome, not successful analysis.

Host regex/analyzer jobs reserve their own process count, estimated memory and CPU/wall allowance under the existing host admission authority. Account decoded source, original-byte mapping and native matcher memory together; multiplying an individual maximum by 100 model workers is not safe host admission. Use the fixed bounded host pool or sequential fallback, not one unbounded process per read_batch item.

A host job runs with its own cancellation identity and bounded output. It releases only its own reservation after termination/collection. A complete target file read by the host for matching is scan work; only returned previews count as model source delivery.

## 7. Backend-specific pressure

Normalize retryable rate/overload responses through existing backend_pressure and Retry-After logic. Bind pressure to the correct provider/route/shared-resource group. Unrelated eligible backend work continues. Authentication, unsupported configuration and invalid model identifiers fail explicitly rather than enter an endless pressure retry loop.

Persist next eligible times and retry attempts so restart does not hammer the provider. No sleeping inside a write transaction or occupying a model slot solely for a deferred admission. The scheduler returns BACKEND_BACKPRESSURE with the real limiting resource; queue emptiness during backoff is not review completion.

## 8. Failure-injection and ledger assertions

Run concurrent claims with combined reservations exceeding the remaining balance: only fitting claims commit, and failed claims release global grants. Retry a settlement twice: consumed/held totals change once. Return valid usage after a simulated timeout hold and verify reconciliation replaces uncertainty without double charging.

Return no usage after an uncertain provider timeout: strict policy retains a hold/unknown result, not zero. Change pricing capability to unavailable: new strict-currency admission fails clearly. Cancel an in-flight request and verify physical-resource and financial outcomes are represented separately.

Repeat a source/search cursor and checkpoint across attempts: actual work accumulates; no counter reset occurs. Exhaust optional allowance while canonical work remains: optional discovery defers, registered leads persist, and completion stays false. Increase simultaneous regex requests beyond host capacity: peak child count/memory reservations remain bounded. Backpressure one backend while another runs.

## 9. Implementation sequence and exit

First characterize existing accounting identities/units. Add missing dimensions to reservation projections without duplicating ledgers. Implement reserve/claim/release compensation, exact settlement and uncertainty recovery. Add required-cost estimator and optional guard, then host-resource limits and bounded fan-out. Run deterministic ledger reconstruction and all concurrency tests before enabling strict claims.

Completion evidence includes per-dimension balance equations, request/reservation identities, uncertainty states, actual provider-contract assumptions and collected test outcomes. No free retries, 50/50 spending guarantee, budget reset by continuation, model-authored accounting or invented refund is permitted.
