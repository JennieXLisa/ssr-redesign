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

**S1-IN-R04 — Submodules.** Do not fetch submodules by default. Provide an explicit opt-in. When fetched, use the revisions pinned by the selected parent commit, not the latest submodule branches. Report missing, unfetched submodules as excluded and continue without repeated prompts. Do not claim their contents were indexed. The opt-in includes nested submodules as specified in S1-IN-R15. Already populated local submodules are captured under S1-IN-R16 without requiring a fetch opt-in.

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

## Approved symbolic-link boundary

**S1-IN-R13 — Snapshot-only link resolution.** Preserve an included symbolic link as a link with its recorded target. Navigation may resolve it only to included contents within the same captured project's Git snapshot. Do not follow it into the host filesystem, another project, or uncaptured source; do not fetch or import a target merely because a link names it. A path inside the original working directory is not sufficient if its target was excluded from the snapshot. Index a captured target file once rather than creating duplicate file/symbol records through link aliases. Report external, broken, or excluded targets without claiming their contents were indexed.

A correctly recorded link whose target is outside the captured scope does not create a requirement to import that target or prevent completion by itself. Failures to capture or process an included record remain subject to S1-IN-R11 and S1-IN-R12. Resolution mechanics remain open below; they must preserve this boundary.

## Approved capture precondition

**S1-IN-R14 — Stable input during capture; snapshot-first processing.** The researcher keeps local source unchanged until snapshot creation finishes. State this precondition at intake and report when the immutable snapshot is complete. Structural indexing and applicable scanning start only after that completed snapshot exists. They and subsequent source retrieval use its captured contents, never the original working directory. Later changes to or removal of the original directory do not alter the snapshot or automatically trigger recapture or reindexing.

This is a researcher-supplied stability precondition, not a guarantee of atomic capture of a changing local directory. Do not add file watching or ongoing comparison with the working directory. Snapshot-finalization mechanics remain part of the implementation design; incomplete captures must not be presented as completed snapshots.

## Approved nested-submodule inclusion

**S1-IN-R15 — Recursive submodule opt-in.** Opting into submodule fetching also includes nested submodules recursively under the same opt-in. At each level, use the revision pinned by that submodule's immediate parent commit. Do not substitute the latest branch tip or request separate approval for each nested level. Without opt-in, fetch neither top-level nor nested submodules; retain the exclusion reporting required by S1-IN-R04.

This governs fetched submodules. Already populated local submodule working files follow S1-IN-R16 instead. Fetch/authentication failures remain explicit under the existing failure and completeness requirements; they must not be silently reported as successful full intake.

## Approved populated-local-submodule treatment

**S1-IN-R16 — Capture already-present submodule working files.** For local-directory input, include already populated submodules and their already populated nested submodules by default. Capture their current on-disk files, including staged/unstaged edits and eligible untracked files, using the same inclusion, ignore, Git-metadata exclusion, and stable-input rules as other local source. Preserve local deletions. A fetch opt-in is not required to capture source already present within the selected project.

Do not fetch, reset, update, or change an already populated submodule's checkout to match a parent-pinned revision. The local working-file rule takes precedence for that existing source. When submodules are missing, downloading them still requires the recursive fetch opt-in in S1-IN-R04 and S1-IN-R15; fetched revisions remain parent-pinned. Perform those downloads in harness-managed storage without populating or altering the researcher's checkout. Enabling fetching does not replace already-present working files with committed versions.

Without fetch opt-in, capture the already-present source, report missing submodules as excluded, and continue without repeated prompts or claims that absent contents were indexed. Snapshot-only symbolic-link restrictions continue to apply; local-submodule inclusion does not authorize following external source links. Exact storage representation and provenance fields remain part of the implementation design.

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
| S1-IN-T13 | Include a relative symbolic link to a captured source file and later change the working copy. | Preserve the link; navigation returns the captured target bytes; aliases do not duplicate target indexing. |
| S1-IN-T14 | Include a symbolic link to a file outside the project or in another project. | Preserve and report the link; do not read, capture, scan, or return the external target's contents. |
| S1-IN-T15 | Include a broken link or a link to a target excluded by the selected intake policy. | Report the absent/excluded target; no live-filesystem fallback, implicit inclusion, or false target-indexing claim. |
| S1-IN-T16 | Pause snapshot creation before finalization and observe processing dispatch. | No structural indexing or scanner processing starts before the snapshot is complete; the incomplete capture is not reported as a completed snapshot. |
| S1-IN-T17 | After successful local capture, edit or remove original files, then index, scan, and retrieve source. | All operations use the captured bytes without a live-directory fallback, ongoing comparison, or automatic reindexing. |
| S1-IN-T18 | Opt into fetching a remote with submodules nested at multiple levels and newer commits on their branches. | Include every nested level using its immediate parent's pinned revision, without separate prompts or branch-tip substitution. |
| S1-IN-T19 | Supply the same nested-submodule remote without opt-in. | Fetch no submodules at any level; report the excluded top-level submodule entries without inspecting unfetched descendants or claiming their contents were indexed. |
| S1-IN-T20 | Supply populated local submodules, including nested ones, with local edits, untracked/ignored files, and deletions; do not enable fetching. | Capture eligible current working files under the agreed ignore rules, not parent-pinned or staged-only contents; exclude Git metadata; perform no fetch or checkout mutation. |
| S1-IN-T21 | Supply a local project containing both populated and missing submodules without fetch opt-in. | Capture populated source; report missing submodules as excluded; perform no downloads, repeated prompts, or false indexing claims. |
| S1-IN-T22 | Enable recursive fetching for a local project with modified populated submodules and missing submodules. | Preserve populated working-file contents; fetch only missing submodules under S1-IN-R04/R15 into managed storage; leave the researcher's directories and Git state unchanged. |

## Decisions still requiring discussion

- Symbolic-link resolution mechanics, including chains/cycles and absolute-target handling within the approved snapshot-only boundary.
- Authentication, Git LFS, and controls for safely cloning untrusted repositories.
- Exact ignore precedence, encoding/type classification, and retrieval behavior for non-text files.
- PostgreSQL records, intake/run states, durable progress, retry policy, CLI/API fields, and modular implementation ownership.

Do not silently choose these mechanisms while implementing the approved requirements. Complete this group's design and implementation steps collaboratively before assigning it as executable development work.
