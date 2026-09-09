# H0 — Contract-hardening correction and handoff

Revision:2 ·2026-09-09. **Status: design contracts specified and executable reference checks supplied; ready for Codex implementation against these contracts, not runtime- or release-certified.** The preceding OPEN checkpoint is preserved in history/pre-hardening-metadata/CONTRACT_HARDENING.md.

The user asked to fix all findings from Codex's review against harness09891721b9d3509a3d618c7a25d3a3f184b0e225. This pass replaces missing mechanisms with exact protocols, schemas, reference fixtures and per-feature integration instructions. It does not claim the harness/controller implement them or that production tests ran. User-approved analytical autonomy, independent leads, whole coverage and immutable evidence remain intact.

## Finding-to-correction map

| Finding | Selected normative correction | Executable design evidence | Production integration gate |
|---|---|---|---|
| H01 premature yield claim | [YIELD_SETTLEMENT](contracts/YIELD_SETTLEMENT.md), [STATE_MACHINE](contracts/STATE_MACHINE.md): prepare while RUNNING, seal predecessor, then publish waiting/runnable | Yield interleavings, claim-fence SQL reference and terminal matrices | Real claim/finalizer race with transcript seal deliberately blocked |
| H02 oversized synthesis | [FILE_SYNTHESIS](contracts/FILE_SYNTHESIS.md): immutable host manifest, bounded staged decisions/reference pages, small final seal | 10000 required decisions, journal CAS/replay, missing sets, seal byte bound | Actual large canonical file through atomic publication and real receipts |
| H03 undefined prefix proof | [PREFIX_RECEIPTS](contracts/PREFIX_RECEIPTS.md), [INPUT_REVISIONS](contracts/INPUT_REVISIONS.md): exact versioned bodies/chains, completed response boundary, two-store reconciliation | Closed schemas, identity/hash/call/parent/input negative fixtures, transcript association | Production runtime reducer, appendable capture seals and restart reconciliation |
| H04 unenforced170k | [CONTEXT_BUDGET](contracts/CONTEXT_BUDGET.md):170000/16384/4096,149520 hard input,127092 checkpoint threshold, bounded dossier/eviction | Boundary/365k/changed-request/unknown-counter/dossier fixtures | Real route tokenizer/protocol projector, zero-call oversized dispatch tests |
| H05 descriptive SDK/roles | [SDK](contracts/SDK.md), [ROLE_PROJECTIONS](contracts/ROLE_PROJECTIONS.md), [ABI](contracts/schemas/sdk-abi.json), [exact declarations](contracts/reference/public-api.pyi) | All closed DTOs, missing/unknown/enum/null/type cases, exact field/signature comparison | Matching installed harness/controller classes and provider projections |
| H06 incomplete migration | [STATE_MACHINE](contracts/STATE_MACHINE.md), [MIGRATION_PLAN](contracts/MIGRATION_PLAN.md), [matrix](contracts/schemas/state-transitions.json) | Exhaustive selected matrices and SQL settlement-fence model | Actual CHECK/trigger/view/FK/fingerprint migrations and every admission/recovery path |
| H07 stranded outcomes | Exact investigation/falsification tables in STATE_MACHINE and machine-readable matrix | Four investigation tuples, terminal outcomes, forbidden reopening | Real candidate/task/artifact/successor/completion transactions |
| H08 assumed adapter IR | [CALLSITE_IR](contracts/CALLSITE_IR.md): typed optional capability, original ranges, explicit unsupported gaps | Inert Python schema-shaped pilot for aliases/shadowing/flags/ranges/overflow | Real first Python adapter, then support only additional languages whose fixtures pass |
| H09 unwanted compatibility | [CUTOVER](contracts/CUTOVER.md): single collaborative-v1 runtime/new pair, historical data read-only | One-mode/mismatch contracts and cutover cases | Quiescent two-store activation and installed matching-pair/refusal tests |
| H10 stale package metadata | [manifest](MANIFEST.json), [traceability](TRACEABILITY.json), [validation](VALIDATION_REPORT.md), [publication](PUBLISH_HANDOFF.md) | Reproducible full-tree hashes, feature plan membership, structural/schema/reference validators | Verify final GitHub commit/CI plus actual code results during implementation |

[RESOURCE_BOUNDS.md](contracts/RESOURCE_BOUNDS.md) additionally freezes lead/root/review, live-consumer, interest, pending-publication and no-progress limits with rollback/replay semantics. Full worker capacity still queues a valid independently recorded lead; metadata exhaustion is explicit, not a silent drop.

## Exactly what is frozen

The machine-readable schemas define required properties, bounds, nullability, enum domains and unknown-field rejection. sdk-abi.json/public-api.pyi define constructor/method parameter order, keyword-only/default/annotation/return rules and DTO field order. state-transitions.json defines complete selected task/agent/review/intent domains and outcome tuples. The generator reproduces these without network access or importing target/application code.

Semantic checks beyond JSON Schema—receipt parent chains, exact subject/facet coverage, transaction fencing, material validity, tokenizer accuracy, graph safety and migration preservation—are explicitly assigned to owners and tests. A schema PASS is not an accepted finding, a migrated database or a verified provider request.

## Feature-plan integration and precedence

Every feature now has a concrete contract-hardening integration section in its dedicated IMPLEMENTATION_PLAN.md. The unsafe early PENDING flow, generic new-role analysis shapes, whole-file terminal arrays, invented callsite_records interface, and old-runtime/four-pair prescriptions are replaced in their owners. Earlier approved requirement/test ledgers and historical snapshots remain unchanged; later delegated corrections are attributed in ENGINEERING_DECISIONS.md.

Shared contract documents own fields/transaction rules once. Feature plans specify where to wire those rules and the exact assertions to test. A contradiction found during implementation is a defect to amend explicitly, not permission to weaken a receipt, overwrite an input revision, fabricate coverage or invent a second scheduler.

## Implementation order

R0 pins the actual worktrees, schema resources and installed/import boundaries. Then implement input/receipt/state foundations and their failure fixtures before exposing nonterminal publication or yield. Implement bounded synthesis before enabling large-file parent completion. Integrate the final-request context gate before paid dispatch. Add mixed-role readiness/outcome closure, then the first typed callsite adapter and exact paired controller SDK. Run real migrations/installed-package tests before any separately authorized deployment.

The reference-model and structural checks can run now using `python tools/validate_docs.py` and `python tools/validate_hardening.py`. Migration ordinal allocation, selected dependency wheel hashes and route tokenizer certification are implementation/build facts to record, not open behavioral choices. No additional consultation is required to follow the selected contracts. No runtime capability is called complete until its actual integration tests pass.
