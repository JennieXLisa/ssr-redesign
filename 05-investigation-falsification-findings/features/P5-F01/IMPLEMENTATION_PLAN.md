# P5-F01 — Candidate investigation: implementation plan

Updated: 2026-09-09. Documentation only. Read the [feature](../P5-F01-candidate-investigation.md), [role projections](../../../contracts/ROLE_PROJECTIONS.md), [STATE.md](../../../contracts/STATE.md) and P6-F01 admission.

## Contract-hardening integration — Normative investigation outcome mapping

Use the exact four-row table in STATE_MACHINE.md and state-transitions.json. SUPPORT_FOR_FALSIFICATION creates one exact-revision falsifier intent only when the argument artifact and required terminal proof are available. DISMISS_WITH_EVIDENCE ends this revision with its scoped evidence and no successor. INCONCLUSIVE ends it with an explicit limitation and no automatic retry. All three terminal tasks reach COMPLETED only after predecessor settlement.

NEED_CONTEXT is exclusively record_investigation_progress with checkpoint and registered request IDs, followed by explicit yield_work. It is not terminal submit_investigation. A malformed terminal NEED_CONTEXT returns MORE_ANALYSIS guidance and creates no completed task. Preserve candidate maturity separately from the new disposition axis; no path/control facts are filled to move an enum. Test each outcome→artifact→candidate→task→successor→completion tuple and distinguish provider timeout/refusal from analytical uncertainty.

Normative source: [hardening contract index](../../../CONTRACT_HARDENING.md). Preserve the existing feature procedure below except where this explicit correction replaces it; implement the linked exact schemas, not a local incompatible approximation.

## 1. Separate three gates in the existing candidate authority

Extract reusable argument validation from CandidateService/investigation/falsification paths without creating another candidate state store. Define `can_start_investigation`, `argument_ready_for_falsification` and `current_finding_valid` as separate predicates with shared subchecks and structured blocker lists.

Investigation admission requires a current seed/unfinished candidate, a meaningful question, permitted observed anchors and sufficient registered input to begin analysis. It must not require the complete path, controls review or upheld falsifier that the investigation is supposed to obtain.

Falsifier readiness requires the complete supported argument plus accepted material/producer receipts, but not an existing upheld verdict. Final finding validity adds the independent upheld verdict and current-revision checks. Calling the old full final gate to decide falsifier admission would create a circular prerequisite; test that explicitly.

## 2. Bind the actual starting material

Build an immutable investigation request containing candidate family/revision, existing candidate identity, argument/input digest, accepted evidence/artifact references, observed source anchors, declared assumptions/unknowns and required analytical facets. Derive host identity via P1-F03 and issue an input_token. Do not freeze the agent's research navigation to only the initially attached files.

Current input identity is not 'latest candidate whenever submit arrives'. A new material artifact or revised candidate produces an explicit input delta under P1-F05. The investigator must receive it before submitting against the updated token. Optional supplementary analysis remains optional unless the material-dependency owner invalidates a bound facet.

Keep the original invocation profile for investigations; do not replace long-investigation limits with discovery's shorter budget or create one new attempt per maturity enum automatically.

## 3. Investigator tools and missing context

Use the project-wide source/index tools, exact accepted-analysis retrieval, progress saving, contextual requests and independent lead registration already defined. A request for missing caller/configuration/storage behavior can create a blocking dependency and explicit yield. A separate new suspected issue transfers to the harness through report_lead and does not automatically block this candidate.

Material source inspection remains current-attempt evidence. The investigator cannot simply concatenate summaries from other workers into a supported path. It must bind influence, reachability, control behavior, preconditions/configuration, impact and counterevidence to source-backed facets. Unknown dynamic behavior remains a limitation, not an invented path segment.

## 4. Validate the structured argument

