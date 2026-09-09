# Initial configuration and limits

Contract: collaborative-v1. These are selected initial engineering defaults, not benchmark-derived optima. Bind effective values, rule versions and tool-contract hashes to each new review. Existing role wall-time/token/provider limits remain authoritative and are not reset by pagination, yield, repair or a new checkpoint.

## Activation

`review.execution_mode = "collaborative-v1"` is explicit at review creation. Default remains the installed legacy mode until the paired release gate authorizes a default change. Never convert an active legacy review in place. Expose a dry-run effective policy before creating work. New capability absence is an error, not silent legacy behavior.

## Bounds

All counts are positive integers unless explicitly allowing zero. Unknown fields, NaN, bool-as-integer and overflow are rejected. The effective ceiling is the minimum of this feature's configured ceiling and the existing enclosing role/runtime/transport ceiling. No limit is multiplied because a request is batched.

| Setting | Initial value | Meaning |
|---|---:|---|
| navigation.page_items | 25 | Default metadata page; caller may request up to 100. |
| navigation.max_page_items | 100 | Applies before serializing results. |
| navigation.source_page_bytes | 16384 | Preferred returned source bytes per page. |
| navigation.max_source_page_bytes | 65536 | Still bounded by aggregate tool/context allowance. |
| navigation.max_cursor_bytes | 16384 | Encoded cursor; decoded payload capped at 12288. |
| navigation.max_pattern_bytes | 4096 | UTF-8 query length; NUL rejected, explicit newlines allowed. |
| navigation.search_matches | 25 | Default result occurrences per page; ceiling 100. |
| navigation.preview_bytes | 512 | Preferred original-source preview per occurrence. |
| navigation.search_file_bytes | 8388608 | Maximum file input for initial full-context matcher. |
| navigation.search_call_scan_bytes | 33554432 | Actual verified input examined per call; rescan work is charged. |
| navigation.search_call_files | 128 | Bound file count independently of bytes. |
| navigation.matcher_memory_bytes | 134217728 | Per matcher job limit; includes text/offset-map overhead. |
| navigation.matcher_deadline_seconds | 5 | Hard isolated matcher job timeout; not a target execution timeout. |
| navigation.matcher_parallelism | 2 | Host-wide bounded pool, not one child per analytical agent. |
| navigation.max_selected_file_ids | 64 | Larger scopes use manifest filters. |
| checkpoint.max_encoded_bytes | 65536 | Whole portable checkpoint state, further limited by the enclosing role. |
| tools.max_input_bytes | 65536 | Whole compact input envelope; field-count maxima do not multiply it. |
| navigation.batch_items | 8 | Independent read-like requests per batch. |
| freshness.interests_per_work | 256 | No silent eviction; caller may release irrelevant interests. |
| freshness.notice_items_per_turn | 8 | Combined with normal result/context budget. |
| freshness.events_per_interest_check | 128 | Bound examined event span; preserve continuation. |
| collaboration.open_requests_per_work | 8 | Count unresolved owned requests, not already joined consumers. |
| collaboration.max_dependency_depth | 8 | Host checks graph and returns a visible boundary outcome. |
| collaboration.request_revisions | 8 | Finite revision cap; no silent repeated speculative loops. |
| scheduling.coverage_every_n_dispatches | 4 | Every fourth opportunity for eligible canonical coverage when competing work exists. |
| scheduling.focused_backlog_per_worker | 2 | Optional seed inquiries capped at 2 × effective configured worker upper bound. |
| scheduling.max_no_progress_continuations | 3 | Requires host-observed progress delta, not a model's assertion. |
| scheduling.required_cost_samples | 5 | Minimum recent accepted attempts before empirical class estimate replaces configured estimate. |

The approximately 100-worker example is an operator-selected bound subject to all provider/shared-resource limits, not the default or a tested capacity claim. New focused/context roles inherit the corresponding investigation/review role profiles unless configured otherwise. Do not replace long-investigation limits with a short discovery quantum.

## Budgets and fairness

Maintain existing hard dimensions (tokens, provider concurrency, time and optionally money). Before admission reserve the actual next attempt's worst permitted provider-use envelope. Costs with missing provider usage remain unknown/estimated, not zero. A strict currency budget cannot be declared enforced without trustworthy pricing and usage; use known token bounds or explicitly reject that strict mode.

Canonical coverage reserve estimation uses recorded accepted class costs or an explicit configured startup estimate. Compute remaining required estimate separately from a guaranteed funding claim. Optional discovery is inadmissible when admitting it would consume the estimated remaining canonical work allowance; already required investigation/coverage may still run under hard limits, with any funding shortfall visible. The estimate is recomputed only from committed accounting and never releases live reservations. Report both estimate and hard remaining resources.

Request/lead recording remains available until its bounded proposal capacity is reached. A full execution pool queues valid leads; insufficient budget marks the independent task WAITING_FOR_BUDGET in its reason projection (not a new false success state). Do not suppress the record or preempt another worker.

## Cursor secret and lifecycle

Use a 32-byte cryptographic random project-local key; store only in `<private_project_data>/.host-secrets/cursor-key-v1.json` with private directory and file permissions/owner ACL. The JSON contains format version, generation, key_id and base64 key. Source text is never part of this file. Reject symlinks and insecure ownership/mode using existing safe-path helpers.

First provisioning occurs under the existing project coordinator lock: create a temporary private file exclusively, write/flush/fsync, atomically publish without overwriting an established key, fsync directory, then commit a source-free provisioning receipt containing key_id/generation (not the secret) in ssr.db. A crash after file creation can reconcile the exact private file and receipt. A receipt without the file is loss, not first initialization. Workers only load established keys. No ordinary read silently creates or rotates one.

No time-based expiry within a retained review; tokens still depend on current review access and supported contract/key generation. Explicit rotate/repair is an operator action under the coordinator with recorded reason and generation change, never implicit in a failed read. Keep one active key. Old-generation cursors and source convenience handles fail clearly; existing evidence coordinates and hashes remain resolvable, and authorized new reads can issue fresh handles. Repair does not reset knowledge, coverage, budgets or completed results. No key-management service or per-page key.

## Trusted optional dependencies

Select official `google-re2`, import name `re2`, from a pinned SSR-owned release artifact. Pin exact version/hash for each supported platform during the package build; this design does not claim a currently installed version. Missing capability returns MATCHER_UNAVAILABLE for regex and case-insensitive literal mode, never a fallback to Python backtracking regex. Plain case-sensitive literal mode remains available through standard-library exact search.

Semgrep adapter is optional and disabled until an operator provisions a pinned host-owned executable/rule bundle. No target-owned configuration, network rule download, metrics, dependency installation or target execution is allowed. Its absence does not block canonical coverage or host-first queries. Record tool/rule digest and scanned/skipped/error sets on every run.


The matcher must reserve and enforce total child memory including decode maps and native allocations. Use compact arrays or arithmetic for byte mapping, not an unbounded Python-object list per source character. Set the native compiled-regex memory budget to at most 16 MiB within the overall job bound; measure fixed child/runtime overhead during capability preflight. If a permitted file cannot fit the remaining memory, report a scan limitation rather than relying on host OOM recovery. These are initial bounds, not measured capacity guarantees.
