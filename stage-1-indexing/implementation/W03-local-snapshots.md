# W03 — Capture local working files into immutable Git

Depends on: W02. Owner: capture.local, capture.git_store, capture.publication and source metadata.

Requirement traceability: S1-IN-R01, S1-IN-R03, S1-IN-R05, S1-IN-R06, S1-IN-R08, S1-IN-R13, S1-IN-R14, S1-IN-R16, S1-IN-R18, S1-IN-R20, S1-IN-R21.

## Read before editing

Read ../IMPLEMENTATION.md, the specification sections for this capability, and the directly related contracts. Reuse settled types/algorithms; do not restart a repository-wide architecture survey.

## Intended files and boundary

- `src/ssr/capture/local.py`
- `src/ssr/capture/git_store.py`
- `src/ssr/capture/publication.py`
- `src/ssr/source/encoding.py`
- `tests/capture/test_local.py`

## Implementation recipe

1. Enumerate source with lstat/rooted no-follow traversal. Separate source files, Git metadata, exclusions and link records. Read current working bytes including eligible untracked files; never substitute HEAD or staged bytes.
2. Implement isolated Gitignore evaluation for untracked files, preserving tracked files and the include-ignored override. Test vendor/build/generated paths with and without actual ignore rules.
3. Flatten populated local submodules/nested submodules using their working bytes and own ignore inventories. Preserve deletions and provenance; do not contact remotes or change their Git states.
4. Detect LFS pointers and record explicit skipped underlying content. Preserve materialized local content. Record binary/unsupported text metadata; keep all included raw bytes in Git.
5. Build raw blobs/trees with filters disabled; create one immutable snapshot ref and commit per capture. Persist FINALIZING manifest before ref publication and READY only after Git verification.
6. Implement capture recovery for a crash before objects, after tree/commit creation, after ref creation and before READY. A ref/content mismatch is an integrity error.
7. Store exact raw path identity, encoding/line metadata and snapshot-only link mapping. Change/remove the original directory and prove managed reads still resolve captured bytes.

## Verification commands

These are the required implementation commands/test targets; they are not claims that tests already exist or were run while writing this specification.

```sh
uv run pytest tests/capture/test_local.py tests/capture/test_publication.py tests/source/test_encoding.py
```

## Acceptance evidence

- Tracked/staged/working differences, ignored files, local submodule edits and deletions match the approved intake scenarios.
- External/broken/cyclic links never read outside the snapshot.
- No parser/scanner job is eligible until capture is READY.

## Stop condition and receipt

No remote fetching, source execution, file watchers or live-directory index updates.

Complete W03 only after its real entry-point/owner tests pass. Record implemented requirement IDs, changed files, actual command results, unrun checks and the commit in IMPLEMENTATION_RECEIPT.md. Commit/push when authorized; do not silently advance the next task or add another planning document.
