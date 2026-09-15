# Language extraction and binding policies

Read with [extraction.md](extraction.md), [resolution.md](resolution.md) and
[`records.py`](../contracts/v1/records.py). W07–W11 produce observations; W12
produces final bindings after the inventory barrier. These are finite navigation
rules, not an interpreter or a promise to identify every runtime target.

## Shared recipe and record meaning

For each original file, create the module scope first. Walk declaration syntax
and executable expressions separately: discover every callable/type occurrence,
then assign lexical declarations and expression evaluation scopes. Preserve
original-byte half-open ranges, including CRLF; apply SourceUnit's boundary map
before constructing any record. A callable body owns its operations, while a
default, decorator, computed name or capture initializer can belong elsewhere.
Scope ancestry is syntactic; symbol lookup uses the language rules below rather
than blindly walking that ancestry. Do not execute captured source.

Use `DeclarationRecord` for symbols, parameters, imports and all writes/deletes
that can shadow or invalidate them. `namespace` separates type-only bindings
from values. `whole_scope` means the name shadows throughout its scope, not that
its value is initialized throughout it. `visible_from` is the original-byte
boundary at which a straight-line declaration/initializer completes; initialized
hoisted declarations use the scope start. `tdz` also blocks fallback to an outer
name before initialization. `after_declaration` starts lookup eligibility there;
`dynamic` supplies a shadow/invalidation fact without proving availability.
Global/nonlocal redirect records are interpreted before ordinary local lookup.

An assignment record has no callable target unless the adapter has explicit
support for that syntax and evidence. Emit writes from destructuring, augmented
assignment, loop/exception binders, deletes and imports too. Stop on the nearest
applicable non-callable/unknown binding; never continue outward to a convenient
same-name function. A conditional write, escaping receiver, unknown mutation or
ambiguous initialization prevents the constructor shortcut. For deferred bodies,
inspect possible writes in the captured enclosing scope, including textually
later writes: source offset alone does not establish execution order across a
closure boundary. Unsupported dynamic scope mutation leaves a diagnostic and
`UNRESOLVED / DYNAMIC_TARGET`, not a fabricated link.

Source access modifiers and exports are distinct from lexical visibility. Record
explicit applicable modifiers with declared origin and source evidence. Missing
modifiers are unknown unless a versioned language rule establishes the default;
that fact is inferred with rule/backend provenance. Do not manufacture public,
static, return types, synthetic constructors, names or bodies to fill fields.
Anonymous callable expressions use kind `LAMBDA` and `local_name=null`; a named
function expression uses its actual inner name. Assignment names and export
aliases belong in declaration/import records, not in anonymous local names.

## Python (W07)

Prescan each function for parameters, assignments, deletes, imports, nested defs,
loop/with/exception/pattern binders and global/nonlocal directives. Function-local
names shadow for the whole function even before assignment. Resolve an unchanged
direct nested def after its definition, or recursion from its own body. A local
assignment to `f` anywhere blocks an outer `f()` before that assignment; retain
that call as unresolved rather than predicting an exception or a target. Global
uses the module table; nonlocal uses the nearest enclosing function binding.
Class bodies execute in their own namespace, but method bodies do not inherit
class attributes as unqualified lexical locals. Comprehensions have their own
scope; unsupported annotation/lazy-evaluation ownership emits an ownership
limitation rather than attributing execution to the function body. [LP1]

Record decorators and default expressions in the enclosing evaluation scope;
the function range includes decorators. A lambda has its own expression body.
Map `import a as b` and `from .a import f as g` through captured package boundaries
and retain alias records. A unique captured declared export gives
`CAPTURED_IMPORT`; missing capture/package evidence gives `MISSING_IMPORT` or
`EXTERNAL_SOURCE_NOT_CAPTURED`. Wildcard imports, dynamic import hooks, computed
`__all__`, monkey-patching and writes to imported names do not establish targets.
Do not import modules to inspect them. Preserve declared underscore names;
underscores are not access-control evidence.

## JavaScript / JSX (W08)

Predeclare parameters and hoisted function/`var` names in the appropriate
function/module scope. Lexical `let`/`const`/class bindings occupy their block's
TDZ until initialization; an earlier call cannot fall back to an outer binding.
`var` is initialized without a callable value, so only its supported initializer
can establish a target. Named function-expression names belong to the inner
function, while an outer variable assigned an arrow remains a variable binding.
Block functions follow the frozen strict/module mode; unsupported legacy sloppy
block semantics remain unresolved. Parameters and assignment patterns shadow
equally named outer functions. [LP2]

