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

Automatic retries default to three attempts per explicit retry cycle (the initial attempt and two retries) for transient database/network/I/O failures, with retry delays of 1 and 5 seconds. The strict settings schema permits an explicitly configured attempt/delay sequence; lifetime attempt history is never reset. Record each error, next action and attempt number. Deterministic invalid source syntax, invalid rules, unsupported selected rule modes and configuration errors do not auto-retry. Out-of-memory/resource pressure pauses new claiming and exposes a resource diagnostic; resume after resources/settings are corrected. A changed semantic setting creates a different dataset fingerprint rather than relabeling old output.

An exhausted failure remains FAILED and blocks applicable completion. The researcher may explicitly retry a failed job/run after correction. Valid completed steps are retained. A Semgrep failure does not reparse source. A resolution failure does not rescan flags. Removing a problematic file from scope requires a new explicitly selected capture/scope, not a hidden retry tactic.

## Dataset barriers and publication

All required extraction work must succeed before final cross-file resolution starts. This is an inventory dependency, not a wave barrier between every file. Name/scanner jobs for supported source require that file's extraction publication; they do not wait for unrelated files. Raw scanner output produced earlier may be staged but not published with guessed owners. Extraction and eligible name/scanner work otherwise refill continuously up to the worker budget. After the inventory barrier, resolve files independently and publish their complete results. Compiler translation-unit observations are staged first and reconciled per physical source file before its resolution job succeeds.

Dataset completion takes the dataset lock under the common order below and verifies the frozen plan against actual work, no required unfinished/failed work, no current-generation staging ownership, and a valid output manifest. It changes any nonterminal dataset state to SUCCEEDED (including an empty or drained paused dataset). Writers check the same state while holding that lock and cannot publish afterward. Abandoned older-generation staging does not block completion; it remains invisible and separately collectible. Do not derive completion solely from a cached count. Use a count query or maintained counters updated in the same publication transaction, with an audit query proving equivalence.

## Partial navigation and coverage

Within each navigation request, read visible records and coverage from one read-only transaction. Work-unit success means only that file/component completed. Incoming callers can still be incomplete while other files resolve. Counts show current failed files, not cumulative attempts. If one file has two failed flagging components, it counts once in `flagging.failed_files`. If one required flagging component succeeds and another is pending, the file is not completed.

Return compact run-wide coverage even when query filters narrow files. A raw source read can succeed while index_complete is false. Live result pagination requires refresh for records inserted before an earlier cursor position; source continuation replays remain fixed sections.

## Operational commands

Provide `ssr index create SNAPSHOT`, `ssr index run RUN`, `ssr index status RUN`, `ssr index pause RUN`, `ssr index resume RUN`, and `ssr index retry RUN --failed`. Creating a run validates/fixes its semantic inputs and plans work without changing source. Running/resuming launches the local pool. Pausing stops new claims and lets owned tasks finish/publish; an interrupted process is handled by leases. Retrying resets only eligible failed work and does not alter successful datasets.

Status and diagnostic listing are paged, with operation, file, component, attempt, last error and remediation. No background polling or automatic API/provider calls are necessary for the CLI. Human-requested processes can run until completion; the implementing agent must not claim a process completed merely because it was started.

## Shared-run control: intent is not dataset state

`index_runs.control_intent` is durable and has three values: HOLD on create, RUN after run/resume, PAUSE after pause. It is independent of the reported aggregate state. A dataset has demand exactly when **at least one referencing run has RUN intent**, including runs whose aggregate state currently reports a failure in another component. A pool launched for a run claims only its selected datasets and rechecks that launching run's RUN intent; another pool can continue the same shared work. Exiting/crashing a pool does not change durable intent or successful publications.

