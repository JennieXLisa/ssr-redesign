# P1-F07 — Tool results and validation errors: implementation plan

Updated: 2026-09-09. Documentation only. Read the [feature](../P1-F07-tool-results-and-validation-errors.md) and [common envelope](../../../contracts/TOOLS.md). The objective is actionable information in the actual provider-bound response, not merely richer internal exceptions.

## Contract-hardening integration — Frozen error shape and proof-aware recovery

Use the closed Issue, IssueDetails and Error shapes in hardening-v1.schema.json, with exact repair_action and retry_kind enums. Details are typed safe expected/observed metadata; never forward an exception dict or source fragment. Normalize internal PREFIX_*/MANIFEST_* errors to the public INTEGRITY_FAILURE/RECEIPT_PENDING/STALE_INPUT codes while retaining actionable safe messages and exact field pointers.

Before effect validation, reject malformed/truncated arguments; after an effect commits, return COMMITTED with its original receipt even if later transport delivery is unknown. Distinguish yield preparation committed from continuation published and staged synthesis accepted from full file completed. Tests must inspect the final provider-facing projection, not just host logs.

Normative source: [hardening contract index](../../../CONTRACT_HARDENING.md). Preserve the existing feature procedure below except where this explicit correction replaces it; implement the linked exact schemas, not a local incompatible approximation.

## 1. Own diagnostics at the existing boundary

Map `ToolBrokerError`, `_validated_denial_context`, `_bounded_tool_error_value`, argument/evidence/link/falsification diagnostic constructors, `ToolExecution`, runner exception classification and SDK denial projections. In the inspected refactor the low-level diagnostic owner is `ssr.tools.diagnostics`; do not create another error formatter in every new tool.

Keep legacy exception identities and wire forms for legacy attempts. Add a collaborative projection from typed internal issues to the common envelope. Domain validators remain owners of semantic checks; the common layer owns safe representation, ordering, limits and recovery classification. Avoid a catch-all `except Exception: return empty_result`.

## 2. Validate in prerequisite stages

Use five explicit stages: payload framing/size; schema/field types; execution and subject authorization; immutable reference integrity; independent semantic facets. A later stage only runs when the prerequisites it requires succeeded.

Payload too large or undecodable: return a bounded framing issue without recursively exploring the body. Malformed top-level type: do not manufacture field-level errors for an object that does not exist. Stale lease, wrong review or unauthorized subject: stop protected inspection. Unresolvable evidence: report that reference and mark dependent source checks NOT_EVALUATED rather than alleging false hash/containment failures.

After safe prerequisites, collect independent issues in one response: missing field, invalid enum and a separately invalid range can coexist. Keep deterministic ordering by stage then JSON pointer/code. Include up to the contract's issue bound and an explicit omitted count; do not falsely imply the list is exhaustive when validation stopped early. Protected details use nondisclosing UNKNOWN_OR_UNAVAILABLE-style outcomes rather than reveal another review's IDs.

## 3. Map internal paths back to model inputs

P1-F03 normalizes compact inputs into larger domain objects. Carry a source-map from internal field paths to input JSON pointers while normalizing. A failure at an internally derived field must distinguish host inconsistency from agent error. Do not ask the model to fix a host-derived snapshot hash or lease token it cannot supply.

For each registered issue code define allowed detail fields, retry_kind, repair_action and safe message template. Permit concrete numeric bounds, supported enum choices, actual requested line numbers and authorized reference alternatives. Do not echo arbitrary SQL, exception repr, provider body, absolute host paths, credential-like text or source snippets through error details.

Example: a valid file has 96 readable lines and the request asks for 180–200. Return the affected input pointer, actual limit and valid range action. Do not merely say SOURCE_ACCESS_DENIED. An unknown protected file, however, must not reveal its true line count.

## 4. Separate result state, completeness and commitment

The common envelope has independent `status`, `completeness`, `page` and `effect`. `OK` does not imply a whole repository was examined; `PARTIAL` does not imply failure of every returned item; `COMMITTED` describes effects, not vulnerability validity.

Use NONE when no semantic effect occurred, PREPARED only with an actual recoverable prepared operation, COMMITTED only after the domain transaction, and UNKNOWN when the original outcome is not established. A source result can be useful while a scan is incomplete. A rejected input must not look committed. A read-like document lookup may have durable interest bookkeeping; expose its actual operation outcome rather than claiming it is a pure no-effect operation.

Keep missing analysis distinct from pending review, pending acceptance, failed review, unsupported result kind and unavailable visibility. An empty incoming relationship list cannot assert unreachability. No-match search must state examined scope/omissions. Catalogue metadata cannot imply source is readable.

## 5. Construct repair advice from executable capabilities

The error registry maps each recovery action to a tool/control operation actually exposed to that role. Before delivering a suggestion, verify the action is supported by the active contract. If no agent action can repair it, classify HOST_RECOVERY or NONE; do not tell the model to run an unavailable attach-evidence tool.

Use FIX_INPUT for malformed arguments, MORE_ANALYSIS for missing analytical material, RETRY_SAME_OPERATION for host-safe prepared retries, and HOST_RECOVERY/NONE for authority or infrastructure failures. REFRESH_INPUTS belongs in repair_action, not an invented retry_kind. Recovery never fills control effectiveness, reachability, severity or supported-finding flags automatically.

## 6. Enforce final byte bounds safely

Construct the full structured result, measure encoded UTF-8 JSON bytes, then reduce optional diagnostics/details in deterministic order. Preserve status, effect commitment, primary code, location and omission indicators. Never truncate inside a JSON string and return malformed output. Never drop `COMMITTED` or `OUTCOME_UNKNOWN` merely to fit a verbose message.

Reserve a minimal diagnostic envelope in normal result budgeting. If configuration cannot represent that envelope, reject configuration before worker admission. A runtime overflow uses the minimal valid safe outcome; it does not recursively invoke the same oversized formatter.

Keep detailed server diagnostics in their allowed internal channel while model-facing errors remain sanitized. Ordinary logs store codes, counters, IDs permitted by policy and hashes—not the raw input that caused rejection. Tool result content must survive provider-adapter conversion; verify both intermediate ToolExecution and final provider payload.

## 7. Tests that expose guessing failures

For each major tool family, supply one valid call and negative cases: wrong type, extra field, invalid enum, foreign subject, stale attempt, oversized page, unresolved reference and resource exhaustion. Assert exact code/location/retry/action/commit state, not only `is_error`.

Build a multi-issue fixture with a valid authorized container plus three independent field errors. Verify all appear within the cap. Build one broken reference with dependent validations and assert NOT_EVALUATED rather than three fabricated failures. Exceed the cap and check omitted_count. Ensure deterministic ordering across runs.

Use a sentinel credential, absolute host path and source fragment in thrown exceptions and invalid fields. Inspect model-bound JSON, ordinary audit/SDK payloads and logs; none may leak those sentinels. Verify legitimate authorized IDs and numeric repair bounds still survive sanitization.

Script a model receiving a validation result and executing the suggested tool/action. Confirm it is actually available and resolves the stated issue. Exercise response-budget trimming, committed-operation ACK recovery and unknown outcome; no result loses its commitment semantics. Repeat through every supported provider serialization path and legacy compatibility projection.

## 8. Delivery and non-goals

Implement the issue registry and staged collector; add normalization path mapping; integrate existing domain validators; test final provider projection and SDK denial views; then enable collaborative common envelopes. Do not move business validation into generic JSON middleware, infer semantic truth from schema validity, or introduce a diagnostic model. Runtime acceptance requires observed final-payload tests, not a dictionary of nicer messages alone.
