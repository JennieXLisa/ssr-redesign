# Stage 1 — References and callsites

Status: approved behavior from the researcher discussion. This records the agreed separation of source occurrences from resolution results; it is not a complete database schema, implementation plan, or test-results report.

Read with [function-records.md](function-records.md), [indexing-progress.md](indexing-progress.md), and [source-intake.md](source-intake.md). Git owns captured source; PostgreSQL stores searchable records. Existing snapshot identity, processing completeness, and partial-query requirements apply.

## Approved requirements

**S1-RF-R01 — Separate observations from resolution.** Represent a source reference occurrence separately from the result of resolving its target. Structural extraction records what appears in the source without requiring successful target resolution. Subsequent resolution links to that occurrence rather than replacing it with a guessed target or discarding it when binding is unavailable. These are logical responsibilities; exact tables and interfaces remain to be specified.

**S1-RF-R02 — Reference occurrence information.** Retain the occurrence's identity, indexing-run and snapshot/file associations, exact source location, enclosing function or module, referenced expression, and usage kind. Distinguish calls, imports, symbols passed as callback arguments, and other symbol uses where extraction supports that distinction. Preserve source spelling independently of any resolved qualified target name. Names alone must not collapse occurrences from different locations or scopes. The expression representation and complete usage vocabulary remain open.

**S1-RF-R03 — Callsite information.** A call occurrence additionally retains receiver and argument locations where present. The researcher or model must be able to open the actual callsite and its argument expressions from the immutable snapshot, not merely see an edge between two functions. A function passed as an argument is a reference, not by itself a direct invocation of that function. Do not infer eventual callback execution solely from argument position. Calls and non-call references remain distinguishable in queries.

**S1-RF-R04 — Resolution information.** Associate each resolution result with its source occurrence and retain the resolved target or candidate targets, the resolution outcome, and its producing backend/version and basis. Preserve resolved, ambiguous, and unresolved outcomes without promoting a name match to an established binding. Processing still pending or dependent on unfinished inventory is distinct from an unresolved outcome after supported resolution. Apply S1-IX-R04's cross-file completeness rule; a target not yet extracted is not evidence that it does not exist.

**S1-RF-R05 — Independent progress and reuse.** An occurrence can become available before its target resolution finishes. Completing or retrying resolution must not require reparsing solely to recreate an already valid occurrence. Retain compatible completed extraction under S1-IX-R03. Resolution enrichment must preserve the original expression and source identity. Result publication and completeness reporting follow S1-IX-R02/R05; this separation does not authorize mixing runs, incomplete successful markers, or hidden processing failures.

**S1-RF-R06 — One relationship source for navigation.** Derive incoming caller and outgoing callee views from the same call occurrences and associated resolution records, rather than maintaining independently authored caller/callee lists. Reference queries also expose the supported non-call occurrences. Preserve unresolved callsites as searchable observations even when no target link exists. Return bounded results and the relevant partial-processing indicators; available relationships are not a guarantee of an exhaustive caller list while other required work is unfinished.

## Illustrative record flow

For `obj->something()` inside a function, extraction records the expression, containing function, file/range, and receiver location. Resolution can subsequently associate that occurrence with `Test::something` when the selected backend establishes the binding. The occurrence remains useful and retrievable before that association exists. This illustration does not select a C++ backend or assert that syntax parsing alone establishes the type.

## Derived acceptance scenarios

These are required observations for future tests, not tests executed here.

| ID | Scenario | Required observation |
|---|---|---|
| S1-RF-T01 | Extract a member call before running its supported resolver. | The occurrence, enclosing function, expression, receiver/argument locations, and exact snapshot source are available; resolution is explicitly unfinished. |
| S1-RF-T02 | Resolve that occurrence to an established method target. | The target and backend/basis link to the original occurrence without changing its expression/location or reparsing solely to reconstruct it. |
| S1-RF-T03 | Process ambiguous and unresolved references, including a reference whose target file has not yet been extracted. | Preserve each occurrence; distinguish candidate or unresolved outcomes from pending cross-file processing; do not select a target solely by matching its name. |
| S1-RF-T04 | Compare a direct function call, an import reference, and passing a function as an argument to another call. | Usage kinds remain distinguishable; passing the function does not fabricate a direct call to it or prove callback execution. |
| S1-RF-T05 | Query callers and callees for resolved calls at several distinct source locations. | Both directions derive from the same underlying records and can open individual callsites; same-name occurrences are not collapsed and unfinished coverage stays explicit. |
| S1-RF-T06 | Interrupt resolution after structural extraction has committed, then resume with compatible inputs. | Retain the valid occurrence set and its snapshot/run association; recover resolution without unnecessary re-extraction, duplicate publication, or loss of unresolved observations. |

## Decisions still requiring discussion

- PostgreSQL tables, keys, constraints, exact fields, and occurrence identity rules.
- Usage-kind vocabulary and expression, receiver, and argument representations.
- Resolver-specific identity/binding proofs, candidate representation, and enrichment conflict handling.
- Publication revisions, pagination consistency, and exact shared query responses.

Specify these mechanisms with the researcher before implementation. No automated taint analysis, model-generated call graph, or mandatory whole-repository model review is introduced by this agreement.
