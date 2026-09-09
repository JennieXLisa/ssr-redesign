# Executable role submissions and compact host normalization

Contract: `role-projections-v1`. Resolves H05 and H02. New closed executable objects live in `schemas/hardening-v1.schema.json`. The whole input cap remains 65536 UTF-8 bytes after canonical serialization. The host must reject malformed/truncated arguments before deriving an operation or publication receipt.

## Exact new-role tools

| Tool | Exact schema definition | Terminal behavior |
|---|---|---|
| submit_focused_analysis | FocusedResult | Terminal analytical result; LEADS_RECORDED requires recorded lead IDs, NO_SUPPORTED_LEAD has none, INCONCLUSIVE requires unknowns |
| publish_context_answer | ContextAnswer | Nonterminal accepted/pending artifact for an exact routed request revision, using producer prefix proof |
| submit_context_review | ContextResult | Terminal small reference to a previously accepted answer artifact; identity/hash/request/outcome must equal that artifact |
| record_investigation_progress | InvestigationProgress | Nonterminal NEED_CONTEXT progress tied to checkpoint and registered requests; use explicit yield afterward |
| stage_file_synthesis | SynthesisStage | Nonterminal bounded journal/reference-set pages, immutable producer provenance |
| submit_file_synthesis | SynthesisSeal | Terminal small root reference; host constructs the complete canonical file result from manifest and decisions |

The ContextAnswer body requires scope_checked, every requested facet ID with its status/analysis/references, conditional answer, assumptions, counterevidence, unknowns and outcome. The host checks exact facet coverage, uniqueness, request revision and producer routing. ANSWERED cannot hide unresolved required facets; INCONCLUSIVE/NEEDS_DIFFERENT_SCOPE must identify the unresolved/out-of-scope facets; CONTRADICTED_ASSUMPTION needs a contradicted facet with evidence. A receipt validates provenance, not the truth of the answer.

FocusedResult requires question, checked subjects, observations, counterevidence, assumptions, unknowns, disposition and exact registered lead/request IDs. It has no canonical coverage-completion flag. A lead is registered independently through report_lead, not embedded as an unbounded seed array in this terminal result. Every supplied reference resolves through current authorization and original authorship; an empty observation set cannot support LEADS_RECORDED without valid separately registered lead origins.

ContextResult contains no second arbitrary answer body; it seals the exact accepted/pending publication under the original identity. If answer acceptance is still pending, terminal semantic output may be stored but task completion awaits proof. The terminal result must not wait for its own ACK. A context task required to produce a complete canonical review unit must also publish that full semantic unit artifact explicitly; an answer alone gives no coverage credit.

## Existing analytical roles

SYMBOL_REVIEW, LINK_REVIEW, INVESTIGATION and FALSIFICATION retain the baseline's full **semantic** validators. Mechanical normalization is an explicit top-level mapping, never recursive deletion of fields named id/path. Freeze the selected implementation checkout's original schema hash, removed-top-level-field list, provider projection hash and normalized full-schema hash in the release artifact. This preserves analytical obligations without maintaining an old executing mode.

The only removable fields are outer review_run_id, task_id, agent_run_id, snapshot_id, attempt_number, execution contract identity and an assignment/candidate/file identity uniquely fixed by the actual input revision. Any similarly named field inside path segments, source/evidence links, lead proposals or cross-file claims remains agent-selected. Input token validation uses INPUT_REVISIONS.md, not a mutable “latest” lookup.

SYMBOL_REVIEW still supplies complete per-unit/per-symbol dispositions and documentation, controls, effects, errors, unknowns and evidence; host IDs do not complete absent analysis. LINK_REVIEW still supplies explicit typed relationship observations and uncertainty. INVESTIGATION retains its path/state/lifecycle argument schema and the total outcome map in STATE_MACHINE.md; NEED_CONTEXT is nonterminal, not a disguised completed investigation. FALSIFICATION retains independent challenges, UPHELD/REFUTED/INCONCLUSIVE and material evidence bound to the exact argument.

FILE_REVIEW is the single symbol-review-then-synthesis workflow. It now uses FILE_SYNTHESIS.md, not a model-visible complete contribution/evidence/lineage array. The host inherits mechanical manifest facts and model-authored staged reconciliation, then runs the full existing canonical publication validator. Do not implement both old large-body and new staged providers as optional runtime modes.

## Error mapping, provider projection and acceptance

Normalize into typed internal proposals only after input-revision/request-delivery checks. Preserve a deterministic field-origin map so a host validation error points to the actual model field or staged decision key, not an invented hidden field. Where a required full semantic field cannot be mapped mechanically, it must remain in the model/staged contract. No host default may assert control effectiveness, severity, reachability or complete evidence.

Compile each tool's provider schema from the exact closed definition. A provider lacking a supported union/nullable form uses separate named variants or a pinned tested schema projection with identical accepted set; it cannot accept a generic unconstrained analysis object and call it equivalent. Runtime host validation always uses the full canonical schema plus semantic checks. Hash the complete advertised tool set and check its context cost under CONTEXT_BUDGET.md.

Fixtures include missing field, unknown field, null in a nonnullable field, bool-as-integer, incorrect enum, duplicate facet/lead ID, stale token, foreign source, unsupported role, malformed/truncated output, required facet left unresolved under ANSWERED, wrong artifact hash, and a synthesis file requiring thousands of decisions. Run them against reference schemas and the later installed provider adapters. Shape success does not by itself close receipt, material-validity, canonical-coverage or terminal-settlement gates.

FILE_REVIEW maps to the terminal tool `submit_file_synthesis` in the new broker role table; FOCUSED_ANALYSIS maps to `submit_focused_analysis`, CONTEXT_REVIEW to `submit_context_review`. This is one selected mapping, not simultaneous old/new aliases. `publish_context_answer`, `record_investigation_progress`, and `stage_file_synthesis` remain nonterminal. Full canonical internal file-result validation is retained behind the small synthesis seal.
