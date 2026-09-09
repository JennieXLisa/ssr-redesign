# P1-F01 — Research access and assignment ownership: implementation plan

Updated: 2026-09-09. Documentation only; none of the runtime tests below has been executed by this authoring change. Read the [feature specification](../P1-F01-research-access-and-ownership.md), [baseline](../../../BASELINE.md), and [tool contract](../../../contracts/TOOLS.md). Proposed helper names are private integration seams, not claims about existing APIs.

## Contract-hardening integration — authority and cutover

Research permission remains independent of owned deliverables. New runtime eligibility additionally requires collaborative-v1 state/receipt/input capabilities, not a legacy-mode facade. A source-readable subject does not grant visibility into pending prefix-backed artifacts, staged synthesis, another work's input token or quota-recovery rows.

Map BrokerScope and source handlers to the actual modular checkout at0989172, not old agent.py paths. Apply the same current execution/input authority to every read and mutation; host recovery of an old committed effect uses its captured predecessor identity, never a successor lease. Use [CUTOVER.md](../../../contracts/CUTOVER.md) and [INPUT_REVISIONS.md](../../../contracts/INPUT_REVISIONS.md) for those exact boundaries.

## 1. Change inventory before changing permissions

In the authorized harness checkout, locate `BrokerScope.authorize`, `_revalidate_scope`, `_allowed_paths`, `_file_ids`, every `allowed_symbol_ids` use, assigned-line/byte callbacks, `_tool_available`, `terminal_submission_preconditions_satisfied`, and the source-read interval tracker. The refactor map locates these responsibilities in `ssr.tools`, `ssr.tools.source_handlers`, worker request construction and domain submission modules. Do not assume a module move removed the policy.

Create a caller map classifying each use as execution authorization, research authorization, result visibility, or submission ownership. Source reads/searches/stat, symbol lookup and structural navigation use research authorization. Task role/lease/control identity uses execution authorization. Owned inventory membership, required unit inspection and canonical publication use submission ownership. Accepted-result readers retain their own visibility gate. One shared set must no longer imply all four decisions.

The change is enabled only for the pinned collaborative review contract. Legacy attempts retain the same tool definitions, source scope, rejection behavior and receipt interpretation. Do not overwrite an old execution contract after admission.

## 2. Internal values and dependency direction

Keep an immutable execution context containing the real review, snapshot, task, agent run, attempt, lease and control generation. Load assignment separately from the work request: owned review unit/file/candidate, input revision and required output contract. Define a small research-policy component that returns an authorized canonical file locator for a requested indexed subject.

An internal authorized locator contains snapshot ID, file ID/path, expected manifest hash/classification and policy digest. It contains neither every project path nor an ownership grant. The broker calls the policy; source handlers receive the resulting immutable locator plus resolver and size allowances. Source verification must not import the broker or runner. Do not implement dependency injection by passing a mutable whole broker to each handler.

```text
read_subject(execution, requested_symbol, range):
    execution_authority.require_active(execution)
    symbol = inventory.get_in_snapshot(execution.snapshot, requested_symbol)
    locator = research_policy.authorize_file(execution, symbol.file_id)
    return verified_reader.read(locator, range)
```

The inventory lookup and policy do not accept an agent-provided snapshot override. Missing/foreign IDs are rejected; name search is a separate explicit request, not an error fallback.

## 3. On-demand membership rather than a project-sized allowlist

Resolve through the existing snapshot manifest and locator association. Query `(snapshot_id,file_id)` or the canonical manifest path using an index; do not hash every file each request to reverse an opaque ID. If no inverse file-ID lookup exists, use the small indexing-owned locator association specified by P1-F02/P7-F01. The file manifest remains authoritative.

Readable classifications retain the existing capture policy: authorized captured context files may be read even without callable symbols; excluded/uncaptured files are not made readable. Metadata visibility and byte availability remain distinct. Directory/name discovery also respects metadata visibility before revealing identities.

Cache only bounded immutable lookup facts within an attempt or existing shared cache owner. Never cache an expired lease as valid or transfer one review's permission decision to another review. Invalidating control/permission generations must make subsequent calls recheck authority. No per-read permission database, generic policy server, or project-wide initial prompt is needed.

