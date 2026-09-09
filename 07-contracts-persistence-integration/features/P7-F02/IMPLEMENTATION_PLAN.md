# P7-F02 — Public SDK and controller integration: implementation plan

Updated: 2026-09-09. Documentation only. Read the [feature](../P7-F02-public-sdk-and-controller.md), [SDK contract](../../../contracts/SDK.md), [baseline](../../../BASELINE.md), P6-F01 admission and P6-F04 completion. The controller consumes harness authority; it must not recreate candidate/readiness/coverage logic.

## Contract-hardening integration — Frozen SDK signatures, DTOs and paired contract proof

Implement the exact methods/constructor annotations/defaults in contracts/reference/public-api.pyi and schemas/sdk-abi.json. DTO field order, nullability, bounds and closed enums come from hardening-v1.schema.json; use immutable slots/keyword-only dataclasses and reject unknown keys/bool-as-int. Export facade and concrete DTO identities must match the same frozen bundle in both packages.

Use actual CommandContext and ProjectQueryContext boundaries, exact admission tokens and public child dispatch. The matching new pair is the only executable pair; CONTRACT_MISMATCH happens before mutation for any missing/wrong ABI/schema/state/prefix/counter capability. Inspect signatures and compare serialized fixtures in installed wheel tests. Add pagination-domain/visibility tests and source-free Error/Issue projection checks; no client-side inferred task transitions.

Normative source: [hardening contract index](../../../CONTRACT_HARDENING.md). Preserve the existing feature procedure below except where this explicit correction replaces it; implement the linked exact schemas, not a local incompatible approximation.

## 1. Map current public and controller boundaries

Inspect actual public exports/signatures/DTO contract versions in ssr.application and ssr.query, controller compatibility checks, registration/query contexts, child_wire, child_dispatch, supervisor/admission, explorer/API projections and frontend request state. Preserve intended facade class identity and delayed harness imports inside the authenticated coordinator child.

The parent-side wire parser must remain engine-import-free. Do not move a convenient ssr import to module scope in child_wire/parent initialization. The controller may use its own job/evaluation databases, but not query a registered harness ssr.db or invoke private CLI helpers.

Produce an old→new interface map before changing any consumer. Package version alone is not proof that every selected capability or schema variant is present.

## 2. Add explicit negotiated public services

Implement the selected public CollaborativeReviewService methods `capabilities(context)`, `plan_collaborative_slice(context, review_run_id, requested_capacity)` and `drive_collaborative_slice(context, plan, admission_token)` through existing application ownership. Implement CollaborativeQueryService `list_work`, `list_requests`, `list_artifacts`, `list_current_findings` and `get_review_completion` through existing query/context/content owners.

Use SDK.md's typed fields and errors, not introspection of private dataclasses as the wire contract. Preserve old service signatures/imports/enum values. New capability negotiation returns exact mode/tool/result/plan/event versions, supported producer/features and required storage horizon. Reject unsupported mode before creating a durable controller execution job.

Query contexts resolve registration→project→review/snapshot under current authorization on every operation. Do not accept an arbitrary database path or model-supplied project ID as a substitute. Exact source/transcript reads remain separate sensitive-content methods with their own handles and bounds.

## 3. Dynamic plan and admission vector

Build CollaborativeSlicePlan in a short read-only harness transaction. Include plan ID/digest, review/config/mode/capability identities, control generation, selection policy/version, requested/effective capacity ceilings, per-resource route/backend/model identities, command budget and state-as-of metadata. Normal unrelated publications do not stale the plan merely because queue membership changed.

The plan authorizes bounded reevaluation under those ceilings. At drive/claim time, harness readiness owners recheck actual task prerequisites/revisions and local balances. The controller grants only its global resource vector/upper bound. A capacity grant cannot override task eligibility or widen source authority.

Exact-task commands are a separate explicit variant. If the selected task becomes unavailable, return the real blocker; never substitute another task just to use the slot. A changed configuration/control/capability digest invalidates a dynamic plan, unlike an ordinary new eligible task.

Test provisional controller grant followed by lost harness claim: release that exact grant once. Do not open both stores under a pretend shared transaction or use force reservation reconciliation to bypass unknown live children.

## 4. Authenticated child command path

Extend child_wire with strict collaborative command/plan/result variants and closed field validation. Preserve exact-task versus dynamic distinction, maximum frame/option bounds, canonical serialization and authentication manifest identity. Public engine dispatch occurs only after manifest, execution authority and command DTO agree.

