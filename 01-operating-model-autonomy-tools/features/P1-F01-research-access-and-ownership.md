# P1-F01 — Research access and assignment ownership

Version: 0.1  
Behavior: AGREED  
Implementation direction: AGREED  
Detailed document: FIRST DRAFT — pending document review  
Implementation readiness: PENDING REFACTOR MAPPING AND CONTRACT DECISIONS  
Implementation/test status: NOT IMPLEMENTED OR RUN BY THIS DOCUMENTATION TASK

Decision basis: P1-D01, P1-D02, P1-D14 and P1-D15 in the
[decision register](../../DECISION_REGISTER.md).

## 1. Purpose

Give analysts read-only research access throughout the authorized immutable project
snapshot while preserving their particular assignment and publication authority.
A reviewer must be able to inspect a relevant helper, caller, configuration file,
or surrounding declaration without first acquiring another review assignment.

Background reviewers, focused analysts, investigators and falsifiers receive this
research access. File synthesizers also receive source and index access for
reconciliation and cross-symbol reasoning; that does not direct them to repeat
all completed symbol reviews.

**Example:** a reviewer owns review unit A. It follows an indexed relationship to
helper B in another permitted file, reads B, and continues the analysis of A.
The read needs no new model approval, scope-expansion conversation, or worker.
It does not complete B's coverage or let A submit another worker's result.

This feature implements an authority separation. It does not require a new agent
framework, replacement index, or independent permission-management system.

## 2. Reference baseline and reuse

Reference repository: `JennieXLisa/source-review-harness`  
Reference branch: `codex/0.1.2-investigation-tool-recovery`  
Reference commit: `8b7ed0e335d4f4fb5ae53ef6e059334661279f20`

These are inspected source references, not proof of the refactor's present state.
Read the actual delivered refactor before assigning implementation paths. The
current code-level facts below are narrower than the new requirements. See the
[baseline notes](../../SOURCES.md).

| Inspected owner | Observed behavior | Treatment in this feature |
|---|---|---|
| `BrokerScope.authorize()` in `src/ssr/tools.py` | Checks active review/task/agent, snapshot, role, attempt and lease. File and symbol reviewers' allowed paths must equal their assigned file. | Retain execution authentication. Separate the assigned-file rule from general research reads; retain its appropriate use in assignment validation. |
| `ToolBroker.__init__()` | Bounds allowed-path/symbol collections by `max_context_items`, creates a source scope from them, and builds a file-ID map from those paths. | Do not implement project-wide access by filling those collections with the entire repository. Separate response/context selection from accessibility. |
| Broker's attempt-local source-read state | Maintains read intervals for the current attempt rather than inheriting them on retry. | Preserve honest attempt-local read accounting. Access permission is not a record that a new attempt inspected the source. |
| `SourceScope` / `SourceResolver.resolve()` | Checks scope, bounded range and exact hashes; resolves original source coordinates. | Reuse verified reads. A focused authorization component may compose an internal per-read scope without changing canonical assignment ownership. |
| `read_verified_file()` | Checks manifest membership, permitted captured classifications, safe file access, exact size and content hash. | Keep these checks. Do not replace them with an arbitrary filesystem read. |

The inspected source reader allows captured `REVIEW_FULL`, `REVIEW_COMPACT` and
`CONTEXT_ONLY` content. The manifest's existence alone is not enough: a row without
permitted captured content must not be treated as readable. This feature does not
change classification, target execution, or filesystem safety policy.[^source]

The broker's assignment coupling and context-item checks are visible in the
inspected construction and authorization path.[^broker]

## 3. Agreed requirements

The following requirements formalize the agreed behavior. Exact wire schemas,
code identifiers, and rollout policy are not approved merely by these IDs.