## 4. Remove only research clipping

For collaborative `source_read`, replace assigned-symbol line/byte clipping with the authorized requested range. For `source_search`, scan the permitted selection rather than only the owned symbol's bytes. For symbol and relationship queries, replace assigned-ID filtering with snapshot/research visibility filtering. For `source_stat`, report file metadata without misrepresenting assigned bounds as the only readable bounds.

Continue calling the existing `SourceResolver` and safe file reader. A one-file internal `SourceScope` is an adapter parameter for this read, not a new public scope grant. Preserve path normalization, symlink/regular-file checks, file-size/hash verification, exact byte conventions and source-free persistence rules.

Open the source/index tool set to synthesis for contradiction checking. Keep its compact initial child-result index and canonical contribution contract. Do not automatically load every child's full source or analysis merely because tools are now available.

## 5. Keep deliverables narrow

A reviewer assigned unit A may read helper B and cite relevant context through P1-F03. It must still account for exactly A's inventory membership and original required source ranges. Reading B cannot complete B's task, substitute for unread parts of A, or permit claiming authorship of B's accepted review.

Keep required-read predicates on actual delivered original-byte intervals owned by the current attempt. Do not mark a range read when a source selection is requested, an index row is returned, or another agent's summary is consumed. Checkpoints retain references; a restarted attempt begins with no inherited source-read credit.

An independent observation about B goes through `report_lead`, with its own operation and accepted record. Do not implement that capability by letting a normal review submission mutate arbitrary candidates. Candidate and coverage ownership remain enforced by their domain validators at commit.

## 6. Admission and commit checks

At admission, derive research policy and tool-contract version from the immutable review configuration. Include their identity in the existing execution-contract construction before provider invocation. Match role/task identifiers explicitly, including legacy/link tasks; do not silently give an unmapped role maximum authority.

For reads, validate the current attempt at use. For writes, revalidate lease, generation, owned subject and input revision inside the short authoritative transaction after expensive source validation. A valid source locator or signed cursor is not a lease. A stale attempt must not mutate the successor's task or result state.

Do not change public SDK version numbers merely to make compatibility tests pass. New capabilities must be advertised through P7-F02/P7-F03, with old DTOs/imports preserved where the contract promises compatibility.

## 7. Concrete fixtures and acceptance sequence

Build one immutable test snapshot with owned unit A, permitted helper B in another file, context-only configuration C without symbols, excluded X, a parse-error file P, and an ID from snapshot S2. Script ordinary reviewer, investigator, falsifier and synthesizer attempts against these subjects.

1. Read B and C from A's attempt: verify exact returned bytes and unchanged A/B task rows.
2. Query P: metadata reports the parse limitation rather than pretending the file is absent or successfully indexed.
3. Read X or S2's symbol: reject before content disclosure; inspect response/audit for protected metadata.
4. Submit a result claiming B's canonical membership through A: reject and roll back every domain write.
5. Read B but leave part of A unread: A's completeness precondition fails with the actual missing A ranges.
6. Expire the lease after obtaining a valid cursor: continuation fails execution authorization despite valid cursor authentication.
7. Resume the same work as a new attempt: references remain useful, while delivered-range credit starts empty.
8. Repeat against a manifest larger than `max_context_items`: metadata/source responses stay bounded; admission does not materialize the full project per worker.
9. Run the same fixtures under the legacy contract: old tool/prompt hashes and intended denials remain unchanged.

Add tests at broker dispatch, source-handler and domain-commit boundaries, not only at the new policy helper. Preserve existing integrity and investigation-finalization race regressions. Record actual command, test collection and exit status; a documentation pass is not runtime verification.

## 8. Commit exits and non-goals

First implementation commit introduces the explicit policy seam with legacy characterization tests. Second routes collaborative research through it. Third adds synthesis/other-role exposure and submission-negative tests. Keep changes reviewable and do not mix a dependency upgrade or unrelated refactor into them.

Completion evidence is the caller classification map, exact role/capability matrix, collected tests, original-byte assertions and public/execution-contract compatibility results. There is no new filesystem browser, generic role framework, coverage shortcut or private-result publication policy in this feature. Any unavailable refactor API is mapped to the actual owner before coding; it is not hidden behind fallback behavior.
