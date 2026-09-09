# H0 — Contract hardening before implementation

Recorded: 2026-09-09  
Status: **OPEN — IMPLEMENTATION NOT READY**.  
Reviewed documentation baseline: `be6958512fbeb98ff600fc4aa3a497109681a5f6`.  
Harness code baseline supplied by the reviewer and resolved on GitHub: `09891721b9d3509a3d618c7a25d3a3f184b0e225`.

This gate responds to the user's supplied Codex review. It is not a ninth runtime phase and does not replace the eight-phase/feature organization. Baseline inspection and isolated contract/test preparation may proceed; affected production feature implementation must not proceed on the assumption that the current prose and structural checks freeze all required contracts.

The reviewer reports 115 documents, 34 features, 204 completion requirements, 206 scenarios, 632 links, and 30 schema fixtures passing in its project environment. Those are attributed structural results, not tests reproduced by this amendment and not proof of semantic implementability. Published files, a passing schema fixture, and an implemented runtime are different facts.

## 1. Issue register and current evidence

| Gate | Finding and owners | Status in this amendment | Required closure artifact |
|---|---|---|---|
| H01 | Early requeue during yield; P3-F03/P6-F02/P7-F01 | Code/design incompatibility verified; corrective protocol specified, integration tests not run | [Yield settlement contract](contracts/YIELD_SETTLEMENT.md), migration/receipt integration, adversarial claim/answer/finalization tests |
| H02 | File synthesis has no demonstrated bounded terminal encoding; P4-F02/P1-F03 | Open | Immutable host contribution manifest, bounded reconciliation staging, small final seal, exact schemas and large-cardinality fixtures |
| H03 | Mid-attempt publication has no executable prefix-receipt contract; P4-F01/P1-F06/P3-F03 | Open; completed-graph-only runtime receipt verified in code | Versioned producer-prefix and transcript-prefix contracts, append/replay/reconciliation algorithms, negative fixtures |
| H04 | 170k context budget not enforceable from the current specification; P1-F04/P1-F05/P6-F03 | Open; current configuration lacks necessary numerical policy | Host preflight algorithm, concrete headroom/dossier limits, eviction order, exact 170k-route tests |
| H05 | SDK and new-role terminal contracts not frozen; P1-F03/P7-F02 | Open; current SDK defers signature choices until implementation | Machine-readable SDK surface and closed role input/output/error schemas with executable fixtures |
| H06 | New task/review states and kinds lack complete migration map; P7-F01/P6-F02/P6-F04 | Open; baseline TaskState and phase-coupled claim SQL verified | One exhaustive state/transition matrix and migration/eligibility/recovery/query/receipt coverage checklist |
| H07 | Investigation outcome mapping incomplete; P5-F01/P5-F02/P6-F04 | Open | Total outcome-to-artifact/candidate/task/successor/completion table with row-specific tests |
| H08 | Operation extraction assumes unimplemented adapter IR; P2-F01 | Open; current LanguageAdapter/InventoryResult lack that typed interface | Versioned minimal callsite/binding IR, Python pilot, explicit support matrix and unsupported outcomes |
| H09 | Legacy-runtime default conflicts with reviewer-reported user direction; P7-F03 | Policy reconciliation required; do not claim a prior approval not established by these sources | Record coordinated collaborative-v1 cutover scope separately from data preservation and optional historical inspection |
| H10 | Manifest, publication handoff and validation provenance are stale; P8-F03 | Open; earlier validation reports are not current certification | Regenerated tracked-file manifest, baseline/traceability updates and separately recorded structural/semantic results |

