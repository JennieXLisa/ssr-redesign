# P1-F05 — Submission and return to analysis: implementation plan

Updated: 2026-09-09. Documentation, not executed runtime work. Read the [feature](../P1-F05-submission-and-return-to-analysis.md), [tool outcomes](../../../contracts/TOOLS.md), [role projections](../../../contracts/ROLE_PROJECTIONS.md) and [state](../../../contracts/STATE.md).

## Contract-hardening integration — Bounded repair and nonterminal investigation progress

Apply the same final-request context gate to original submission, repair, checkpoint and return-to-analysis exchanges. Truncated tool arguments never create a semantic operation or prefix; retain usage and reduce context or select staged output before another attempt. Two checkpoint exchanges and the per-root no-progress counter prevent unchanged retry loops.

An investigator needing context uses record_investigation_progress with exact checkpoint/request revisions, not terminal NEED_CONTEXT. Return MORE_ANALYSIS guidance for NEED_CONTEXT supplied to a terminal tool, with no task completion. Valid terminal outcomes use STATE_MACHINE.md's exact mapping. Mandatory new input becomes authoritative for submission only after its actual request binding is OBSERVED; optional notice receipt is not that binding.

Normative source: [hardening contract index](../../../CONTRACT_HARDENING.md). Preserve the existing feature procedure below except where this explicit correction replaces it; implement the linked exact schemas, not a local incompatible approximation.

## 1. Refactor the policy branch, not the whole provider loop

Locate the existing AgentRunner terminal-tool branch, terminal-repair counters/tool filtering, `agent_policy`, `agent_contract`, error taxonomy and worker finalization entry points. The inspected refactor retains one mutable turn loop in `ssr.agent`; extracted helpers do not own provider conversation order. Keep that single loop.

Build a collaborative rejection classifier called after host tool validation. Its output is a small typed decision: return to ordinary tools, request explicit input refresh, retry prepared host operation, stop current authority, or finish accepted submission. Preserve legacy terminal-repair logic behind the legacy execution contract; do not weaken old source-precondition tests globally.

## 2. Classify using cause and commit state

Use typed validator codes plus P1-F07's outcome envelope, never substring matching on error prose.

| Cause | Agent-visible action | Runtime action |
|---|---|---|
| Invalid field/enum/schema | FIX_INPUT with exact input pointer | Keep conversation and ordinary authorized tool surface |
| Missing source/control/path assessment | MORE_ANALYSIS with missing facet/range | Permit source/index/context tools within remaining budgets |
| Stale bound input | MORE_ANALYSIS plus repair_action REFRESH_INPUTS | Require explicit input delta/token before accepting a new result |
| Prepared persistence failure | RETRY_SAME_OPERATION | Host retries the same prepared semantic object, no new inference |
| Unauthorized/stale lease/integrity failure | HOST_RECOVERY or NONE | Stop the affected operation; no repair path grants authority |
| Result already committed | Return original receipt | Settle that result, do not ask model to rewrite it |

REFRESH_INPUTS is a repair action, not an undeclared extra retry_kind enum. Keep this mapping consistent with TOOLS.md and its schema. A backend safety refusal, provider exhaustion and invalid analytical submission are different outcomes; do not collapse them into a generic failure that changes retry policy.

## 3. Normal rejection flow

On a complete provider tool call, record the real exchange and parse the collaborative role input via P1-F03. If validation rejects without committing, construct bounded actionable issues and append the normal tool result using the original provider tool-call ID. The next model request includes the ordinary permitted research tools, not a terminal-only schema repair surface.

Do not require a new conversation, lease or task merely because the model attempted a submission. Preserve provider-opaque continuation only within its owning attempt. Keep the same cumulative time, tool, row, token and cost accounting. A rejected submission consumes its actual resources; restoring the tool set must not reset counters or grant an additional request budget.