| Requirement | Required behavior |
|---|---|
| P1-F01-R01 | Analytical research access MUST be read-only and bound to the authorized review snapshot. It MUST NOT use the live target as substitute evidence. |
| P1-F01-R02 | Background reviewers, focused analysts, investigators and falsifiers MUST be able to inspect permitted source outside their assigned file or symbol. |
| P1-F01-R03 | File synthesizers MUST have source and index access for reconciliation. Their required work remains synthesis, not routine re-review of all children. |
| P1-F01-R04 | The host MUST distinguish execution identity, assignment ownership and research policy. Research permission MUST NOT implicitly enlarge the assignment or terminal-result authority. |
| P1-F01-R05 | Permitted cross-file research MUST NOT require another worker, manual approval for each read, or a new coverage assignment. Ordinary deterministic authorization is still required. |
| P1-F01-R06 | Access MUST be resolved on demand through the existing snapshot manifest and index. Full project file/symbol catalogues MUST NOT be required in every worker or initial prompt. |
| P1-F01-R07 | Accessible project size MUST NOT be conflated with the number of context items returned to the model. Actual reads, result pages and cumulative usage remain bounded by applicable configured limits. |
| P1-F01-R08 | Existing role/attempt/lease/control checks MUST continue to apply. Broad research permission MUST NOT authorize operations from a stale or inactive execution attempt. |
| P1-F01-R09 | Existing exclusions, captured-content checks, snapshot integrity and filesystem boundaries MUST remain enforced. A valid-looking ID or path is a lookup input, not a grant. |
| P1-F01-R10 | Reading subject B while assigned A MUST NOT complete B's coverage, claim B's task, publish B's private result, or mutate B's lifecycle. |
| P1-F01-R11 | Required source-read accounting MUST describe the ranges actually returned to the current attempt. A prior read or available summary MUST NOT automatically count as that attempt's source inspection. |
| P1-F01-R12 | The implementation MUST reuse the existing broker, index and source-verification authorities where applicable. It MUST NOT introduce a second inventory or competing coverage/acceptance authority as an access shortcut. |

The unchanged assignment contract still governs what a final result may contain.
Cross-file evidence support may require P1-F03 and the Phase 4 contracts; broader
reading alone does not silently relax those validators. Independent leads use
P1-F06's explicit registration boundary, not a side effect of a read.

## 4. Implementation mechanism agreed in discussion

### 4.1 Three responsibilities inside the existing host

| Responsibility | Host-owned material | Decision |
|---|---|---|
| Execution identity | Review, snapshot, task, agent, attempt, lease and applicable control state. | Is this operation from a currently authorized execution? |
| Assignment | The review unit, synthesis, candidate or other deliverable and its assigned result contract. | What must be completed, and which state may this result affect? |
| Research policy | The bound snapshot and applicable permitted-source policy. | May the requested source or index information be accessed? |

These are logical responsibilities. They need not be three services, three tables,
or three new public classes. Reuse the existing representations where they express
the distinction cleanly. Do not pass the entire worker or broker into extracted
helpers simply to give them unrestricted access to its state.

### 4.2 On-demand read path

For an existing symbol ID, use this processing order:

1. Authenticate the active attempt through the existing host checks.
2. Resolve the ID against the attempt's bound snapshot, not a model-selected
   snapshot or an unqualified global lookup.
3. Determine its file and requested range from verified indexed metadata.
4. Check research access against the existing manifest, captured-source policy
   and relevant host authorization. Do not use assignment membership as the
   general read-permission rule.
5. Call the existing verified source reader for the bounded range.
6. Apply response limits and record the range actually returned for this attempt.
7. Return source with its exact metadata; leave assignment and canonical coverage
   state unchanged.

For file-ID, path, search and relationship operations, the same execution and
research policy must be applied. P1-F02 will specify their discovery and paging
interfaces. Do not create a second policy by copying authorization into every
handler. Retrieval of private or unpublished analysis has additional acceptance
rules; permitted source access alone does not make those records shareable.

### 4.3 Scope composition without a project-wide per-worker list

