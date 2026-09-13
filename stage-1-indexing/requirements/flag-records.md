# Stage 1 — Security-interest flag records

Status: approved behavior from the researcher discussion. This records the agreed observation fields, display grouping, custom-rule support, rule-selection modes, conflicting-ID handling, identical-rule deduplication, and pre-scan validation; it is not a complete database schema, rule catalogue, implementation plan, or test-results report.

Read with [function-records.md](function-records.md), [reference-records.md](reference-records.md), [indexing-progress.md](indexing-progress.md), and [source-intake.md](source-intake.md). Existing snapshot, provenance, completion, and partial-query requirements apply. Flags are stored in PostgreSQL and link to source retained in the immutable Git snapshot.

## Approved requirements

**S1-FL-R01 — Research observations, not vulnerability verdicts.** Record security-interest matches without requiring proof of a vulnerability or confirmed sensitive behavior. An interesting function name such as `execute_command` qualifies as a name-based observation even when its implementation has not been resolved. Identify the basis of the observation; a name match does not establish command execution, attacker reachability, or exploitability. Recording a flag does not create an investigation or trigger a model call.

**S1-FL-R02 — Required observation information.** Each flag retains the following information, linked to its indexing run and captured source. Exact field types and identifiers remain to be designed.

| Information | Required meaning |
|---|---|
| Category | The kind of security interest, for example command execution. This is a research classification, not a vulnerability classification or severity. |
| Signal kind | Distinguish an interesting-name match from a code-pattern match. Preserve what kind of evidence caused the flag. |
| Reason | Explain what matched and why the rule treats it as interesting, without asserting behavior unsupported by the match. |
| Location | Snapshot, file, and exact matched source range. |
| Owner | The associated function, method, anonymous callable, or module, as supported by the indexed source. |
| Provenance | Rule identity, producing scanner/extractor and version, and the relevant rule-set/configuration association. |

**S1-FL-R03 — Exact source and callable association.** Link a flag to the matched location and its indexed owner rather than copying a complete function body into the record. An operation in a lambda's own body links to that callable under S1-FN-R09, not solely to the outer function. Preserve the enclosing-scope navigation. A name match and an operation inside the same function may have different source ranges. Retrieval must open their corresponding captured source, not a changed working copy.

**S1-FL-R04 — Keep independent matches separate.** Preserve independently produced observations even when they concern the same function or operation. A function-name rule matching `execute_command` and a Semgrep rule matching an operation in its body are separate observations with their own reasons, locations, and provenance. Do not merge them into a fabricated stronger verdict or count them as separate confirmed vulnerabilities. Exact retry/deduplication keys remain to be specified; replaying the same publication is distinct from receiving an independent rule match.

**S1-FL-R05 — Group for display without losing evidence.** Query results may group related observations under the function or other indexed owner while retaining access to each individual match. Grouping is presentation, not replacement of the underlying records. Support bounded retrieval and the previously agreed category/path/function filtering rather than inserting every flag into a model's context. Keep the distinction between pending flagging and completed applicable flagging with no matches under S1-IX-R05. A displayed group does not imply that all applicable rules or other indexing steps have finished.

**S1-FL-R06 — Built-in and researcher-supplied reconnaissance rules.** Provide a maintained built-in reconnaissance ruleset and support researcher-supplied Semgrep rules and interesting-name patterns alongside it in Stage 1. A researcher must be able to add a project-specific name such as `dispatch_admin_command` or a custom code-pattern rule without changing harness source code. Custom-rule matches follow the same observation, exact-location, ownership, provenance, and partial-completeness requirements as built-in matches; neither becomes a vulnerability verdict or an automatic investigation task.

Each indexing run records its exact selected rules and associated versions/configuration. Retain the selected rule definitions or immutable references sufficient to identify their exact contents, rather than relying only on a mutable file path or rule name. Changing a custom rule file or the built-in ruleset must not silently change the rules bound to an existing run or rewrite earlier observations. Default/custom selection is specified in S1-FL-R07; conflicting rule IDs are handled under S1-FL-R08 and repeated identical definitions under S1-FL-R09. The storage representation, rule-input format, name-pattern semantics, and exact definition-comparison algorithm remain to be specified with the researcher.

**S1-FL-R07 — Default combined mode and explicit custom-only mode.** By default, run the built-in reconnaissance rules together with any researcher-supplied Semgrep rules and interesting-name patterns. Without custom rules, this default uses the built-ins. Provide an explicit custom-only mode that uses only the researcher-selected custom rules and name patterns, without silently adding built-in rules of either kind.

