# P8-F03 — Delivery and release handoff: implementation plan

Updated: 2026-09-09. Documentation only; no release, application install or live migration is performed by this change. Read the [feature](../P8-F03-delivery-and-release.md), [DELIVERY.md](../../../DELIVERY.md), [BASELINE.md](../../../BASELINE.md), P7-F03 versioning and P8-F01 acceptance.

## 1. Separate documentation, code and live authority

The documentation repository contains the selected design and implementation guidance. It is not the running harness, not proof that its modules exist in the installed package, and not authorization to mutate live reviews. An implementing task must select actual source/controller worktrees and permit code changes. Live provider spend, controller restart, package installation and real database migration remain separately authorized actions.

Read the implementation repos' applicable AGENTS.md, current implemented specification, working-tree changes and handoff boundaries. Record exact refs/import origins. Do not reset an unexpected worktree or overwrite concurrent changes to match a historical design baseline. Verify the observed modular-refactor map against actual code before assigning helper destinations.

## 2. Establish R0 baseline evidence

Record source commits, uncommitted changes, Python/frontend/runtime dependencies, schema horizon/checksums, supported public SDK contracts and effective config. Run relevant existing tests and actual collection for tools/source, evidence, distributed publication, investigation finalization/successor races, query/SDK compatibility and controller supervision.

Classify failures with evidence: baseline-reproduced, introduced by this slice, environment/capability unavailable, or unknown. Do not call a failure pre-existing merely because its test name looks unrelated. Preserve private/public class identity, stored hashes and installed package origins in the baseline report.

The initial output is a concrete owner/caller/test map, not a proposed wholesale rewrite. Required behavior changes are distinct from the behavior-preserving modular refactor. New code can use the refactored boundaries without moving every large module again.

## 3. Implement dependency slices, not runtime phase barriers

Follow R1–R7 in DELIVERY.md with each feature's detailed plan open. Each slice must end in a coherent testable boundary; do not expose a capability whose acceptance, recovery or controller path is missing.

| Slice | Implementation sequence | Mandatory exit evidence |
|---|---|---|
| R1 | Shared refs/outcomes/operations; mode identity; access ownership; basic source/catalogue/index queries | Cross-file read without foreign coverage authority; exact identity and legacy hash tests |
| R2 | Per-file search/cursors; checkpoints; rejection→research; grouped reads | Page-size/byte invariance; no-progress/encoding failures; CAS and actual-delivery tests |
| R3 | Artifact producer/turn receipts; availability/interests/notices; independent lead registration | Real receipt gates; no lost lookup race/ACK; accepted lead survives proposer failure |
| R4 | Context routing/inbox/answers; yield/wake; cycles/shared cancellation; full-unit adoption | End-to-end help request while coverage continues; all race and no-false-coverage cases |
| R5 | Mixed eligibility/refill; resources/fairness; candidate investigation/falsification/promotion; validity and closure | Unrelated coverage remains active during finding; current gate and closure invariants |
| R6 | Operation models/priorities/summaries/analyzers; negotiated SDK/controller/UI | Explicit support limits, no task-per-hit explosion; all compatibility/package checks |
| R7 | Integrated acceptance, separately authorized quality/protocol evaluation, release build | Traceability, failures/limits, immutable artifacts and operator decision record |

These labels describe development order, not new user-selectable partial review modes. Some foundations appear in several feature plans because the owning interface must exist before its consumers; implement one shared owner, not duplicate variants.

## 4. Feature-sized code commits

For each feature, first add/update characterization and positive/negative tests for its contract. Implement the narrow owning logic, wire all callers/guards, then run integration/race cases. Inspect the diff for accidental behavior changes, source leakage, weakened validation and stale public imports. Commit one coherent change with its test result and remaining disabled prerequisites recorded.

A small private helper name is developer discretion. Changing source permission, accepted-answer timing, candidate gate, retry semantics, cursor meaning, budgets or public schema is not a local naming choice. Record a material deviation as an explicit engineering amendment with affected requirements/tests before enabling it.

Do not hide missing functions behind broad 'TODO integrate' paths while marking a feature done. If a required dependency is not yet present, the dependent capability remains unavailable and the slice report identifies the exact interface/gate. Partial implementation is recorded honestly, not treated as final completion.

## 5. Continuous cross-repository compatibility

