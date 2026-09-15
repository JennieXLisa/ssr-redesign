# W13 — Implement built-in/custom reconnaissance and full-scope scanner accounting

Depends on: W07, W08, W09, W10, W11. Owner: rules loaders/comparison/name engine/Semgrep adapter.

Requirement traceability: S1-FL-R01, S1-FL-R02, S1-FL-R03, S1-FL-R04, S1-FL-R05, S1-FL-R06, S1-FL-R07, S1-FL-R08, S1-FL-R09, S1-FL-R10, S1-FL-R11, S1-FL-R12, S1-IN-R09, S1-IX-R03.

## Read before editing

Read ../IMPLEMENTATION.md, the specification sections for this capability, and the directly related contracts. Reuse settled types/algorithms; do not restart a repository-wide architecture survey.

## Intended files and boundary

- `src/ssr/rules/`
- `src/ssr/rules/builtin/`
- `tests/rules/`
- `tests/scanner/`

## Implementation recipe

1. Adopt the supplied initial name and Semgrep catalogue, requiring positive/negative fixtures for every shipped rule. Add only the documented API mappings; keep rule IDs/versions explicit.
2. Implement safe YAML, schema validation, canonical definition comparison, same-key conflict errors and identical-definition consolidation retaining all source references.
3. Implement combined/custom-only selection and frozen manifest persistence. Validate the full selection against local syntax fixtures before scanning any captured target source.
4. Implement local-name wildcard/regex matching exactly as specified. No qualified-name selector or exact-match third mode.
5. Run Semgrep through the installed [native-isolation.md](../specification/native-isolation.md) runner/policy for both rule validation and target scanning, with approved flags and no hidden ignore/size/timeout suppression. Require the policy/readiness receipt, exact executable inventory and scanner-only scratch. Reconcile every expected applicable file and isolate batch failures to uncommitted files.
6. Map matches back to original-byte spans and executable owners. Preserve generic Lua/Zsh pattern provenance, overlapping independent rules, and explicit parser/scanner failures.
7. Publish per-file name/Semgrep components separately, retaining extraction if scanning fails. Update coverage only through the common publication/completion owner.

## Verification commands

These are the required implementation commands/test targets; they are not claims that tests already exist or were run while writing this specification.

```sh
uv run pytest tests/rules tests/scanner tests/indexing/test_flagging_resume.py
uv run pytest tests/processes/test_scanner_isolation.py
```

## Acceptance evidence

- Every built-in rule has an actual executed positive/negative fixture.
- A large generated file and a file hidden by target .semgrepignore are still accounted for.
- Custom-only results never claim built-in coverage; invalid selection runs no valid subset.

## Stop condition and receipt

No autofix, cloud registry fetch, vulnerability verdicts, taint product, secret validation or auto-created investigations.

Complete W13 only after its real entry-point/owner tests pass. Record implemented requirement IDs, changed files, actual command results, unrun checks and the commit in IMPLEMENTATION_RECEIPT.md. Commit/push when authorized; do not silently advance the next task or add another planning document.
