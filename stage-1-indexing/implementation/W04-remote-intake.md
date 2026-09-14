# W04 — Clone public HTTPS revisions and opted-in submodules

Depends on: W03. Owner: capture.remote and capture.submodules.

Requirement traceability: S1-IN-R01, S1-IN-R02, S1-IN-R04, S1-IN-R15, S1-IN-R17, S1-IN-R18, S1-IN-R19, S1-IN-R20.

## Read before editing

Read ../IMPLEMENTATION.md, the specification sections for this capability, and the directly related contracts. Reuse settled types/algorithms; do not restart a repository-wide architecture survey.

## Intended files and boundary

- `src/ssr/capture/remote.py`
- `src/ssr/capture/submodules.py`
- `tests/capture/test_remote.py`
- `tests/capture/test_submodules.py`

## Implementation recipe

1. Implement the public HTTPS URL parser and isolated Git process runner specified in capture.md. Pin public DNS addresses, verify TLS, reject credentials and redirects rather than invoking ambient login mechanisms.
2. Clone without checkout or submodule recursion; resolve the selected branch/tag/commit to a recorded OID. Read the selected tree/raw blobs and pass them to the same managed snapshot builder as local capture.
3. Without opt-in, report gitlink exclusions and perform no child-network requests. With opt-in, resolve each immediate parent pin and URL, fetch recursively and flatten only the requested captured source.
4. Handle relative repository URLs using Git repository-relative semantics; keep local populated submodule bytes authoritative. Missing local children use their immediate parent HEAD pin, never a branch-tip guess.
5. Detect LFS pointers without LFS downloads. Preserve an explicit exclusion even when a remote advertises credentials or a download URL.
6. Inject a fake HTTPS Git transport for deterministic tests and an optional documented public smoke test. Do not rely on a mutable public branch for the required CI acceptance suite.

## Verification commands

These are the required implementation commands/test targets; they are not claims that tests already exist or were run while writing this specification.

```sh
uv run pytest tests/capture/test_remote.py tests/capture/test_submodules.py tests/capture/test_transport_isolation.py
```

## Acceptance evidence

- Requested OIDs do not change when a remote branch later moves.
- Nested auth/protocol failures block opted-in capture and never trigger credentials.
- A recorder proves no LFS, opted-out submodule or external-link requests occurred.

## Stop condition and receipt

No private-repository workflow, provider-specific GitHub cloning API or remote-source execution.

Complete W04 only after its real entry-point/owner tests pass. Record implemented requirement IDs, changed files, actual command results, unrun checks and the commit in IMPLEMENTATION_RECEIPT.md. Commit/push when authorized; do not silently advance the next task or add another planning document.
