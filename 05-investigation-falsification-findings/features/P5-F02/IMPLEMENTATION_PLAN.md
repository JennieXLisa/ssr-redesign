# P5-F02 — Falsification and current findings: implementation plan

Updated: 2026-09-09. Documentation only. Read the [feature](../P5-F02-falsification-and-current-findings.md), [STATE.md](../../../contracts/STATE.md), P5-F01 readiness and P5-F03 validity changes.

## 1. Create one falsifier for an exact ready argument

Use the shared argument-ready predicate from CandidateService, not review-wide FALSIFYING state. Required inputs are current candidate family/revision, complete argument digest, accepted material/evidence references, assumptions, counterevidence and required investigation/producer receipts. Readiness is rechecked at plan, claim and commit.

The task identity/uniqueness key includes candidate revision and argument/readiness fingerprint. Replayed readiness events do not create multiple equivalent falsifiers. A materially changed argument needs a new task/revision relationship; do not mutate the old task's input hash while it runs.

## 2. Build a genuinely fresh conversation

Allocate a distinct agent run and provider conversation with its own attempt/lease. Construct a bounded dossier from the explicit claim, structured argument, cited source refs, configuration assumptions, known counterevidence and challenge facets. Do not copy the investigator's opaque reasoning/transcript or provider continuation token.

The same model may be used where policy permits, but record that limitation; do not call it model diversity. Independence means separate execution and an independently authored challenge/verdict, not simply a different role label on the same conversation.

Verify both internal agent identity and actual message construction in tests. A fake distinct ID with inherited investigator history must fail the intended independence requirement.

## 3. Contrary-context research remains available

Give the falsifier the P1 research/index/reference/checkpoint tools and P3 contextual requests. It can inspect another caller, guard, registration, exceptional path or configuration beyond the investigator-selected excerpts. Source permission is broad within the authorized snapshot; accepted-result visibility and source-read requirements remain separate.

The falsifier may receive other accepted analysis as context, but must independently inspect material source and explain its challenges. Request text presents the investigator's assumptions as claims to test, not instructions to agree. A helper review answer is not an automatic verdict.

## 4. Verdict validation

Accept only UPHELD, REFUTED or INCONCLUSIVE under the exact assigned candidate/revision/argument digest. Preserve challenge answers, source/evidence/counterevidence refs and limitations. Verify required material reads for the falsifier attempt and all producer/turn/runtime/transcript receipts.

Malformed response, refusal, timeout or missing transcript is an operational/acceptance failure, not a fabricated INCONCLUSIVE verdict. UPHELD on a stale revision remains historical and cannot promote the current candidate. REFUTED preserves its source-backed reason; INCONCLUSIVE preserves missing facts without claiming safety.

Use the role's existing semantic validator through P1-F03 compact normalization and P1-F07 diagnostics. Reject a falsifier that is the same agent run/conversation as the investigator. Do not fill missing challenge fields mechanically.

## 5. One current-finding predicate

Place the authoritative predicate with CandidateService/current validity, reused by promotion, public query, report scoring and export. It checks current family pointer/revision, exact complete argument, current accepted material, required source/producer receipts, distinct accepted UPHELD falsification, and absence of a validity hold.

Historical FINAL_READY is not sufficient. Priority, maturity, model confidence and severity remain different fields. A scanner hit or agreement among several agents never substitutes for the gate.

```text
with candidate_transaction():
    state = load_current_family_revision(family_id)
    verdict = load_exact_accepted_falsification(state.argument_digest)
    blockers = current_finding_gate(state, verdict)
    if blockers: return structured_not_ready(blockers)
    if same_promotion_already_committed(): return original_receipt
    promote_current_revision_and_emit_event()
```

Recheck inside the transaction after preparation. A new material hold/revision racing with promotion must win or force rejection/retry; it cannot leave the old argument publicly current. Promotion is host work and consumes no model slot. A full model pool must not prevent this short coordinator action from running.

## 6. Receipts and late outcomes

If the falsification payload committed but a required receipt remains pending, expose pending acceptance and reconcile it through P4-F01. Do not rerun a fresh model verdict merely to obtain the same receipt. Duplicate publication/promotion is idempotent.

An old attempt may finalize its exact recorded outcome after another task claims work. It must not use the current mutable task row to identify what to settle. A late upheld verdict for a superseded argument cannot alter the family pointer or clear a new validity hold.

Subsequent counterevidence creates a separate current-validity transition while preserving old verdict/history. That is not editing the falsifier's accepted output.

## 7. Public projections and reporting

Project CurrentFinding through the supported SDK with family/candidate revision, argument digest, validity generation, exact upheld verdict receipt and review incompleteness. The controller must not recalculate readiness from partial fields. Current query/export consumers call the same gate; historical views label their state-as-of identity.

An upheld finding can be available while canonical coverage is still in progress. Its report must say IN_PROGRESS and disclose relevant limitations. Finding availability alone does not authorize source export or complete the review.

## 8. Tests

Create a complete investigation and inspect the new falsifier request: distinct run/conversation, no inherited opaque messages, exact claim/material input. Let it discover a contrary caller through project-wide navigation and produce REFUTED; no current finding appears. Test INCONCLUSIVE and operational refusal separately.

Accept UPHELD while all model slots are occupied; host promotion proceeds without another model task. Remove each gate prerequisite and assert the same blocker in readiness query and export. Forge same-agent identity or reuse a verdict from another revision and require rejection.

Race a validity hold/new revision with promotion in both orders. A pre-hold promotion may remain historical, but current eligibility immediately reflects the hold. Duplicate promotion events yield one outcome. Export with unrelated coverage running reports the incomplete review rather than waiting for a global packaging phase.

## 9. Delivery and exit

Implement exact falsifier task identity and fresh dossier; wire tools/independent source predicates; integrate accepted verdict receipts; centralize current gate and host promotion; update SDK/query/export projections; run race and stale-verdict tests. No voting consensus, copied investigator conversation, UI-computed validity or global phase barrier is allowed. Completion evidence includes actual provider request fixtures and shared-gate consistency tests.
