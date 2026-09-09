# Implementation baseline and reuse map

Inspection date: 2026-09-09. This is a read-only source/metadata inspection, not a test run or certification of refactor equivalence.

## Observed references

| Repository / reference | Observed commit | Meaning |
|---|---|---|
| source-review-harness / codex/0.1.2-investigation-tool-recovery | `8b7ed0e335d4f4fb5ae53ef6e059334661279f20` | User-selected original behavior baseline; still present. |
| source-review-harness / codex/modular-refactor | `8f548f229dcac1c1d8aec2c5f8973353643ee99a` | Newly observed refactor branch; compare reports 36 commits ahead of original baseline. Not assumed deployed or approved. |
| source-review-harness / main | `de3bfa6cfff012f5d26cbab3c7c5a1dd0f22dd5a` | Observed branch metadata only, not selected automatically. |
| ssr-control / codex/controller-modular-refactor | `b7705ed35be54323fdf2a6d4a2ac8f2811d66745` | Observed branch and documentation tree; its code not fully re-audited. |
| ssr-control / main | `dfb5114beebe386756f62c4fda1ac0a340391f9f` | Observed branch metadata; installed release is unknown. |
| ssr-redesign / main | `017bde3f0c1f59a01ca9d8b11273f5000676a7be` | Last remote documentation checkpoint read during this task. Local approvals continued to F02 v0.16. |

Do not reset a developer's worktree to one of these commits. Read its AGENTS.md, status, selected ref, actual module map, and installed import paths. Reconcile changes and retain concurrent work. Feature behavior is a separately versioned change after structural extraction.

## Concrete reuse and integration

| Responsibility | Observed refactor owner / retained owner | Intended work |
|---|---|---|
| Source read/search result construction | `ssr.tooling.source_handlers`; `source_read_result` takes explicit dependencies and assigned-range callbacks | Replace assignment-based research restriction with P1-F01 policy, then extend source selection, search and paging. Do not bypass the verified reader. |
| Broker execution identity / read accounting | `ssr.tools` still owns BrokerScope and broker dispatch | Keep attempt/lease authority; split research permission from assignment and record only final delivered intervals. |
| Tool schemas / diagnostics | `ssr.tooling.contracts`, `ssr.tooling.diagnostics`, `ssr.tooling.types` | Version agent tools, preserve legacy surface, add actionable common outcomes and bounded normalization. |
| Metadata and result retrieval | `ssr.tooling.metadata_handlers`, `distributed_handlers`, `candidate_handlers` | Delegate to existing index/query and acceptance owners, not duplicate private-result visibility logic. |
| Source integrity | `ssr.source.SourceResolver`, `read_verified_file` | Preserve snapshot/classification/regular-file/hash/byte semantics. |
| Inventory and dependency graph | `ssr.indexing`, `ssr.symbol_graph`, symbol workflow | Reuse symbol IDs, conservative resolution and SCCs; dynamic contextual requests are additional work edges, not guessed call edges. |
| Runner and provider control | `ssr.agent`, `agent_policy`, `agent_prompts`, `agent_events`, `agent_types` | One loop with return-to-analysis, delivered-result evidence, notices and bounded grouped reads. |
| Worker recovery/finalization | `worker_guards`, `worker_finalization`, `worker_transcripts`, `worker_context_recovery` | Preserve original-attempt/successor isolation, independent transcript store and bounded recovery. |
| Public review planning | `ssr.application.review_planning`; public DTOs stay in `application.reviews` | Add collaborative prerequisite planning via explicit capability surfaces, reuse underlying admission. |
| Queries | `query.analysis_records`, `candidate_associations`, `review_outcomes`, `review_receipts` behind `ReviewQueryService` | Retain exact projection/visibility boundaries; add collaboration and availability projections. |
| Candidate / evidence / publication | existing `candidates`, `evidence`, `investigation`, `falsification`, `distributed_file_publication` | Retain single acceptance/final-gate owners. Extend producer paths and material-input revision binding. |
| Controller | public SDK integration; prior `controller.explorer`, `supervisor`, `child_dispatch`, job and admission owners | Locate refactored equivalents; never import harness private code or query harness DB directly. Parent-side child command interfaces must retain intended delayed engine imports. |

The refactor module map explicitly leaves some integrity-sensitive concentrations in place. Do not invent completed extractions or impose a new folder hierarchy just to match feature numbering.

## Baseline validation required before implementation

Read both repository specifications and AGENTS.md. Run and record existing source/tool, distributed publication, investigation-finalization race, SDK compatibility and affected controller tests. Verify unittest and pytest collection independently; unittest alone may miss pytest-style functions. New features must not be validated against an older installed wheel accidentally. Select the actual paired build before declaring compatibility.

No application suite, live provider call, wheel installation, 100-worker performance test, or migration was run in authoring this package. Failures discovered during implementation need baseline evidence before being called pre-existing.

See [SOURCES.md](SOURCES.md) for exact references.
