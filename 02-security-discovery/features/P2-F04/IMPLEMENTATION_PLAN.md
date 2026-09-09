# P2-F04 — Trusted analyzers and host-first answers: implementation plan

Updated: 2026-09-09. Documentation only; no analyzer or reviewed target was executed. Read the [feature](../P2-F04-trusted-analyzers.md), [configuration](../../../contracts/CONFIGURATION.md) and [state](../../../contracts/STATE.md).

## 1. Capability dispatch before model allocation

Introduce a small host capability registry above existing index/query services. Each entry declares supported question kind, required indexed inputs, output contract, producer identity/version, limitations and resource policy. A declaration lookup or exact stored binding query should execute through the index, not consume a model task. Control sufficiency, ownership or exploitability questions remain semantic unless a capability explicitly establishes that property.

Return one of supported deterministic answer, unsupported semantic question, incomplete analysis with limitations, or operational failure. Do not answer 'safe' because the mechanical query returned no edge. Unsupported mechanical analysis can be forwarded to contextual review with the original question and limitations; it must not masquerade as a completed answer.

## 2. Trusted executable adapter contract

For optional external analyzers, select only an operator-provisioned executable and SSR-owned rules/configuration by exact pinned artifact digest. The agent may request a registered capability with bounded source subjects; it cannot supply an executable path, arbitrary command, environment variables, shell fragment or remote rules URL.

The selected Semgrep integration is optional and remains disabled until provisioned. Verify executable/rule bundle identity before launch and record version/digest. An absent analyzer is a declared discovery limitation while canonical review continues. No implicit package installation, network rules download, target build or target import is allowed.

Use an argv vector built by the adapter, not a shell command string. Set a controlled working directory, explicit allowlisted environment and read-only snapshot view. Target-owned analyzer configurations, startup files, plugins and ignore policies are not execution authority. Scope comes from the manifest selection and SSR policy.

## 3. Resource and cancellation boundary

Run external tools in an isolated host job with bounded CPU/wall time, memory, file/output bytes and process count. Network access is disabled by the execution environment, not merely by omitting a CLI URL. Child credentials are absent. Use existing process supervision/cancellation utilities where suitable; do not expose this child process as a general shell tool to the model.

Reserve host analyzer capacity independently of analytical model slots but under global resource admission. A full analyzer pool produces queued/unavailable capability status, not unbounded process spawning. On timeout/cancellation terminate the exact child/process group, collect bounded status and release its reservation once. Do not kill unrelated workers or report a clean scan.

Snapshot selection must reject escaping symlinks/path substitutions. Temporary output belongs in an isolated host-owned directory, never the reviewed source tree. Cleanup only paths created by this job and retain governed diagnostic artifacts as configured.

## 4. Normalize outputs through verified source

Treat analyzer JSON/SARIF/text output as untrusted structured input. Bound total bytes, depth, item counts and diagnostic text before parsing. Resolve every reported path against the selected immutable snapshot, then validate line/column conventions and convert to original-byte coordinates through the source owner. Verify the file hash and range. A path outside selection is a rejected observation, not a scope extension.

Normalize rule ID, operation family, source references, analyzer confidence/kind, configuration assumptions and limitations. Keep analyzer-reported text separate from host-verified facts and apply ordinary source-free/credential guards before persistence. Do not copy snippets or raw output into ssr.db. Raw diagnostic artifacts, if retained, use their separately governed storage.

A scanner hit is an observation, not a candidate verdict. A missing hit is not canonical review completion. False positives remain inspectable observations with provenance. Model roles may consume accepted normalized results but must verify material source and controls themselves.

## 5. Producer provenance without fake agents

Artifacts use explicit producer variants: HOST_QUERY for an existing deterministic service and STATIC_ANALYZER for the pinned external adapter. Record actual capability ID/version, input selection/hash, tool/rule digest, invocation receipt, scope disposition and output hash. Do not fabricate an agent_run_id or transcript to satisfy model-only schemas.

The artifact acceptance owner validates the appropriate producer variant. Required model-turn receipts apply to model-authored artifacts, not mechanically to a host query. Conversely, a host query cannot use its producer type to assert an analytical conclusion outside its registered capability.

Persist normalized observations, per-file scanned/skipped/error status and producer receipt through the existing result/availability path. Idempotent rerun identity includes input snapshot/selection and analyzer/rule versions. A changed tool version creates new provenance, not silent replacement of accepted historical observations.

## 6. Completeness and recovery

Track selected files separately from files actually examined. Per-file unsupported language, size limits, parse errors and interrupted output remain visible. A truncated output stream prevents a complete-result claim even when the process exit code is zero. Nonzero exit codes distinguish expected analyzer findings from operational failure according to the pinned adapter's documented protocol; do not assume all nonzero values are equivalent.

A crash before normalized acceptance leaves an incomplete job that may be rerun under the same bounded identity. A crash after acceptance recovers the original artifact receipt. Re-running a tool does not create duplicate model investigations per hit: P2-F02 grouping and P1-F06 lead admission remain separate owners.

## 7. Tests

Use a fake deterministic analyzer executable under the host test harness, not target code, to emit valid output, foreign paths, malformed JSON, oversized diagnostics, partial streams, credential-shaped text and timeouts. Assert safe argv/environment, disabled target configuration, path/range verification, scope status and exactly-once reservation release.

Create a target fixture containing a malicious analyzer config or executable script with a sentinel side effect; verify the adapter never executes or adopts it. Test missing tool/rules artifacts and digest mismatch. A clean fake scan must leave canonical coverage unchanged. A supported binding query must cause zero model calls; unsupported authorization interpretation must explicitly escalate rather than invent a deterministic answer.

Use different producer variants to test schema acceptance and prove no fabricated model IDs. Repeat the same run to verify idempotent accepted observation identities, then change the rule digest to prove version separation.

## 8. Build and release sequence

Implement host-query capability declarations first; add producer-union contracts/fixtures; add an isolated adapter harness with fake executable tests; then integrate the actually pinned optional analyzer during separately authorized release preflight. Do not block basic canonical review or index queries on an optional tool installation. Completion requires capability-support documentation, isolation tests, normalized source assertions and real adapter artifact coordinates. No remote marketplace, plugin manager model or target execution framework belongs here.
