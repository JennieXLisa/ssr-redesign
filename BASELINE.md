# Verified baseline and implementation owners

Updated:2026-09-09. The Codex review baseline is harness **09891721b9d3509a3d618c7a25d3a3f184b0e225**. This is a pinned source baseline, not a claim about any installed/live process. The design repository before this hardening pass was009dd51; the exact working tree was obtained and verified at6460d32856e9c0afa26b3561a72f0b5b30b26ee2. Earlier baseline and validation records are preserved in history/pre-hardening-metadata.

## Observed facts and reuse map

| Responsibility | Verified source at0989172 | Consequence for the plan |
|---|---|---|
| Claim/admission | src/ssr/orchestration/service.py; contracts.py | PENDING claim terminalizes active agents; keep prepared yield RUNNING until settlement and change every claim path coherently |
| Task/agent states | src/ssr/orchestration/contracts.py | WAITING_DEPENDENCY/new task kinds are not existing enum support; implement full new matrix/migration |
| Agent loop | src/ssr/agent/runtime.py, events.py, policy.py, prompts.py, types.py | These are package modules; old agent.py/agent_events.py paths are not current owners |
| Tool broker and schemas | src/ssr/tools/broker.py, contracts.py, diagnostics.py, source_handlers.py, metadata_handlers.py, terminal_handlers.py | Broker retains authority; extend handlers without creating another tool/permission subsystem |
| Symbol workflow | broker imports ssr.symbol_review.submission and ssr.symbol_review.workflow | Preserve their canonical validators and original identities; do not prescribe obsolete flat module paths |
| Worker execution | src/ssr/worker/__init__.py exposes runtime.WorkflowWorker, guards, transcripts, types | Preserve exact-attempt supervision/finalization; verify internal finalizer signatures before integrating |
| Runtime receipts | src/ssr/runtime_receipt.py, contract1.0 | Current domain is completed graphs; runtime-prefix-v1/terminal2.0 are new explicit contracts |
| Transcript proof | src/ssr/transcript/receipt.py and reconciliation.py | Current completed capture requires terminal runtime receipt; add appendable prefix seals without forging completion |
| Schema owner | src/ssr/db/database.py, schema_contract.py, migrations/ | Admission checks migration history/FKs/canonical object fingerprints; rebuild all affected constraints/views safely |
| Language adapter | src/ssr/languages/base.py | InventoryResult has symbols/relationships/diagnostics; typed callsite/argument/binding capability is new work |
| Public application vocabulary | src/ssr/application/__init__.py | Reuse actual CommandContext, SSRConfig, SchedulingAdmissionToken; projects/reviews are packages, not assumed flat modules |

The earlier controller source observation was dfb5114beebe386756f62c4fda1ac0a340391f9f; it is a navigation aid only. This correction does not claim a fresh full controller audit. Codex must resolve the selected controller checkout and map its authenticated child dispatch/SDK signature checks to the new exact ABI before implementation. No live database or installed artifact was inspected or changed by this task.

## Concrete verification required before code

Read the selected implementation repository's AGENTS.md, actual schema ledger and module map. Record its source commit and any local edits. Compare the pinned behavior above with that checkout; where names moved, preserve the owning transaction and proof boundary rather than recreating old modules. Inventory all task/role/phase switches and canonical public DTO checks. Run the pre-change invariant regressions; old-runtime behavior itself is not a compatibility requirement for the new release.

New exact contracts live in contracts/ and generated schemas/reference declarations. Reference tests in this repository use no ssr imports and cannot certify production locks, transcript writes, actual migration resources or provider token counting. Those are the first implementation acceptance fixtures described in CODEX_HANDOFF.md and DELIVERY.md.

Permanent source URLs are in [SOURCES.md](SOURCES.md). All new helper/table names are selected contract names or logical ownership, not claims that they already exist in0989172.
