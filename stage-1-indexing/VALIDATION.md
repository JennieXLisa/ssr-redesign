# Specification validation and implementation status

Edition 1.0, 14 September 2026. This report describes checks on the specification assets, not a working SSR harness.

## Executed here

```sh
python stage-1-indexing/validation/export_schemas.py
python stage-1-indexing/validation/check_contracts.py
```

Execution environment: Python 3.13.5, Pydantic 2.13.4. The production target remains Python 3.12; W01 must verify its actual locked dependency environment. **94 specification/reference/structure checks passed**. The machine-readable outcome is [validation/results.json](validation/results.json).

The checks cover JSON Schema validity for each named API model; strict request boundaries; invalid modes, ranges, coverage counts and error envelopes; pure UTF-8 source-page sizing, Unicode/escaping and character-safe boundaries; adjacent page coverage and repeated continuation sections under changing progress; a calculated minimum budget that succeeds when resubmitted; the ordered task dependency graph; mapping of all 83 approved requirement IDs; rule/fixture identity accounting; Python/TOML/YAML syntax and relative links against the repository baseline.

The source-reader reference is an in-memory UTF-8 model. It is deliberately not a Git reader, PostgreSQL navigation service, access-control system, or proof of all production codecs. Rule fixture accounting confirms that the authored files correspond to the authored rule IDs, not that Semgrep accepts or matches those patterns.

## Not executed here

PostgreSQL 17 schema application, transaction/lease/crash integration, local or HTTPS source capture, Git/submodule/LFS behavior, Tree-sitter grammar/query conformance, Python-adapter integration, libclang context/binding tests, Semgrep compilation and positive/negative execution, Linux/macOS/WSL installation, backup/restore, and performance benchmarks have not been run. No vulnerability findings or completeness of a real repository are claimed.

These are mandatory development gates, not waived checks. Each work recipe names its future test commands and stop conditions. W15 must record actual PASS/FAIL/NOT RUN for every gate in [tests-and-delivery.md](specification/tests-and-delivery.md). Schema/reference checks cannot substitute for them.

## Provenance and package boundary

The approved documentation baseline is `JennieXLisa/ssr-redesign` at `c2c238d325d82188e47d8b83b9d963800754d986`. Existing requirements, AGENTS.md, and the two discussion-era API contracts are retained. New implementation decisions are identified in [decisions-and-sources.md](specification/decisions-and-sources.md). This edition closes those documents' open implementation mechanisms under the researcher's delegated instruction, without claiming those decisions were individually approved or that implementation is complete.

The downloadable package is an overlay for that repository. Its manifest hashes the delivered files; copy it over an existing checkout without removing the historical requirements. A publication receipt may record the later Git commit separately so the package manifest does not attempt to hash itself or its own commit identity.