Source-precondition failures identify missing original-byte ranges or facets. Ordinary research remains possible, not just a single hard-coded corrective read. The domain precondition still runs on the next submission. Returning to analysis is not bypassing a required-read gate.

## 4. Explicit input refresh

The old `input_token` selects the exact assignment/candidate material provided to the attempt. When an input changes, create a host-owned delta containing previous/new revision and digests, changed material references and reason. Deliver it at a normal safe boundary through the work-input owner; expose the new token via the current `review_context` assignment projection. Do not invent a separate unversioned refresh endpoint.

The model must receive the delta before using the new token. Record that association with the model-bound request and updated work input. A previously constructed old result cannot be auto-normalized against the latest database row. The analyst revises affected claims and submits against the explicit new token. Retain old revisions and rejected results as attributable history under the existing content policy.

Not every update forces refresh: new supplementary analysis can remain optional. Material invalidation is decided by the owning candidate/dependency rule, not by the existence of any notice. No automatic suspension merely because another worker wrote unrelated metadata.

## 5. No-progress and resource boundaries

Keep separate counters for submission attempts, consecutive equivalent rejections and ordinary analytical work. A progress marker should refer to accepted new material, an answered request, or an explicitly revised checked argument. A longer paragraph alone is not progress. Do not invent a new manager model to grade progress.

On repeated identical rejection with unchanged semantic input, give the configured remaining allowance and concrete missing action. At the existing bounded stop, retain the latest valid checkpoint and explicit incomplete/needs-evidence outcome. Never convert exhaustion into UPHELD, dismissed-safe or completed coverage. Actual counter defaults come from CONFIGURATION.md, not local helper constants that drift.

Context pressure uses P1-F04 saving and P6-F02 yielding. Tool failure cannot strand a model in endless terminal formatting retries when ordinary research is still authorized and affordable.

## 6. Acceptance versus attempt finalization

After semantic validation, the domain owner commits the result and operation outcome atomically. The runner must check that outcome before deciding whether another model repair is needed. Persistence uncertainty invokes P1-F08 reconciliation; changed analytical resubmission is not a recovery strategy.

Some investigation commits make a task available for another attempt before the previous attempt finishes events/transcript/runtime receipts. Keep original task/agent/attempt/lease identities in the finalization material. A late failure cannot derive its target from the task's current mutable attempt count. Existing successor-isolation behavior in worker_finalization remains mandatory.

If a result is semantically committed but acceptance awaits a required receipt, represent that pending state through its existing owner. Do not fabricate a successful receipt, rerun the model to regenerate the same result, or overwrite accepted history. Later corrections use a new artifact/candidate revision path.

## 7. Test the actual conversation transitions

Use a scripted provider: first it submits a result missing a required helper range, next it requests that helper, then it submits a corrected argument. Assert one attempt/conversation, restored research tools, correctly paired tool IDs, accumulated usage and domain validation on both submissions.

Return an invalid enum and an independent missing field: both errors reach the provider projection together. Cause a stale candidate revision during inference: old submission fails; the next issued delta identifies exactly what changed; only a result bound to the new input can proceed. Test that a mere optional new analysis notice does not force revision.

Inject commit success followed by lost tool ACK, runtime receipt failure and predecessor finalization after successor claim. Assert one accepted domain result, no extra model judgment and no successor mutation. Cancel between validation and commit; acceptance fails with no new writes. Repeated no-progress reaches a truthful bounded stop and leaves coverage unfinished.

Also run legacy fixtures to verify unchanged schemas, repair limits and execution-contract hashing. Tests must inspect final model-bound tool availability, not only the classifier return value.

## 8. Implementation commits and exit

Implement the typed classifier and unit tests; wire it into the existing loop with scripted conversation tests; add explicit input-delta handling; integrate commit-state recovery and finalization races. Keep these separately reviewable from source-scope changes. Completion requires actual exchange traces, error field mappings, budget assertions and original/successor attempt isolation. No separate repair agent, automatic successful defaults, infinite loop or mutable accepted-result editor belongs here.
