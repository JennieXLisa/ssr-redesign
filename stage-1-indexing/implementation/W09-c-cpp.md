# W09 — Add C/C++ structure and compiler binding observations

Depends on: W07. Owner: languages.c, languages.cpp and resolution.clang.

Requirement traceability: S1-FN-R03, S1-FN-R05, S1-FN-R06, S1-FN-R07, S1-FN-R09, S1-RF-R03, S1-RF-R04.

## Read before editing

Read ../IMPLEMENTATION.md, the specification sections for this capability, and the directly related contracts. Reuse settled types/algorithms; do not restart a repository-wide architecture survey.

## Intended files and boundary

- `src/ssr/languages/c/`
- `src/ssr/languages/cpp/`
- `src/ssr/resolution/clang.py`
- `tests/languages/test_c_cpp.py`
- `tests/resolution/test_clang.py`

## Implementation recipe

1. Extract declarations/definitions, nested scopes, templates, overload signatures, methods/operators, constructors/destructors, lambdas and call argument ranges with the pinned C/C++ grammars.
2. Distinguish function-pointer variable declarations from callable declarations. Preserve preprocessor source locations and mapping limitations.
3. Integrate the selected libclang distribution in a worker process using read-only snapshot materialization. Parse captured compilation database data through the explicit flag whitelist and path remapper.
4. Collect cursor USRs, declaration/definition associations and call references, mapping them back to structural occurrences by original file/range. Do not publish a compiler guess under binding errors.
5. Stage observations by translation-unit context, ready for W12 per-physical-reference reconciliation. Retain external identities and context limitations without creating captured external files.
6. Prove the explicit new Test/member-call fixture and its overload/shadowing/reassignment/missing-header counterexamples.

## Verification commands

These are the required implementation commands/test targets; they are not claims that tests already exist or were run while writing this specification.

```sh
uv run pytest tests/languages/test_c_cpp.py tests/resolution/test_clang.py tests/capture/test_untrusted_compile_database.py
```

## Acceptance evidence

- The captured-header Test::something example binds and opens its exact definition.
- Overloads/virtual/context disagreements are not arbitrarily collapsed.
- Compiler database command/plugin/response-file input never executes or imports outside source.

## Stop condition and receipt

No compiling/running the reviewed program, unrestricted build commands or taint graph.

Complete W09 only after its real entry-point/owner tests pass. Record implemented requirement IDs, changed files, actual command results, unrun checks and the commit in IMPLEMENTATION_RECEIPT.md. Commit/push when authorized; do not silently advance the next task or add another planning document.
