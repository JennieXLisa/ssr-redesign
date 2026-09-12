# Stage 1 — Per-file indexing progress

Status: approved behavior from the researcher discussion. This is a requirements record, not a complete implementation plan or a test-results report.

This group extends [source-intake.md](source-intake.md), particularly S1-IN-R07, R09-R12, R21, and R22. Snapshot capture remains separate from indexing. PostgreSQL holds indexing records; all processing and source retrieval use the completed immutable Git snapshot. No model calls are introduced.

## Approved requirements

**S1-IX-R01 — Per-file, per-step progress.** Track progress for each file within its indexing run, distinguishing structural extraction, reference resolution, and security flagging. Do not reduce these to one file-level indexed flag. Keep the snapshot, run, and relevant processing version/configuration associations required by S1-IN-R07.

| Processing step | Required output |
|---|---|
| Structural extraction | The agreed definitions, signatures, scopes, imports, and source-located reference/callsite occurrences. |
| Reference resolution | Connections to indexed definitions, retaining resolved, ambiguous, and unresolved outcomes with their basis. |
| Security flagging | Interesting-name observations and applicable Semgrep matches, including reasons and source locations. |

Apply only the steps required by the file's agreed treatment. Binary metadata and unsupported-source retrieval do not claim structural extraction. An applicable step that fails cannot be relabeled inapplicable. Security flagging is not complete while a required flagging component remains unfinished.

**S1-IX-R02 — Publish results with their completion marker.** Make a completed file-step's result set and its completion marker visible together. A crash must not expose a successful marker with missing results or expose a partially written result set as the completed output. Internal staging is permitted, but its exact representation and transaction boundaries remain to be designed. Processing progress may be reported without presenting unfinished output as complete.

**S1-IX-R03 — Resume without discarding valid work.** Persist enough progress to resume unfinished or failed steps against the same snapshot and compatible processing configuration. Retain valid completed results; a Semgrep failure must not force successful structural extraction to run again. Replaying publication or resuming after a lost acknowledgment must not duplicate records or count the same completion twice. Existing failure/completeness rules remain authoritative; this does not authorize endless automatic retries.

**S1-IX-R04 — Respect cross-file dependencies.** Reference resolution must account for the full structural inventory required for the selected index run. Do not finalize no-target-found merely because the defining file has not been extracted yet. Provisional relationships may be queryable under S1-IN-R22, but their incomplete status must remain explicit until the necessary inventory and resolution work finish. An explicitly unresolved outcome after supported resolution is different from an unfinished resolution step. This does not require full taint or data-flow analysis.

**S1-IX-R05 — Make partial queries specific.** Return available committed results together with the relevant processing-completeness information. A function may be retrievable while its references or flags are still pending. Distinguish no matches from completed applicable processing from no matches currently available during unfinished processing. Caller lists can remain incomplete even when the queried function's own file has finished, because other files may contain additional callers. File-step completion is not whole-run completion; S1-IN-R12 still governs the latter.

Worker counts and memory settings discussed for the researcher's machines were provisional tuning suggestions, not approved fixed defaults or performance guarantees. They must not change the required scope, result semantics, or completion conditions.

## Derived acceptance scenarios

These are required observations for future tests, not executed test results.

| ID | Scenario | Required observation |
|---|---|---|
| S1-IX-T01 | Complete a file's extraction and flags while resolution remains unfinished. | The function and committed flags are queryable from the exact snapshot; resolution and overall indexing remain explicitly incomplete. |
| S1-IX-T02 | Interrupt publication before commit and after commit but before acknowledgment; then resume. | No completed marker refers to missing results; uncommitted output is not exposed as complete; replay preserves one result set and one completion. |
| S1-IX-T03 | Fail applicable Semgrep processing after structural extraction succeeds. | Preserve the structural results and their completed status; resume the failed processing without reparsing solely because scanning failed; the run remains incomplete until its required processing succeeds. |
| S1-IX-T04 | Extract a caller before its defining target file; query before and after that file is processed. | Early results disclose incomplete resolution; later resolution incorporates the target. The caller is not permanently finalized as unresolved merely because extraction order delayed its target. |
| S1-IX-T05 | Query a function before another file containing a caller has been processed. | Its own file's completion does not imply an exhaustive caller list. The list's status reflects the remaining cross-file work. |
| S1-IX-T06 | Compare unfinished flagging, completed flagging with zero matches, and inapplicable steps for binary/unsupported files. | Distinct processing outcomes are visible. None is represented as an equivalent empty successful semantic index. |

## Decisions still requiring discussion

- Exact progress/status fields, PostgreSQL schema, and result-publication transactions.
- Work claiming, retry classification, recovery controls, and compatible-progress checks.
- Resolution prerequisites and completion publication across files.
- Partial-query response fields and pagination while more results become available.

Specify those mechanisms with the researcher before assigning implementation. Do not add a new scheduler, store, or automatic investigation workflow merely to record indexing progress.