Dispatch the new command inside child_dispatch using supported SDK calls. Translate public ApplicationServiceError into allowlisted controller-safe error fields; no raw exception/provider/config mapping leaks. Heartbeats/events/results retain original child/job generation and request correlation. Unknown command/DTO versions fail closed, not generic JSON passthrough.

The supervisor claims durable jobs and owns child launch/admission/settlement. HTTP handlers only create/control those jobs. Existing authenticated terminal receipt and parent-loss handling remain unchanged unless an explicit new wire version requires a corresponding test.

## 5. Query projections and event refresh

WorkSummary separates logical work/root, actual task/attempt, category, queued/running/waiting/terminal state, source-safe subject refs and prerequisite/resource blockers. Include accepted answer/lead relationships and independently projected result availability. Do not infer acceptance from task COMPLETED or infer full coverage from the displayed page.

CurrentFinding projects exact family/current revision, argument digest, validity generation and accepted independent verdict. Historical findings/packages remain distinct. get_review_completion uses the shared harness gate and bounded blockers. Unknown usage, required receipts and unfunded obligations remain visible, not hidden behind a spinner or zero cost.

Version safe events such as WORK_READY/WAITING, REQUEST_ROUTED, ANSWER_AVAILABLE, LEAD_RECORDED, ARTIFACT_AVAILABLE, FINDING_VALIDITY_CHANGED and RESOURCE_BLOCKED. Events are UI refresh hints tied to review/job generations; authoritative query responses remain the source of state. On event gaps or reconnect, refresh bounded queries rather than replaying guessed UI transitions.

## 6. Frontend request lifecycle

Extend typed API response unions and state reducers before rendering new statuses. Keep current selection identity `(registration,review,work/subject,query generation)` in every asynchronous request. Abort or ignore stale responses when the user changes projects/reviews/filters. A late old response cannot overwrite the new view.

Keep independent pagination cursors for different lists and an explicit refresh action. Current-finding invalidation triggers an authoritative status refresh, not automatic source download. Freshness/inbox notices show compact references; retrieving source/transcripts remains an explicit user action.

Preserve lazy historical transcript capture lookup: collapsed attempts do not initiate capture/history scans. An expanded attempt fetches only its own bounded content. Subscriptions/streams are closed on unmount/selection change, and reconnect does not duplicate listeners or apply old job-generation events.

Show pending acceptance, queued follow-up, dependency wait, backend pressure and budget blockers with different text/actions derived from typed codes. Do not offer an action unsupported by negotiated capabilities. An unknown future enum yields an explicit unsupported-version state, not false success or an unhandled crash.

## 7. Packaging and exact new-pair compatibility

Build the harness wheel and controller backend/frontend packages in clean environments. Verify public import paths and DTO class identity from installed artifacts, not editable sibling checkouts. Ensure package discovery includes new private modules without accidentally packaging old and new shadowing paths.

Run the exact new/new pair and mismatch-refusal tests; old/old and mixed old/new executing pair support are not required. New controller against old harness must report unavailable collaboration cleanly; it cannot probe private methods as fallback.

Frontend build must regenerate packaged static assets and the existing hash manifest where source changes. Typecheck, lint, component tests and production build use the repo's verified scripts, not invented commands. No live installed controller is restarted during these checks.

## 8. Integration tests

Invoke capability negotiation with missing mode, mismatched plan version and unsupported producer receipt contract; no durable execution job is created. Run a valid dynamic plan, add a new ready context task during execution and verify refill within original resource ceilings. Change control/config generation and verify new claims stop. Exact-task plan must never run another task.

Instrument parent imports with a sentinel/blocked ssr import and parse/validate child_wire successfully; authenticated child can import the public SDK at dispatch. Submit forged launch authority, unknown fields, oversized frames and late terminal receipts; none bypass job generation or leak project state.

Exercise UI A→B selection with delayed A responses, reconnect event gaps, expanded/collapsed historical attempts and held current findings. Assert request counts and selected state, not only snapshots. API/SDK query and export must agree on current validity/closure for the same fixture.

## 9. Delivery sequence and exit

Ship harness public DTO/services and fixtures first, then negotiated controller wire/dispatch and supervisor routing, then safe explorer/API projections, then frontend state/rendering and packaged assets. Keep dormant unsupported UI controls disabled until negotiation succeeds. Finish with the exact matching new pair and mismatch refusals and clean artifact tests.

Completion evidence includes public signature/contract maps, frame/request fixtures, capacity/claim traces, import-boundary tests, frontend race/lazy-loading assertions and installed artifact hashes. No controller project SQL, CLI-output parsing, broad fallback to private helpers, UI-computed finding gates or automatic source/transcript fetch is permitted.
