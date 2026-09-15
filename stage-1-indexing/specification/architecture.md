# Architecture, dependencies and ownership

Normative for Stage 1. Implements the scope and sharing requirements, in particular S1-IN-R07/R20/R21, S1-IX-R01–R05 and S1-NV-R01. The database remains PostgreSQL; no SQLite, graph service, vector service, Redis, task broker or LLM service is required by this architecture.

## Runtime and dependencies

Use Python 3.12 for the application, PostgreSQL 17, Git 2.47 or newer with HTTPS/libcurl support, psycopg 3 with its connection pool, Pydantic 2 for strict DTO validation, the `regex` package for name/content expressions, and `wcmatch` for path globs. Use psutil for available-memory/RSS reporting. Use argparse from the standard library for the CLI; do not add an HTTP server merely to expose local commands. Use pytest, Hypothesis, import-linter, build and Ruff in development. Use `uv` to create and freeze the application environment. Semgrep CE runs in a separate tool environment, not inside the application dependency graph.

Retain the original harness's declared parser baseline: tree-sitter 0.26.0; tree-sitter-bash 0.25.1; c 0.24.2; cpp 0.23.4; java 0.23.5; javascript 0.25.0; lua 0.5.0; php 0.24.1; typescript 0.23.2; zsh 0.63.3. Python uses `ast` and `tokenize`. These versions come from the read-only `0989172` pyproject, not an assertion that the new adapter suite has already passed. W01 locks all resolved dependency versions and tests wheel/resource loading on macOS arm64 and Linux x86-64. [Sources S1–S3](decisions-and-sources.md)

Use libclang through its Python bindings for C/C++ semantic binding, with the library and bindings from the same installed distribution. Start with the `libclang` 18.1.1 distribution; record its actual version and resource-directory digest. Missing headers/build flags are explicit context limitations, not a reason to discard the structural index. Do not execute a build to obtain compiler inputs. All other language resolution is the finite, source-backed algorithm in resolution.md, not a promised general-purpose type checker. [S4–S5]

For dependencies without an exact baseline above, resolve one supported release in the named major family in W01, commit `uv.lock`, and then use frozen installation. Record the Semgrep executable version plus SHA-256, its help/capability probe and its separately locked environment. This is a reproducibility step, not an invitation to compare frameworks or choose new architecture. A failing pinned parser/tool must be investigated with a minimal fixture; version changes require the affected conformance suite and an explicit change record.

## Package map

```text
src/ssr/
  config/       settings.py, loading.py
  contracts/    common.py, navigation.py, intake.py, indexing.py, errors.py
  storage/      connection.py, migrations/, repositories/ (one per capability)
  capture/      local.py, remote.py, submodules.py, git_store.py, publication.py
  source/       encoding.py, positions.py, reader.py, continuation.py, materialize.py
  indexing/     planner.py, worker.py, leases.py, publication.py, completion.py
  languages/    protocol.py, registry.py, python/, javascript/, typescript/,
                c/, cpp/, java/, php/, lua/, bash/, zsh/
  resolution/   scope.py, imports.py, members.py, clang.py, associations.py
  rules/        models.py, loading.py, comparison.py, names.py, semgrep.py, builtin/
  navigation/   functions.py, references.py, files.py, text.py, flags.py, paging.py
  cli/          main.py, capture.py, index.py, query.py, rendering.py
```

Names describe intended responsibility, not a requirement to create every empty file. Create a module when its task implements it. No catch-all `service.py` owning capture, SQL, scanners and source reading. No line-count quota; split a module when it owns independent rules or dependencies. Domain owners accept repositories/source-reader interfaces, not the whole application object.

`contracts` has no I/O. `storage` owns connections and SQL, not analysis policy. `capture` is the only owner of managed snapshot publication. `source` owns original-byte interpretation. `languages` returns extraction values without database access. `resolution` consumes published inventories. `rules` executes selected rules but cannot declare whole-index completion. `indexing.publication` alone makes results authoritative. `navigation` is read-only. The CLI parses/renders and calls owners; it contains no alternative lookup logic.

## Dependency direction

All packages may import `contracts`; low-level packages may import `config`. Language adapters cannot import navigation, CLI, orchestration or storage. Storage repositories cannot call capture/scanners. Navigation may use storage repositories and source interfaces but not worker implementations. Composition occurs in CLI startup. Inject a clock and process runner for tests; do not introduce a general plugin framework or service locator.

Transactions are explicit owner scopes using psycopg transactions. Helpers neither commit nor retain connections across slow Git/compiler/scanner calls. A connection checked out for a request is returned before external work. PostgreSQL's short queue locks are for claiming/publication, not the lifetime of parsing. [S6–S7]

## Deployment and resources

Supported execution environments: native macOS arm64 and Linux x86-64; Windows uses Linux in WSL2. PostgreSQL may be local or addressed through a configured DSN. Stage 1 does not require shared multi-machine workers or a tenant system, but does not impose an invented one-project or one-run database restriction. Multiple runs have distinct work identities; each running worker pool obeys the shared budget for its instance.

Ship a conservative default of four heavy worker slots and two scanner slots within those four. A Semgrep invocation using one internal worker consumes one heavy slot. Compiler work consumes a heavy slot too. Configuration can change throughput without changing dataset identity. Database connection pool: minimum 1, maximum `worker_slots + 4`. Stop claiming new heavy work when available memory is below the configured 2 GiB low-water mark; resume claiming after 3 GiB is available. Both thresholds are configurable and measured through psutil within the runtime/WSL environment. Do not delete or skip jobs. With insufficient resources for one file, surface `RESOURCE_REQUIRED` and preserve the job for operator resumption.

Configuration is TOML plus explicitly named environment variables for the database DSN and storage root. The exact settings/profile models, file locations, merge algorithm and process/doctor boundaries are fixed in [configuration-and-processes.md](configuration-and-processes.md). Do not ingest configuration from the research target automatically. Precedence: explicit operation parameters, selected SSR project settings, installation settings, shipped defaults. Freeze semantic settings per dataset: parser versions, language overrides, semantic context, resolver version, rules and scanner version. Exclude worker count, connection limits and diagnostic verbosity from semantic fingerprints.

## API and serialization ownership

All public operation results validate against the contract models. Use UTF-8 JSON with `ensure_ascii=False`, `allow_nan=False`, separators `(',', ':')`, no BOM, and no added whitespace for byte accounting. The compact JSON payload is the wire unit. A CLI `--json` writes exactly that payload followed by one transport newline; the newline is not part of the payload budget. Human rendering is a separate view and must not be used as the model transport. Later provider envelopes have their own budget and must not be advertised as included in the Stage 1 payload byte limit.

Use the shared `errors` array for failures. Identifiers are opaque canonical UUID strings. Never reuse the example IDs `idx_12` or `fn_42` as production formats. Source records carry deterministic UUIDv5 identities within a dataset; projects, captures and requested runs use UUIDv4. Every query resolves the run's dataset references rather than inferring a snapshot from a path.
