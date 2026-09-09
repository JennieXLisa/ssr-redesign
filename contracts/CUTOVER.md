# Coordinated collaborative-v1 cutover

Contract: `cutover-v1`. This is the selected correction for H09, implementing the user's supplied no-runtime-backward-compatibility direction. It supersedes earlier legacy-default, dual-mode runtime and four old/new harness/controller pairing requirements. Preserving good implementation components is not a requirement to preserve the old workflow.

## CO-R01 — One new execution workflow

The new release creates and executes only `collaborative-v1` reviews. Its configuration accepts that value or defaults to it after the new release's admission preflight; `legacy` is not an executable alternative. Missing schema, prefix receipt, context-counter, role or SDK capabilities fail before review creation/dispatch. There is no silent fallback to a legacy scheduler, old tool schema, old whole-file review mode, or old candidate phase gating.

Canonical review is symbol/review-unit analysis followed by file synthesis. Focused and contextual work run in the same continuously admitted pool. Existing internals, source/evidence validators and public context types can be reused when they implement this contract; import facade reuse does not create an obligation to keep old callable signatures operational.

## CO-R02 — One coordinated harness/controller pair

Build and pin one compatible collaborative harness and controller release. Test exact new SDK ABI, DTO order/types/serialization, closed enums, schema bundle hashes, prefix/runtime versions, authenticated child commands and frontend projections. The new controller refuses an old/incompatible engine with CONTRACT_MISMATCH before mutation. The new harness does not emulate an old controller's runtime command surface.

Delete the previous four-pair compatibility test requirement. Replace it with: matching new pair succeeds; each mismatched capability/ABI/version is rejected before any effect; clean installed packages work without a sibling checkout. This is a stricter single-contract pairing, not looser validation. Inert old database/report readers are tested separately where shipped.

## CO-R03 — Preserve history without converting active work

Cutover is an explicit operator/deployment operation, not something these documentation commits perform. Require no live old execution/writer, unsettled provider request or active lease before migrating project storage. The old runtime/operator must finish or explicitly stop/settle those runs first. An active old review is not converted in place to ANALYZING or a fabricated new prefix contract.

Retain old immutable source, evidence, results, receipts and reports under their original version/provenance. Historical rows cannot be admitted by the new scheduler or mutated by new-mode normalization. Optional read-only historical inspection may be implemented behind a version-aware reader. It is acceptable for a new runtime to direct an operator to an archived compatible reader instead of implementing every old report parser; it must not destroy or relabel the original data.

Do not edit old migration checksums or regenerate old receipts with new fields. Back up both stores through the existing safe backup authority. Separate ssr.db/transcript.db migrations have separate commits and an activation barrier; new execution stays disabled until both validate. Recovery from failed migration restores or completes the exact acknowledged stage, never runs old and new writers concurrently.

## CO-R04 — Release and rollback meaning

A release manifest supplies immutable source commits, wheel/sdist hashes, schema/ABI bundle hashes, supported route/tokenizer capabilities and frontend asset digests. No branch name alone authorizes installation. Before any separately authorized rollout, run state/receipt/synthesis/context integration fixtures and paired installed-package tests.

Rollback means restore the verified pre-cutover backup and matching archived binaries after proving no new writers remain, or apply an explicit forward repair that preserves new data. Do not start an old engine against migrated collaborative rows, and do not roll back schema by deleting new history. The documentation authoring task does not install, migrate, restart, or spend on providers.

## Verification

CO-T01 new review defaults only to collaborative-v1. CO-T02 old-mode configuration is rejected. CO-T03 mismatch in any mandatory capability/ABI digest causes zero mutation. CO-T04 active-old lease/provider uncertainty blocks cutover. CO-T05 historical rows survive with original IDs/hashes and are not claimable. CO-T06 project migration succeeds but transcript migration fails: activation stays blocked. CO-T07 clean matching pair runs without checkout imports; mismatched pair fails clearly. CO-T08 rollback plan requires exclusive writer proof and exact backup/binary identities.
