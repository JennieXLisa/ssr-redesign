# P1-F03 — Reference-based inputs and submissions: implementation plan

Updated: 2026-09-09. Design guidance, not implemented behavior. Read the [feature](../P1-F03-reference-based-inputs-and-submissions.md), [role projections](../../../contracts/ROLE_PROJECTIONS.md), [tools](../../../contracts/TOOLS.md) and [state](../../../contracts/STATE.md). This plan specifies the actual normalization and commit sequence; it does not authorize an unvalidated generic analysis dictionary.

## 1. Inventory the real role contracts

Use the authorized implementation checkout and identify each SYMBOL_REVIEW, FILE_REVIEW, LINK_REVIEW, INVESTIGATION and FALSIFICATION input/result parser, validator and commit function. Include the new FOCUSED_ANALYSIS and CONTEXT_REVIEW contracts only once their owners exist. Record every outer field supplied mechanically by the task and every nested field chosen analytically by the model.

The mechanically removable set is role-specific. A candidate-owned investigation can derive its outer candidate_id; a new lead still needs explicitly selected subjects. Never recursively remove all fields named symbol_id, candidate_id or path: nested path steps, candidate proposals and reference choices carry analysis. Store this transform as a reviewed mapping used to generate the collaborative model schema and the inverse host normalization. Legacy schemas and their hashes remain unchanged.

A schema comparison test must prove that all nonmechanical required fields, enums, bounds and additional-property restrictions survive the transform. The provider projection may be simpler than the internal schema, but the host always enforces the complete internal contract.

## 2. Internal normalized submission

Define a private prepared submission with operation identity, execution/assignment identity, bound input revision/digest, typed semantic result, verified references and a source-map from internal field paths back to model JSON pointers. Keep raw provider bodies out of it. Do not allocate accepted evidence IDs or mutate domain rows merely to parse input.

Model input is the role-specific body plus `input_token` and typed references. The host loads the token's recorded issued input, not whatever happens to be the newest task row. Validate token contract, issuer/work/review/snapshot, revision and digest. Verify the referenced work is still active and the revision is either unchanged or explicitly acknowledged through the input-delta protocol. A stale token returns a refresh-required analytical error; normalization must not silently graft the old conclusion onto the current candidate.

```text
normalize(call, execution):
    issued = inputs.resolve_exact(call.input_token, execution.work)
    require_current_input_or_explicit_delta(issued, execution)
    semantic = role_parser.parse(call.analysis)
    references = resolve_typed_refs(call, execution)
    full_result = project_host_identity(issued, semantic, references)
    return PreparedSubmission(full_result, references, field_path_map)
```

## 3. Resolve reference kinds separately

SOURCE_REF: authenticate its domain-separated token using the P1-F02 codec, then validate review/snapshot, file hash, half-open range, span hash and optional contained symbol. Reopen through the verified source resolver. It identifies bytes; it is not an accepted claim. A rotated or invalid token requires a fresh authorized read/reference. Its original durable evidence coordinates are not invalidated by key rotation.

EVIDENCE_REF: retrieve the exact existing evidence record through `EvidenceRepository.resolve` or its refactored owner. Check current availability, source identity, claim/kind and owning result visibility. Keep original creator identity. A new use belongs to the consuming result/operation, not a rewrite of `created_by_agent_run_id`.

ARTIFACT_REF: resolve the exact immutable result and required receipt/visibility state through its owner. A readable source file does not authorize private child-result contents. Do not replace unavailable D18 with newer D19. Record whether the artifact is merely context or a material dependency explicitly selected by the analyst.

A SYMBOL_REF or RELATIONSHIP_REF is navigation/subject identity, not evidence. Reject a notice batch ID in an evidence field even when both happen to look like UUIDs. No text-similarity search is allowed to repair an unknown reference.

## 4. Build evidence without damaging existing provenance

For a new claim, combine the model's safe claim/kind with host-resolved source coordinates and actual producer operation. Call the existing evidence preparation/verification owner before the commit transaction. Preserve its exact hash and containment checks.