The critical source path is [claim_task in service.py](https://github.com/JennieXLisa/source-review-harness/blob/09891721b9d3509a3d618c7a25d3a3f184b0e225/src/ssr/orchestration/service.py#L1158-L1260): PENDING selection precedes `_terminalize_active_agents`. [TaskState](https://github.com/JennieXLisa/source-review-harness/blob/09891721b9d3509a3d618c7a25d3a3f184b0e225/src/ssr/orchestration/contracts.py) does not include WAITING_DEPENDENCY. [runtime_receipt.py](https://github.com/JennieXLisa/source-review-harness/blob/09891721b9d3509a3d618c7a25d3a3f184b0e225/src/ssr/runtime_receipt.py) identifies its domain as completed agent runtime event graphs. [languages/base.py](https://github.com/JennieXLisa/source-review-harness/blob/09891721b9d3509a3d618c7a25d3a3f184b0e225/src/ssr/languages/base.py) exposes symbols, generic relationships and diagnostics, not the proposed callsite_records interface.

## 2. H01 selected correction

Keep a yielding task RUNNING while a durable yield intent is prepared and its original execution settles. Stop ordinary inference, but retain exact host finalization authority. Only after original runtime and required terminal transcript receipts are verified may one orchestration transaction publish PENDING or WAITING_DEPENDENCY and clear the lease. Answers arriving during settlement leave durable wake information but cannot requeue the task. The finalizer rechecks answers when publishing continuation.

This protocol is specified in [YIELD_SETTLEMENT.md](contracts/YIELD_SETTLEMENT.md), and replaces the unsafe sequences in the two implementation plans and shared state document. It has 18 explicit acceptance scenarios. These scenarios have not been run against the harness; the protocol is not marked implemented or release-ready.

## 3. H02 bounded synthesis contract to complete

Use an immutable host-owned manifest for the full contribution set, unit dispositions, dependency/SCC coverage, input revisions and evidence/proposal lineage. Paginated model retrieval and model-authored reconciliation decisions reference that exact manifest. Preserve existing host pass-through of unchanged proposals where its contract already supports it.

A manifest plus one unbounded delta array is insufficient: the worst case can require a decision for every proposal. Define bounded, durable reconciliation fragments with exact manifest/generation identity, unique decision keys, fragment digest, producer receipt and replay behavior. A small final seal references the manifest and accepted decision-set root; it must not retransmit every disposition or evidence ID. Full canonical publication remains one authoritative transaction after all required decisions and dependencies validate.

Close H02 only with exact staging/seal schemas, stale-manifest and duplicate-fragment rejection, and size proofs/fixtures for many units and many changed/conflicting proposals. Every individual provider input must fit the configured cap. Increasing the cap alone does not close the issue. Document any irreducible single-item size limit as an explicit supported-bound outcome, never false file completion.

## 4. H03 producer-prefix and immutable input contracts to complete

Define a versioned receipt that binds review/task/agent/attempt/control identity, execution-contract digest, exact immutable input revision, request/response identities and hashes, tool call identity/argument hash, event-prefix end and chain digest, and required source-delivery/material receipt references. The prefix ends at a completed producer response that requests the action; it must not wait for that action's own acknowledgment. A partial or malformed response cannot qualify.

Specify transcript-prefix identity, canonical hashing/framing, append-only seals, next-prefix extension validation, uniqueness, bounded validation, restart reconstruction and explicit rejection reasons. A seal authenticates only its included completed prefix, not future turns or the whole unfinished attempt. Retain source-free project records and sensitive transcript bytes in their existing separate owners. Document the real two-database reconciliation order rather than claiming an atomic cross-database commit.

Leads/answers remain ACCEPTANCE_PENDING until their required proofs exist. Do not disable the approved immediate nonterminal workflow as a workaround; implement its missing proof contract first. Missing receipt support must be a capability gate, not a forged AGENT_TERMINAL or reuse of another producer's receipt.

## 5. H04 context policy to complete

Freeze route-level effective context capacity, reserved output/reasoning tokens, tokenizer/protocol overhead and safety margin. Define the maximum input from those quantities and measure the final assembled request: system instructions, tool definitions, dossier, history, source/tool results, notices and pending calls. Byte limits are separate constraints; an assumed characters-per-token ratio is not an enforced token budget.

Specify concrete 170,000-token-route values, preflight refusal before any oversized provider call, a checkpoint/compaction trigger before emergency exhaustion, and a deterministic history reduction order. Protect mandatory instruction/assignment/input provenance and complete tool-call/result groups. Bound the dossier independently in tokens and bytes; retain references rather than repeatedly copying all source. Handle an oversized mandatory dossier as an explicit blocker rather than retrying an unchanged over-limit request.

Acceptance includes the reviewer-reported 365k-prompt regression as a constructed oversized fixture, maximal tool/schema overhead, batches/notices, checkpoint failures, pending tool pairs, truncated tool arguments, unknown tokenizer accounting, and repeated no-progress recovery. Do not claim to have inspected the historical 365k incident logs from this review text alone.

## 6. H05 exact public and role surfaces to complete

Freeze exact exported callable signatures (positional/keyword-only/defaults/return types), DTO field order and types, nullability, bounds, closed enums, error shapes and serialization. Include cursor type/domain, capability versioning, admission tokens and opaque reference semantics. The current phrase 'defined here consistently when implemented' is not a frozen contract.

Provide executable schemas for FOCUSED_ANALYSIS and CONTEXT_REVIEW terminal outputs, not generic unvalidated analysis dictionaries. Identify every preserved semantic requirement, normalization step and conditional constraint. Version/hash the transformation for existing roles; host-filled identity must not erase required analysis. Add positive/negative examples and contract-comparison tests consumed by both implementing repositories.

Input-revision tokens must bind the exact material set and delivered deltas; changing an input token is not equivalent to proving the agent received its contents. Prefix receipts, staged synthesis and yield all consume the same frozen identity rules.

## 7. H06/H07 state and disposition completeness

Inventory every affected table CHECK constraint, transition trigger, eligibility view/index, claim query, type-to-phase switch, role map, retry/orphan recovery path, runtime receipt rule, public projection, exporter and completion predicate. Name existing owners at 0989172 and map them to the eventual implementation checkout. No code path may treat a new kind/state as an unknown value and silently omit it.

Write exhaustive permitted transitions, their exact guards, writer authority, atomic writes, events, replay key and resource effects. Include prepared yield, receipt pending/failure, cancellation during settlement, normal continuation versus operational retry, and single-slot dependency progress. Do not reduce this work to Python enum additions.

For each investigation outcome (SUPPORT_FOR_FALSIFICATION, DISMISS_WITH_EVIDENCE, NEED_CONTEXT, INCONCLUSIVE), define accepted artifact/state, candidate maturity/disposition, task destination after settlement, successor creation, and completion/limitation blocker. Specify operational refusal/timeouts and malformed output separately. 'Inconclusive' must neither loop forever nor count as a supported/dismissed vulnerability. Add one executable transition fixture for every row and forbidden transition.

## 8. H08 typed operation IR and bounds

Define the minimum versioned source-derived representation: callsite identity/range, containing symbol or explicit no-symbol location, callee/receiver expression references, ordered positional/keyword arguments and expansion forms, binding state/basis and extractor limitations. Retain existing symbol/source identities and original byte ranges. Do not create a universal language-analysis framework or execute target imports to infer bindings.

Prove one supported Python path first: imported aliases, shadowing, keyword shell mode, dynamic options, multiple calls on one line and unknown receiver types. Other languages remain explicit unsupported/model-gap outcomes until their adapters pass equivalent contract fixtures. A successful generic symbol inventory is not evidence that operation semantics were extracted.

Across H04/H06/H08, also close numeric/algorithmic bounds for independent lead proposals, request consumers/fanout, interest counts, per-root depth/revisions, pending artifacts and no-progress continuations. Full worker capacity queues a valid lead; exhausted metadata capacity returns an explicit outcome rather than silently dropping it. Counter bounds must be transactional and retry-idempotent.

## 9. H09 compatibility scope

The review reports a user decision that runtime backward compatibility is unnecessary. The published documents instead retain legacy execution by default; the earlier behavior-preserving refactor instructions also preserved compatibility. This amendment does not fabricate evidence of when the newer instruction was given.

The recommended correction is a coordinated collaborative-v1 cutover with exact new harness/controller contracts. Optional read-only historical database/report inspection is a separate capability, not continued support for the old scheduler or four old/new runtime pairings. Preserve immutable evidence/history and inspect active reviews before any separately authorized cutover; dropping compatibility is not permission to delete data, reinterpret old receipts or silently migrate an active review.

Record the selected scope in ENGINEERING_DECISIONS, CONFIGURATION, SDK, DELIVERY, integration tests and release gates together. Until reconciled, the old-mode default/four-pair wording must not be treated as a settled requirement for the new implementation.

## 10. H10 publication metadata and validation

Refresh baseline source references to the actual reviewed/pinned checkout while retaining historical observations. Regenerate a manifest from the final tracked tree including all 34 dedicated feature plans and the feature index. Define exclusions for the manifest's own bytes and any publication record containing a later commit; avoid a self-referential hash promise. Preserve prior historical manifests as historical files.

Rebuild traceability from real requirement/test/schema IDs. Make structural validation reproducible, and separately record semantic contract checks, harness regression results, controller integration, installed-artifact tests and live-provider tests as PASSED/FAILED/NOT_RUN. Previously recorded hashes and structural counts are not current after subsequent edits. A GitHub commit proves publication, not application correctness.

## 11. Closure and delivery order

1. Finish H01 and H06's settlement/state foundations; H01's document correction is the first committed change, not the whole hardening milestone.
2. Freeze H03/H05 identities, prefix receipts and executable role/SDK contracts, and H02's manifest/staging protocol against those identities.
3. Freeze H04 context/resource admission and H07 outcome/completion transitions; add executable reference/model/schema fixtures before feature enablement.
4. Prove H08's first-language IR and reconcile H09 cutover scope. Generate a coordinated dependency plan rather than implementing two inconsistent protocol variants.
5. Complete H10 last over the final tree; request an independent semantic reread against the pinned code and exact contract fixtures. Only then reopen the gated feature delivery slices.

Closing the specification gate requires a concrete normative contract and executable contract fixtures for each item, not another paragraph saying 'handle the race' or 'validate the schema'. Closing implementation/release gates additionally requires the real harness/controller tests; this documentation amendment claims none of those results.