A focused policy component integrated with the broker can authorize a resolved
file/range and construct the narrow internal `SourceScope` needed by the existing
resolver. This scope represents one permitted read, not a new model-controlled
coverage assignment. It does not require a persistent scope record for each read.

The exact function names and object shape must be mapped to the refactored code.
The critical property is that only host-validated manifest membership can produce
that internal resolver input. A caller must not bypass the research check by
constructing arbitrary paths or changing the snapshot.

Bounded caches for immutable metadata may be useful, but are optional. A cache
must not substitute for checking whether the current attempt remains authorized.
Do not introduce a distributed cache or precompute a complete per-agent ACL merely
to support ordinary index queries.

## 5. Interfaces and data — specified meaning, pending exact signatures

| Boundary | Input meaning | Output meaning | Still to confirm |
|---|---|---|---|
| Attempt authorization | Host-bound execution identity plus current durable lifecycle. | Authorized current attempt, or an explicit failure. | Refactored owner and exact call signature. |
| Indexed subject resolution | Existing subject ID and the host-bound snapshot. | Matching indexed subject and original source coordinates. | How existing lookup interfaces are exposed in P1-F02. |
| Research permission | Authorized attempt, resolved file/range, applicable project policy. | Permission to perform the bounded read, or denial. | Smallest internal representation; no new public schema is implied. |
| Verified source read | Host-authorized scope and exact range/hash expectations. | Verified source and original coordinates/hashes. | Whether refactor changes the owner, not the integrity guarantees. |
| Assignment validation | Original assignment and the submitted result's affected subjects. | Result remains within the assignment's publication authority. | Cross-file reference details with P1-F03/Phase 4. |

The model cannot supply a new lease, change assignment ownership, choose another
review snapshot, or grant itself rights by adding identifiers to a payload.
Precise error schemas are P1-F07's responsibility; F01 must supply enough internal
cause information for the model-facing layer to explain failures accurately.

## 6. Ordered implementation guidance

This is guidance derived from the agreed mechanism, not authorization to implement
before the open contract decisions below are settled.

### Step A — Map the refactored owners and old coupling

Locate the current equivalents of broker authorization/construction, worker scope
selection, source scope/resolution, indexed lookup filters, dossier selection,
read-interval accounting and terminal assignment validation. Record which reads of
`allowed_paths` or `allowed_symbol_ids` represent research versus assignment.

**Do not globally replace every use of an allowed-path collection.** Some consumers
may enforce evidence containment, assignment ownership or publication boundaries.
Classify each consumer and make its intended meaning explicit.

Exit evidence: a short old-owner/new-owner map and the affected test list, including
negative publication tests. Confirm remaining role mappings with the user when
an existing role does not clearly fit the approved responsibilities.

### Step B — Retain identity and assignment checks

Preserve the current construction and revalidation of task/agent/attempt ownership.
Keep canonical assignment subjects separate from the research policy. Do not
remove task-type, lease, generation or snapshot checks while broadening reads.

Exit evidence: baseline stale-attempt and ownership tests still exercise the same
authority, plus a test that wider reads leave assignment identity unchanged.

### Step C — Add the focused research-access decision

Use the bound snapshot, manifest and existing permitted-content rules. Make the
policy callable by the broker's read/navigation handlers. Prefer existing query
and resolver components over new stores. Resolve membership on demand.

Exit evidence: authorized cross-file reads succeed; excluded, foreign-snapshot
and unsafe reads fail. The same policy is reached for alternative lookup inputs.

### Step D — Wire the read surfaces without changing result ownership

Separate file-catalog selection and tool context limits from the set of researchable
files. Adjust source/stat/navigation filtering to use research authorization. Expose
the approved read/index capabilities to synthesis while retaining its narrow
assignment objective. Preserve attempt-local read accounting and byte limits.

