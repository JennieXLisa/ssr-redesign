# Codex implementation handoff — corrected collaborative-v1 plan

Read this file, AGENTS.md, CONTRACT_HARDENING.md and DELIVERY.md, then the relevant feature's specification and dedicated IMPLEMENTATION_PLAN.md from FEATURE_IMPLEMENTATION_INDEX.md. The user authorized design correction and GitHub publication; application code changes and any live actions must belong to the subsequent explicit Codex task.

## Start from facts

Pinned review baseline: source-review-harness09891721b9d3509a3d618c7a25d3a3f184b0e225. Resolve the actual selected worktree and controller commit; record any differences without overwriting unrelated edits. BASELINE.md records the verified package owners. Read current migrations and schema admission fingerprints. Do not recreate old flat agent.py/tooling modules merely because historical documents name them.

Run the design checks before code:

```sh
python -m pip install 'jsonschema==4.23.0'
python tools/validate_docs.py
python tools/validate_hardening.py
python tools/refresh_manifest.py --check
```

These are document/schema/reference checks, not harness tests. Preserve their distinction in your report. The schema generator must produce byte-identical outputs; do not edit generated JSON or the ABI stub independently.

## First code slices and mandatory assertions

1. Bind immutable input revisions to actual requests and add exact prefix/terminal proof support. Required capture remains in transcript.db; semantic availability remains in ssr.db with honest reconciliation. Prove a lead/answer can publish while its producer continues without waiting for its own ACK or forging AGENT_TERMINAL.
2. Implement the complete task/review/agent transition and migration bundle. Prepare yield while RUNNING, settle original receipts, then atomically publish WAITING_DEPENDENCY/PENDING. Block real claim—including exact-task claim—during a paused predecessor seal. Implement cancellation/expiry/replay fences before making mixed-role work runnable.
3. Replace file parent output with frozen host manifests, stage_file_synthesis and the small final seal. Run a large file with many required reconciliation decisions; every provider input remains bounded, but the full canonical publication still validates all units/evidence/lineage atomically.
4. Put the170k request gate around every actual provider path. Count projected schemas/history/tool groups/notices. Test149520 maximum input,127092 soft threshold and a365000-token constructed rejection with zero transport calls. Prove tokenizer/template accuracy for the selected gateway; the arithmetic model alone is not certification.
5. Use the exact new-role schemas and SDK ABI. Implement all investigation outcome tuples and completion limitations, finite quotas/no-progress, and callsite-ir-v1 in one Python adapter before claiming wider operation semantics. Cut over only to one matching collaborative harness/controller pair; old runtime is not a fallback.

## Delivery discipline

Work one feature/contract integration at a time. Keep one transaction owner per effect. Add real negative/race fixtures before exposing a capability, commit each coherent slice, and record source commit, schema/ABI changes, tests collected/executed and unresolved integration failures. A requirement to add tests is not evidence the tests passed.

Do not weaken accepted source/evidence/falsification gates to get a green run. Do not classify operational timeout as a model's INCONCLUSIVE answer. Do not reopen a completed task for new material; use a successor revision. Do not import controller-private or application-private state across the public SDK. No manager model, separate knowledge store, message broker or generic workflow framework is needed.

## Cutover and release

The new runtime is collaborative-v1 only. Preserve old immutable data/history read-only, reject old/new ABI mismatch before mutation, and require no active old writers before migration. Separate project and transcript migration activation is explicit. Run actual source/wheel/migration/controller/route tests; only then report implementation readiness. Installation, live migration, restart, provider spending and target execution require their separately authorized scope.
