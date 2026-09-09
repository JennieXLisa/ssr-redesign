# Frozen collaborative public SDK contract

Contract: `sdk-abi-v1`, wire mode `collaborative-v1`. Resolves H05/H09. Exact callable ABI is `schemas/sdk-abi.json`; every referenced request/result/error object is a closed `$defs` type in `schemas/hardening-v1.schema.json`. `reference/public-api.pyi` is the generated signature/DTO declaration. These are selected new interfaces to implement, not claims that the current harness exports them.

## Exports, construction and signatures

Export CollaborativeReviewService from `ssr.application`, CollaborativeQueryService from `ssr.query`, and the new DTOs from `ssr.collaborative.dto`. The public facade must re-export the same class objects, not redeclare equivalent dataclasses. ReviewService constructor is `(config: SSRConfig)`; QueryService constructor takes no arguments. Reuse the actual public CommandContext and SchedulingAdmissionToken from ssr.application and ProjectQueryContext from ssr.query.context; no replacement authentication context or controller-owned task authority.

All method signatures include self as the first ordinary parameter. `context` is positional-or-keyword; every following parameter is keyword-only. No **kwargs, inferred defaults or optional omitted fields outside those frozen in the ABI manifest are permitted.

```python
capabilities(self, context: CommandContext) -> Capabilities
plan_collaborative_slice(self, context: CommandContext, *, review_run_id: str,
                         requested_capacity: int, exact_task_id: str | None = None) -> SlicePlan
drive_collaborative_slice(self, context: CommandContext, *, plan: SlicePlan,
                          admission_token: SchedulingAdmissionToken) -> DriveResult
list_work(self, context: ProjectQueryContext, *, review_run_id: str,
          filters: WorkFilter, page: PageRequest) -> WorkPage
list_requests(self, context: ProjectQueryContext, *, review_run_id: str,
              task_id: str | None, page: PageRequest) -> RequestPage
list_artifacts(self, context: ProjectQueryContext, *, review_run_id: str,
               filters: ArtifactFilter, page: PageRequest) -> ArtifactPage
list_current_findings(self, context: ProjectQueryContext, *, review_run_id: str,
                      page: PageRequest) -> FindingPage
get_review_completion(self, context: ProjectQueryContext, *, review_run_id: str) -> Completion
```

The three command/service methods retain existing coordinator/admission authority. Planning is read-only; it neither reserves resources nor issues task leases. The dynamic plan permits bounded eligibility re-evaluation within its exact resource vector and command budgets, not a frozen batch of tasks. Exact-task plans may claim only their selected task. Driver rechecks cancellation/admission token before each refill and never multiplies capacity through batching.

## DTO order, types and defaults

All generated DTOs are frozen, slots-based, keyword-only dataclasses. Their field order is `x-python-field-order` in the schema, repeated in sdk-abi.json and verified by the generator. Required nullable fields remain present as null on the wire. Collections use tuples in Python, JSON arrays on wire, in the documented stable order. Unknown keys, bool-as-integer, nonfinite numbers, negative counts, out-of-range integers and duplicate object keys are rejected. IDs are bounded to 200 characters; opaque tokens are bounded to 4096; byte/source cursor references remain governed by their separate 16384 limit.

All counts/sequences are nonnegative integers at most 2^53−1. Timestamp fields are UTC `YYYY-MM-DDTHH:MM:SS.sssZ`; strings are not interpreted in local time. Explicit list filters use empty tuples for no restriction. PageRequest is exactly `{cursor: null|string, limit: 1..100}`; no hidden default when the DTO is supplied. The convenience caller may construct limit=25, but the service signature itself does not silently synthesize a page.

Serialization uses UTF-8 compact JSON, exact declared wire key names, enum strings and all declared fields. Canonical hashes sort keys; ordinary presentation need not preserve key order, but dataclass/signature identity is part of the new paired ABI. Prohibited source/prose does not enter ordinary WorkSummary/RequestSummary; full content uses the explicitly authorized existing reader.

## Pagination and availability

Use typed authenticated query cursors with domain SDK_WORK, SDK_REQUEST, SDK_ARTIFACT or SDK_FINDING; never accept a source/search token as an SDK page. Payload binds project/review, canonical filter hash, state contract and policy digest, initial H and last ordering tuple. Work/request pages order `(created_sequence,id)`; artifact pages order `(availability_sequence,artifact_id)`; findings order `(validity_publication_sequence,candidate_id)` through H. Current visibility/status rechecks apply on each page; H does not freeze authorization. Mutable state is observed at the page transaction and recorded in as_of_sequence. New arrivals require refresh. Return exhausted/next_cursor consistently; no numeric offset into a changing list.

List methods return only the exact declared page type and at most 100 rows. Work/Artifact summaries point to paged subject/result manifests instead of embedding unbounded membership. If dynamic visibility produces an empty page before H is exhausted, return a progressing cursor and exhausted=false, not a false final page. Scans have a bounded host work allowance and no hidden model calls.

## Error form and capability negotiation

Raise `CollaborativeServiceError` carrying the immutable Error DTO; do not expose arbitrary Python exceptions or dictionaries across the SDK. The controller serializes failures as `{ok:false,error:<Error>}` and successes as `{ok:true,value:<declared DTO>}`. It must not reinterpret an exception message to infer retryability. Error.code/retry_kind/commit_state and Issue locations are closed by the schema. SQL paths, raw source, lease secrets and provider bodies never appear in diagnostics.

Before running a new review, compare exact schema-bundle, SDK ABI, state, runtime and prefix receipt digests advertised by Capabilities. Both releases embed the same generated contract artifact. Mismatch is CONTRACT_MISMATCH before mutation, not a best-effort downgrade. The new harness/controller pair is the only supported executing combination. Old runtime mode and four old/new executing pair tests are removed. Historical database/report inspection is read-only and preserves original schema/receipt meaning; it is not a legacy scheduling mode.

Controller parent code may compare inert contract descriptors without importing engine execution modules prematurely. Authenticated child dispatch imports public services only after existing execution authority validation. Do not duplicate core task/candidate eligibility in the UI. Events are source-free hints; after a missed sequence, query the authoritative service. Preserve lazy transcript reads and stale frontend request cancellation.

## Tests and implementation sequence

Generate the .pyi, schemas and ABI fingerprint together; compare regenerated bytes to committed artifacts. Compile/inspect declarations and test every field's requiredness/nullability/bounds/enum, method positional/keyword/default/return properties, class identity through public re-exports, and serialization round trips. Run mismatched-digest rejection before any coordinator mutation. Test independent list cursors, exact-task plan restrictions, expired plan, capacity-vector sums, direct source-content refusal and event-gap refresh.

The schema fixtures prove the selected wire contract, not the behavior of the current engine. Codex must implement this exact facade on the pinned owners, then run the same fixtures against installed wheels for the coordinated pair. Freeze generated-schema hashes in both distribution manifests. There is no requirement to preserve old runtime signatures as a second supported workflow.
