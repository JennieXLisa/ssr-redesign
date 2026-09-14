# Stage 1 — Implementation specification and developer entry point

Edition: 1.0, 14 September 2026. Scope: source intake, immutable snapshots, structural indexing, supported reference resolution, security-interest flags, and researcher navigation. No LLM invocation, autonomous review, threat-model generation, exploitation workflow, or backward-compatible runtime is part of this stage.

## Read this first

This completes the design details delegated by the researcher after the approved requirements and two partial API contracts. The files under `requirements/` retain the agreed behavior and its IDs; they are not instructions to repeat the original design interview. The two older contract documents remain the decision history for function search and reading. The documents in [specification/](specification/architecture.md) now resolve their open implementation mechanisms. The new implementation choices are engineering decisions made under that delegation, not claims that the researcher individually approved each library, column, or numeric constant.

Use this precedence: explicit researcher decisions in the requirements; the concrete specification in this edition; machine-readable contract models and configuration in `contracts/v1/`; then task recipes. If an executable contract contradicts prose, stop and identify the exact discrepancy instead of choosing whichever is easier. A failed backend is not permission to downgrade a requirement, silently skip source, or label a partial result complete.

The package specifies development work. It does not claim that a harness implements it. Validation performed on the package itself is recorded in [VALIDATION.md](VALIDATION.md); the full runtime release gates remain unexecuted until implementation.

## Architecture in one paragraph

A Python application owns a PostgreSQL database and one bare managed Git repository per research project. Capture completes before processing. Immutable, versioned extraction/resolution/flagging datasets can be shared by runs using compatible inputs. Workers publish complete file-step results under leases; navigation reads only published records and exact Git bytes. Tree-sitter/Python AST provide structure. Conservative language adapters and a C/C++ libclang adapter establish supported bindings; uncertain relationships remain explicit. Semgrep CE and local-name rules generate observations, not vulnerability decisions. The CLI and future tool adapters invoke the same operations.

## Implementation order — execute one task at a time

| Task | Deliverable | Depends on |
|---|---|---|
| W01 | Installable package, dependency lock, configuration, PostgreSQL bootstrap | None |
| W02 | Database schema, transaction boundary, typed records and contract validation | W01 |
| W03 | Local capture, immutable Git publication, exclusions and source manifest | W02 |
| W04 | Public HTTPS intake, opted-in submodules, LFS reporting | W03 |
| W05 | Byte-accurate reader, source pages, repeatable continuations, errors | W03 |
| W06 | Resumable file-step execution and publication ownership | W02, W05 |
| W07 | Python structural extraction and shared adapter conformance suite | W06 |
| W08 | JavaScript/JSX and TypeScript/TSX extraction | W07 |
| W09 | C and C++ extraction and libclang binding integration | W07 |
| W10 | Java and PHP extraction | W07 |
| W11 | Lua, shell/Bash, and Zsh extraction | W07 |
| W12 | Cross-file bindings, declaration/definition association, one-hop queries | W08–W11 |
| W13 | Built-in/custom rules, validation, name flags, Semgrep adapter | W07–W11 |
| W14 | Search, outlines, discovery, content search, live pagination, coverage | W05, W12, W13 |
| W15 | Crash/replay, full-scope audits, packaging, benchmark and developer handoff | W04, W06, W14 |

The order above is deliberately linear for an implementing agent even where tasks have independent dependencies. Do not start W12 while still inventing the extraction record shape. Do not parallelize two agents across the same migration, contract, or package. W08–W11 are separate language tasks, not permission to rewrite the shared indexer four times.

Each task has its own recipe in [implementation/](implementation/README.md). A task receipt must identify the requirement IDs implemented, owning package, modified files, actual test commands/results, remaining blockers, and commit. No estimates based on token budget are acceptance criteria. No new planning document is needed before each task.

## Specification map

| Document | What it fixes |
|---|---|
| [Architecture](specification/architecture.md) | Packages, dependencies, ownership, configuration, version policy |
| [Storage](specification/storage.md) | PostgreSQL entities, keys, uniqueness, indexes, publication and reuse |
| [Capture](specification/capture.md) | Local/remote algorithms, Git publication, submodules, links, LFS, recovery |
| [Extraction](specification/extraction.md) | Source normalization, adapter output, language constructs, errors |
| [Resolution](specification/resolution.md) | Supported binding cases, compiler inputs, identity association, limitations |
| [Rules](specification/rules.md) | Categories, rule formats, comparison, scanning and coverage accounting |
| [Navigation](specification/navigation.md) | Operations, ordering, cursors, filters, errors and response limits |
| [Source reading](specification/source-reading.md) | Encoding, byte/line conventions, whole-response budgets, token algorithm |
| [Execution](specification/execution.md) | States, leases, retries, staged visibility, consistent completion |
| [Tests and delivery](specification/tests-and-delivery.md) | Fixture matrix, integration/crash tests, receipts and release gates |
| [Decisions and sources](specification/decisions-and-sources.md) | Delegated selections, maintained boundaries, primary references |

[TRACEABILITY.json](TRACEABILITY.json) maps every approved requirement ID to its implementation tasks. Contract models and example defaults are specification assets, not a second production implementation. Copy/adapt their types into the owning production package during W02; do not ship two competing DTO definitions.

## Completion boundary

Stage 1 is done only when a fresh installation can capture local and remote test repositories, index every included file according to its declared treatment, report all exclusions/limitations, survive interruption, and exercise the complete CLI-to-owner navigation path against PostgreSQL and managed Git. All supported-language conformance fixtures and applicable scanner gates must pass. A full structural scan with unresolved targets can complete honestly; a parser/scanner crash cannot be renamed an unresolved target. Do not mark W15 complete based only on schema validation or mocked adapters.
