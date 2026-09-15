# W15 — Prove full scope, recovery and installation; hand over

Depends on: W04, W06, W14. Owner: integration tests, packaging and delivery documentation.

Requirement traceability: ALL_APPROVED_REQUIREMENTS.

## Read before editing

Read ../IMPLEMENTATION.md, the specification sections for this capability, and the directly related contracts. Reuse settled types/algorithms; do not restart a repository-wide architecture survey.

## Intended files and boundary

- `tests/end_to_end/`
- `tests/crash/`
- `tests/packaging/`
- `benchmarks/`
- `IMPLEMENTATION_RECEIPT.md`

## Implementation recipe

1. Run the entire approved requirement/acceptance matrix on real PostgreSQL, managed Git, actual language adapters and the pinned Semgrep executable. Reconcile all included files against required work outcomes.
2. Inject crashes at every capture/publication/lease boundary and test predecessor/successor fencing. Compare final normalized result digests between serial and parallel runs.
3. Build/install the wheel in clean Linux x86-64 and macOS arm64 environments; verify query resources, built-in rules, compiler library setup and offline tool capability checks. Document Windows as WSL2, not native-tested Windows.
4. Follow G20's exact [benchmark protocol](../specification/tests-and-delivery.md#benchmark-record) and [pinned corpora](../contracts/v1/benchmark-corpus.json). Capture the entire CPython v3.12.0 tree through normal public-HTTPS intake, verifying peeled commit `0fb18b02c8ad56299d6a2910be0bab8ad601ef24`; never execute its code. Generate the separate 100-replica language-source volume corpus with `validation/reference_benchmark.py` (manifest-only by default; explicit new trusted absolute `--output` for bytes). For each corpus, freeze exact tool/resource/rule/profile digests and run 1/2/4/8 heavy slots with 2 scanner slots bounded by total heavy slots, three fresh PostgreSQL/Git-storage repetitions each. Compare normalized success records, terminal failures, blocked work and completeness against serial. Preserve intentionally invalid real test sources and report downstream blocked phases honestly; no `index_complete` claim with failures. Report capture/planning/extraction/resolution/flagging/publication/query timings, RSS and errors for every repetition; warm reuse is separate. Synthetic volume does not prove fixture semantics across mixed profiles or real-world representativeness. The generator regressions establish corpus/write integrity only; runtime measurements remain a W15 gate.
5. Test backup/restore of PostgreSQL plus Git refs and reread exact occurrences after deleting original source/temporary clones.
6. Produce a task/release receipt with commit, exact lock/tool versions, commands/results, supported-binding matrix and remaining explicit limitations. Mark any unrun platform or tool gate as unrun, never pass.
7. Stop at the Stage 1 boundary. Do not create model reviews, threat models or investigations as a demo.

## Verification commands

These are the required implementation commands/test targets; they are not claims that tests already exist or were run while writing this specification.

```sh
uv run pytest
uv run ruff check src tests
uv run lint-imports
uv run python -m build
ssr doctor --json
```

## Acceptance evidence

- No included applicable file is missing, silently skipped or failed while a run claims complete.
- Actual full-stack entry points, not just mocks/schema examples, pass.
- The handoff distinguishes implemented behavior, declared limitations and unrun checks.

## Stop condition and receipt

No new feature phase, backward compatibility or token-usage-driven acceptance waiver.

Complete W15 only after its real entry-point/owner tests pass. Record implemented requirement IDs, changed files, actual command results, unrun checks and the commit in IMPLEMENTATION_RECEIPT.md. Commit/push when authorized; do not silently advance the next task or add another planning document.
