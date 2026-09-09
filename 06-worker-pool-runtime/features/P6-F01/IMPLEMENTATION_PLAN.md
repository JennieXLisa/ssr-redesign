# P6-F01 — Shared-pool scheduling: implementation plan

Updated: 2026-09-09. Documentation only. Read the [feature](../P6-F01-shared-pool-scheduling.md), [SDK plan contract](../../../contracts/SDK.md), [state](../../../contracts/STATE.md) and [configuration](../../../contracts/CONFIGURATION.md). Continuous admission already exists; extend its eligibility/plan contract, not replace the executor.

## 1. Inventory every phase-dependent gate

Trace `drive_slice` and pool reservation/refill state, task claim SQL, role mapping, BrokerScope review-state validation, public review_planning, worker requests, submission validators and closure. A new planner alone is insufficient if a downstream guard still permits investigation only in a repository-wide phase.

Introduce one mode-selected eligibility authority. Legacy mode retains existing predicates. Collaborative mode evaluates each canonical, focused, context, investigation and falsification task against its actual prerequisites while the review is ANALYZING. Shared source/receipt/candidate checks remain with their owners; do not duplicate their logic in the controller.

## 2. Eligibility versus resource fit

Return a typed eligibility result with task/input revision, prerequisite fingerprint, task category/role route and blockers. Canonical units require the existing settled same-file dependencies/SCC rules. Context work requires a routable request revision. Investigation requires an actionable current candidate; falsification requires a complete current argument and accepted receipts, not an existing verdict.

Resource fit is separate: a ready task may be blocked by provider concurrency, per-file caps, budget or host capacity. Do not rewrite it as semantically not ready. Queries/UI must expose these reasons separately.

The public dynamic slice plan binds review mode/config/capability/control digests, total/per-resource ceilings and command budget. It authorizes bounded reevaluation, not a frozen task list. Newly ready work may refill a slot within those ceilings. Exact-task plans are different: they may not substitute another task when their selected target becomes unavailable.

## 3. Deterministic fairness state

Persist successful dispatch count and a coverage-due entitlement under the review scheduler owner. On a proposed admission, coverage is due when an earlier entitlement remains or the next successful dispatch is the configured nth opportunity. With the selected initial value, every fourth opportunity protects eligible fitting canonical coverage.

If coverage is due but no coverage task currently fits real prerequisites/resources, loan the slot to fitting work and keep the due flag. Serving canonical coverage clears the flag. Increment the dispatch counter only after a successful claim/reservation, not on failed plans, denied admission or polling. Do not accumulate an unbounded queue of debt tokens.

Within eligible noncoverage work, use the declared required-unblocking/adjudication class before optional discovery, then recorded waiting age, discovery score where applicable and stable task ID. Ensure aging participates in the database candidate ordering; sorting a fixed top-N slice afterward can hide old work forever. A canonical task boosted by contextual demand remains one coverage task, not two reservations.

```text
candidates = eligible_and_fitting_candidates_by_resource()
due = scheduler.coverage_due or next_dispatch_is_protected()
chosen = choose_coverage_if_due_else_declared_order(candidates, due)
if chosen:
    atomic_claim_and_reserve(chosen, expected_revision)
    record_successful_dispatch_and_entitlement(chosen.category, due)
```

Pure selector tests receive an explicit queue/state snapshot and return the same selected task/reasons. No manager model or hidden relevance score participates.

## 4. Atomic claim and layered admission

Public planning is read-only. The controller grants shared resource-group ceilings through its admission token; the harness performs exact task feasibility/claim within that grant. These are separate stores/authorities, not one distributed transaction.

Before claim recheck plan control/config identity, active review, exact task revision/prerequisites and held budgets. In the harness transaction acquire its lease and local reservation plus fairness state update atomically. If a controller provisional reservation cannot be used because the claim lost a race, settle/release that exact reservation through the existing protocol. Never retain capacity indefinitely or claim another provider outside the granted vector.

No provider call or child handshake belongs inside a project database write transaction. Recheck revocation immediately before dispatch. Every live attempt carries exact reservation/lease IDs for later settlement.

## 5. Refill without cohort barriers

Keep the existing pool's per-slot settlement and admission loop. A completed/yielded attempt releases eligible capacity after its safe settlement; refill that slot even when a slow peer remains active. Host promotion, receipt reconciliation and wake application should run as bounded coordinator work without consuming analytical model slots.

Search candidate pages per resource group or continue through bounded keyset pages when top candidates cannot fit. Do not repeatedly inspect only the same blocked first page. Preserve progress/backoff state so one pressured backend does not stall unrelated fitting work.

When the pool is full, record/queue valid work. Do not interrupt healthy workers or raise concurrency automatically. When no candidate fits, return truthful reasons and the next eligible host wait condition; an empty ready set is not completion.

## 6. State-change integration

Accepted contextual requests can boost existing required tasks; accepted answers create wake intents; argument-ready events enable falsifiers; valid upheld results trigger host promotion. Each event identifies affected tasks/revisions, so reevaluation is bounded rather than a full project scan per model token.

Do not treat every new optional freshness notice as new work or a wake. No-hit canonical units remain in the inventory and protected service. Optional seed backlog and cost guards belong to P2-F02/P6-F03 and cannot delete registered required leads.

## 7. Restart and cancellation

Restore fairness state, queues, leases, provider pressure and reservations from their real owners. Restart must not reset counters and starve coverage. Do not reclaim a task solely because its worker was slow or logs stopped; use lease/control and orphan-recovery rules.

Cancellation invalidates new claims and exact active authority. Late old attempt settlement may release only its own reservation and record its outcome, not change successor input/task state. A stale dynamic plan fails explicitly; its capacity token does not authorize new work indefinitely.

## 8. Simulation and integration tests

Use scripted zero-network workers at W=1,2,3 and 100. Hold one task open while shorter peers repeatedly complete; assert independent refill. With both categories continuously eligible, inspect successful dispatch sequence and protected coverage opportunities. With coverage genuinely blocked, other work proceeds and entitlement is retained for the next fitting opportunity.

Test empty optional queues, full optional backlog, shared provider caps tighter than W, per-file caps and multiple backend groups. Put old eligible work beyond an initial candidate page and prove it is not permanently hidden. Race two claims for one task and verify one lease/reservation/fairness increment.

Restart mid-fairness cycle and during provisional controller admission. Assert preserved service state and no leaked/double reservations. Exact-task plan becoming unavailable must not fall back to another task. These are correctness simulations, not evidence of real 100-worker throughput.

## 9. Delivery sequence

Centralize mode-selected eligibility; characterize the existing refill loop; add pure selector/persisted fairness; wire layered exact reservation/claim; integrate event-based readiness; update public plan/drive guards together. Completion evidence includes actual admission traces, capacity maxima and cross-layer guard tests. No second executor, permanent 50/50 worker partition, global new-mode phase barrier or preemption policy is introduced.