| Operation/event | Required effect and guard |
|---|---|
| create | Freeze dataset references and set HOLD. Reused SUCCEEDED datasets are never reset. |
| run / resume | Set only the selected run's intent to RUN and start its local pool. Do not reset failed work. Calling on a complete run is a successful no-op. |
| pause A | Set only A's intent to PAUSE. A's pool stops admission; existing leases remain valid and can heartbeat/publish. No shared work row is cancelled, failed, or reset. |
| A and B share unfinished extraction; A paused, B RUN | B continues claiming and publishing. A remains queryable and its coverage may grow; pause is not a snapshot of derived progress. |
| last RUN consumer paused | Stop new claims. Drain owned work; dataset may remain RUNNING while draining and becomes PAUSED when idle, unless failure/success has higher precedence. |
| retry A --failed | Reset only FAILED rows in A's selected datasets whose semantic inputs are unchanged. Preserve lifetime attempt_count/generation, reset retry-cycle count, clear error/next-attempt/lease fields, leave committed successes untouched. Intent is unchanged: retry on PAUSE does not implicitly resume. Shared consumers observe the same reset; no duplicate dataset is created. |
| expired lease | Under the common locks, invalidate ownership and return eligible work to PENDING or FAILED according to retry exhaustion. Reclaim even if all consumers are paused; never admit its replacement without RUN demand. |
| all required work succeeds | Audit and mark dataset SUCCEEDED regardless of consumer intent. Success is terminal. A paused run whose three datasets finish reports SUCCEEDED, with control_intent still PAUSE in storage. |

Dataset state precedence, recomputed inside the owner transaction: audited frozen complete plan → SUCCEEDED; any live RUNNING work → RUNNING; any FAILED work → FAILED; RUN demand → RUNNING (possibly waiting on a prerequisite); no RUN demand after any attempt → PAUSED; otherwise PLANNED. FAILED is an aggregate observation, not a prohibition on processing independent PENDING work. Admission requires demand, a non-SUCCEEDED dataset, PENDING work, satisfied prerequisites, due retry time and resource availability. An exhausted failed file still blocks final success and dependencies that require its output.

Run status precedence: all selected datasets audited SUCCEEDED → SUCCEEDED; PAUSE intent → PAUSED; HOLD → PLANNED; any selected dataset FAILED → FAILED; otherwise RUNNING. `index_complete` derives from actual completion, never just intent. Cached state columns must be reconciled before returning status; they are not admission authorities. `query_ready` is true only when all selected plans are frozen and their selected extraction metadata is visible. Navigation remains partial and readable after failure/pause.

## Common lock order and exact mutation guards

Every mutation that needs more than one level acquires **datasets (UUID byte order) → index_runs (UUID byte order) → work_units (work_id order) → publications (publication_id order)**. Omit unused levels; never acquire an earlier level later. Plan insertion, run creation/control, retry, lease recovery, final publication and completion use this order. Staging inserts are separate transactions that never subsequently acquire dataset locks or activate results. No transaction retains locks across parsing, Git, compiler/scanner work or user interaction.

Claim first chooses candidate dataset IDs without locks, acquires one dataset `FOR UPDATE SKIP LOCKED`, rechecks launching-run intent/demand, then selects eligible work `FOR UPDATE SKIP LOCKED` ordered by original path bytes, component and work_id. A multiple-row retry first locks every involved dataset in sorted order, then the run, then sorted work rows. Run references are immutable so pause may read their IDs before locking and revalidate the run after acquiring them. New run attachment also locks its datasets before inserting the run; this prevents a phantom consumer racing a last-consumer pause.

Heartbeat/publication predicates are: dataset not SUCCEEDED, work.state=RUNNING, exact token and generation, and `lease_expires_at > clock_timestamp()`. A paused consumer is **not** a reason to reject an otherwise current lease. Heartbeat sets a new database-clock expiry; it cannot extend an already expired lease. Final publication locks dataset then work then its staging publication, repeats those predicates, validates bundle/manifest/snapshot references, and activates output atomically. Replay of an already SUCCEEDED work item is read-only success only when the committed generation/publication/digest matches the submitted result; a different digest is NONDETERMINISTIC_OUTPUT. No state transition rewrites a SUCCEEDED work item.

The first claim and automatic retries increment both lifetime attempt_count and retry_cycle_attempt_count. Automatic attempts in one explicit retry cycle are bounded by max_attempts (default three); explicit retry resets only retry_cycle_attempt_count. This prevents losing historical diagnostics or treating a manually retried exhausted job as permanently ineligible.

Required real-PostgreSQL schedules: A/B shared demand with pause/resume in both orders; pause between claim and publish; all consumers paused then lease expiry; completion racing final publication; retry racing an old worker; and two concurrent last-consumer controls taking overlapping datasets in reversed input order. Use barriers and a bounded test timeout to prove no deadlock, stale publication, duplicate success or premature completion. Pure state-policy tests are a decision oracle, not that concurrency evidence.
