# Stage 1 — Source intake and processing completeness

Status: approved behavior recorded from the design discussion. Implementation details remain in discussion; this is not an implementation-ready plan or a test-results report.

This document covers one requirement group, not the whole indexing stage. SSR is being rebuilt from scratch. Archived implementations are references, not mandatory APIs, schemas, or workflows.

## Outcome

Capture the researcher's selected source in harness-managed immutable Git storage. Process every included file according to its type, preserving progress and explicitly reporting limitations. Resource pressure must not silently narrow the research scope or produce false completion.

Git retains source contents; PostgreSQL is the agreed long-term store for indexing records. No model calls or vulnerability investigations are started by intake or indexing.

## Approved intake requirements

**S1-IN-R01 — Input forms.** Accept a local source directory or a publicly accessible HTTPS Git repository URL under S1-IN-R17 and S1-IN-R19. A local directory need not already be a Git repository. Clone a supplied public HTTPS Git URL into harness-managed storage. Do not modify the researcher's local directory or its Git state.

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
| Unresolved Git LFS pointer | Log the affected path and skip the underlying LFS content under S1-IN-R18. Do not parse or scan the pointer as the actual source file. |

Exact language extractors, classification rules, scanner capability coverage, and their individual completion contracts will be specified with the researcher. A declared unsupported capability differs from a processing failure within a supported capability; do not relabel the latter to obtain success.

## Approved completeness requirements

**S1-IN-R09 — Full included scope.** Process every included file. Do not sample or skip required processing because a file is large, generated, or expensive. Selected exclusions define the scope; resource pressure does not change it. This requirement applies to scanner processing as well as structural indexing.

**S1-IN-R10 — Throughput and interruption.** Control concurrency and retain progress. Resource pressure may slow or pause work. Resume interrupted work rather than restarting the entire repository. Exact persistence boundaries and replay algorithms remain to be designed.

**S1-IN-R11 — Failure handling.** Retry recoverable failures. Persistent failures remain visible blockers rather than empty successes or endless automatic retry loops. Retry classification, limits, and recovery controls remain open; no numeric policy is selected here.

**S1-IN-R12 — Completion criterion.** Declare indexing complete only when every included file has received all required processing for its supported treatment, without outstanding processing failures. Captured source or a partially populated index does not by itself satisfy completion. Preserve diagnostics and declared capability limitations in the result. Explicit LFS exclusions under S1-IN-R18 do not block completion of the remaining scope, but must remain visible in the completion report.

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

Without fetch opt-in, capture the already-present source, report missing submodules as excluded, and continue without repeated prompts or claims that absent contents were indexed. Snapshot-only symbolic-link restrictions continue to apply; local-submodule inclusion does not authorize following external source links. The self-contained storage representation is specified in S1-IN-R20; exact provenance fields remain part of the implementation design.

## Approved remote-access scope

**S1-IN-R17 — Public, unauthenticated repositories only.** Remote Git intake supports repositories accessible without authentication. Do not implement private-repository login, credential collection/storage, or authenticated fallback. Do not request or silently use repository-access tokens, credential helpers, SSH identities, or existing authenticated sessions to make a fetch succeed. Supported URL forms are fixed by S1-IN-R19; transport-isolation mechanics remain to be specified.

The same public-access restriction applies to every opted-in submodule download, including nested and missing local submodules. An opted-in fetch that requires authentication is an explicit intake blocker, not permission to acquire credentials, silently omit the requested source, or report complete intake. Without submodule opt-in, preserve the already agreed exclusion behavior; do not probe excluded repositories for access. Report only what the fetch establishes: an inaccessible remote must not automatically be labeled private when its visibility is unknown. Never echo supplied secrets in diagnostics.

Local-directory capture and already-populated local submodule capture remain unchanged. Do not contact their remotes merely to verify public availability. This requirement restricts remote retrieval, not the researcher's ability to supply existing local source.

## Approved Git LFS exclusion

**S1-IN-R18 — Log and skip unresolved LFS content.** Do not download Git LFS objects or automatically replace LFS pointers with downloaded contents. Log each detected unresolved LFS path with an explicit LFS-skipped reason and continue, without prompting to enable LFS. Apply this rule to remote intake, local input, and included submodules. Do not parse, scan, or present pointer text as the underlying source file or claim that the missing content was indexed.

