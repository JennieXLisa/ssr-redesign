# P8-F01 — Deterministic acceptance: implementation plan

Updated: 2026-09-09. This document specifies tests to implement; it does not report that application tests passed. Read the [feature](../P8-F01-deterministic-acceptance.md), [delivery slices](../../../DELIVERY.md), [STATE.md](../../../contracts/STATE.md) and every feature's detailed plan.

## 1. Create a requirement-to-test inventory

Retain the approved P1-F01/P1-F02 requirement/test ledgers and all feature-specific scenarios. Build a machine-readable mapping from requirement ID to owning feature, implementation symbol, test node ID, fixture, boundary exercised and status. New completion tests supplement earlier requirements rather than replace them with a smaller count.

Use explicit statuses NOT_IMPLEMENTED, NOT_RUN, PASSED, FAILED and BLOCKED_WITH_REASON. A collected-but-skipped test is not passed. Documentation links/schema checks are a separate category from application acceptance, provider conformance and quality evaluation. Do not use total file/test counts as proof of semantic coverage.

Before each slice run the relevant existing baseline tests against the exact authorized checkout and record collection. An observed failure is only called pre-existing when reproduced on the recorded baseline. Preserve meaningful assertions when refactoring test imports.

## 2. Shared disposable project fixture

Build an immutable synthetic source snapshot with a user-facing handler, command builder, process sink, ownership helper, file-write/delete paths, stored configuration writer/consumer, large multiline function, ambiguous/shadowed calls, recursive units, context-only config, parse-error file and excluded content. Include unrelated/no-hit units so early-finding success cannot hide incomplete systematic review.

Use actual snapshot/index/source services to create IDs, hashes, manifest dispositions and same-file dependencies. Do not hand-fill a newest database into an impossible state that production services cannot create. For historical migration tests, replay actual old migrations and period-correct fixtures.

The fixture source is inert review input. SSR's tests and fake host analyzers may execute in isolation; the reviewed target code, import hooks and embedded AGENTS/config instructions must not run. Store scorer/gold expectations outside model-visible source/dossiers.

## 3. Scripted backend and deterministic scheduling

Implement or reuse a fake BackendClient that returns predefined complete model messages/tool calls, chunked streams, malformed arguments, refusals, usage reports and injected failures. Assign real test exchange/request IDs through production recording paths. Do not bypass broker/domain validators by directly marking task states completed.

Use a fake clock and explicit synchronization barriers/hooks at named transaction boundaries instead of timing-sensitive sleeps. Scheduler decisions consume an explicit queue/config/control/resource snapshot. Model-slot tests run W=1,2,3 and 100 with zero network and record actual maximum concurrency in the simulation.

Provide failure hooks before/after preparation, domain commit, receipt seal/link, availability event, model-bound request record, response record, notice ACK, yield, wake, task claim and predecessor finalization. A hook must stop after the named durable boundary, not merely raise somewhere nearby and call it the same crash.

## 4. Mandatory end-to-end collaborative trace

Run this trace through public/application and real broker/task services:

1. Index the fixture and admit canonical reviews plus a focused sink inquiry without a repository-wide phase wait.
2. The inquiry reads source using an existing symbol ID, requests a queued component's contextual review and continues independent work.
3. It reports a separate source-grounded lead through the nonterminal tool. The harness records/queues the follow-up independently.
4. The inquiry checkpoints and yields on an unresolved registered request; its physical execution slot becomes available after safe settlement.
5. The reviewer receives the exact contextual delta, publishes a valid answer with its own turn receipt before full file completion, and continues canonical review.
6. The waiting inquiry wakes once, receives a new attempt/input token and reopens material source rather than inheriting read credit.
7. Investigation reaches a complete argument, a fresh falsifier challenges it, and host promotion produces a current finding while unrelated coverage is still running.
8. Later accepted counterevidence applies a validity hold and required reassessment; stale export/promotion is rejected. Canonical coverage eventually completes through real contribution checks.

Assert database identities/states and model-bound message contents at each point. A final screenshot or report is insufficient evidence that the intermediate behavior worked.

## 5. State invariants to assert after every injected interruption

