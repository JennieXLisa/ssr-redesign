# P4-F02 — Coverage adoption and file synthesis: implementation plan

Updated: 2026-09-09. Documentation only. Read the [feature](../P4-F02-coverage-adoption-and-file-synthesis.md), [STATE.md](../../../contracts/STATE.md) and P4-F01. The new route reuses complete compatible analysis; it must not redefine partial contextual answers as complete coverage.

## 1. Extract one complete-unit validator

Locate symbol-review result parsing, required inventory membership/dispositions, complete documentation checks, dependency-consumption manifest validation, evidence preparation, producer receipts and canonical child settlement. Factor a reusable validator/preparation boundary without weakening its existing rules. Ordinary symbol submission and host adoption call this same authority.

The adoption input is an exact AVAILABLE artifact ID plus target canonical unit/task identity. Resolve both in the same review/snapshot policy context. Verify the artifact's kind is a full unit-result contract produced under an authorized full-unit assignment, not a one-facet context answer with a model-supplied completion flag.

## 2. Compatibility predicate

Compare snapshot and exact source identity, unit kind, complete subject membership, full-range/content/signature hashes where required, inventory/graph generation, review policy, result contract, dependency inputs and producer acceptance receipts. Validate every required disposition/documentation field and evidence closure. Matching a filename, symbol name or unchanged body hash alone is insufficient.

A complete targeted review can qualify only when it actually produced the full canonical unit semantic contract with its own required source-delivery and producer receipts. Do not fabricate that its role was file_review or its task_id was the canonical task. Missing material results in supplementary completion, not inferred defaults.

Prepare an adoption receipt containing target obligation, artifact/result ID, exact compatibility digests, validator version, original producer identities and validation outcome. It references existing payload/evidence rather than copying them.

## 3. Adopt only at a safe canonical task boundary

Never cancel or steal an active canonical review lease merely because another artifact appeared. Adoption is eligible when the target obligation is unclaimed/pending at a safe task boundary. If an original reviewer is active, retain the other artifact as available context and reconsider after normal settlement. Duplicate analysis may complete, but coverage counts once.

Within the canonical task transaction recheck target state/lease, graph/input generation, artifact availability and exact compatibility. A scheduler claim racing with adoption must serialize through the same owner. If the claim wins, adoption defers. If adoption wins, the task is no longer claimable.

```text
prepared = validate_complete_unit_artifact(target, artifact)
with canonical_task_transaction():
    recheck_target_generation_and_no_active_lease()
    recheck_artifact_acceptance(prepared)
    if canonical_acceptance_exists(target):
        retain_other_artifact_as_context()
        return existing_acceptance
    chosen = earliest_eligible_artifact_by_availability_then_id()
    receipt = record_adoption(target, chosen, compatibility_proof)
    settle_obligation_through_host_adoption(target, receipt)
    emit_canonical_progress_event()
```

Selection is stable at the decision point and protected by compare-and-swap/unique canonical acceptance. Once committed, do not replace the chosen contribution merely because another artifact later sorts earlier. Preserve alternatives as independent analysis.

## 4. Do not invent an adopting agent

Host adoption records that a canonical obligation was satisfied by an existing complete contribution. It does not create a fake new agent run, transcript, source-read event or provider usage. Original producer task/attempt/turn remain visible. The canonical task's host-adoption outcome and receipt explain why it can be settled without a newly executed model attempt.

Extend the canonical contribution manifest to distinguish normal child-result and adopted-artifact references explicitly. Validate each through its appropriate receipt path. Do not alter the artifact's original task foreign key to make the old schema accept it.

Canonical coverage metrics count the target unit exactly once. Read accounting remains with the original source-consuming attempt; a synthesizer or adopting host receives no inherited source-read credit.

## 5. File parent input and atomic publication

Build the file parent from all required canonical units/dispositions, including valid adoption receipts. Preserve same-file dependency/SCC accounting, exceptional/unreviewable dispositions and sealed contribution checks. A missing or invalid required unit blocks file completion even if the file has useful early answers or registered leads.

Synthesis receives a compact index of accepted contributions and can retrieve exact details/source for contradictions and cross-symbol interactions. Do not inline all child bodies or require routine re-review. Preserve complete selected child evidence closure and explicit merged/changed proposal lineage.

For independent leads already registered by a contribution, link exact origin operation/candidate IDs rather than seed a second copy. Similar prose alone is not origin identity or semantic merge authority. Any genuinely merged candidate must declare its contributing origins and evidence.

Prepare publication read-only, then commit canonical documents, evidence associations, knowledge, candidates, coverage and parent completion in the existing short atomic publication transaction. If one contribution fails, no partial complete-file state is visible.

## 6. Invalidation and reuse boundaries

An accepted correction to an adopted artifact creates explicit revalidation requirements through the coverage/result owner. Do not delete the original adoption or rewrite its hashes. Historical complete coverage and current validity are represented honestly. A source/policy/contract change requires the existing repeated-review reuse proof or new review work; an old artifact is not silently upgraded to a new schema.

Current artifact availability must be rechecked before adoption/publication. An artifact withdrawn after preparation cannot be counted because its old acceptance receipt once existed. Optional newer analysis is different from a material invalidation; do not invalidate every adopted unit on every project update.

## 7. Test matrix

Produce a complete targeted unit artifact matching every canonical requirement: adopt it with zero second model calls and preserve original producer IDs. Produce a one-facet answer for the same symbol: no coverage credit. Remove each required field/receipt/dependency in turn: adoption fails without default filling.

Race a normal scheduler claim against adoption and a normal result acceptance against another candidate artifact. Assert one canonical acceptance, no stolen live lease, no double source/provider cost and all legitimate origins retained. Test deterministic selection among multiple already eligible artifacts.

Build a file with two normal children, one adopted child and one failed required child. File completion remains blocked; after valid resolution, publication commits all coverage atomically. Inject one invalid child during preparation/commit and assert rollback. Verify already registered lead origins are not duplicated by parent synthesis.

Change policy/input generation or withdraw the artifact between validation and commit. Adoption must recheck. Repeat after restart and compare stored receipts/coverage counts. Legacy distributed-publication tests continue to use unchanged legacy contributions.

## 8. Delivery and exit

Factor the shared validator; implement prepared compatibility/adoption receipt; wire safe task-boundary CAS; extend parent contribution types; integrate origin/evidence closure; run publication/race/reuse fixtures. No parallel coverage database, fake review attempt, completion-by-reading or forced cancellation of healthy workers is allowed. Completion evidence includes exact compatibility failure cases and a full file publication trace with mixed contribution types.
