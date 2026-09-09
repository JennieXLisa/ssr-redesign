# P2-F03 — Conditional summaries and cross-boundary flow: implementation plan

Updated: 2026-09-09. Documentation only. Read the [feature](../P2-F03-conditional-summaries-and-flow.md), [artifact/acceptance state](../../../contracts/STATE.md) and [operation catalogue](../../OPERATION_CATALOG.md). A summary records conditional source-backed claims; it is not a global 'safe function' label.

## 1. Extend accepted function analysis, not a second knowledge store

Locate existing symbol documentation, parameter/return/side-effect fields, knowledge records and typed relationships. Add a versioned security-effect summary projection to accepted analysis. Its owner is the same result/knowledge acceptance path used for normal review. Store a backing result/artifact identity and exact subject/source/model digests rather than copying the whole function body.

A summary contains effects, parameter/return/state influence, guard/branch conditions, control properties, assumptions, counterevidence and unresolved edges. Each asserted relation has source/evidence references. Distinguish structural extractor information from model interpretation and from independent validation. Acceptance of the summary's provenance does not prove every conclusion.

## 2. Parameter and operation-role mapping

Use stable parameter identity within the indexed symbol plus positional/keyword role and corresponding source references. Map a parameter to an operation role such as executable selection, argument value, file destination, file contents, query structure or allocation length. Include branch/configuration conditions under which forwarding occurs.

For a wrapper that selects a fixed executable in branch A but accepts another selector in branch B, persist two conditional effects. A caller constrained to A may use that restriction; an unknown caller cannot inherit it. Do not union all branches into a single unconditional 'tainted' or 'sanitized' flag.

Summaries must say which property a control establishes: membership in an executable allowlist, bounded numeric length in bytes, object ownership for a principal, or query-value binding. Store subject, conditions, failure behavior and post-check transformations. A check that does not stop the operation on failure is not equivalent to an enforced barrier.

## 3. Caller consumption

When reviewing caller C of wrapper W, retrieve W's exact accepted summary artifact through P1-F02. Record its identity/hash and the particular conditional facets consumed. Reopen material source as required by the caller/investigation contract. Translate actual call arguments to W's parameter identities using recorded binding information; unresolved argument packing remains an unknown, not a guessed mapping.

```text
summary = get_exact_available_summary(wrapper_artifact)
for effect in summary.effects:
    mapping = bind_actual_arguments(callsite, summary.parameters)
    applicability = check_recorded_conditions(effect, caller_context)
    record_consumed_facet(effect.id, mapping, applicability, evidence_refs)
```

The analyst supplies semantic applicability judgments with references. Host code can validate identities/structure but must not certify control sufficiency from a function name. Unmet or unknown conditions produce explicit remaining questions. Never rewrite the original summary when one caller has a different interpretation.

## 4. Storage, messages and asynchronous channels

Represent producer/consumer observations using existing typed relationships and source-linked channel identity: resolved database entity/field, configuration key/object, queue/topic/message field, file resource mapping or IPC registration where established. Include operation direction, producer/consumer subjects, transforms, guard conditions and provenance.

Matching strings alone do not establish a channel. Two fields called `command` in unrelated tables are not one flow. Correlate only when source-visible storage/schema/connection identity is compatible. Otherwise create a bounded mapping question with both candidate endpoints. Do not silently connect channels across projects, snapshots or deployments.

A sink analyst can request writers for a resolved stored field, including create/update/import paths. A writer summary can expose a later consumer without requiring the current call graph to contain a direct call edge. The context-request router owns substantial missing interpretation; the query owner performs mechanical indexed lookups without another model.

## 5. Revision and invalidation

Key summary identity to snapshot, symbol range/hash, result contract, analysis artifact and policy/model versions. Exact source reuse across reviews still goes through the reuse owner and new review availability. A new interpretation is a new immutable artifact with supersession/disagreement links, not an UPDATE to old claims.

Record material consumption relationships from candidates/results to exact summary facets. When an accepted correction changes a consumed facet, P4-F03/P5-F03 assess applicability and invalidate current findings where required. A merely adjacent summary update cannot blindly invalidate every caller. Preserve negative assumptions/search domains supporting claims such as absence of a guard; later discovery may challenge them even when old cited spans are unchanged.

## 6. Recursion and bounded exploration

Use existing SCC/call-graph information for recursive functions, but do not implement an unbounded fixed-point taint engine. A summary may mark recursive behavior or unresolved lifecycle transfer explicitly. Repeated consultation of the same subject/artifact/input digest does not create another identical task. If new callers or state channels materially change the question, record a distinct request/revision.

Do not infer full program reachability from an operation summary. Runtime configuration, alternate paths and implicit framework behavior remain part of the investigation argument. A bounded unknown is preferable to a fabricated all-callers proof.

## 7. Persistence and query integration

Validate the summary's source-free payload, typed refs and producer receipt with the ordinary artifact owner. Insert summary/facet associations and accepted relationships in one domain publication transaction or its existing pending/available sequence. Query by exact subject/effect family/channel identity using indexes, not scans of free-text documentation. Summaries create no canonical coverage unless the entire underlying review-unit contract is complete and adopted by P4-F02.

Updates cannot modify immutable extractor edges. Keep model-authored channel/flow relationships in their attributable accepted relation namespace. Every reader sees provenance and resolution limits rather than a flattened graph of mixed certainty.

## 8. Tests and delivery

Use fixtures for one wrapper with safe branch A and unresolved branch B, two callers selecting different branches, query binding plus missing ownership, length checks in different units, asynchronous lifetime release, and a stored configuration field connecting a user-facing writer to a background process launch. Assertions inspect conditional facets, parameter mapping, consumed artifact IDs and unresolved channel states.

Create two same-named fields in different stores and ensure no false link. Correct a summary consumed by a candidate: preserve history and route only applicable material invalidation. Repeat summary publication to prove idempotent identity; use incomplete unit analysis to verify no coverage adoption.

Implement summary schema/projection first, caller/parameter mapping second, channel observations third, then revision/material-dependency integration. Keep the initial feature a reusable analysis representation and query capability, not a whole-program solver or a second knowledge graph service. Completion requires per-facet evidence/condition assertions and actual cross-file fixture traces.
