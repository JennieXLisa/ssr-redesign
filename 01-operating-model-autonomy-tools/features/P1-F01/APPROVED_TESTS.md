# P1-F01 — preserved acceptance scenarios

These are the original twelve scenario identifiers and expected results, not application test results.

| Test | Setup/action | Expected result |
|---|---|---|
| F01-T01 — Cross-file access | Assign reviewer A to one unit; read indexed helper B in another permitted file. | Exact B source is returned; A/B assignment and coverage state remain unchanged. |
| F01-T02 — Same-file context | Read a permitted declaration outside A's assigned byte range. | Research succeeds without widening A's required coverage disposition. |
| F01-T03 — Foreign coverage | After T01, submit completion for B through A's result authority. | Submission fails its ownership check and performs no partial domain publication. |
| F01-T04 — Exclusion | Request content for an excluded or non-readable manifest entry. | No source is returned, including through alternate ID/path inputs. |
| F01-T05 — Snapshot binding | Request an ID belonging to a different snapshot. | No silent rebinding or foreign source disclosure. |
| F01-T06 — Stale attempt | Revoke/expire the attempt, then repeat a previously permitted read. | Execution authorization rejects it despite any cached metadata. |
| F01-T07 — Integrity | Alter disposable snapshot bytes after manifest capture. | Existing file/hash safety checks fail; no automatic recapture. |
| F01-T08 — Large inventory | Use a project with more permitted files than `max_context_items`. | Access initialization does not fail solely because of project size; responses remain bounded and initial context does not inline the catalogue. |
| F01-T09 — Synthesis | Supply conflicting child summaries and request their permitted source. | Synthesizer can check source/index context; child authorship and coverage requirements are unchanged. |
| F01-T10 — Attempt read truth | Start a new attempt after an earlier one read B. | Prior reads do not satisfy the new attempt's material-read requirements automatically. |
| F01-T11 — Alternate surfaces | Reach the same file via existing file, symbol or relationship navigation paths. | Research authorization is consistent; no handler is a permission bypass. |
| F01-T12 — Context-only source | Read a permitted `CONTEXT_ONLY` file. | Source is available under existing policy but no new coverage task/disposition is created by the read. |
