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
3. Adopt contracts/v1/settings.py and defaults.toml with configuration-and-processes.md's exact installation/project paths, precedence, separate explicit JSON semantic profile and unknown-field behavior. Load secrets only from named SSR environment variables, never target files; reject unknown settings with the shared actionable error format.
4. Add a PostgreSQL 17 development Compose service with a persistent local volume and loopback-only port. Read the password from a developer-supplied environment variable; do not commit credentials. A direct DSN remains supported.
5. Implement ssr doctor using configuration-and-processes.md's concrete probes for real Git HTTPS/TLS/pinning, PostgreSQL connectivity/version, each grammar capsule, syntax/query behavior, regex/glob behavior, libclang and the exact Semgrep invocation/no-network boundary. Emit version/digest/capability receipts. Version/help output alone is insufficient. Report missing prerequisites, not silently drop a language.
W01 probes installed grammar support only. Language-specific extraction queries are introduced and registered by W07–W11; W01 must not depend on those later files.

6. Build/package `processes.runner`, isolation policies and the small trusted native launcher from [native-isolation.md](../specification/native-isolation.md). On macOS use the exact Seatbelt policy and tested OS receipt; on Linux/WSL use the specified bubblewrap, Landlock and seccomp sequence and fixed runtime capsule. Fail missing enforcement/readiness; do not substitute environment flags. Prove allowed reads and denied filesystem/network/exec operations before running actual tool probes. This is SSR helper compilation, not reviewed-source execution.
7. Add import-linter boundaries reflecting architecture.md. Build a wheel and test installation outside the checkout so grammar/query/rule/native-policy resources are actually packaged.

## Verification commands

These are the required implementation commands/test targets; they are not claims that tests already exist or were run while writing this specification.

```sh
uv sync --frozen
uv run pytest tests/packaging tests/config
uv run pytest tests/processes/test_isolation.py tests/processes/test_doctor_tools.py
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
