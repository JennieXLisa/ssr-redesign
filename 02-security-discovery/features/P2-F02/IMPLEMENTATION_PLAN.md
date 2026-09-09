# P2-F02 — Prioritized discovery: implementation plan

Updated: 2026-09-09. Documentation only. Read the [feature](../P2-F02-prioritized-discovery.md), [configuration](../../../contracts/CONFIGURATION.md) and [state](../../../contracts/STATE.md). Priority affects work order, not the validity or severity of a security claim.

## Contract-hardening integration — Discovery admission under finite root budgets

Ranking an existing canonical unit changes its priority, not its coverage identity or resource entitlement. Optional focused roots must reserve real root/review capacities before task creation; reuse the existing work-conserving pool and required-work budget protection. Do not infer analytical success from an operation-count or lexical match.

Record rule/model/IR generation and unsupported support gaps alongside priority reasons. At full focused/lead quota keep canonical coverage runnable, preserve already registered leads, and emit explicit LIMIT_REACHED/required-work blockers. Test no-hit repositories, many repeated lexical observations, IR unsupported-language fixtures, counter replay and required coverage dispatch under optional discovery pressure.

Normative source: [hardening contract index](../../../CONTRACT_HARDENING.md). Preserve the existing feature procedure below except where this explicit correction replaces it; implement the linked exact schemas, not a local incompatible approximation.

## 1. Inputs and retained responsibilities

Consume the snapshot manifest, completed inventory segments, operation observations, registered entrypoint/control relationships and existing work/dependency state. Canonical unit creation remains with the coverage planner. Task eligibility/admission remains with P6-F01; this feature emits priority reasons and optional inquiry seeds, not active worker reservations.

Build a bounded project sketch from recorded modules, routes/RPC/IPC consumers and configuration anchors as they become available. Do not wait for a model to finish an architecture report before admitting reviewable work. Do not execute route-registration code to discover external entrypoints; unsupported registration remains an explicit gap.

## 2. Group the question, not every name match

Normalize an inquiry seed as review/snapshot, concrete question/facet, contributing observation IDs, subject set, starting references, checked assumptions/unknowns and score components. Group exact duplicates by operation occurrence plus question facet and compatible assumptions. A common file, API name or CWE is not enough to merge distinct concerns.

For repeated observations from multiple host models at one callsite, retain all provenance but create one compatible inquiry intent. For two callsites to the same helper under different guards, preserve the different questions. Additional agent-reported leads use P1-F06 and do not disappear because optional discovery's backlog is full.

Questions must ask for missing security facts: who controls an executable selector, what binds an object to a principal, whether length units match an allocation, or which writer supplies a stored field. Do not create tasks phrased as 'confirm this vulnerability'. A valid inquiry can finish with no supported candidate.

## 3. Deterministic initial score

Implement the selected additive components as pure policy code with versioned tables. Exposure 0–3, effect authority 0–3, unresolved boundary 0–2 and shared-dependency benefit 0–2 remain separately recorded. The component function receives explicit observations/relationships, never unrestricted prose or a model-generated severity score.

Use fixtures to define each bucket before enabling it. For exposure, distinguish source-visible external registration, indirect interface association, unknown exposure and no identified exposure; unknown must be labeled, not claimed unreachable. For effect authority, use modeled resource effect and explicit privilege context, not guessed deployment privilege. Unresolved-boundary points identify a concrete unanswered trust/resource question. Shared benefit counts distinct active consumers that an accepted answer can unblock, capped at the selected component maximum.

```text
priority = score(exposure_evidence, operation_model, open_facets, consumers)
record = {components, total, policy_version, reason_refs, source_generation}
```

The implementation must not silently assign a deployment-dependent component when evidence is absent. Its reason output includes the uncertainty. This score is only a deterministic ordering suggestion; it never changes candidate confidence, severity, coverage disposition or final gates.

## 4. Prefer existing required work when it answers the question

For a seed's relevant subjects, inspect canonical unit/task identities and current dispositions through their owner. If required queued work can answer the question, attach the context via P3-F01 and request a bounded priority boost. Preserve definite same-file dependency eligibility and SCC rules; priority cannot claim a blocked parent or skip required callees.

If a compatible contextual request is already underway, join it under its exact equivalence rules rather than spawn another model. If accepted analysis fully answers the same question under compatible assumptions, reuse its exact artifact ID with provenance. A generic function summary that omits the requested branch does not count as an answer.

Create FOCUSED_ANALYSIS only when a meaningful cross-component question remains beyond the required review's directly usable answer. Assign one durable task/work descriptor with source-backed starting points; do not allocate one worker for every observation. Task creation still uses the ordinary coordinator transaction.

## 5. Backlog, fairness and replay

Count optional outstanding focused roots through the task owner. Enforce `focused_backlog_per_worker × effective worker upper bound` before materializing more optional roots. This is not a license to discard valid registered leads or required dependency work; record deferred optional seed metadata with a reason and reconsider when capacity changes.

Within equal scores, rotate stable subsystem/family buckets before stable subject/seed identity as specified by P6-F01. Store the policy version and selection components so an identical queue snapshot is reproducible. Scheduler aging and the protected canonical opportunity remain independent; ranking cannot starve no-hit files.

Re-evaluate priority on explicit new accepted observations, new consumers or task dispositions. Update the score record/generation without changing an in-flight attempt's original assignment. A changed score does not invalidate its source or result contract.

## 6. Seed persistence transaction

Prepare candidate seed descriptors outside the lock. In a short write, verify review mode/config generation, exact seed key and backlog/eligibility state. Reuse an existing equivalent seed/task identity; otherwise insert the seed plus FOCUSED_ANALYSIS work descriptor or explicit deferral. Commit priority reasons and task intent together. No provider call occurs inside the transaction.

Two discovery passes racing on the same key must not create two tasks. A model/registry generation change is explicit provenance; it does not rewrite previous evidence or silently merge independently reasoned leads. A failed transaction leaves no half-created task.

## 7. Evaluation fixtures and tests

Construct a small repository fixture with an exposed handler, internal dangerous operation of unknown reachability, shared authorization helper, low-signal utility and untagged files. Assert score decomposition and reason anchors, not merely resulting order. Change only one input factor and assert only its component changes.

Provide an already queued canonical task with the same question: verify contextual attachment/priority request, not a duplicate focused worker. Add a compatible running request and verify joining. Provide a summary missing the requested configuration branch and verify that reuse is rejected as insufficient.

Replay identical observations and race two seed insertions: one work identity. Fill optional backlog: existing required work and valid report_lead registration remain possible; new optional roots defer visibly. Run enough scheduler choices to prove canonical/no-hit service occurs under persistent high-priority arrivals. No scoring test should change candidate validity.

## 8. Implementation slices and bounds

Implement pure grouping/score functions with fixtures first, then existing-work lookup, then transactional seed materialization and priority projection, then scheduler integration. Produce replay records for benchmark comparison: canonical order only, priority ordering, and priority plus focused inquiries. Do not claim speed improvement without that comparison. No required orientation manager, embedding ranking, task-per-hit expansion or bypass of canonical dependency order belongs here.
