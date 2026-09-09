# Enforced context admission and continuation dossier

Contract: `context-policy-v1`. Resolves H04; owners P1-F04, P1-F05, P1-F09 and P6-F03. This is a host policy, not prompt advice or a claim about an installed model. The reference arithmetic and boundary tests are in `tools/contract_reference.py` and `tools/test_contract_hardening.py`.

## CB-R01 — Bind an effective route, not an advertised marketing limit

At review creation record the configured context ceiling, the provider's verified route ceiling, tokenizer/chat-template identity, protocol adapter digest, and maximum supported output tokens. At each dispatch revalidate that the route and counter identities still match. Set `E = min(configured_context_ceiling, verified_route_context_ceiling)`. The normal profile has configured ceiling **170000 tokens**; a smaller proven route lowers E. A larger route does not silently raise the configured ceiling.

`O = min(configured_output_reserve, verified_route_output_ceiling)`, default configured reserve **16384 tokens**. O covers the provider's total completion accounting, including hidden reasoning where charged against the context window. When the provider separates reasoning and visible output, their hard upper bounds must sum to at most O; a route whose reasoning contribution cannot be bounded is inadmissible. Never obtain extra input capacity by silently reducing O for an ordinary analysis request.

`M = 4096 tokens` is the default additional safety margin. Protocol/template overhead is counted in input, not assumed to be covered by M. `I_max = E - O - M` must be positive. For E=170000 and O=16384, **I_max=149520**. At creation reject a configuration whose mandatory instruction/schema/assignment envelope cannot fit I_max. The checkpoint-specific completion cap may be 4096, but retain O in admission arithmetic so checkpointing cannot enlarge an already-bound context contract.

## CB-R02 — Count the actual final request

Count the exact model-bound representation after protocol projection: system/developer instructions, role tool definitions and descriptions, current assignment and input token, dossier, full message history, structured tool-call arguments/results, notices, provider continuation fields and template delimiters. Bind `request_hash`, `token_count`, counter identity and E/O/M to a source-free dispatch receipt. A count of only text messages, only the dossier, or only model-visible prose is insufficient.

Use a pinned, locally supplied route tokenizer/template or a provider token-count interface whose result applies to these exact serialized inputs. A demonstrated conservative upper bound may be supported as a named capability with inequality tests against the route's exact counter; an arbitrary bytes/4 heuristic is prohibited. Unknown count returns `TOKEN_ACCOUNTING_UNAVAILABLE` before paid dispatch. This document's arithmetic tests assume a supplied correct count; they are not evidence that any specific gateway tokenizer is correct.

A transport adapter must assert that the counted and sent request identities match. No source/result/notice may be appended after counting. Changing tool schema, continuation state or route requires recomposition and recount. Pin maximum-output/reasoning controls in that same transport request. If the provider reports actual input tokens above the computed upper bound, stop admitting that route, retain real usage, and require counter recertification; do not keep using a known-underestimating counter.

## CB-R03 — Two thresholds, one hard gate

The soft checkpoint threshold is `T = floor(85 * I_max / 100)`: **127092 tokens** on the 170k profile. The hard gate is always `measured_input <= I_max`. A request at 149520 is admissible only if the soft-threshold control action has already selected the safe checkpoint/finalization path; ordinary research should checkpoint at T instead of running until the hard gate rejects it.

At the next safe model boundary, if ordinary assembled input exceeds T, schedule the ordinary checkpoint tool under a checkpoint-only capability projection. This is an existing work exchange, not a new manager agent. Finish or reconcile the prior tool group first. Reserve space before formatting the group's results: the response allowance is the minimum of tool byte limits, aggregate limits and the remaining measured input capacity. A result that cannot fit stays an explicit unreturned/paged result; do not credit its bytes as delivered.

The checkpoint-only exchange has output ceiling 4096 tokens and at most **2 attempts**. Both consume the actual cumulative work budget. If a valid latest checkpoint already covers all mandatory work updates and there are no unresolved tool effects, the host may directly enter the prescribed yield/settlement path without another summarization exchange. It cannot invent a checkpoint body from raw private model reasoning.

## CB-R04 — Deterministic reduction order

Before dropping anything, construct a preservation set: current system/policy instructions; role schema and input revision; active assignment/question; latest accepted checkpoint identity; currently unresolved hypotheses/counterevidence referenced by that checkpoint; mandatory input deltas not yet incorporated; and every incomplete tool-call/result group. These items cannot be evicted merely because they are large.

Remove optional material in this order, oldest complete group first within each class:

1. Repeated source previews or analysis/list pages already represented by a valid checkpoint and exact resolvable references.
2. Superseded complete lookup/listing exchanges and already-acknowledged optional freshness notices. Pending notices stay pending in durable bookkeeping.
3. Earlier fully settled tool/result groups whose decisions and unresolved consequences are preserved in the latest checkpoint.
4. Earlier ordinary assistant/user-analysis exchanges covered by that checkpoint, preserving the current task's externally supplied constraints in the dossier.