Resolve unique direct declarations and explicit relative ES imports/exports with
the fixed captured-path policy in resolution.md. Track named/default aliases and
re-exports, detect cycles, and retain conflicting star exports as candidates;
an export name does not itself create an extra function symbol. Literal CommonJS
require/module.exports patterns require a frozen CommonJS profile, unshadowed
loader/export names and no writes; otherwise retain observations only. Dynamic
imports, computed properties, reassignment, `eval` and unknown prototype mutation
invalidate shortcuts. JSX element names are not synthetic calls; actual calls
inside expression containers retain their evaluation owner. Arrow bodies own
their calls, while computed method names are evaluated outside those bodies.

## TypeScript / TSX (W08)

Apply the JS rules plus separate type/value lookup tables. Interfaces and aliases
create type bindings; `import type`/`export type` cannot supply a value-call
target. Classes/enums may have both namespace entries without inventing two
source occurrences. Preserve overload signatures as separate declaration
occurrences with null bodies; an implementation is another occurrence. Name or
arity alone does not select an overload or establish SAME_ENTITY. Keep multiple
supported signatures candidate-only until a supported semantic backend proves
the choice. Ambient declarations are readable declarations, not executable
implementations. Namespace merging and conditional/generic types require
explicit identity/type support; syntax alone does not prove them. [LP3]

Use the TSX capsule for TSX, with the same JSX ownership rule. Source annotations
are declared type facts, not inferred runtime receiver types. Respect parameter
and block shadowing in the value namespace even when a same-name type exists.

## C / C++ (W09 observations; W12 final bindings)

Walk declarators outward from the declared identifier to distinguish callable
declarations from variables holding function pointers. Preserve prototype-only
occurrences with null body; C++ templates, cv/ref qualifiers, operators and
overloads keep distinct occurrences. Record lexical block/namespace/type scopes,
internal-linkage/static and access evidence. No repository-wide name match may
cross translation units or namespaces. Preprocessor branches remain original
source observations; compiler context determines which binding evidence applies.

W09 emits sanitized translation-unit cursor/reference/USR observations using
physical file/range correspondence. These can establish a declaration and its
definition as the same compiler entity without publishing W12's final groups or
caller/callee results. Out-of-class member definitions retain W09's specified
structural ownership and explicit qualifier evidence; never move their physical
source into the header or invent a containing class span in another file.
W12 reconciles all contexts and publishes SAME_ENTITY plus final navigation.
The `cpp-test-member` fixture requires this positive path for the exact statement
`auto obj = new Test(); obj->something();`. [LP4]

Compiler-confirmed references use `CLANG_REFERENCE`; missing headers or flags
give `MISSING_BUILD_CONTEXT`. Function pointers, casts, aliases, overload/virtual
dispatch or reassigned receivers cannot be resolved through name/arity guesses.
For a supported compiler declaration reference distinguish static declaration
navigation from a claim about a unique runtime override. Conflicting supported
translation-unit observations are `AMBIGUOUS / CONTEXT_DISAGREEMENT`; a single
unproven guess is unresolved. Headers alone do not supply universal build context.

## Java (W10)

Create package/type/method/block scopes, parameter/local bindings, explicit
constructors, lambdas and anonymous-class methods. Method-name lookup is distinct
from variable lookup: a local variable is not automatically a shadowing method
declaration. Nested classes have their own member tables. Imports name captured
types or static members; wildcard imports need a unique supported captured
candidate, not a search through every file. Preserve access/static/final source
modifiers, overload signatures, and separate constructors. [LP5]

Resolve an accessible unique static/private direct method when no overload or
dispatch uncertainty remains. Declared receiver types establish member
declarations only under the supported member policy; interface/virtual dispatch,
overloads, reflection and reassignment retain candidates/limitations. A literal
constructor initializer is invalidated by conflicting writes/escapes. Method and
lambda bodies own their calls; constructor arguments are evaluated by the caller.
Anonymous-class methods belong to that class, never to the enclosing method.
Initializer/annotation ownership not represented by the current scope model must
emit `OWNERSHIP_LIMITATION`, not a fabricated `<init>` callable.

