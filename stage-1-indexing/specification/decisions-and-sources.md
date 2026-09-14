# Delegated implementation decisions and sources

The researcher authorized completion of the remaining specification without another approval for every routine choice. This edition chooses concrete mechanisms under that authority. It does not rewrite the agreed source scope or call earlier proposed features approved unless they were actually accepted.

## Decisions resolved in this edition

| Area | Decision and rationale |
|---|---|
| Primary storage | PostgreSQL 17 and managed bare Git; permanent ownership, not a SQLite migration plan. |
| Code graph | Normalized occurrence/binding tables with one-hop queries. No Joern or taint engine. |
| Model work | None in Stage 1. Human-directed threat modeling and analysis are outside this implementation. |
| Languages | Preserve Python, JS/JSX, TS/TSX, PHP, C, C++, Java, Lua, shell/Bash and Zsh. Structural and semantic capabilities are reported separately. |
| Binding precision | Finite conservative binding rules plus libclang for C/C++. No name-only calls promoted into proven bindings, and no claim of full runtime call-graph completeness. |
| Rule changes | New immutable flagging dataset/run; reuse compatible extraction and resolution datasets. |
| Continuations | Self-contained, validated JSON/base64url tokens. Not authentication capabilities. No cursor sessions or key-management subsystem. |
| Source response | 50,000-byte default; 1,000,000-byte maximum initial override; complete compact JSON payload accounting; no source-size limit. |
| Live metadata | Reserve worst-case numeric/boolean metadata lengths before fixing source sections, so live counters cannot enlarge a token's source interval. |
| Search patterns | `regex` VERSION1 Unicode search; whole-name wildcard matching. Names remain local only. |
| Context-sensitive build flags | Accept captured compilation databases as data, sanitize them, never run command strings or target build scripts. |
| Capture publication | Git objects/ref first, PostgreSQL READY record second, idempotent reconciliation after a crash; not a fictional distributed transaction. |
| Parser error nodes | Failed structural extraction with diagnostics; source remains readable. Deterministic syntax failure is not automatically retried forever. |
| Scope controls | No automatic vendor/build/generated exclusions. Gitignore, missing opted-out submodules, unresolved LFS content and boundary links remain explicit. |
| Transport | Public HTTPS, no ambient credentials, TLS verification, public-address pinning, redirects rejected with a resubmission diagnostic. |
| Scheduling | Ordinary local parallel worker pools backed by durable database work rows. No distributed queue service, no newly imposed one-run restriction. |

The upper response bound is a new transport-safety setting, not a reversal of the 50 KB default or a limit on captured/indexed source. The conformance tests distinguish every transport bound from analysis completeness. Regex timeouts and scanner failures are explicit failed operations, not no-match results.

## Primary sources consulted

External sources support tool behavior, not the correctness of SSR's proposed architecture. Accessed 14 September 2026. Version-specific details must be checked against the W01 lock and capability fixture; this package does not claim to have installed the future production environment.

- S1: Original harness dependency declaration, read-only commit `0989172`, `JennieXLisa/source-review-harness/pyproject.toml`. GitHub repository source; retained parser baseline only, not inherited architecture.
- S2: Tree-sitter Python bindings and QueryCursor API: https://tree-sitter.github.io/py-tree-sitter/ and https://tree-sitter.github.io/py-tree-sitter/classes/tree_sitter.QueryCursor.html
- S3: Python 3.12 AST documentation, including AST column/UTF-8 offsets: https://docs.python.org/3.12/library/ast.html
- S4: libclang cursor/type/reference API tutorial: https://clang.llvm.org/docs/LibClang.html
- S5: Compilation database object/arguments specification: https://clang.llvm.org/docs/JSONCompilationDatabase.html
- S6: PostgreSQL 17 SELECT/locking documentation: https://www.postgresql.org/docs/17/sql-select.html
- S7: psycopg 3 transaction management: https://www.psycopg.org/psycopg3/docs/basic/transactions.html
- S8: Git config, protocol/credential isolation, TLS, redirect controls and `http.curloptResolve`: https://git-scm.com/docs/git-config
- S9: Git raw object reads: https://git-scm.com/docs/git-cat-file ; raw object creation and index construction: https://git-scm.com/docs/git-hash-object and https://git-scm.com/docs/git-update-index
- S10: Semgrep CLI, suppression/size/timeout defaults, JSON output and local rules: https://docs.semgrep.dev/cli-reference
- S11: `regex` package behavior and timeout support: https://pypi.org/project/regex/

No performance claim in this package is an M5/i9 benchmark. W15 measures the finished pipeline at 2, 4, and 8 workers on a pinned repository and selected rule manifest. Do not translate hardware core count into a promised indexing duration.
