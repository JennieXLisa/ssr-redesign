# W09 — Add C/C++ structure and compiler binding observations

Depends on: W07. Owner: languages.c, languages.cpp and resolution.clang.

Requirement traceability: S1-FN-R03, S1-FN-R05, S1-FN-R06, S1-FN-R07, S1-FN-R09, S1-RF-R03, S1-RF-R04.

## Read before editing

Read ../IMPLEMENTATION.md, [the strict compiler profile](../specification/compiler-profile.md), [durable compiler work](../specification/compiler-work.md), the C/C++ section of resolution.md, and `contracts/v1/compiler_records.py`. Reuse settled types/algorithms; do not restart a repository-wide architecture survey.

## Intended files and boundary

- `src/ssr/languages/c/`
- `src/ssr/languages/cpp/`
- `src/ssr/resolution/clang.py`
- `src/ssr/storage/compiler_contexts.py` (uses the shared transaction/lease/publication owner)
- `tests/languages/test_c_cpp.py`
- `tests/resolution/test_clang.py`

## Implementation recipe

1. Extract declarations/definitions, nested scopes, templates, overload signatures, methods/operators, constructors/destructors, lambdas and call argument ranges with the pinned C/C++ grammars.
2. Distinguish function-pointer variable declarations from callable declarations. Preserve preprocessor source locations and mapping limitations.
3. Integrate the selected libclang distribution through [native-isolation.md](../specification/native-isolation.md)'s installed runner, fixed compiler worker, resource policy and readiness gate. Implement compiler-profile.md's exact option grammar, POSIX data tokenizer and no-follow inventory remapping. Reject invalid contexts atomically; do not run compilation commands or silently strip rejected flags. Actual file-access/executable-mapping/network denial tests are required in addition to argument validation.
4. Collect cursor USRs, declaration/definition identity evidence and call references, mapping them back to structural occurrences by original file/range. Do not publish a compiler guess under binding errors.
5. Implement compiler-work.md's input census from captured commands or typed CompilerOptions before allocating context IDs; keep all rejected/default contexts and persist the exact effective hash payload. After complete extraction freeze actual C/C++ reference anchors, then claim separate resolution-owned context work. Publish typed complete file visits, positive inactive evidence, exact entity/reference anchors and publication-bound diagnostics through the common fenced owner. W09 evidence is readable only through visible_compiler_publications. Retain external identities and context limitations without creating captured external files or unmapped structural references.
6. Prove the explicit new Test/member-call fixture produces the correct mapped staged observation, declaration USR and matching definition observation/range. Cover overload/shadowing/reassignment/missing-header counterexamples, hostile compiler input and unmapped cursors. The staged evidence is this task's acceptance boundary; W12 owns final reconciliation, SAME_ENTITY association and the exact definition read through public navigation.

## Verification commands

These are the required implementation commands/test targets; they are not claims that tests already exist or were run while writing this specification.

```sh
uv run pytest tests/languages/test_c_cpp.py tests/resolution/test_clang.py tests/capture/test_untrusted_compile_database.py
uv run pytest tests/storage/test_compiler_contexts.py tests/indexing/test_compiler_context_recovery.py
```

## Acceptance evidence

- The captured-header Test::something example stages its mapped member-call/declaration reference and matching definition USR/range from the captured implementation file. This test uses W09's real adapter entry point and staging owner; it does not depend on W12's association/navigation implementation.
- Overloads/virtual/context disagreements are not arbitrarily collapsed.
- Compiler database shell/plugin/response-file/unknown-option input yields explicit invalid-context diagnostics; validated flags retain macro values and include order. No target command executes. Include and frontend file access stays within the verified snapshot and explicit toolchain resource boundaries.
- A missing header or invalid context retains structural references with binding limitations; library startup/worker/isolation failures are FAILED work. Unmapped/multiply mapped cursors never become guessed captured references.
- Restore the exact frozen context/reference census and resume after interrupted staging. Prove invalid-context publication, stale lease/retry fencing, ignored abandoned diagnostics, and lossless manifest reconstruction against disposable PostgreSQL. Reference-policy regressions alone do not satisfy this database/adapter gate.
- W12 remains responsible for proving the same member-call fixture's final declaration/definition association and exact captured definition read; W09 completion does not claim that later gate has passed.

## Stop condition and receipt

No compiling/running the reviewed program, unrestricted build commands or taint graph.

Complete W09 only after its real entry-point/owner tests pass. Record implemented requirement IDs, changed files, actual command results, unrun checks and the commit in IMPLEMENTATION_RECEIPT.md. Commit/push when authorized; do not silently advance the next task or add another planning document.
