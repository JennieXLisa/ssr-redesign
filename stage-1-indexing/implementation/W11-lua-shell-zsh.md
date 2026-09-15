# W11 — Add Lua, Bash/shell and Zsh adapters

Depends on: W07. Owner: languages.lua, languages.bash and languages.zsh.

Requirement traceability: S1-IN-R08, S1-FN-R02, S1-FN-R09, S1-RF-R02, S1-RF-R03.

## Read before editing

Read ../IMPLEMENTATION.md, the specification sections for this capability, and the directly related contracts. Include [language-policies.md](../specification/language-policies.md), `contracts/v1/records.py`, and Lua/Bash/Zsh cases in `contracts/v1/language-fixtures.json`. Reuse settled types/algorithms; do not restart a repository-wide architecture survey.

## Intended files and boundary

- `src/ssr/languages/lua/`
- `src/ssr/languages/bash/`
- `src/ssr/languages/zsh/`
- `tests/languages/test_lua_shell.py`

## Implementation recipe

1. Implement Lua named/local/anonymous functions, table and colon-method ownership, call expressions and literal require records.
2. Implement Bash functions, top-level commands, command/process substitutions and literal source relationships using the Bash grammar.
3. Implement Zsh using its own pinned grammar and packaged queries; do not switch to Bash to suppress Zsh parse failures.
4. Emit the language-policy declarations and invalidations: Lua local visibility differs from local-function recursion; shell function availability depends on definition/source execution and is not lexical merely because definitions are nested. Preserve expanded command words, builtin/dispatch prefixes and conditional definitions for conservative W12 binding.
5. Run the common span/ownership/error suite with shebang-based extensionless scripts and known dotfiles. Compare actual published extraction projections to the authored language goldens; verify Zsh anonymous-function invocation and its body ownership under the dedicated installed grammar. W12 compares the separate final binding projections.

Apply [language-profiles.md](../specification/language-profiles.md)'s exact mapping:
`shell_mode` must match the source dialect and becomes the frozen Bash/Zsh
selection; `cwd_snapshot` becomes a captured directory basis for source-link
resolution. A null cwd is unknown, never the worker cwd. Dialect changes alter
extraction identity; cwd-only changes alter resolution identity. Lua rejects
shell-only settings. Test real grammar selection and profile-aware source links
without executing or sourcing any target script.

## Verification commands

These are the required implementation commands/test targets; they are not claims that tests already exist or were run while writing this specification.

```sh
uv run pytest tests/languages/test_lua_shell.py tests/languages/test_conformance.py
```

## Acceptance evidence

- Extensionless recognized scripts are classified without execution.
- Top-level commands have module ownership; nested callable bodies stay distinct.
- Zsh syntax is either correctly parsed or explicitly failed, never silently relabeled.
- Golden source cases cover colon/table functions, command/process substitutions, literal source links and expanded command negatives. Their executable integrity check does not compile queries or run adapters; provide installed-grammar and real publication evidence separately.

## Stop condition and receipt

No shell/source execution or simulated runtime command evaluation.

Complete W11 only after its real entry-point/owner tests pass. Record implemented requirement IDs, changed files, actual command results, unrun checks and the commit in IMPLEMENTATION_RECEIPT.md. Commit/push when authorized; do not silently advance the next task or add another planning document.