## PHP (W10)

Maintain namespace/class/function scopes and distinguish variable names from
function/class names. Preserve source spelling; the name resolver uses PHP's
case rules for the relevant name category, not a universal casefold. Unconditional
named function declarations have namespace visibility independent of textual
call order; conditional/nested declarations require execution and therefore
cannot be treated as hoisted lexical locals. Parameters/local variable writes
shadow variable-call expressions, not ordinary namespace function names. [LP6]

Resolve fully qualified names, `use function` aliases, and namespace-qualified
names through captured declarations. Apply PHP's unqualified function fallback
only with sufficient captured namespace/global evidence. Class imports are not
function imports. Literal includes supply source links; conditional/computed
includes and autoloaders do not prove runtime availability. Variable functions,
dynamic member names, reference captures and writes invalidate direct shortcuts.
Closure `use` captures and arrow implicit captures belong to their callable;
capture syntax does not prove the captured value is a function. Named methods
keep class ownership and actual access modifiers. Mixed HTML contributes bytes
but no PHP callable or command of its own. [LP6–LP8]

## Lua (W11)

Create chunk/block/function scopes. A local becomes visible after its declaration;
`local x = x` reads the previous outer binding in its initializer. Handle
`local function f` specially so its own body can refer to the local `f`.
Ordinary `function f` assigns a name rather than declaring a universally hoisted
function. Parameters/upvalues and later writes govern direct-call eligibility.
Colon definitions record the declared member name and implicit receiver evidence;
do not create a class from a table. Anonymous table function values retain null
local names. Calls inside them belong to those functions. [LP9]

Literal unshadowed `require` records a module link using resolution.md's captured
path rules. It does not prove a returned table's member target, simulate
`package.path`, inspect `_ENV`, or run module code. Constant table-member support
needs explicit initialization/no-mutation evidence; computed keys, metatables,
reassigned names/tables and branch-dependent definitions remain unresolved.
Lua has no source access modifier or ES-style export declaration to fabricate.

## Bash / shell and Zsh (W11)

Record script/module commands and each function body separately. Function
definitions become available when their definition executes; syntactic nesting
does not imply lexical function visibility. The finite positive case is a literal
same-script function defined unconditionally before a straight-line command,
with no competing definition, unset, alias/eval/source mutation or dispatch
override. Dynamic command words and calls whose availability depends on a branch,
autoload or caller environment stay unresolved. `command`/`builtin` prefixes must
not turn a same-name user function into the target. A local shell variable named
`f` is not a lexical declaration of the command `f`. [LP10–LP11]

Record literal `source`/`.` paths as links only through captured files. Propagate
definitions only for an explicitly supported unambiguous straight-line source
case with a frozen path basis; no ambient PATH/cwd or execution. Commands inside
command/process substitutions retain the nearest callable/module owner; these
substitutions are not invented functions. Shell expansion text is preserved.
Use the dedicated Zsh grammar. Its anonymous functions have null local names and
own their body commands; Zsh explicitly invokes this construct immediately, unlike
an ordinary lambda expression. W11 must verify its syntactic invocation mapping
against the installed grammar before emitting an outer invocation record. [LP11]

## Grammar and implementation gates

This file intentionally provides semantic handlers, not unverified Tree-sitter
query/node names. Use the versions selected in architecture.md and installed by
W01. For each capsule, record package version/digest, grammar ABI, and the exact
shipped/generated `node-types.json` digest; inspect its fields before authoring
queries. Compile packaged queries and run node-shape fixtures under that same
lock. `node-types.json` describes named types/fields, not language binding rules.
The Tree-sitter documentation describes this resource. [LP12]

No locked runtime adapters or compiled query resources were executed to author
this corpus. Their creation, installed-wheel/resource checks and real
registry → adapter → bundle validation → publication tests remain W07–W11 gates.
Zsh anonymous forms and PHP's mixed/php-only selection require their own probes;
a failing probe is a visible gate, never permission to silently drop a dialect.

## Executable golden format and reuse

[`language-fixtures.json`](../contracts/v1/language-fixtures.json) contains actual
UTF-8 source strings. Encode them exactly, without newline normalization. Each
span stores `start_byte`, `end_byte`, and the exact selected `text`. Keys are
fixture locators `path@start:end:kind`, not production UUIDs. Runtime tests map
real IDs to these locators using captured file and physical occurrence ranges.