The inspected evidence ID derives from source coordinates/hashes plus claim and kind, while insertion also checks producer fields. Therefore, do not blindly call `record` as a new author when an identical evidence identity exists. Add an explicit reuse path: under the domain transaction load the existing identity, compare every content-defining field, preserve the existing author, and add the consuming result's evidence-usage link. A changed claim/kind is a different evidence item. A conflict in immutable fields is an integrity failure, not an UPDATE request.

Concurrent identical preparation is expected. On uniqueness conflict, re-read and perform the same content comparison inside the transaction; only an exact identity may be reused. Never use INSERT OR REPLACE or drop the original provenance to make a test pass. The current operation's contribution linkage records who selected the evidence and for what claim.

## 5. Distinguish source verification from source delivery

A verified token proves that the host can identify authentic bytes. Required inspection predicates must additionally consult original-byte intervals actually included in model-bound exchanges for this attempt. Metadata lookup, old checkpoints, an advertised artifact or another agent's summary cannot satisfy them.

For a whole-function requirement, calculate coverage against the original required range, not against the union of any references the model supplied. For a material candidate path, preserve the domain's current required-read facets. If more source is required, report the missing selected ranges at the agent input locations and allow P1-F05 return to analysis. Do not invent that the model inspected a range simply because its hash verified.

Cross-file evidence can support a claim about assigned unit A without granting canonical coverage ownership of B. The role validator still checks A's exact inventory/dispositions. Candidate-path subjects are not constrained to A merely because its origin was a unit review.

## 6. Validation and atomic commit

Perform parsing, safe-prose checks, immutable source verification and full role validation before acquiring the final write transaction. Preserve independent issue locations through the normalization source-map. Inside the short transaction recheck work input revision, candidate/graph revision, lease/control generation and required accepted-reference state. Revalidate any mutable authority used by the prepared object; immutable source need not be re-parsed under a long lock.

Commit role payload, evidence rows or usage links, publication associations and the tool-operation COMMITTED outcome through the existing domain transaction owner. No helper commits independently. Required transcript/producer-exchange receipts remain real prerequisites; use ACCEPTANCE_PENDING where allowed, not fabricated completion. If domain commit succeeded and the acknowledgment was lost, P1-F08 recovers the original receipt without another model result.

```text
prepared = normalize_and_validate(call)
with domain_transaction():
    require_same_lease_and_revision(prepared)
    resolve_mutable_acceptance_prerequisites(prepared)
    result = domain_commit(prepared)
    operations.commit_outcome(prepared.operation_id, result.receipt)
return result.receipt
```

## 7. Tests with observable assertions

Create two agents, the same snapshot range and distinct claims. Exact same source plus a different claim produces distinct immutable evidence. An exact reused claim preserves its first creator and records a second use. Pause two transactions before identical insert and verify one immutable evidence identity with both legitimate contribution links, not an author collision masked by overwrite.

Supply a forged SourceRef, wrong-snapshot symbol, artifact ID in an evidence field, a span outside its declared symbol and a protected child artifact. Assert typed field-specific rejection and zero accepted-result/evidence-usage effects.

Change the candidate revision after provider request construction but before submission. Assert rejection against the old input_token; fetching current context may issue an explicit delta, but replay of the old result remains stale. Repeat cancellation after prepare and before commit; no successor state changes.

For every role remove one analytical required field and prove normalization does not fill it. Also supply redundant forged outer identity fields and prove unknown-field rejection rather than accepting a model-provided lease. Round-trip valid compact results through full domain parsers and compare semantics with equivalent legacy fixtures under separate contracts.

## 8. Delivery slices and completion evidence

First implement reference resolvers and transform tests without enabling writes. Then add role normalization and error source-maps. Then add evidence reuse/usage transactions and real-delivery predicates. Finally integrate all role commit paths and P1-F08 recovery.

The completion record includes per-role field maps, source/evidence/artifact type tests, concurrency barriers, exact immutable-record assertions and preserved public contract checks. No embedding lookup, second evidence store, automatic severity/control flags or general mutable result editor belongs in this feature.