Record the selected mode alongside the exact effective rules bound to the indexing run under S1-FL-R06. Make that selection visible in flag-query results and progress/completion reports, including empty results. Custom-only completion means the selected custom rule processing finished; it does not claim that the built-in catalogue ran. Partial-processing indicators remain required in both modes. Rule selection does not change source capture or structural/reference-indexing scope, and required processing for the selected rules must not be silently skipped. A later selection must not rewrite an existing run's recorded mode, rules, or observations. Exact option names and empty custom-only selection handling remain open; conflicting rule IDs follow S1-FL-R08.

**S1-FL-R08 — Reject conflicting rule IDs.** Reject the effective rule selection when different rule definitions share an ID within the same rule engine. Apply this to both combined and custom-only modes, including built-in/custom and custom/custom conflicts. Do not silently override, discard, or rename a conflicting rule, or choose a winner based on file/loading order.

The error must identify the rule engine, conflicting ID, and both rule sources with their file locations so the researcher can correct or rename the conflicting definition. Treat this as an invalid rule selection, not successful scanning with no matches. Different IDs matching the same code remain independent observations under S1-FL-R04; a conflict is not inferred merely from overlapping matches. Repeated identical definitions follow S1-FL-R09. The exact definition-comparison algorithm and machine-readable error fields remain to be specified.

**S1-FL-R09 — Deduplicate identical rule selections and retain provenance.** When selected rules have the same engine, ID, and identical complete definition, consolidate them into one effective rule rather than raising a conflict. Apply this in combined and custom-only modes. Duplicate inclusion must not cause the same rule to run repeatedly over the same input or multiply its observations merely because it appeared in several selected sources. Retain all contributing rule-source references and locations with the run's recorded effective selection; deduplication must not discard their provenance or change the frozen rule definition.

Different IDs remain separate rules even when their patterns or matches coincide. Different definitions sharing the same engine and ID still fail under S1-FL-R08; do not infer identical definitions merely from identical match output. This requirement governs duplicate selection, not an exactly-once process-execution guarantee after a crash. Existing progress/replay requirements remain in force. Exact definition comparison and persistence keys remain implementation decisions to specify with the researcher.

**S1-FL-R10 — Validate the complete selected ruleset before scanning.** Validate the complete effective selection of built-in/custom Semgrep rules and interesting-name patterns before starting its scanning or name-rule matching. Apply this in both combined and custom-only modes. An invalid selected rule blocks that selection from scanning; do not silently skip it, run only the valid subset, or report successful scanning with no matches. Return an actionable error identifying the rule source/location and the problem so the researcher can correct it. Conflict and identical-duplicate handling remain governed by S1-FL-R08/R09.

Validation failure must not discard already-completed structural indexing. Correcting the rules must retain compatible completed extraction and must not force reparsing solely because the rule selection was invalid or changed. Preserve the snapshot and existing results under the established reuse requirements; a correction does not authorize silently rewriting rules or observations already bound to an existing run under S1-FL-R06/R07. Exact validation checks, error fields, validation timing relative to structural indexing, and the corrected-selection/run association remain to be specified with the researcher. Passing pre-scan validation is not a guarantee that later scanning cannot fail; such failures still follow the existing progress and completion requirements.

## Illustrative grouped view

```text
Function: execute_command
  Observation 1: interesting-name match
    Reason: function name matches the configured command-execution name rule
    Location: function name in the captured source
  Observation 2: code-pattern match
    Reason: an operation in the body matches the selected Semgrep rule
    Location: the matched operation in the captured source
```

Both observations retain their actual rule identities and producing versions. The illustration selects no particular Semgrep rule, severity, or numerical confidence scale.

## Derived acceptance scenarios

These are required observations for future tests, not executed test results.

