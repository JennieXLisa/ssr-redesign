# W01 — Bootstrap the installable package and locked tools

Depends on: none. Owner: config, CLI composition and installation metadata.

Requirement traceability: S1-IN-R07, S1-NV-R01.

## Read before editing

Read ../IMPLEMENTATION.md, the specification sections for this capability, and the directly related contracts. Reuse settled types/algorithms; do not restart a repository-wide architecture survey.

## Intended files and boundary

- `pyproject.toml`
- `uv.lock`
- `src/ssr/config/settings.py`
- `src/ssr/cli/main.py`
- `tests/packaging/test_install.py`

## Implementation recipe

1. Create the src-layout Python 3.12 package and an ssr console entry point. Keep import-time work free of database connections, parser initialization and network access.
2. Declare the selected parser pins and application dependencies from architecture.md. Resolve/freeze once using uv; install Semgrep CE in a separate tool environment and record its executable version/digest. Do not add agent/provider dependencies.
3. Define a strict TOML settings model with defaults from contracts/v1/defaults.toml. Load secrets only from named SSR environment variables, never target files; reject unknown settings with the shared actionable error format.
4. Add a PostgreSQL 17 development Compose service with a persistent local volume and loopback-only port. Read the password from a developer-supplied environment variable; do not commit credentials. A direct DSN remains supported.
5. Implement ssr doctor to verify Git HTTPS support, PostgreSQL connectivity/version, each grammar capsule, a minimal syntax/query probe, regex/glob behavior, and the Semgrep CLI capabilities. It must report missing prerequisites, not silently drop a language.
W01 probes installed grammar support only. Language-specific extraction queries are introduced and registered by W07–W11; W01 must not depend on those later files.

6. Add import-linter boundaries reflecting architecture.md. Build a wheel and test installation outside the checkout so grammar/query/rule resources are actually packaged.

## Verification commands

These are the required implementation commands/test targets; they are not claims that tests already exist or were run while writing this specification.

```sh
uv sync --frozen
uv run pytest tests/packaging tests/config
uv run python -m build
ssr doctor --json
```

## Acceptance evidence

- An installed wheel exposes the same CLI without cwd-dependent imports.
- All declared languages load their grammars; a missing grammar produces a prerequisite error.
- Changing working directory does not cause target configuration to be read.

## Stop condition and receipt

No capture implementation, database result schema, worker pool or agent runtime in this task.

Complete W01 only after its real entry-point/owner tests pass. Record implemented requirement IDs, changed files, actual command results, unrun checks and the commit in IMPLEMENTATION_RECEIPT.md. Commit/push when authorized; do not silently advance the next task or add another planning document.