This is an explicit scope exclusion, not a processing failure or an intake/indexing blocker. Keep the excluded paths and reason visible in the intake and completion reports. It does not permit skipping ordinary large files. Actual file contents already present in a local working directory remain subject to the approved working-file capture and processing rules; no LFS download is needed or attempted for them. The immutable snapshot must not later be silently hydrated or otherwise changed.

## Approved remote transport

**S1-IN-R19 — HTTPS-only Git retrieval.** Accept public, unauthenticated HTTPS Git repository URLs from any Git host, not only GitHub. Reject SSH URLs and SCP-style Git addresses, plain HTTP, git://, file://, and other non-HTTPS remote forms with an actionable explanation. Do not silently rewrite the supplied transport or fall back to another protocol. Remote transfers must remain HTTPS; do not follow a redirect that downgrades to another protocol. Local directory paths continue to use working-file capture under S1-IN-R01/R03, not Git URL cloning.

For each opted-in submodule download, resolve a relative repository URL against its immediate parent's remote using Git's repository-relative URL semantics, then apply the same HTTPS-only and public-access requirements to the effective URL. Apply this at every nested level. If a required download has no acceptable HTTPS URL, report an intake blocker rather than silently skipping it, converting an SSH address to HTTPS, or claiming complete intake. Already-populated local submodules remain governed by S1-IN-R16; without fetch opt-in, do not contact excluded submodule remotes.

## Approved self-contained snapshot layout

**S1-IN-R20 — One managed repository per project; self-contained snapshots.** Use one harness-managed Git repository per SSR project. Each capture produces a separate snapshot commit identifying its immutable source tree. A later capture must not replace the source identified by an earlier snapshot. Keep the managed storage separate from the researcher's source directory.

Incorporate included submodule contents, including nested ones, as ordinary directories at their original project-relative paths inside that snapshot tree. Preserve file contents, modes, and symbolic links under the existing capture rules. Do not leave an included submodule represented only by a Git link that requires a separate repository to retrieve its files. Exclude nested Git metadata. Indexing, scanning, and source retrieval must be able to use the completed managed snapshot without the original checkout, source remote, or separately maintained submodule repositories.

Keep provenance separately in PostgreSQL: associate the snapshot ID with its managed Git commit, input source, capture options, submodule origins/revision information, and exclusions. Distinguish the managed snapshot commit from upstream repository commits. For populated local submodules, retain the fact that working files were captured; an observed local HEAD or parent-pinned revision must not be presented as proof that modified captured files equal that commit. Exact field types and the capture/publication transaction sequence remain to be specified.

This layout changes only the harness representation, not the researcher's repositories. Local working-file precedence, recursive fetch opt-in, public HTTPS restrictions, snapshot-only link resolution, and LFS/other explicit exclusions remain unchanged. Incorporating submodules does not import excluded content or authorize external link traversal.

## Approved lifecycle separation

**S1-IN-R21 — Separate snapshot capture from indexing.** Track snapshot-capture status separately from indexing-run status. A snapshot can be successfully captured while indexing has not started, is running, or has failed. Successful capture does not mean indexing is complete. An indexing failure or interruption must not change the identity, captured contents, or successful capture status of the completed snapshot.

Start structural indexing and applicable scanning only after the completed snapshot exists, as required by S1-IN-R14. Retrying or resuming indexing uses that same snapshot ID and managed Git commit, retaining compatible progress under S1-IN-R07/R10. Do not reclone, recapture, fetch newer source, or consult the original working directory merely because indexing failed. Report capture and indexing outcomes separately so the researcher can identify which operation needs attention.

