# Specification validation and implementation status

Edition 1.1, 16 September 2026. This report describes checks on the specification/reference assets, not a working SSR harness.

## Executed here

```sh
PYTHONDONTWRITEBYTECODE=1 uv run --no-project --python 3.12 --with-requirements stage-1-indexing/validation/requirements.txt python -B stage-1-indexing/validation/run_checks.py
python3 -B stage-1-indexing/validation/refresh_manifest.py
python3 -B stage-1-indexing/validation/refresh_manifest.py --check
git diff --check
```

Execution environment: Python 3.12.12, Pydantic 2.13.4, jsonschema 4.26.0 and PyYAML 6.0.3 on native macOS arm64. **94 core specification/reference/structure checks and 95 regression tests passed**, with zero failures, errors or skips. The machine-readable outcomes are [validation/results.json](validation/results.json) and [validation/regression-results.json](validation/regression-results.json). The combined command regenerates all three schema bundles, validates them and parses every delivered Python source before running the regressions. W01 still must verify the actual production dependency lock and installed resources.

The checks cover JSON Schema validity for each named API model; strict request boundaries; invalid modes, ranges, coverage counts and error envelopes; pure UTF-8 source-page sizing, Unicode/escaping and character-safe boundaries; adjacent page coverage and repeated continuation sections under changing progress; a calculated minimum budget that succeeds when resubmitted; the ordered task dependency graph; mapping of all 83 approved requirement IDs; rule/fixture identity accounting; Python/TOML/YAML syntax and relative links against the repository baseline.

Regressions additionally cover large independent-error batches/operational codes, exact shared-record types and invalid ownership, five codec offset maps and original source coordinates, shared-run demand/admission/lease decision tables, publication-specific diagnostic manifests, strict settings/profile validation, adversarial compiler-input/path sanitization, and language golden/comparator integrity. The language corpus contains 32 authored cases and 40 actual source strings covering all 12 supported dialects, with positive, negative, malformed-source and Unicode/CRLF cases. These are authored expectations, not captured output from running all adapters.

The source-reader reference is an in-memory UTF-8 paging model, not a Git reader or PostgreSQL navigation service. SourceUnit transcoding tests cover the five declared codecs but do not prove the production reader/materializer integration. Rule fixture accounting confirms that the authored files correspond to the authored rule IDs, not that Semgrep accepts or matches those patterns. Pure compiler tests validate the sanitizer, not installed libclang or OS containment. Lifecycle tests validate decisions, not concurrent PostgreSQL behavior.

The revised SQL was separately parsed with pglast 8.4: **42 statements parsed successfully**. Reproduce with `uv run --no-project --python 3.12 --with pglast==8.4 python -B -c "from pathlib import Path; from pglast import parse_sql; print(len(parse_sql(Path('stage-1-indexing/contracts/v1/schema.sql').read_text())))"`. This is parser syntax evidence only, not PostgreSQL 17 migration execution, foreign-key transaction behavior or a database integration pass.

## Review corrections and evidence boundary

| Review area | Delivered correction |
|---|---|
| Shared internal contracts | SourceUnit/ExtractionBundle plus scopes, imports, declaration invalidations, origins/provenance, SQL projection and valid/invalid fixtures. Original-byte and ownership guards are executable. |
| Language algorithms | Explicit per-language visibility/shadowing/import/member/ownership policy and exact source/output projections with a reusable comparator. Real grammar queries and runtime adapter output remain implementation gates. |
| Shared datasets and controls | Durable HOLD/RUN/PAUSE intent, explicit demand/state precedence, retry-cycle counters, frozen per-file plan, common dataset→run→work→publication lock order and concurrency schedules. |
| Caller/progress fields | Preserved upstream ecfb05d's owner_name and frozen rule-mode/digest contracts and regression tests. |
| Error contract | No 32-item truncation; the 65,536-byte error target is not a hard ceiling. Operational codes use the shared closed registry; large independent batches are tested. |
| CRLF paging | Preserved upstream ce84d76's indivisible-atom prose/reference reconciliation and exact-minimum regression tests. |
| Compiler inputs | Exhaustive option grammar, POSIX tokenizer, rooted mapping, context-error/trust policy, adversarial sanitizer tests, and separate W09 observation/W12 navigation acceptance. |
| Acceptance/delivery | Concrete golden inputs, deterministic manifest/validation commands, and pinned benchmark inputs with explicit production evidence boundaries; no benchmark timing or runtime gate is claimed here. |

Additional corrections fix configuration locations/merging, capture manifest representation, the process-runner boundary, mandatory real TLS transport tests, auxiliary cursor-key mappings, scanner source maps and active-publication diagnostic provenance. The original approved requirements were not rewritten.

## Not executed here

PostgreSQL 17 schema application, transaction/lease/crash integration, local or HTTPS source capture, Git/submodule/LFS behavior, Tree-sitter grammar/query conformance, Python-adapter integration, libclang context/binding tests, Semgrep compilation and positive/negative execution, Linux/macOS/WSL installation, backup/restore, and performance benchmarks have not been run. No vulnerability findings or completeness of a real repository are claimed.

These are mandatory development gates, not waived checks. Each work recipe names its future test commands and stop conditions. W15 must record actual PASS/FAIL/NOT RUN for every gate in [tests-and-delivery.md](specification/tests-and-delivery.md). Schema/reference checks cannot substitute for them.

## Provenance and package boundary

The approved documentation baseline is `JennieXLisa/ssr-redesign` at `c2c238d325d82188e47d8b83b9d963800754d986`. This correction pass starts from the existing fixes through `ecfb05da9e94c26af33e7218c29d23bb0c351746`. Requirements, AGENTS.md and the two discussion-era API contracts are retained. Engineering choices remain delegated refinements, not claims of individual approval or runtime completion. IMPLEMENTATION.md now explicitly distinguishes supplied mechanisms/fixtures from unimplemented grammar, sandbox and runtime integration work.

The downloadable package is an overlay for that repository. Its manifest hashes the delivered files; copy it over an existing checkout without removing the historical requirements. A publication receipt may record the later Git commit separately so the package manifest does not attempt to hash itself or its own commit identity.
