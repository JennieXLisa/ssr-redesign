# W10 — Add Java and PHP adapters

Depends on: W07. Owner: languages.java and languages.php.

Requirement traceability: S1-IN-R08, S1-FN-R02, S1-FN-R03, S1-FN-R05, S1-FN-R09, S1-RF-R02, S1-RF-R03.

## Read before editing

Read ../IMPLEMENTATION.md, the specification sections for this capability, and the directly related contracts. Include [language-policies.md](../specification/language-policies.md), `contracts/v1/records.py`, and Java/PHP cases in `contracts/v1/language-fixtures.json`. Reuse settled types/algorithms; do not restart a repository-wide architecture survey.

## Intended files and boundary

- `src/ssr/languages/java/`
- `src/ssr/languages/php/`
- `tests/languages/test_java.py`
- `tests/languages/test_php.py`

## Implementation recipe

1. Implement the Java construct mapping including constructors, lambda expressions, anonymous-class methods, records and namespace/import ownership.
2. Implement PHP mixed and PHP-only parsing, functions/methods/closures/arrows, classes/traits/interfaces, namespaces/use aliases and receiver/argument locations.
3. Record declared types, access modifiers and source ranges without replacing unavailable semantic type information with defaults. Follow the Java method-versus-variable namespace policy and PHP function/variable/use-function distinctions; retain writes and conditional declaration availability for W12.
4. Reuse deterministic IDs, common errors and publication. Add separate fixtures for language-specific ownership and parse errors.
5. Prove both adapters through the worker-to-published-index path, not only grammar node matching. Use the shared golden comparator on actual extraction projections; include Java anonymous-class/lambda ownership and both mixed and PHP-only input modes. W12 compares final binding projections.

## Verification commands

These are the required implementation commands/test targets; they are not claims that tests already exist or were run while writing this specification.

```sh
uv run pytest tests/languages/test_java.py tests/languages/test_php.py tests/languages/test_conformance.py
```

## Acceptance evidence

- Mixed PHP/HTML keeps actual PHP callables and correct byte offsets.
- Java anonymous-class methods do not become the outer method body.
- All shared conformance obligations pass.
- Compile the actual pinned grammar queries and match the Java/PHP source fixtures. Running the authored corpus integrity test is not evidence that these adapters or PHP capsules were executed.

## Stop condition and receipt

No Maven/Gradle/Composer execution, dependency downloads or target runtime.

Complete W10 only after its real entry-point/owner tests pass. Record implemented requirement IDs, changed files, actual command results, unrun checks and the commit in IMPLEMENTATION_RECEIPT.md. Commit/push when authorized; do not silently advance the next task or add another planning document.