Use the four baseline/new harness-controller combinations for supported legacy behavior, not only both changed repos together. Record which combinations support collaborative mode and which reject it by negotiation. Preserve parent engine-import boundaries, exact-task command semantics, authenticated job generations, source-free DTOs and lazy historical transcript fetching.

Run new public query/command tests against installed wheels as well as development source. Controller tests must verify packaged frontend static assets and their hash manifest, not merely the source TypeScript build directory. A sibling editable checkout cannot silently satisfy a missing wheel module.

Any change to the schema/protocol/version range must be justified by actual migration and wire support. Do not bump an accepted range or ignore unknown fields only to make a pair test green.

## 6. Acceptance packet per slice

Store a bounded report containing starting/ending commit, touched authority map, requirements implemented, public/schema/contract changes, migration fixtures, exact test commands/node IDs/collection/results, fault-injection traces, clean import checks, unresolved blockers and actions not performed. Link machine-readable evidence rather than copy huge logs into every feature document.

A test result must identify the code/artifact it exercised. A green documentation validator only checks documentation structure/schema examples; it does not certify runtime algorithms. Unrun provider/quality tests remain NOT_RUN. Evidence from a different model revision or source snapshot cannot be relabeled as current acceptance.

Keep previous reports immutable or versioned. Do not remove failing outcomes when a later rerun passes; explain the corrective commit and retain the sequence.

## 7. Build immutable paired artifacts

After code acceptance and explicit release authorization, build from clean recorded commits in isolated environments. Produce wheel/sdist and controller package assets using the repos' actual build commands. Verify package file lists, import origins, supported contracts/schema horizon and hashes. Reinstall into a fresh environment with no source checkout on sys.path and run the packaged smoke/compatibility suite.

The release manifest includes exact source SHA, dirty status, artifact filename/size/SHA-256, dependency lock or environment digest, migration checksums, SDK/tool/result/mode versions, provider capability requirements and optional matcher/analyzer artifact/rule digests. No 'latest', mutable branch-only reference or unverified local path is sufficient for pairing.

Preserve the old accepted artifact coordinates. Do not silently replace an existing wheel under the same filename/version with different bytes. Source publication, build, installation and deployment are separate steps with separately observed results.

## 8. Operator deployment and rollback procedure

Before live changes, obtain actual authorization and identify the target process/state roots. Use the controller/coordinator's safe pause/quiescence and live-writer checks; do not infer safety from an empty UI queue. Take a consistent backup using the existing storage owner, including governed transcript and cursor-key/provisioning state where continuation must survive.

Apply migration/install/restart only through the approved operator path, record commands/outcomes and verify installed hashes plus public capabilities. New collaborative reviews are explicitly selected; old reviews retain legacy contracts. Monitor required receipts, unknown usage, closure blockers and current validity after startup.

Rollback is not an automatic package downgrade when old code cannot read the new schema. Restore a consistent backup to a compatible isolated state or use an approved reader-compatible recovery release. Never edit migration history, copy partial tables or clear receipt holds to force startup. Preserve evidence of the failed rollout and do not reset review identities to hide it.

## 9. Release gating tests

Create a deliberately incomplete feature build without real turn receipts: capability remains disabled despite schema presence. Package a stale/omitted private module and prove clean installed tests detect it. Supply an old controller to the new harness and verify supported legacy behavior; unsupported collaboration fails clearly.

Inject migration failure and verify no new-mode-ready advertisement. Restore matched/mismatched cursor-key backups and inspect explicit continuation behavior. Simulate unknown live writer status and assert deployment/recovery refuses unsafe mutation.

Run the complete P8-F01 trace and compare current-finding/export/completion projections. Publish only actual test/run statuses. A positive P8-F02 timing result with degraded coverage or unmeasured quality does not automatically satisfy release approval.

## 10. Final developer handoff

The final handoff identifies completed slices/features, exact source/build artifacts, public compatibility, migrations, executed tests, remaining empirical limits, operational pause boundary and next authorized action. It must distinguish IMPLEMENTED, TESTED, BUILT, INSTALLED and DEPLOYED. None is inferred from another.

No big-bang rewrite, force reset, automatic live run, paid experiment without scope, permanently proliferating partial modes or handoff that only says 'add tests and integrate' is permitted. The developer can vary local decomposition, but must preserve the selected interfaces, transaction guarantees and actual evidence of completion.