At most one active lease per logical task; no duplicate semantic tool effect; every accepted result has the correct real producer/receipt chain; no current finding bypasses the shared exact-revision gate; no required canonical unit is satisfied by partial analysis; no source/read credit crosses attempts; no reservation release changes a successor's ownership; no required obligation is lost by closure or routing races.

For each operation classify the expected crash outcome as no committed effect, pending recoverable effect, or committed immutable receipt. Restart the coordinator and replay reconciliation twice. Assert idempotence, exact effect IDs and visible blockers rather than merely absence of exceptions.

Run both orders for lookup/publication, answer/yield, route/producer-completion, adoption/claim, challenge/promotion and challenge/export-registration. Concurrent reciprocal dependency insertions must not both pass. An old finalizer must leave captured successor fields unchanged.

## 6. Navigation and payload correctness suite

For source pages compare concatenated actual original bytes with the selected range, including UTF-8/multibyte/CRLF/long-line cases. Inspect final provider payload after trimming: only retained source receives delivery descriptors. Requesting a last page does not prove earlier pages were consumed.

For search compare ordered occurrence tuples across page sizes 1,7,25 and explicit multiline/anchor/zero-length/pending-match fixtures. Vary preview allowance without changing occurrence enumeration. Decode/memory/time omissions keep completeness false. Invalid query/matcher/selection cursors cannot silently restart or widen scope.

For metadata/query tests include duplicate names, direct-parent semantics, directory prefix collisions, repeated relationship callsites, unresolved incoming spelling matches, exact D18 retrieval after D19 publication and H-bounded lists across withdrawal/restoration. Verify source-research access does not expose private artifact bodies.

## 7. Security and contract negative suite

Use unique sentinels for credentials, source snippets, cursor secrets, absolute host paths and raw provider data. Inspect ordinary state/logs/errors/SDK projections after every new write/read path. With governed sensitive capture enabled, verify exact permitted captured bytes remain intact in the separate store while transport secrets remain absent.

Test unknown fields/discriminators, boolean integers, stale input tokens, wrong review/snapshot refs, forged cursor tags, unsupported provider schema projection and unavailable capability. Multi-error fixtures must produce independent actionable issues while protected/dependent checks stop safely. Execute the suggested recovery action in scripted conversations to prove it exists for that role.

Target-owned instructions/configurations are untrusted data. A synthetic malicious analyzer config/import must never execute. A fake analyzer emits foreign paths/oversized output to exercise normalization/isolation.

## 8. Public and package verification

Run tests through installed wheel/sdist imports in clean temporary environments, not only editable source. Inspect module origins and DTO identity. Include all four supported legacy harness/controller pairs and new/new collaborative negotiation. Parent child-wire parsing must not import the engine prematurely.

Frontend tests must assert request counts and stale-response isolation: collapsed historical attempts do not fetch capture history, changing reviews ignores late old responses, stream reconnect refreshes authority, and new notices do not auto-download source. Verify built assets and hash manifests are actually included in the controller package.

## 9. Evidence artifacts and acceptance gate

For each run record source commit, dependency lock/artifact digests, schema horizon, effective config/capability versions, collected test IDs, command, exit status, skipped/blocked reasons, deterministic seed/clock schedule and resulting trace hash. Store synthetic trace artifacts outside ordinary production state. Do not embed real secrets into published test reports.

A slice passes only when all of its required runtime and compatibility tests pass or an explicitly documented optional capability remains disabled. A blocked mandatory producer receipt/claim/closure path cannot be waived by a green JSON Schema fixture. Full application acceptance requires the integrated trace plus failure matrix, not only unit tests of pure helpers.

## 10. Implementation order and non-goals

Build shared fixtures and failure hooks first, then add each feature's tests with its implementation commit. Add end-to-end traces early enough to catch inconsistent contracts before final release. Keep the documentation validator for structural checks and report its limits honestly.

No real provider spend is needed for deterministic acceptance. Real throughput, finding quality and cost savings belong to P8-F02, not claims derived from fake workers. Do not weaken old regressions, mark uncollected files tested, execute reviewed targets or call simulation performance a 100-worker production benchmark.