Preserve existing path/state/lifecycle segment contracts and exact source reference checks. Validate sequence/endpoints, subject consistency, claimed transformations, controls with failure behavior, configuration assumptions and bounded impact. Do not reduce all bug classes to a string-taint path; memory lifetime and state transitions retain their typed argument forms.

Normalize compact model input through P1-F03 into the full internal result. Aggregate independent safe validation issues through P1-F07 and return to research on analytical gaps. Host metadata may supply execution IDs, not missing controls-reviewed flags, severity or proof conclusions.

A coherent result can establish several facets at once. Compute the supported maturity progression from validated facets and emit the required audited transitions within the host service; do not force another model exchange solely to increment the next enum. Old transition receipts remain historical; the new runtime uses the exhaustive collaborative state matrix.

## 5. Apply exact analytical outcomes

The machine-readable table in contracts/schemas/state-transitions.json is authoritative. SUPPORT_FOR_FALSIFICATION yields an accepted complete argument, READY_FOR_FALSIFICATION and one exact-revision falsifier successor after required proof. DISMISS_WITH_EVIDENCE yields a scoped DISMISSED disposition and no successor. INCONCLUSIVE yields a limitation disposition and no automatic successor. These three terminal results complete the investigation task only after terminal settlement.

NEED_CONTEXT is a nonterminal InvestigationProgress operation with a valid checkpoint and registered context request IDs. It leaves the task RUNNING until explicit yield is prepared/settled, then publishes WAITING_DEPENDENCY or PENDING. A terminal submit_investigation containing NEED_CONTEXT returns MORE_ANALYSIS guidance without effect. Malformed input/refusal/timeout remains operational failure, not an invented analytical disposition.

Candidate disposition is distinct from maturity; use the existing source/argument validators and preserve historical revision identities. The completion owner counts INCONCLUSIVE as a limitation only after all required work/receipt obligations settle.

## 6. Commit and concurrency

Prepare source verification and argument parsing outside the write lock. Inside the candidate/task transaction recheck current family pointer, revision/input digest, lease/control generation, artifact availability and exact operation replay. Commit accepted argument/progress, material dependencies, investigation artifact/receipt and required task intent together through existing owners.

```text
prepared = prepare_investigation(exact_input, result)
with candidate_transaction():
    require_current_family_revision_and_attempt(prepared)
    recheck_material_acceptance(prepared)
    apply_validated_facets_and_outcome(prepared)
    publish_or_mark_receipt_pending(prepared.artifact)
    create_falsifier_intent_if_argument_ready(prepared)
    commit_operation_receipt()
```

A concurrent investigator or late result cannot overwrite a newer revision. Preserve its attributable rejected/historical attempt without rebinding to current state. A semantically committed result awaiting a receipt is pending, not a reason to ask the model to regenerate the same argument. Keep predecessor/successor finalization identities separate.

## 7. End-to-end tests

Start candidate A with one observed sink and an unresolved caller while unrelated canonical file B runs. A's investigation must admit without waiting for B or a complete path. Script a contextual dependency, yield, accepted answer and resumed investigation. Assert exact input delta and independent source reads.

Submit a complete multi-facet argument and verify host progression/falsifier intent without one provider attempt per enum. Test partial argument: falsifier readiness false with precise blockers. Test complete argument/no verdict: falsifier readiness true while final finding validity remains false.

Race input revision change between preparation and commit; stale result cannot update current candidate. Supply a summary without material source delivery, broken path endpoint, unsupported control conclusion and missing impact: each produces meaningful rejection, not filled defaults. Inject postcommit receipt failure and late finalization after successor claim; no duplicate accepted result or successor corruption.

## 8. Implementation order and exit

Characterize existing argument/final gates; extract shared facet validation; add collaborative admission and compact normalization; implement multi-facet host progression/outcome transactions; wire contextual continuation; then integrate falsifier task creation. Test planner, claim SQL, broker role checks and submit guards together so no residual global-phase check strands ready candidates. No stage-approval model, candidate database rewrite or completed-proof admission requirement is allowed.