| ID | Scenario | Required observation |
|---|---|---|
| S1-FL-T01 | Index a function named `execute_command` whose behavior is not resolved. | Record the applicable name-based flag with category, reason, exact location, owner, and provenance; do not require confirmed command execution or create an investigation. |
| S1-FL-T02 | Match a name rule and a Semgrep code-pattern rule in the same function. | Retain two observations with their own reasons, locations, and provenance; a grouped view exposes both without reporting two vulnerabilities or inventing a stronger conclusion. |
| S1-FL-T03 | Match an operation inside a lambda nested within another function. | Link the operation's flag to the lambda and its exact source location; keep the enclosing scope navigable rather than substituting the outer function as the sole owner. |
| S1-FL-T04 | Retrieve a flag after the original working source changes or disappears. | Its location opens the immutable captured source and retains the correct run/rule configuration; no live-source substitution occurs. |
| S1-FL-T05 | Query available flags while another required flagging component is unfinished, then query after completion. | Return bounded committed observations with explicit completeness information; distinguish incomplete empty results from completed applicable processing with no matches. |
| S1-FL-T06 | Select built-in rules together with a researcher-supplied name pattern matching `dispatch_admin_command`. | Produce applicable built-in and custom observations without editing harness code; retain each match's selected rule, reason, source location, and owner. |
| S1-FL-T07 | Supply a custom Semgrep code-pattern rule alongside selected built-in rules. | Ingest its matches through the same observation and query contract, preserving independent provenance and completeness reporting without automatic investigation or vulnerability claims. |
| S1-FL-T08 | After a run's rules are recorded, edit a custom rule file or update the built-in ruleset. | The existing run retains its exact selected rule contents and prior observations; results do not silently change because the external rule source changed. |
| S1-FL-T09 | Use default selection first without custom rules, then with a custom name pattern and Semgrep rule in a separate run. | The default runs built-ins alone in the first run and built-ins plus the supplied rules in the second; each records its exact effective selection and retains independent match provenance. |
| S1-FL-T10 | Select custom-only with source matching both built-in-only rules and the supplied custom rules. | Run only the selected custom name/Semgrep rules; do not silently invoke built-ins. Capture and structural/reference processing retain their agreed scope. |
| S1-FL-T11 | Query partial and completed custom-only results, including no matches, then select combined mode for a later run. | Reports identify each run's selection and processing completeness; custom-only never implies built-in coverage, and the earlier run's mode, rules, and observations remain unchanged. |
| S1-FL-T12 | Select a built-in rule and a different custom rule sharing the same engine and ID; reverse their load order. | Reject both selections with the engine, ID, and both source locations identified; no order-dependent winner, silent override, or successful scan claim. |
| S1-FL-T13 | In custom-only mode, select two different custom definitions with the same engine and ID. | Reject the conflicting selection and identify both definitions; apply this consistently to Semgrep rules and interesting-name rules within their respective engines. |
| S1-FL-T14 | Select rules with distinct IDs that match the same source location. | Do not reject them merely for overlapping matches; preserve independent observations and provenance under S1-FL-R04. |
| S1-FL-T15 | In combined mode, select identical built-in and custom definitions with the same engine and ID; reverse source order. | Select and execute one effective rule over each applicable input, retain both source references, and produce no duplicate observations merely from repeated inclusion; neither order raises a conflict. |
| S1-FL-T16 | In custom-only mode, repeat an identical engine/ID/definition across selected files and also select a different ID with the same matching pattern. | Consolidate only the identical same-ID selections and retain all their source references; the different-ID rule remains independent, with no built-in rules added or match multiplicity caused by duplicate selection. |
| S1-FL-T17 | Select valid rules together with an invalid Semgrep rule or invalid name pattern, in combined and custom-only modes. | Validate the full selection before scanning; report the offending source/location and problem. Do not run a valid subset, silently skip the invalid rule, or report successful scanning. |
| S1-FL-T18 | After structural extraction has completed, reject an invalid rule selection, correct it, and retry with compatible source/extraction inputs. | Retain the completed structural records and snapshot; validate the corrected selection before scanning without reparsing solely because rules changed. Preserve existing frozen rule selections and observations. |
| S1-FL-T19 | Accept a valid complete selection, then induce a scanner processing failure. | Pre-scan validation permits scanning but does not conceal a later failure or imply completion; preserve valid structural work and expose the failure under the agreed progress/completeness rules. |

## Decisions still requiring discussion

- The category catalogue, rule-input format, exact selection options, empty custom-only selection handling, exact identical-definition comparison, and name-matching semantics. Custom-rule support, selection modes, conflicting-ID rejection, and identical-rule deduplication are settled by S1-FL-R06/R07/R08/R09.
- Exact pre-scan validation checks, actionable error fields, timing relative to structural indexing, and corrected-selection/run association under S1-FL-R10.
- Exact PostgreSQL fields, enums, keys, per-match provenance, immutable rule storage, and retry/deduplication rules.
- Scanner-to-source range mapping and association when a result spans multiple owners or structural extraction is unavailable.
- Exact grouping, ordering, pagination, and query response contracts. No ranking or confidence-score policy is selected here.

Define these mechanisms with the researcher before implementation. Do not replace broad, explainable reconnaissance signals with vulnerability verdicts, automatic per-flag tasks, or mandatory model review of every match.
