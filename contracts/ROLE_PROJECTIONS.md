# Compact agent submission projections

The internal semantic contracts are reused, not replaced by an unvalidated generic `analysis` dictionary. A developer must generate/test the smaller model-facing envelope from the exact installed role schema and preserve every nonmechanical field and constraint.

## Mechanically removable identity fields

At the outer request/result boundary only, the host may supply these fields when the assigned work uniquely determines them: review_run_id, task_id, agent_run_id, snapshot_id, attempt_number, assignment path/file identity, inventory/review-graph identity and hash, candidate_id for a candidate-owned task, and current execution contract/version identity. The model-facing result instead carries the issued input_token and role-specific semantic body.

Do not recursively remove similarly named fields inside a path, evidence link, candidate proposal, question or cross-file claim. Those can be genuine model-selected analytical subjects. Lease tokens and provider secrets never become model input. The exact set removed from each installed schema is a recorded contract transform and tested by comparing required properties and constraints before/after normalization.

## Semantic bodies that remain mandatory

| Role | Preserved semantic responsibility |
|---|---|
| SYMBOL_REVIEW | Complete required unit documentation, per-symbol dispositions, purpose/parameters/returns/side effects/errors, inputs/effects/controls, unknowns, source refs and provisional proposals. |
| FILE_REVIEW synthesis | Exact accepted contribution selection, inventory/dependency coverage, reconciliation/merged proposal lineage, residual file-level analysis and explicit unresolved conflicts. No whole-child-body retransmission requirement. |
| LINK_REVIEW | Covered subjects, proposed typed relationships, confidence/provenance, exact evidence and unresolved targets. No automatic promotion of name matches. |
| FOCUSED_ANALYSIS | Concrete question, checked subjects, evidence/counterevidence, assumptions, unknowns, proposed leads or explicit no-supported-lead outcome. It has no implicit complete-file coverage. |
| CONTEXT_REVIEW | Requested facets/revision, checked scope, conditional answer, evidence/counterevidence, unresolved or declined scope and real producer identity. |
| INVESTIGATION | Complete or partial path/state/lifecycle argument; influence/reachability/controls/configuration/impact/counterevidence/unknowns; exact current material and explicit disposition. |
| FALSIFICATION | UPHELD/REFUTED/INCONCLUSIVE, independent challenges, material source refs, counterevidence and limitations bound to exact candidate argument. |

## Normalization and validation

Resolve the input_token to the attempt's recorded input plus explicit accepted deltas. Revalidate current work/candidate revision. Resolve typed source/evidence refs and build existing internal proposal types. Run full role validators and source-read requirements. Only then call the canonical commit owner. A selected symbol ID can identify source, but cannot fill a missing control analysis, path hop, approval flag or severity.

Keep the normalized-field-to-model-field map so validator errors identify the actual input location. Unknown fields are rejected. Legacy model/tool schemas remain unchanged on old reviews. Test a missing analytical field in every role; no normalization should make it disappear or invent its value. Test schema normalization with known IDs/hashes, stale inputs, cross-file refs and duplicated producer fields.