Keep each provider tool-call/result group intact. Do not leave orphan result IDs, remove only one call in a parallel group, or drop an uncommitted mutation to make room. Do not remove the current analytical contradiction solely because it conflicts with the latest hypothesis. The source/analysis remains reopenable; evicting its display does not revoke historical delivery receipts, and the next attempt still starts with empty delivery credit.

Recount after each reduction class. Do not repeatedly ask for a shorter summary when the irreducible tool schemas alone exceed the limit. At most two checkpoint attempts and three no-progress continuations apply. If the mandatory preservation set exceeds I_max, return `CONTEXT_LIMIT` with safe size breakdown and stop ordinary dispatch. Preserve the last valid checkpoint and real incomplete outcome; no synthetic terminal success.

## CB-R05 — Bounded restart dossier

The whole dossier is bounded by **8192 tokens and 32768 UTF-8 bytes**, whichever binds first. Its mandatory core is bounded by **4096 tokens and 16384 bytes** and contains task/type/assignment identities, policy/input token, current question, checkpoint identity, current candidate/request revision where applicable, and references to required material manifests. A root manifest reference substitutes for a large mechanically known subject/evidence list; it does not substitute for missing model analysis.

The remaining allowance contains the checkpoint's established observations, hypotheses, counterevidence, explicit unknowns, typed next action, newest required answer deltas and relevant pending-notice summary. Large reference sets remain paginated host records. At admission, select optional items in stable priority: material invalidations, answered blocking requests, explicit unresolved questions, then optional updates. Do not silently omit required material; a required item exceeding the core bound returns an actionable dossier-size blocker, or is represented through an already-defined exact paginated manifest.

The builder returns dossier bytes, token count, included-reference manifest, omitted optional count and mandatory-delta digest. Both limits apply to the final composed dossier, not individually to each section. Its input revision is bound to the actual delivered mandatory set under INPUT_REVISIONS.md. A new attempt gets no prior source-read credit. Opaque provider conversations are never treated as portable checkpoints.

## CB-R06 — Truncation and no-progress handling

An interrupted or `max_tokens`-truncated tool call is not valid JSON to repair by guessing missing fields. No domain operation or prefix publication can originate from it. Retain actual cost and the incomplete response; issue at most the remaining bounded repair/checkpoint exchanges after reducing the request or selecting a staged result interface. An unchanged oversized prompt is not a recovery action.

A no-progress continuation is one with no new accepted artifact/disposition, newly resolved dependency, newly delivered material source interval, or new supported analytical checkpoint content. A new attempt number, repeated cursor or differently worded identical hypothesis is not progress. Compare host-recorded deltas, not an agent-supplied `progress=true`. Three consecutive no-progress continuations produce a visible stopped/limited outcome; no hidden budget reset.

## Implementation sequence

Extend the actual `ssr.agent.runtime` request-composition path, `ssr.agent.policy` counting boundary and `ssr.context`/worker recovery dossier builder. Keep one dispatch gate used by ordinary work, repair, checkpointing, resumes and batched-tool follow-ups. Do not add a second provider client. Store the policy digest on immutable input revisions and runtime request events. Controller projections expose E/O/M, I_max, measured input, threshold, selected counter identity, and safe blockers without source text.

First test pure arithmetic/count binding. Then test the real serializer plus pinned route tokenizer. Finally instrument the transport stub to assert that zero calls are made after rejection. Keep strict byte-envelope tests independent. A 170k-context guarantee is released only after transport integration tests, not after the pure reference suite.

## Required acceptance cases

CB-T01: 170000/16384/4096 yields 149520 hard input and 127092 soft threshold. CB-T02: input 149521 and a constructed 365000-token prompt are rejected with zero dispatch. CB-T03: request exactly at hard boundary passes the hard comparison without exceeding E. CB-T04: 128k verified route lowers E. CB-T05: tool/schema overhead pushes an otherwise fitting history over the limit. CB-T06: notice insertion after counting changes request hash and forces recount. CB-T07: oversized mandatory core blocks rather than erasing instructions. CB-T08: orphan/incomplete tool groups cannot be evicted. CB-T09: completed source history is evicted before mandatory deltas. CB-T10: dossier exceeds tokens but not bytes, and vice versa. CB-T11: unknown tokenizer/reasoning limit denies dispatch. CB-T12: truncated tool JSON produces no lead/answer. CB-T13: checkpoint failure preserves old head and real budget. CB-T14: two failed checkpoint attempts and three no-progress resumes stop finitely. CB-T15: measured provider undercount disables the route. CB-T16: all response-page and batch paths use the same final gate.
