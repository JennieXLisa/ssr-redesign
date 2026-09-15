# W06 — Plan, claim, publish and resume file-step work

Depends on: W02, W05. Owner: indexing planner, worker supervisor, leases and publication.

Requirement traceability: S1-IX-R01, S1-IX-R02, S1-IX-R03, S1-IX-R04, S1-IX-R05, S1-IN-R09, S1-IN-R10, S1-IN-R11, S1-IN-R12, S1-IN-R21, S1-IN-R22.

## Read before editing

Read ../IMPLEMENTATION.md, the specification sections for this capability, and the directly related contracts. Reuse settled types/algorithms; do not restart a repository-wide architecture survey.

## Intended files and boundary

- `src/ssr/indexing/planner.py`
- `src/ssr/indexing/worker.py`
- `src/ssr/indexing/leases.py`
- `src/ssr/indexing/publication.py`
- `tests/indexing/`

## Implementation recipe

1. Implement immutable run→dataset composition and per-file/component planning. Complete resumable, extraction-profile-specific file_metadata preparation, then freeze the applicability plan and expose query_ready; never change shared snapshot classification when a new run overrides language/encoding. Use fake deterministic processors only as fixtures, not a substitute for later real adapter gates.
2. Claim eligible work with SKIP LOCKED in a short transaction, generation fencing and database-clock lease expiry. Heartbeats require matching ownership and cannot resurrect an old generation.
3. Write staging publications in bounded batches; validate the complete output manifest and atomically activate it with the file-step success marker. Join visible publication state in every read.
4. Implement execution.md's exact HOLD/RUN/PAUSE intent policy, separate dataset state precedence, retry-cycle versus lifetime attempts, and dataset→run→work→publication lock order. Test A/B shared-dataset pause, all-consumers pause/drain, retry while paused, expiry while paused, and completion/publication races. Preserve successful components on every retry path; pausing A must not stop B.
5. Enforce extraction-inventory readiness before final reference resolution. Continue refilling independent extraction/flagging jobs without introducing whole-repo review waves.
6. Implement dataset/run completion audits, run-wide coverage and current-failure counts. Block completion while any required metadata/component job remains failed or unfinished.
7. Test lease expiry, stale predecessor, duplicate acknowledgment and crash boundaries using real PostgreSQL transactions and process barriers.

## Verification commands

These are the required implementation commands/test targets; they are not claims that tests already exist or were run while writing this specification.

```sh
uv run pytest tests/indexing tests/storage/test_publication_visibility.py
```

## Acceptance evidence

- Only the current fenced worker can make output visible.
- Lost acknowledgment reuses one publication and does not double-count completion.
- A scanner-component failure leaves successful extraction intact.

## Stop condition and receipt

No distributed broker, cross-project priority system, task-by-vulnerability workflow or agent runtime.

Complete W06 only after its real entry-point/owner tests pass. Record implemented requirement IDs, changed files, actual command results, unrun checks and the commit in IMPLEMENTATION_RECEIPT.md. Commit/push when authorized; do not silently advance the next task or add another planning document.