This settles lifecycle separation and snapshot reuse, not the exact status enums, transition guards, database schema, or retry algorithm. Those mechanisms remain to be specified together. Indexing completion continues to require S1-IN-R12; separating status does not permit a partial index to be labeled complete.

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
| S1-IN-T23 | Supply a publicly accessible Git URL while repository credentials are also available in the host environment. | Fetch anonymously without invoking credential helpers or using authenticated sessions; preserve the selected revision and snapshot behavior. |
| S1-IN-T24 | Supply a remote requiring authentication, or opt into a required nested submodule download that requires it. | Report an explicit fetch/access blocker without credential prompts, authenticated fallback, secret disclosure, silent exclusion, or a complete-intake claim. |
| S1-IN-T25 | Supply existing local source whose configured remote is private or unreachable, with submodule fetching disabled. | Capture eligible local working files without contacting that remote or rejecting the local source because of remote visibility. |
| S1-IN-T26 | Supply a public remote and included submodules containing unresolved LFS pointers. | Perform no LFS downloads or automatic content replacement; log each affected path as excluded and continue without indexing pointer text as the underlying files. |
| S1-IN-T27 | Complete all required non-LFS processing with unresolved LFS pointers still present. | Permit completion of the remaining scope while retaining explicit LFS exclusions; do not claim the missing contents were captured or indexed. |
| S1-IN-T28 | Supply local working files containing both actual LFS-managed contents with local edits and unresolved LFS pointers. | Capture and process the actual eligible working contents unchanged; log and skip unresolved LFS content without downloading, overwriting local files, or later mutating the snapshot. |
| S1-IN-T29 | Supply public HTTPS Git remotes on different hosts, including a host other than GitHub. | Accept the transport without a GitHub-only restriction; clone anonymously at the selected revision. |
| S1-IN-T30 | Supply SSH/SCP-style, HTTP, git://, or file:// remote forms, or an HTTPS remote redirecting to HTTP. | Reject the unsupported transport or downgrade with an explanation; do not rewrite it, use a fallback protocol, or invoke credentials. Local directory capture remains available. |
| S1-IN-T31 | Opt into nested submodule downloads using relative URLs and an explicit non-HTTPS URL. | Resolve each relative URL against its immediate parent's remote and allow only effective public HTTPS URLs; reject the non-HTTPS required download as a blocker without silent omission or conversion. |
| S1-IN-T32 | Perform two captures with different working contents for the same SSR project. | Both snapshot commits reside in that project's managed Git repository; each snapshot retrieves its own captured contents without replacing the earlier snapshot. |
| S1-IN-T33 | Capture fetched submodules and nested submodules, then make the origin repositories and temporary clones unavailable. | Included contents remain accessible at their original project-relative paths using only the managed snapshot; no included path depends on a separate submodule repository. PostgreSQL retains the snapshot-commit association and submodule provenance. |
| S1-IN-T34 | Capture modified populated local submodules alongside excluded/missing source and unresolved LFS pointers. | Included working-file contents appear directly in the managed tree without nested Git metadata or changes to the input checkout. Provenance distinguishes captured working files from upstream revisions; existing exclusions and snapshot-only link restrictions remain in force. |
| S1-IN-T35 | Complete snapshot capture, then observe indexing before it starts, while running, and after an induced failure. | Capture remains successful with the same snapshot ID and commit; indexing has its own outcome. Neither capture success nor the partial index is reported as completed indexing. |
| S1-IN-T36 | After capture and partial indexing, interrupt processing and make the original directory or remote unavailable; then resume indexing. | Resume against the same managed snapshot and retain compatible progress, without cloning, recapturing, fetching, or reading the original source. Indexing completion still requires all remaining processing under S1-IN-R12. |

## Decisions still requiring discussion

- Symbolic-link resolution mechanics, including chains/cycles and absolute-target handling within the approved snapshot-only boundary.
- Isolation from ambient authentication and controls for safely cloning untrusted repositories, including URL validation and redirect enforcement. Remote protocol scope is settled by S1-IN-R19; private-repository authentication is outside scope under S1-IN-R17; LFS content retrieval is excluded under S1-IN-R18.
- Exact ignore precedence, encoding/type classification, and retrieval behavior for non-text files.
- Exact PostgreSQL records and provenance fields, snapshot finalization, capture/indexing status enums and transitions, durable progress, retry policy, CLI/API fields, and modular implementation ownership. The managed repository and included-submodule layout is settled by S1-IN-R20; capture/indexing lifecycle separation is settled by S1-IN-R21.

Do not silently choose these mechanisms while implementing the approved requirements. Complete this group's design and implementation steps collaboratively before assigning it as executable development work.
