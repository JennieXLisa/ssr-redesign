# P1-F01 — preserved approved requirements

The original twelve requirements are retained verbatim. Their previously open implementation details are now supplied by the current feature guide and shared contracts. Historical code mapping remains in the preserved original document.

| Requirement | Required behavior |
|---|---|
| P1-F01-R01 | Analytical research access MUST be read-only and bound to the authorized review snapshot. It MUST NOT use the live target as substitute evidence. |
| P1-F01-R02 | Background reviewers, focused analysts, investigators and falsifiers MUST be able to inspect permitted source outside their assigned file or symbol. |
| P1-F01-R03 | File synthesizers MUST have source and index access for reconciliation. Their required work remains synthesis, not routine re-review of all children. |
| P1-F01-R04 | The host MUST distinguish execution identity, assignment ownership and research policy. Research permission MUST NOT implicitly enlarge the assignment or terminal-result authority. |
| P1-F01-R05 | Permitted cross-file research MUST NOT require another worker, manual approval for each read, or a new coverage assignment. Ordinary deterministic authorization is still required. |
| P1-F01-R06 | Access MUST be resolved on demand through the existing snapshot manifest and index. Full project file/symbol catalogues MUST NOT be required in every worker or initial prompt. |
| P1-F01-R07 | Accessible project size MUST NOT be conflated with the number of context items returned to the model. Actual reads, result pages and cumulative usage remain bounded by applicable configured limits. |
| P1-F01-R08 | Existing role/attempt/lease/control checks MUST continue to apply. Broad research permission MUST NOT authorize operations from a stale or inactive execution attempt. |
| P1-F01-R09 | Existing exclusions, captured-content checks, snapshot integrity and filesystem boundaries MUST remain enforced. A valid-looking ID or path is a lookup input, not a grant. |
| P1-F01-R10 | Reading subject B while assigned A MUST NOT complete B's coverage, claim B's task, publish B's private result, or mutate B's lifecycle. |
| P1-F01-R11 | Required source-read accounting MUST describe the ranges actually returned to the current attempt. A prior read or available summary MUST NOT automatically count as that attempt's source inspection. |
| P1-F01-R12 | The implementation MUST reuse the existing broker, index and source-verification authorities where applicable. It MUST NOT introduce a second inventory or competing coverage/acceptance authority as an access shortcut. |
