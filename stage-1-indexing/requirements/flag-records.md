# Stage 1 — Security-interest flag records

Status: approved behavior from the researcher discussion. This records the agreed observation fields and display grouping; it is not a complete database schema, rule catalogue, implementation plan, or test-results report.

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

## Decisions still requiring discussion

- The category catalogue, rule selection, researcher customization, and name-matching semantics.
- Exact PostgreSQL fields, enums, keys, per-match provenance, and retry/deduplication rules.
- Scanner-to-source range mapping and association when a result spans multiple owners or structural extraction is unavailable.
- Exact grouping, ordering, pagination, and query response contracts. No ranking or confidence-score policy is selected here.

Define these mechanisms with the researcher before implementation. Do not replace broad, explainable reconnaissance signals with vulnerability verdicts, automatic per-flag tasks, or mandatory model review of every match.
