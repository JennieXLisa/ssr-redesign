# Stage 1 — Source intake and processing completeness

Status: approved behavior recorded from the design discussion. Implementation details remain in discussion; this is not an implementation-ready plan or a test-results report.

This document covers one requirement group, not the whole indexing stage. SSR is being rebuilt from scratch. Archived implementations are references, not mandatory APIs, schemas, or workflows.

## Outcome

Capture the researcher's selected source in harness-managed immutable Git storage. Process every included file according to its type, preserving progress and explicitly reporting limitations. Resource pressure must not silently narrow the research scope or produce false completion.

Git retains source contents; PostgreSQL is the agreed long-term store for indexing records. No model calls or vulnerability investigations are started by intake or indexing.

## Approved intake requirements

**S1-IN-R01 — Input forms.** Accept a local source directory or a remote Git repository URL. A local directory need not already be a Git repository. Clone a supplied Git URL into harness-managed storage. Do not modify the researcher's local directory or its Git state.

**S1-IN-R02 — Remote revision.** Permit an explicit branch, tag, or commit selection. Without one, select the default branch's current commit at intake. Record the resolved commit and use that fixed source version. Do not automatically pull a moving branch during indexing or investigation.

**S1-IN-R03 — Local working files.** Capture current on-disk files by default, including staged and unstaged edits and new untracked files, subject to the inclusion rules below. Deleted files remain absent. Do not silently substitute HEAD or the staging area's contents for the working files. Create the immutable snapshot in harness-managed storage.

**S1-IN-R04 — Submodules.** Do not fetch submodules by default. Provide an explicit opt-in. When fetched, use the revisions pinned by the selected parent commit, not the latest submodule branches. Report unfetched submodules as excluded and continue without repeated prompts. Do not claim their contents were indexed. Nested-submodule and populated-local-submodule details remain open below.

**S1-IN-R05 — Ignore rules.** Respect .gitignore for untracked files by default, with an explicit option to include ignored files. Keep tracked files even when they match an ignore pattern. Exclude Git metadata and harness-owned storage from the captured target. Report skipped paths and their reasons.

**S1-IN-R06 — No directory-name exclusions.** Do not add blanket exclusions for vendor, build, or generated directories. Apply the selected ignore policy, but do not infer irrelevance from a directory name. Including a file does not create an obligation for an LLM to review it.

**S1-IN-R07 — Snapshot consistency.** Structural indexing, applicable scanning, and source retrieval use the same captured immutable contents. Associate derived records with the snapshot and the relevant indexer/scanner/rule versions and configuration. Reuse compatible completed indexing across investigations rather than rescanning at each conversation start.

## Approved file treatment

**S1-IN-R08 — Treatment by file type.**

| File type | Required treatment |
|---|---|
| Supported source | Capture; extract the agreed structural records and references; apply applicable security-interest flagging. |
| Documentation, configuration, and other text | Capture and make searchable/retrievable without mandatory model summaries. |
| Binary | Capture and record metadata. Binary analysis is outside Stage 1. |
| Unsupported source | Preserve captured source and text retrieval where applicable; report the unsupported indexing capability. Do not claim structural extraction occurred. |
| Supported source that fails parsing | Preserve captured source and retrieval where applicable; report the parse failure. Do not substitute an empty successful symbol inventory. |

Exact language extractors, classification rules, scanner capability coverage, and their individual completion contracts will be specified with the researcher. A declared unsupported capability differs from a processing failure within a supported capability; do not relabel the latter to obtain success.

## Approved completeness requirements

**S1-IN-R09 — Full included scope.** Process every included file. Do not sample or skip required processing because a file is large, generated, or expensive. Selected exclusions define the scope; resource pressure does not change it. This requirement applies to scanner processing as well as structural indexing.

**S1-IN-R10 — Throughput and interruption.** Control concurrency and retain progress. Resource pressure may slow or pause work. Resume interrupted work rather than restarting the entire repository. Exact persistence boundaries and replay algorithms remain to be designed.

**S1-IN-R11 — Failure handling.** Retry recoverable failures. Persistent failures remain visible blockers rather than empty successes or endless automatic retry loops. Retry classification, limits, and recovery controls remain open; no numeric policy is selected here.

**S1-IN-R12 — Completion criterion.** Declare indexing complete only when every included file has received all required processing for its supported treatment, without outstanding processing failures. Captured source or a partially populated index does not by itself satisfy completion. Preserve diagnostics and declared capability limitations in the result.

An explicitly unresolved call target is a resolution result, not proof that the file was skipped. Conversely, a parser or scanner timeout is not a successful no-match result. Binary metadata completion does not claim binary analysis, and unsupported text retrieval does not claim language-semantic support.

## Derived acceptance scenarios

These scenarios make the approved behavior testable. They are not tests executed here and do not settle the open implementation mechanisms.

| ID | Scenario | Required observation |
|---|---|---|
| S1-IN-T01 | Supply unpacked source without Git metadata. | A managed snapshot is created; the input directory is unchanged. |
| S1-IN-T02 | Supply a Git URL with a selected revision, then move its branch. | Recorded and retrieved source stays at the resolved intake commit. |
| S1-IN-T03 | Supply tracked edits, different staged/working versions, an untracked file, and a deletion. | Capture eligible working-file bytes; omit the deleted file; preserve the input repository state. |
| S1-IN-T04 | Supply a remote with submodules and no opt-in. | No submodule fetch; exclusions are reported; no repeated prompt or false indexing claim. |
| S1-IN-T05 | Opt in to a submodule whose branch has advanced. | Capture its parent-pinned revision rather than the advanced branch tip. |
| S1-IN-T06 | Mix ignored untracked files and tracked files matching an ignore pattern. | Default excludes only the ignored untracked files; the override includes them; tracked files remain included. |
| S1-IN-T07 | Include vendor/build/generated directories that are not excluded by the selected policy. | Names alone do not remove those files from capture or required processing. |
| S1-IN-T08 | Include supported source, documentation, configuration, binary, and unsupported text. | Each receives the corresponding treatment, with no invented semantic coverage. |
| S1-IN-T09 | Reduce available processing resources or interrupt indexing. | Work slows/pauses and can resume; required files are not silently skipped. |
| S1-IN-T10 | Force a supported parser or applicable scanner to fail persistently. | Failure remains visible; the run does not report complete processing. |
| S1-IN-T11 | Process a call whose target cannot be resolved. | Keep its occurrence and explicit unresolved result; do not confuse it with an unprocessed file. |
| S1-IN-T12 | Start another investigation over the same snapshot and analysis configuration. | Reuse compatible completed indexing; a new conversation alone does not trigger rescanning. |

## Decisions still requiring discussion

- Symbolic links, external targets, and cycles.
- Local files changing during capture and the snapshot-consistency check.
- Nested submodules and existing populated submodules in local working directories.
- Authentication, Git LFS, and controls for safely cloning untrusted repositories.
- Exact ignore precedence, encoding/type classification, and retrieval behavior for non-text files.
- PostgreSQL records, intake/run states, durable progress, retry policy, CLI/API fields, and modular implementation ownership.

Do not silently choose these mechanisms while implementing the approved requirements. Complete this group's design and implementation steps collaboratively before assigning it as executable development work.
