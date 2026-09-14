# Structural extraction and language adapters

Implements S1-IN-R08–R12, S1-IX-R01–R05, S1-FN-R01–R09 and S1-RF-R01–R03. Structural extraction is a complete traversal of included supported source, not an LLM summarization pass.

## Shared adapter interface

Each adapter implements `extract(source: SourceUnit) -> ExtractionBundle`. SourceUnit contains file/snapshot identity, original bytes, selected language, decoding/offset map and parser profile. The bundle contains symbols, source occurrences, scopes, imports, reference/call occurrences, ordered arguments and diagnostics. It performs no SQL, subprocess build, network I/O or publication. Parser instances are local to a worker process; do not share mutable parser state between threads.

Symbols contain stable ID, local name or null for anonymous constructs, qualified display name or generated label, kind, language, owner scope, signature, and declared/inferred/unknown properties. Occurrences contain their own IDs and declaration/definition/body/signature/name ranges. Parameters preserve ordinal, name, type-text/type-origin and default-expression range. Calls retain the expression/callee/receiver/argument ranges and syntactic usage kind even when unresolved. No mandatory complete AST or complete function source is stored in PostgreSQL.

Represent module-level executable source with a module scope, not a fabricated named function. Use the innermost executable owner for a call or flag. A nested lambda has its own owner; simply testing containment against an outer function's entire byte range is insufficient. Default-value expressions, decorators/annotations and lambda capture initializers belong to the context in which their expressions are evaluated when the adapter knows it; otherwise retain their enclosing syntax scope and an explicit ownership limitation. Do not assert that creating a lambda invokes its body.

## Exact construct mapping

| Language | Adapter inputs and required callable/type constructs |
|---|---|
| Python | `ast.parse` after `tokenize.detect_encoding`; FunctionDef, AsyncFunctionDef, Lambda, ClassDef, nested defs, decorators, parameter variants and annotations. Function ranges include decorators. `ast` positions refer to UTF-8 columns in its parse representation; map them to original bytes. |
| JavaScript / JSX | javascript grammar; function_declaration, function_expression, generator functions, arrow_function, method_definition, class declarations/expressions, import/export statements, call/new expressions. JSX syntax must not hide nearby callables. |
| TypeScript / TSX | correct TypeScript or TSX grammar capsule; JS callables plus signatures/overloads, constructors, interfaces, type aliases, namespaces, type parameters and modifiers. Declaration-only signatures have no body. |
| C | c grammar; function_definition, function declarators/prototypes, struct/union/enum declarations, typedefs, calls and preprocessor-located occurrences. Distinguish declarations from function-pointer variables. |
| C++ | cpp grammar; free/member/template functions, constructors/destructors, conversion/operators, qualified out-of-class definitions, lambdas, classes/structs, namespaces and overload signatures. Preserve template and cv/ref qualifiers. |
| Java | java grammar; method/constructor declarations, lambda_expression, class/interface/enum/record and anonymous-class methods, imports, invocation/object creation and modifiers. |
| PHP | php grammar for mixed PHP/HTML and php-only capsule where appropriate; functions, methods, anonymous/arrow functions, classes/traits/interfaces, namespaces/use, calls/member calls and closure uses. |
| Lua | lua grammar; function declarations/definitions/expressions, local functions, dotted/colon names, table-contained function expressions, calls and literal require occurrences. |
| shell / Bash | bash grammar; function_definition, command nodes, command/process substitutions and sourced-file references. Top-level commands belong to the script module. Builtins and dynamic command names remain distinguishable. |
| Zsh | zsh grammar, not Bash relabeling; functions, anonymous function forms supported by the pinned grammar, commands, substitutions and source references. Keep unsupported Zsh-specific constructs diagnostic rather than switching parsers silently. |

The table is a construct contract, not a portable list of identical AST node names. In each language task, inspect the pinned grammar's `node-types.json` and create tested query resources under that adapter's package. Use tree cursor traversal with field-aware handlers for scope/ownership; use Tree-sitter queries for recognizable constructs. Compile all packaged queries at installation test time. A grammar upgrade must rerun the node-shape fixtures. [S2–S3]

## Classification

Recognize `.py`, `.js/.mjs/.cjs/.jsx`, `.ts/.mts/.cts/.tsx`, `.php/.phtml`, `.c`, `.cc/.cpp/.cxx/.hpp/.hh/.hxx`, `.java`, `.lua`, `.sh/.bash` and `.zsh`, plus captured interpreter shebangs and known shell dotfiles. Handle `.h` by testing C and C++ grammar compatibility: select the unique successful grammar; if both succeed, choose C for shared declarations and record the ambiguity so C++ translation units can supply semantic context. A configured path-glob language override is authoritative and frozen in the extraction fingerprint. No filename or directory-name rule excludes source.

Text without a supported structural language stays available to text search/reading. Binary receives metadata. Language detection uncertainty is reported in metadata, not converted into fabricated symbols. HTML/configuration text is not automatically an additional supported programming language. Mixed PHP/HTML remains PHP through its proper grammar. Extensionless scripts can be classified by a recognized shebang; do not run them to identify the interpreter.

## Parse errors and completeness

For Tree-sitter, detect ERROR and missing nodes and capture their exact original-byte locations. A zero-symbol valid file is SUCCEEDED; a failed parse is FAILED, not the same empty bundle. Keep diagnostic source references without publishing a complete structural result. Python SyntaxError follows the same rule. Unsupported grammar syntax is a documented extraction failure for a supported file, not automatic reclassification as unsupported source to obtain a green run.

Partial queries see committed file-step bundles. A file whose extraction is in progress may have no visible outline yet; that is an explicitly partial result. Publishing whole file bundles is compatible with available-result querying and avoids half-owned nested functions. Resource exhaustion leaves failed/pending work and preserves all other completed files.

## Source transformation and location maps

Capture owns original bytes. Extraction may decode and produce a UTF-8 parser buffer, but must keep a monotone map of parser byte boundaries to original byte boundaries. BOM handling, CRLF and multibyte text must round-trip through source reading. Never persist a parser-buffer offset as if it were an original-byte offset. Store line-start information for original text during metadata preparation; derive readable coordinates consistently under source-reading.md.

Canonical qualified names are display context. Local names remain the only name-rule/search target. Anonymous labels use `lambda@path:line:column` or `anonymous@...`, with distinct occurrence IDs for same-line constructs; the label is not a declared name or identity key.

## Mandatory adapter fixtures

Every language supplies: a named callable; a nested/owned callable where supported; a declaration-only construct where applicable; two same-name scopes; an unresolved call; a known direct call; a multibyte/CRLF file; and a parser error. Languages supporting lambdas add nested and same-line lambda fixtures. C/C++ add function-pointer declarations, templates and header/implementation pairs. TS adds overload signatures and TSX. Java adds constructor and anonymous-class method. PHP adds mixed HTML. Shell/Zsh add substitutions and top-level commands. Lua adds colon methods and anonymous table functions.

For every recorded span, tests select original bytes and compare the expected source exactly. Test absence of fabricated bodies/names and ownership of calls inside nested bodies. Run the actual registry→adapter→bundle-validation→publication path, not only individual syntax handlers.
