# W11 — Add Lua, Bash/shell and Zsh adapters

Depends on: W07. Owner: languages.lua, languages.bash and languages.zsh.

Requirement traceability: S1-IN-R08, S1-FN-R02, S1-FN-R09, S1-RF-R02, S1-RF-R03.

## Read before editing

Read ../IMPLEMENTATION.md, the specification sections for this capability, and the directly related contracts. Reuse settled types/algorithms; do not restart a repository-wide architecture survey.

## Intended files and boundary

- `src/ssr/languages/lua/`
- `src/ssr/languages/bash/`
- `src/ssr/languages/zsh/`
- `tests/languages/test_lua_shell.py`

## Implementation recipe

1. Implement Lua named/local/anonymous functions, table and colon-method ownership, call expressions and literal require records.
2. Implement Bash functions, top-level commands, command/process substitutions and literal source relationships using the Bash grammar.
3. Implement Zsh using its own pinned grammar and packaged queries; do not switch to Bash to suppress Zsh parse failures.
4. Keep dynamic command/function expressions unresolved, preserving their exact source rather than pretending every word names an indexed function.
5. Run the common span/ownership/error suite with shebang-based extensionless scripts and known dotfiles.

## Verification commands

These are the required implementation commands/test targets; they are not claims that tests already exist or were run while writing this specification.

```sh
uv run pytest tests/languages/test_lua_shell.py tests/languages/test_conformance.py
```

## Acceptance evidence

- Extensionless recognized scripts are classified without execution.
- Top-level commands have module ownership; nested callable bodies stay distinct.
- Zsh syntax is either correctly parsed or explicitly failed, never silently relabeled.

## Stop condition and receipt

No shell/source execution or simulated runtime command evaluation.

Complete W11 only after its real entry-point/owner tests pass. Record implemented requirement IDs, changed files, actual command results, unrun checks and the commit in IMPLEMENTATION_RECEIPT.md. Commit/push when authorized; do not silently advance the next task or add another planning document.
