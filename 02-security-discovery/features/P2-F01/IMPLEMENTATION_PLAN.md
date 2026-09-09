# P2-F01 — Security-operation index: implementation plan

Updated: 2026-09-09. Design only; no scanner or target was run. Read the [feature](../P2-F01-security-operation-index.md), [operation catalogue](../../OPERATION_CATALOG.md), [baseline](../../../BASELINE.md), and [state contract](../../../contracts/STATE.md). Operation observations are navigable source facts with modeled semantics, not findings.

## Contract-hardening integration — Versioned callsite IR before operation modeling

Implement the optional callsite-ir-v1 adapter capability and strict CallsiteBatch schema before enabling operation-role extraction. At0989172 LanguageAdapter only provides generic symbols/relationships. Replace adapter.callsite_records with the typed capability wrapper: inject snapshot/file/hash, map existing symbol IDs, validate original ranges and required argument completeness, then persist one explicit IR generation/batch.

Use the inert Python pilot as the first contract fixture: subprocess aliases/from-import, local/parameter shadowing, dynamic shell flags, ** expansion, multiple calls, module-level null owner and UTF-8 offsets. An unsupported scope/language returns unknown/unsupported—not a false EXACT binding or clean operation scan. Only afterward derive registry observations from supported binding/role fields; other language families remain capability gaps until their own adapter fixtures pass.

Normative source: [hardening contract index](../../../CONTRACT_HARDENING.md). Preserve the existing feature procedure below except where this explicit correction replaces it; implement the linked exact schemas, not a local incompatible approximation.

## 1. Extend the existing inventory pipeline

Locate deterministic language adapters, normalized symbols/relationships, inventory diagnostics and existing security-tag persistence. Insert a derived operation-observation pass after a file's immutable inventory is complete. The pass consumes the same adapter representation and snapshot bytes; do not parse the repository again with a model or replace existing symbol IDs.

Keep indexing and operation-model versions separate. A parser-successful file can have incomplete operation-model coverage. Store that limitation rather than mark the entire file analyzed. An operation pass may complete incrementally per file without a repository-wide discovery barrier.

## 2. Registry entry contract

Represent each shipped operation model as inert validated data: model_id, version/hash, supported language/framework, canonical API binding or syntactic decision predicate, operation family, receiver/argument roles, option semantics and declared limitations. Hash the effective registry and bind it to the review configuration. Reject duplicate model identities and overlapping exact predicates without explicit precedence.

Argument roles refer to argument positions, keyword names or adapter-provided expression references. Do not store target source expressions or literal secrets in ordinary operation rows. Use source anchors and permitted structural constants/enums where the data policy allows them. The target cannot add executable model code or load a registry from its own repository.

Example model intent: Python subprocess.run has executable/argv, shell mode, cwd and environment roles. A POSIX fork model describes process creation and inherited-resource/lifecycle questions, not a shell command argument. A receiver method named execute has no database/process classification unless binding or declared framework modeling establishes it.

## 3. Resolve binding before assigning semantics

Use the adapter's lexical/import/scope information and recorded resolver decisions. For `import subprocess as ps; ps.call(...)`, classify through the imported module binding only when no intervening shadowing invalidates it. For a local variable also named ps or an unrelated execute method, record unresolved/ambiguous support rather than reuse a global name heuristic.

Do not evaluate target imports, decorators, plugins or configuration code to infer types. Dynamic dispatch, macro expansion or unsupported alias forms retain a precise limitation and source callsite. Text-name matches can be low-assurance discovery observations but must be labeled lexical, not resolved API calls.

```text
batch = host_callsite_capability.extract_verified(file_inventory)
for callsite in batch.calls:
    binding = callsite.binding
    candidates = registry.match(language, binding, callsite.structural_kind)
    for model in compatible_candidates(candidates):
        roles = model.select_typed_argument_roles(callsite.arguments)
        emit_observation(binding, roles, exact_source_anchor, limitations)
```

No confidence upgrade occurs merely because a local-name lookup returns one declaration. The observation retains extractor/resolver/model provenance independently.

## 4. Extract sensitive dimensions explicitly

Process operations: distinguish interpreted command text, executable selection, argv/option values, environment, working directory and source-visible privilege context. Record unknown dynamic shell mode as unknown, not false. Structured argv changes the shell-interpolation question but does not prove argument authorization.

Filesystem operations: record path/resource selector, content source, mode/overwrite semantics, link behavior, check/use relationship and source-visible downstream consumers. A fixed filename only constrains destination; it does not close content interpretation or object authorization. Reads can also produce data consumed by another sensitive operation.

Database/query operations: distinguish syntax fragments from bound values and record object/tenant selection independently. Network operations: separate destination/protocol, redirects and credentials. Memory operations: model lengths/units/signedness/lifetime roles rather than force them into a string-taint template. Security decisions may originate in control/state-transition patterns with no dangerous API.

Do not infer control effectiveness, exploitability or severity in the extractor. Those require the analyst workflow.

## 5. Observation identity and persistence

Use a deterministic derived identity over snapshot, existing subject, exact callsite/decision range, model identity/version and interpretation facet. Rerunning the same pass produces the same observation; a registry/producer change creates a new generation rather than rewriting previously used semantics.

Prepare and verify source anchors outside the short write transaction. Commit observations, explicit subject associations, producer/model digests and per-file scan disposition atomically for the completed file pass. On partial pass, retain named completion/limitation state; no complete claim before all applicable adapters settle. Do not create a candidate or worker for each observation.

Expose retrieval by existing subject, family, binding status and model generation through the current query owner. Add only the small association/index needed by these queries. No graph database or parallel source store is required.

## 6. Failure and regeneration

Parser failure means no deterministic claims for unavailable constructs, while permitted source remains inspectable. Unknown model family/framework becomes a support gap. Source hash mismatch is integrity failure; do not fall back to live bytes. Registry updates cannot silently reinterpret a running review or completed finding: a new generation is explicitly selected at new review/admission or through the versioned reuse policy.

On restart, query completed derived-pass identities and resume missing files. A failure after preparation but before commit is safe to rerun. Partial output cannot appear as a successful clean scan. If two hosts process the same file generation, uniqueness plus exact-field comparison yields one accepted observation set; inconsistent fields are an integrity error.

## 7. Fixture-based tests

Use inert fixtures for aliased subprocess, shadowed aliases, generic execute methods, shell true/false/dynamic, POSIX fork without exec, Node-style process launch, fixed-path variable-content writes, overwrite/delete/link cases, bound SQL values plus missing ownership, and a state/authorization decision without known sinks.

Assert operation family and each extracted role/reference, not just match count. Same source/model rerun preserves IDs; model-generation change does not overwrite old observations. Unsupported constructs produce limitations. No observation changes candidate maturity, canonical coverage or read-delivery credit. Supply malicious target registry/config/import code and verify it is never executed or loaded as authority.

## 8. Implementation sequence and exit

Add registry schema/version fixtures; implement one existing-language adapter end to end; wire per-file persistence/idempotency; add remaining supported family models incrementally; expose bounded retrieval; integrate P2-F02 ranking. Release evidence must list supported binding forms/families and unsupported cases, not claim universal recognition. Avoid a task per API match, magic-string vulnerability verdicts, target execution or an exhaustive homegrown static-analysis framework.
