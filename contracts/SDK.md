# Collaborative public SDK and controller contract

Contract version: collaborative-v1. Add public facades; keep old signatures and DTO identities. These proposed names are the selected integration contract, not current exported APIs.

## Service methods

| Facade / method | Inputs | Output and authority |
|---|---|---|
| CollaborativeReviewService.capabilities | public application context | Supported execution, tool, artifact, notice, scheduling and query contract identities. Read only. |
| plan_collaborative_slice | context, review_run_id, requested_capacity | CollaborativeSlicePlan; no task leases, provider calls or mutations. |
| drive_collaborative_slice | context, plan, admission_token | Bounded slice outcome with actual settled attempts/usage, independent refill, explicit blockers and public effect refs. |
| CollaborativeQueryService.list_work | query context, review_run_id, typed filters, cursor, limit | Work summary pages, canonical owned subjects, active/queued/waiting reasons and current attempt identity. |
| list_requests | context, review_run_id, task_id optional, cursor, limit | Consumer/producer/request revision, states and permitted answer refs; no private pending answer body. |
| list_artifacts | context, review_run_id, subject/filter, cursor, limit | Acceptance availability, type/provenance and current status. Explicit detail/content reader remains separate. |
| list_current_findings | context, review_run_id, cursor, limit | Only currently eligible family revisions with valid upheld receipts; historical query explicitly labels historical rows. |
| get_review_completion | context, review_run_id | Authoritative coverage/work/receipt/material-event/resource blockers and terminal/limited status. |

Use existing public context types and ownership checks. New positional/keyword choices are defined here consistently when implemented; they must be tested in strict signature negotiation. Do not add optional parameters to old methods and assume that is harmless to a strict consumer.

## Required typed projections

CollaborativeSlicePlan contains plan_id/digest, review_id, immutable config/mode/capability digests, control_generation, requested/effective total upper bounds, per-resource capacity vector, command-wide budget envelope, exact_task_id nullable, selection_policy identity, and read state-as-of. A dynamic plan authorizes bounded eligibility reevaluation, not a frozen list of all task IDs. A task claim still validates its exact input revision and availability under current state. An operator exact-task plan may not claim another task if the target becomes unavailable.

Capacity vector identifies backend/protocol/model route and shared resource-group identity, maximum concurrent provider calls and host-process categories where relevant. Controller assigns shared upper-bound admission; harness owns actual per-task feasibility. No provider count is multiplied by batching or a new task type.

WorkSummary includes task/root IDs, task type, owned subjects, mode, state, reason code, current attempt, readiness/receipt/budget blockers, question refs and result refs. Source-derived freeform text is available only in existing explicitly authorized content surfaces. Ordinary operational lists use safe metadata.

CurrentFindingSummary includes family/current candidate revision, argument digest, validity generation, independent verdict reference, evidence-verification state and review completion status. It may coexist with IN_PROGRESS coverage. Server computes it with the same predicate export uses; clients cannot declare readiness by combining partial rows.

## Events and UI

Emit typed source-free events for WORK_READY, WORK_WAITING, REQUEST_ROUTED, ANSWER_AVAILABLE, LEAD_RECORDED, ARTIFACT_AVAILABLE, FINDING_VALIDITY_CHANGED and RESOURCE_BLOCKED through the existing event transport. Preserve sequence/cursor/reconnect behavior and scope all events by review/project. Avoid copied source/prompt/transcript in SSE payloads. Event availability is a UI hint; refresh the authoritative query after gaps, not an inferred local transition.

UI shows original assignment with linked independent leads, blocking context requests, producer/answer status and real queue reasons. New information can be advertised without forcing an analyst/provider call or downloading source. A later validity hold clearly removes current-upheld status while preserving historical records. Keep transcript histories lazy and abort obsolete frontend fetches on task/project change.

## Compatibility and packaging gate

Test all four legacy/refactored pairs. Old mode must stay valid in supported pairs; new mode refuses absent capabilities explicitly. Assert parameter equality, enum membership/meaning, dataclass identity, serialized forms and authenticated child-command schemas. Do not import engine symbols early in parent-only code merely to deduplicate type definitions. Build wheels/sdists from clean source, verify no sibling checkout is required, and rebuild hashed frontend assets when UI source changes.

No new-mode deployment before schema, tool, receipt, planner, claim, query, export and controller support agree. Existing installation hashes/version coordinates come from the tested release manifest, never from this design's historical branch references.
