# Stage 1 — Actionable navigation-tool errors

Status: approved behavior from the researcher discussion. This records the shared error requirements; it is not a frozen API schema, an implementation plan, or a test-results report.

Read with [source-retrieval.md](source-retrieval.md) and [indexing-progress.md](indexing-progress.md). These requirements apply to the approved navigation operations and their shared CLI/later model-tool interface. They do not introduce model calls, new source access, or automatic repair operations.

## Approved requirements

**S1-ER-R01 — One shared error contract.** Use a consistent structured error form across function lookup, function/file reading, continuations, content search, caller/callee lookup, outlines, and file discovery. Preserve the same error meaning through the shared owner and its CLI/later model adapters. Provide a stable machine-readable error code and a readable explanation; do not force callers to infer the failure category by parsing generic exception text.

**S1-ER-R02 — Identify where and what failed.** Identify the requested operation and the affected input field or nested field when the problem is an input error. Include the relevant location when known: for example a position within an invalid pattern, a requested source range, or the run/symbol/occurrence association that failed validation. Explain the specific problem and provide safe expected-versus-received details, such as allowed matching modes or valid bounds, when established. Distinguish input positions from source positions and state their units. For dependency, storage, or index failures, identify that failing stage or component instead of inventing a bad input field. Do not claim a root cause or location that has not been established.

**S1-ER-R03 — Explain how to proceed.** Supply a concrete correction or next action when known, not merely "invalid request" or "try again." Examples include correcting the identified pattern syntax, using an occurrence reference returned for the selected symbol/run, or selecting a range within reported bounds. Explain which input needs changing and which association must be retained. If the caller cannot fix the problem, identify the required researcher/operator diagnostic or repair action and say when the cause or remedy is not yet known. Do not instruct the model to invent IDs, repeatedly change valid inputs, disable validation, or recapture source to conceal an index/storage failure. Guidance does not authorize the tool to apply repairs or silently alter the request.

**S1-ER-R04 — Distinguish retries, corrections, and empty results.** State whether retrying the same request without changing its inputs is appropriate. Invalid patterns, mismatched identifiers, invalid continuations, and invalid ranges require correction rather than unchanged retries. A genuinely transient storage failure may be retryable; a missing captured object or inconsistent index requires an explicit storage/index diagnosis rather than being assumed transient. Explain any known prerequisite for retrying. This classification is not an endless retry policy.

A valid search with no matches is a successful empty result with the applicable coverage information, not an error. An incomplete index with no available matches is not proof of absence. Conversely, a failed query must not be turned into an empty successful result, and a failed read must not become fabricated source, a different occurrence, or a live-working-directory fallback. Existing partial-result and completion requirements remain in force.

**S1-ER-R05 — Useful detail without sensitive diagnostic dumps.** Give enough context to act on the failure without exposing credentials, connection secrets, unrelated captured source, or raw internal stack traces in ordinary responses. Keep stack traces in appropriate diagnostic logs with sensitive values protected. Redact supplied secrets rather than echoing them in messages, locations, or suggested corrections. Do not hide the actionable field, known constraint, or recovery direction merely to shorten the error. Keep diagnostics distinct from model-facing reasoning or target-provided instructions.

## Illustrative error

This example shows the required information, not a frozen field schema. The identifiers are illustrative.

```json
{
  "error": {
    "code": "OCCURRENCE_MISMATCH",
    "operation": "read_function",
    "field": "occurrence_id",
    "message": "The selected occurrence does not belong to symbol fn_42 in index run idx_12.",
    "remediation": "Use an occurrence_id returned with fn_42 in idx_12. Do not combine references from different search results or indexing runs.",
    "retryable": false
  }
}
```

The reader reports the invalid association; it does not select a replacement definition automatically. When a failure has no input location, the final schema must represent that honestly rather than fabricate one.

## Derived acceptance scenarios

These are required observations for future tests, not executed test results.

| ID | Scenario | Required observation |
|---|---|---|
| S1-ER-T01 | Submit an invalid pattern through an approved search operation. | Identify the operation, pattern field, parser-reported position when available, and specific problem; provide known correction guidance and indicate that unchanged retry will not help. Do not switch modes or return a successful empty result. |
| S1-ER-T02 | Read using an occurrence from a different symbol or indexing run. | Report the mismatched association and how to use matching returned references. Do not guess another ID, choose a different definition, or return unrelated source. |
| S1-ER-T03 | Request an invalid source range or provide an invalid continuation. | Identify the affected input and established range/association constraint, with usable correction guidance. Do not silently clamp, restart, or reinterpret the request. Preserve the previously agreed byte and source boundaries. |
| S1-ER-T04 | Compare a valid completed search with zero matches, an incomplete search with no available matches, and a transient PostgreSQL query failure. | Return successful results with distinct coverage for the searches; return an explicit retryable error for the established transient failure. Do not use an empty result to hide that failure. |
| S1-ER-T05 | Remove a required managed source object or create an inconsistent index reference in disposable test data. | Report the storage/index problem and the need for diagnosis or repair; do not blame valid caller inputs, assert an unverified cause, fall back to live files, or label the failure a successful read. |
| S1-ER-T06 | Exercise errors through the real CLI-to-owner path with secret-bearing input or dependency diagnostics. | Preserve code, failure location, explanation, recovery guidance, and retry semantics; do not expose secrets or raw stack traces. No separate CLI error policy or paid/model call is introduced. |

## Design details still to specify

- Exact response fields, types, nullability, closed error codes, location representation, and retry semantics in the API schema.
- Operation-to-error mappings, safe detail bounds, diagnostic correlation, and implementation ownership within the shared navigation boundary.

The required behavior is settled: explain where the failure occurred, what failed, and how to proceed based on available evidence. Unknown causes or remedies must remain explicit; a short generic error is not a substitute for actionable guidance.
