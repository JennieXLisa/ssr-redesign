# Processing, durable progress and recovery

Implements S1-IN-R09–R12/R21/R22 and S1-IX-R01–R05. PostgreSQL is both the progress store and lightweight work queue; no separate broker is introduced.

## Dataset planning and states

Capture is separate: CAPTURING, FINALIZING, READY, FAILED. Dataset states are PLANNED, RUNNING, PAUSED, FAILED, SUCCEEDED. Run states are PLANNED, RUNNING, PAUSED, FAILED, SUCCEEDED and reflect the selected datasets without rewriting their immutable references. A run is queryable in every state once its snapshot is READY and its applicability plan is query-ready as defined below. Source and valid published records remain accessible after processing failure.

Work-unit states are PENDING, RUNNING, FAILED, SUCCEEDED. A dependency-unready unit stays PENDING with an explicit prerequisite rather than being claimed and repeatedly failing. A failed unit can be explicitly retried; SUCCEEDED is terminal for the same semantic inputs. Step names are `extract`, `resolve`, `name_flags`, `semgrep_flags`, and `text_metadata`. Extraction, resolution and flagging coverage aggregate the appropriate components. Metadata completion is also required by whole-run completion even though it is not an additional field in the approved compact coverage object.

Plan the entire captured manifest first. Before exposing a query-ready run, complete resumable text_metadata/classification publications for every included file under the frozen extraction profile, then freeze the exact applicable file/component plan. The capture remains independently READY. A newly allocated but not yet query-ready run is observable through status; navigation returns INDEX_INITIALIZING, not misleading zero-total successful pages. Create only applicable work. For a supported source file create extraction; create resolution after identifying its applicable language behavior; name and Semgrep work depend on selected rules. Text/binary/unsupported treatment follows the manifest, not a worker's preference. Files with no reference occurrences complete resolution with a valid empty result after extraction. Empty custom-only selection is rejected before planning.

## Claim, heartbeat and fencing

Claim eligible PENDING work in one short transaction using SELECT FOR UPDATE SKIP LOCKED, ordered by dataset, file path and component. Assign a random lease token, increment the generation and attempt count, set RUNNING and an expiry 120 seconds ahead using the database clock. Commit before parsing or scanner execution. Workers heartbeat every 20 seconds by updating only a matching RUNNING row/token/generation. Parameters are configuration, not content limits. [S6]

A worker may publish only while its current token/generation still owns the row and the dataset accepts publication. Validate these conditions under the row lock in the publication transaction. Once a lease is expired/reclaimed, an old worker's output is rejected even if it finishes successfully. Use the same predicate for heartbeat and publication; process identity or a stale in-memory task object is insufficient.

Workers write staging publication rows and outputs outside the final row lock. These rows are not visible to ordinary navigation. Publish result manifest/counts plus SUCCEEDED marker atomically. If the final commit succeeds but the acknowledgment is lost, inspect the active publication and digest: the same committed digest is successful replay, not a second completion. Conflicting output for identical inputs is an integrity error.

## Recovery table

| Boundary | Recovery |
|---|---|
| Before claim commit | Work remains available; no owner is assumed. |
| After claim, before staging | Expiry/recovery returns it to PENDING; successor uses a new generation. |
| During staging batch writes | Incomplete publication stays invisible; successor may create its own staging set. |
| Before final publication transaction commits | No successful marker is visible. Retry/lease recovery cannot expose a half-result set. |
| After commit, before acknowledgment | Same publication/digest is recognized as already complete. |
| Old worker finishes after reclaim | Reject its stale generation; do not overwrite the successor's output. |
| Database unavailable | Stop making claims; retain process diagnostics, do not invent successful rows. Reconnect and reconcile lease/publication state. |
| Source object unavailable | Fail with STORAGE_INTEGRITY_ERROR; do not recapture or silently fetch a substitute. |

On startup, reconcile expired leases and finalizing captures through their owners. Recovery is idempotent. Do not kill unrelated processes based solely on a reused PID. A killed worker's process group is managed by the parent supervisor that created it; durable lease ownership determines whether results are accepted.

## Retry classification

Automatic retries are limited to three attempts total (the initial attempt and two retries) for transient database/network/I/O failures, with retry delays of 1 and 5 seconds. Record each error, next action and attempt number. Deterministic invalid source syntax, invalid rules, unsupported selected rule modes and configuration errors do not auto-retry. Out-of-memory/resource pressure pauses new claiming and exposes a resource diagnostic; resume after resources/settings are corrected. A changed semantic setting creates a different dataset fingerprint rather than relabeling old output.

An exhausted failure remains FAILED and blocks applicable completion. The researcher may explicitly retry a failed job/run after correction. Valid completed steps are retained. A Semgrep failure does not reparse source. A resolution failure does not rescan flags. Removing a problematic file from scope requires a new explicitly selected capture/scope, not a hidden retry tactic.

## Dataset barriers and publication

All required extraction work must succeed before final cross-file resolution starts. This is an inventory dependency, not a wave barrier between every file. Name/scanner jobs for supported source require that file's extraction publication; they do not wait for unrelated files. Raw scanner output produced earlier may be staged but not published with guessed owners. Extraction and eligible name/scanner work otherwise refill continuously up to the worker budget. After the inventory barrier, resolve files independently and publish their complete results. Compiler translation-unit observations are staged first and reconciled per physical source file before its resolution job succeeds.

Dataset completion takes a short dataset lock and verifies no required unfinished/failed work, no unresolved staging ownership, and a valid output manifest. The operation then changes RUNNING to SUCCEEDED. Writers check this state under compatible locking and cannot publish afterward. Do not derive completion solely from a cached count. Use a count query or maintained counters updated in the same publication transaction, with an audit query proving equivalence.

## Partial navigation and coverage

Within each navigation request, read visible records and coverage from one read-only transaction. Work-unit success means only that file/component completed. Incoming callers can still be incomplete while other files resolve. Counts show current failed files, not cumulative attempts. If one file has two failed flagging components, it counts once in `flagging.failed_files`. If one required flagging component succeeds and another is pending, the file is not completed.

Return compact run-wide coverage even when query filters narrow files. A raw source read can succeed while index_complete is false. Live result pagination requires refresh for records inserted before an earlier cursor position; source continuation replays remain fixed sections.

## Operational commands

Provide `ssr index create SNAPSHOT`, `ssr index run RUN`, `ssr index status RUN`, `ssr index pause RUN`, `ssr index resume RUN`, and `ssr index retry RUN --failed`. Creating a run validates/fixes its semantic inputs and plans work without changing source. Running/resuming launches the local pool. Pausing stops new claims and lets owned tasks finish/publish; an interrupted process is handled by leases. Retrying resets only eligible failed work and does not alter successful datasets.

Status and diagnostic listing are paged, with operation, file, component, attempt, last error and remediation. No background polling or automatic API/provider calls are necessary for the CLI. Human-requested processes can run until completion; the implementing agent must not claim a process completed merely because it was started.