Do not use this step to expose every private review result, alter the final gate,
relax evidence validators, redesign the candidate lifecycle, or add a new tool
category. Use the existing APIs first; coordinate actual interface additions with
P1-F02/P1-F03 and their accepted contracts.

### Step E — Verify the coupled paths

Run the feature tests below plus affected broker/source, worker/context, distributed
publication and SDK tests selected from the real branch. Verify that the model's
actual tool surface permits the approved reads; a Python helper existing behind an
unavailable tool is insufficient.

Check execution-contract impacts: new tool availability, permission semantics or
dossier changes are functional changes. Do not describe changed execution material
as bit-identical to historical receipts. Record required contract/version and
activation decisions; their exact solution must be agreed rather than guessed.

### Step F — Review the resulting document and change scope

Report the new owners, unchanged authorities, observed behavior, tests actually run,
remaining compatibility limits, and any code/specification discrepancy. Do not
claim the entire Phase 1 design is complete when only this authority seam exists.

## 7. State, concurrency and persistence

Use existing durable review/snapshot/configuration and task/attempt identities as
the starting authority. This discussion has not approved a new permissions table,
role database, or per-read scope ledger. Audit/read metadata should use the existing
mechanisms where compatible; any required additional persistent representation
must be justified and discussed.

The active request's resolved target and per-read scope are transient execution
material. Permissions are not source-read receipts. Read accounting remains
attempt-local. New checkpoint or lead records belong to their own feature contracts.

Do not hold a write transaction merely to enumerate an entire repository or perform
source I/O. Preserve existing transaction and lifecycle ownership. If cancellation
or a lease change occurs during a read, preserve the actual authorization/cancellation
boundary; do not let a cached permission authorize later operations from a dead
attempt. Exact cross-call race behavior must be verified at the existing runtime
seam, not claimed solved by a newly named policy object.

The snapshot remains immutable. A file mismatch must be reported as an integrity
failure; do not silently recapture source, substitute live bytes or update the
manifest to fit an unexpected file.

## 8. Failure behavior

| Condition | Required behavior |
|---|---|
| Valid subject outside assignment, inside permitted snapshot | Permit bounded research; do not change assignment ownership. |
| Unknown or wrong-snapshot ID | Reject resolution; do not search another snapshot for a replacement or disclose its contents. |
| Excluded or non-readable captured classification | Deny content access with a permitted diagnostic; manifest presence is not permission. |
| Invalid or oversized requested range | Explain the range/limit problem; preserve configured limits and allow a valid narrower request. |
| Stale lease, wrong attempt, inactive work | Reject the operation under existing execution authorization. |
| File hash or safe-file check fails | Return an integrity failure, not an empty result or a different file. |
| Requested record is private/unpublished analysis | Apply the separate analysis visibility/acceptance contract; broad source access is not publication permission. |
| Source reads succeeded but a terminal result claims another task's coverage | Reject the ownership violation; source access was not a coverage grant. |

Full error payload shape and multi-error collection will be specified in P1-F07.
This table does not authorize exposing protected source in error messages.

## 9. Acceptance tests to implement

These are required test scenarios derived from the agreed behavior. They have not
been run during this documentation task. Use isolated harness fixtures, never the
user's live review database or execution of a reviewed target.

