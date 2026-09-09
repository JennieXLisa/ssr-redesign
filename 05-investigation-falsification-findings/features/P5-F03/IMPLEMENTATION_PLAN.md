# P5-F03 — Counterevidence, reassessment and export: implementation plan

Updated: 2026-09-09. Documentation only. Read the [feature](../P5-F03-counterevidence-reassessment-and-export.md), [STATE.md](../../../contracts/STATE.md), P4-F03 material dependencies and P5-F02 current-finding gate.

## Contract-hardening integration — Reassessment without reopening completed historical work

A completed/refuted/inconclusive argument receives a successor candidate revision/task on genuine new material or explicit operator request. Do not reopen a COMPLETED task or erase its historical disposition. Current-finding queries and exports use the same validity-generation predicate.

Explicit INCONCLUSIVE and unsupported required scope contribute to COMPLETE_WITH_LIMITATIONS only when all other mandatory obligations and receipts settle. Operationally failed canonical work stays blocked/failed rather than being relabeled a valid analytical limitation. Test a challenge racing with export, old verdict after successor revision, exhausted reassessment quota and immutable historical report identity.

Normative source: [hardening contract index](../../../CONTRACT_HARDENING.md). Preserve the existing feature procedure below except where this explicit correction replaces it; implement the linked exact schemas, not a local incompatible approximation.

## 1. Typed challenge producer

Extend accepted review/answer/lead result variants with an explicit challenged candidate-family/revision, facet identity, source-backed observation, evidence refs and applicability explanation. Do not scan arbitrary prose for words such as 'wrong' and automatically invalidate findings.

Validate current producer authority, exact historical target, source-free analysis, reference integrity and the challenge's own producer receipts. A material challenge can be a valid accepted question about an argument; it is not yet a refutation. A malformed or ungrounded challenge is rejected without changing validity.

## 2. Determine affected revisions narrowly

Use material_dependencies to find exact consumers of the challenged artifact/facet or negative-search/registration domain. If the target is current and the accepted challenge is material, place a conservative REVALIDATION_REQUIRED hold. If the target is historical, compare its facet identity with the current revision's explicitly reused facet. An identical reused facet may require a current hold; a changed facet requires separate applicability assessment, not blind refutation.

Facet identity must include substantive claim/conditions/material-reference digests, not a display label or raw sentence equality. An unrelated observation in another subsystem must not invalidate every candidate. Unknown applicability remains a recorded assessment question and cannot be hidden as a conclusive clean result.

## 3. Accept challenge and hold atomically

Prepare reference/source validation outside the lock. In the short project/candidate transaction recheck current family/revision and accepted challenge provenance, insert the immutable challenge relation, apply the exact current validity hold where required, increment validity generation, and record a unique reassessment intent. Expose the accepted challenge and current hold together; optional notification delivery is not the enforcement mechanism.

```text
with candidate_transaction():
    current = load_family_current(family_id)
    applicability = verify_recorded_target_and_material_facet(challenge, current)
    insert_challenge_if_absent(exact_challenge_identity)
    if applicability.requires_current_hold:
        mark_revalidation_required(current, next_validity_generation)
        ensure_one_reassessment_intent(current, challenge_set_revision)
    publish_challenge_availability_and_operation_receipt()
```

Use exact challenge/revision/facet uniqueness for replay. Several relevant challenges may attach to one active reassessment work item with an explicit updated input generation; do not create endless identical successor tasks. New material arriving during reassessment is an input delta and can make an old response stale.

## 4. Create a successor rather than reopen history

Use CandidateService's family compare-and-swap to create a new canonical candidate revision linked to its predecessor. Keep the historical terminal candidate, investigation, falsifier and exported packages unchanged. The successor receives all relevant prior evidence plus the accepted challenges and unresolved applicability questions as explicit input, not a silent edited old argument.

Run the existing investigator/falsifier roles under their current input contract. A prior UPHELD verdict is context only; material changes require fresh independent falsification. Reassessment may uphold a corrected revision, refute the suspicion or remain unresolved. Only P5-F02's current gate can clear the relevant hold/promote the successor.

A late old investigator/falsifier response cannot move the current family pointer backward, overwrite a newer revision or clear challenges it never saw. Compare input/argument/challenge-set generation at commit.

## 5. Budget and closure behavior

If no worker or provider budget is available, keep the reassessment intent/required task and hold. Full pool means queue. Funding exhaustion is a visible unresolved blocker, not dismissal, approval or automatic reuse of the old verdict.

Only an explicitly authenticated limitation-closure control action can close review work with a recorded unresolved limitation under the closure policy. Operator_id or reason prose is audit metadata, not authority. The action cannot label the held candidate currently upheld or alter historical source evidence. Review completion and current finding count remain separate projections.

## 6. Export selection and I/O race

At export preparation, obtain a consistent selection of current-valid candidate family/revision, argument/material digests, validity generation and exact upheld receipt through the shared gate. Record this export-selection fingerprint. Render to a host-owned temporary output outside the transaction using immutable selected source/analysis references.

Before registering/publishing the package as a current export, enter a short authoritative transaction and recheck every selected validity fingerprint. If a hold/revision changed during rendering, reject or retry from a fresh bounded selection. Do not label the stale rendered result 'current'. Cleanup only the temporary output owned by that failed operation.

Once an immutable package has been legitimately committed, a later challenge does not rewrite its bytes. Its manifest records state-as-of identity; current views separately show that the finding/package selection was superseded or held. Current-download/query endpoints must not infer current validity from the mere existence of an old package.

Do not hold database locks while rendering or writing large artifacts. Preserve existing artifact collision checks, hash verification, atomic final placement and idempotent export-operation receipts. Source export remains explicitly authorized; a new finding/hold notice cannot trigger one automatically.

## 7. Recovery boundaries

Crash before challenge transaction: no exposed hold/accepted challenge pair. Crash after hold but before task materialization: the unique required intent remains and reconciliation creates the task once. Crash after successor creation: reuse the family/revision identity, do not fork another sibling silently. Crash after rendering but before registration: verify fingerprints and owned temporary state before retrying publication.

A missing/invalid receipt keeps eligibility false. Do not clear a hold as a repair for unavailable transcript data. Recovery of older events may settle their exact history without mutating a successor's current input/control generation.

## 8. Test traces

Start with a currently upheld finding. A later reviewer discovers a source-backed effective guard: acceptance immediately removes current-export eligibility while old verdict/package hashes remain unchanged. Reassessment creates a successor and a new falsifier; old UPHELD alone cannot promote it.

Challenge an old revision whose facet changed: no automatic current refutation. Repeat with an identically reused facet: current hold is applied. Add an unrelated accepted observation and verify no broad invalidation. Replay one challenge twice and verify one intent; add distinct challenges and verify explicit updated inputs.

Pause export after rendering starts, commit a material hold, then finish export. The old selection must not register as currently valid. Reverse the order: a committed historical package remains unchanged and current status reflects the later hold. Exhaust budget before reassessment and assert visible unresolved closure blocker.

## 9. Build sequence and exit

Implement challenge schemas/producer path; material applicability lookup; atomic hold plus intent; successor revision workflow; current-gate/export fingerprint integration; then full crash/race fixtures. Preserve exact accepted history and separately label current validity. No deletion of old findings, latest-row overwrite, automatic refutation from prose or UI-controlled gate is permitted.