`expected.extraction` is a complete projection of callable/type occurrences
(excluding MODULE/VARIABLE symbols), invocation/callback references, import/export
records and file statuses. Project each symbol occurrence separately. `owner` is
the nearest enclosing callable/type occurrence for symbols, and the evaluation
callable for references; null is the module. Do not attribute deferred bodies by
range alone. Named scope details and the full internal records still must pass
`ExtractionBundle` validation; this projection supplements it. `body=null` on a
declaration is an assertion, not a field to omit. Parser-error fixtures expect
FAILED and no structural inventory; exact backend-specific error text/ranges are
checked by the actual bundle/diagnostic tests after grammar pinning.
Reference `spelling` contains the complete original expression selected by
`range`; `callee` separately identifies its callee text/range. For example,
`spelling="obj.method()"` and `callee.text="obj.method"` are distinct assertions.

`expected.resolution` contains final binding outcomes/bases/targets and proven
association pairs. Normalize target IDs through proven associations to the
lexicographically smallest physical locator solely for test comparison; do not
change production's UUID representative rule. Compiler observations have their
own phase; navigation expectations appear on the C++ positive fixture. A fixture
with a failed file has no final resolution phase, preserving the inventory barrier.

Import `load_fixtures` and `assert_fixture` from
[`reference_language_fixtures.py`](../validation/reference_language_fixtures.py).
Call `assert_fixture(case, actual_projection, phase="extraction")` on the actual
published output, then use `resolution`, `compiler_observations` or `navigation`
at the owning task boundary. The comparator rejects missing/extra records and
wrong names, owners, spans, argument order, targets and outcomes. It never parses
source or derives expected bindings from the actual implementation.

Run the executable corpus checks with:

```sh
python stage-1-indexing/validation/regressions/test_language_fixtures.py
```

To compare an independently produced projection saved as JSON:

```sh
python stage-1-indexing/validation/reference_language_fixtures.py \
  --fixture cpp-test-member --phase navigation --actual actual-navigation.json
```

These checks validate authored byte spans, cross-record integrity and comparator
failure behavior. Passing them is **fixture self-consistency, not parser,
resolver, publication or navigation integration evidence**. The corpus supplies
concrete regression seeds; the broader mandatory matrix in extraction.md remains
a release gate, including full per-language Unicode/CRLF and node-shape coverage.

## Primary language resources

Consulted 16 September 2026. SSR's conservative capability choices above are
design rules; these primary resources support the underlying language semantics.

- LP1: Python 3.12 execution model: https://docs.python.org/3.12/reference/executionmodel.html
- LP2: ECMAScript 2024 environments and functions: https://tc39.es/ecma262/2024/multipage/executable-code-and-execution-contexts.html and https://tc39.es/ecma262/2024/multipage/ecmascript-language-functions-and-classes.html
- LP3: TypeScript module reference, including type-only imports: https://www.typescriptlang.org/docs/handbook/modules/reference.html
- LP4: libclang cursor/type/reference API: https://clang.llvm.org/docs/LibClang.html
- LP5: Java SE 21 names/scopes: https://docs.oracle.com/javase/specs/jls/se21/html/jls-6.html
- LP6: PHP namespace resolution and named functions: https://www.php.net/manual/en/language.namespaces.rules.php and https://www.php.net/manual/en/functions.user-defined.php
- LP7: PHP closures: https://www.php.net/manual/en/functions.anonymous.php
- LP8: PHP arrows: https://www.php.net/manual/en/functions.arrow.php
- LP9: Lua 5.4, sections 3.3.7, 3.4.11 and 3.5: https://www.lua.org/manual/5.4/manual.html
- LP10: Bash function/command semantics: https://www.gnu.org/software/bash/manual/html_node/Shell-Functions.html and https://www.gnu.org/software/bash/manual/html_node/Command-Search-and-Execution.html (upstream fetch timed out during this review; W11 must verify against its installed Bash documentation).
- LP11: Zsh functions, including anonymous invocation: https://zsh.sourceforge.io/Doc/Release/Functions.html
- LP12: Tree-sitter static node-type resource: https://tree-sitter.github.io/tree-sitter/using-parsers/6-static-node-types