| Test | Setup/action | Expected result |
|---|---|---|
| F01-T01 — Cross-file access | Assign reviewer A to one unit; read indexed helper B in another permitted file. | Exact B source is returned; A/B assignment and coverage state remain unchanged. |
| F01-T02 — Same-file context | Read a permitted declaration outside A's assigned byte range. | Research succeeds without widening A's required coverage disposition. |
| F01-T03 — Foreign coverage | After T01, submit completion for B through A's result authority. | Submission fails its ownership check and performs no partial domain publication. |
| F01-T04 — Exclusion | Request content for an excluded or non-readable manifest entry. | No source is returned, including through alternate ID/path inputs. |
| F01-T05 — Snapshot binding | Request an ID belonging to a different snapshot. | No silent rebinding or foreign source disclosure. |
| F01-T06 — Stale attempt | Revoke/expire the attempt, then repeat a previously permitted read. | Execution authorization rejects it despite any cached metadata. |
| F01-T07 — Integrity | Alter disposable snapshot bytes after manifest capture. | Existing file/hash safety checks fail; no automatic recapture. |
| F01-T08 — Large inventory | Use a project with more permitted files than `max_context_items`. | Access initialization does not fail solely because of project size; responses remain bounded and initial context does not inline the catalogue. |
| F01-T09 — Synthesis | Supply conflicting child summaries and request their permitted source. | Synthesizer can check source/index context; child authorship and coverage requirements are unchanged. |
| F01-T10 — Attempt read truth | Start a new attempt after an earlier one read B. | Prior reads do not satisfy the new attempt's material-read requirements automatically. |
| F01-T11 — Alternate surfaces | Reach the same file via existing file, symbol or relationship navigation paths. | Research authorization is consistent; no handler is a permission bypass. |
| F01-T12 — Context-only source | Read a permitted `CONTEXT_ONLY` file. | Source is available under existing policy but no new coverage task/disposition is created by the read. |

The implementation report must identify which actual tests cover each scenario,
what was collected, pass/fail results and checks not run. Do not weaken existing
acceptance tests to make source-access tests pass.

## 10. Limits against overengineering

Do not build a generic RBAC product, network permission service, plugin architecture,
second file inventory, or complete per-worker ACL list. Do not create new model
roles solely to grant access. Do not copy the source resolver's integrity checks
into each handler. Do not treat `SourceScope` construction as authorization by
itself. Do not increase context budgets to accommodate a needlessly copied catalogue.

Do not broaden writes, change canonical coverage, execute target code, alter
classification policy, auto-promote candidates or implement other phases in this
feature. Preserve modular boundaries: the broker coordinates, an identifiable
owner checks research policy, the source resolver verifies bytes, and existing
submission authorities validate their own results.

## 11. Open decisions and dependencies

| Item | Status | Owner / required resolution |
|---|---|---|
| Exact refactored files, constructors and interfaces | NEEDS CODE VERIFICATION | Inspect the accepted refactor and record the owner map before changing code. |
| Exact role/task mapping, including link-review and any legacy roles | NEEDS CODE VERIFICATION / QUESTION IF AMBIGUOUS | Do not invent permissions for an unmapped responsibility or remove approved access because its enum differs. |
| New research-policy contract binding and activation for reviews/attempts | NEEDS DESIGN DECISION | Agree compatibility with historical execution receipts and in-progress work; coordinate with Phase 7. |
| Cross-file evidence reference acceptance in terminal results | CROSS-FEATURE DEPENDENCY | P1-F03 and Phase 4 must specify the legitimate reference/publication route; broader reading alone does not relax their contracts. |
| Name/path lookup, complete-function selection and paging | NEXT FEATURE | P1-F02, using this authority seam. |
| Detailed read-reference lifetime and provenance | PENDING FEATURE DISCUSSION | P1-F03; no signed-handle or registry architecture is prescribed here. |
| Error wire shapes | PENDING FEATURE DISCUSSION | P1-F07; preserve the substantive distinctions required here. |

The implemented feature may be called complete only after its document is reviewed,
its required open choices are resolved, its real integration is mapped and its
acceptance/regression checks are evidenced. Approved direction alone is not a
complete implementation contract.

[^broker]: [Pinned broker code](https://github.com/JennieXLisa/source-review-harness/blob/8b7ed0e335d4f4fb5ae53ef6e059334661279f20/src/ssr/tools.py#L590-L830).
[^source]: [Pinned source resolver and captured-content checks](https://github.com/JennieXLisa/source-review-harness/blob/8b7ed0e335d4f4fb5ae53ef6e059334661279f20/src/ssr/source.py#L1-L240).
