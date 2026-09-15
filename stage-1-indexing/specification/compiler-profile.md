# Strict C/C++ compiler profile

This is the normative expansion of the C/C++ adapter in [resolution.md](resolution.md),
owned by `resolution.clang` and the snapshot materializer. It fixes the accepted
compiler-input language and the trust of observations; it does not authorize
building reviewed projects. The runnable, pure data model is
`validation/reference_compiler.py`. W09 implements and tests the real adapter;
W12 reconciles observations and publishes readable associations.

The durable workflow is [compiler-work.md](compiler-work.md), with typed internal
values in `contracts/v1/compiler_records.py`: frozen expected context/reference
censuses, separate resolution-owned context jobs, fenced active publications and
lossless source/USR/diagnostic projections. Sanitizer input identity is frozen
before resolution allocation; context results never feed extraction fingerprints.

## Frozen inputs and scope

Profile identifier: `strict-posix-clang-v1`. Freeze the captured compilation
database bytes, snapshot/tree identity, selected libclang binary/package identity,
resource-root identities/content versions, exact approved target triples, driver
labels, tokenizer version and this option grammar. The library is selected by
trusted application configuration; the source cannot select a library, executable
or resource installation. An approved driver label is only metadata and is never
executed or included in libclang's argument list.

The accepted command object has `directory`, `file`, either `arguments` or
`command`, and optional `output`. Unknown fields are rejected in this edition.
`directory` is an absolute POSIX directory in the captured source inventory.
`file` names a captured regular file, relative to that directory or absolute
beneath the recorded original source root. The source operand must identify that
same file. `output` is a nonempty string of bounded metadata, never a requested
write; retain `OUTPUT_METADATA_IGNORED`. Each object is one context. Distinct
objects for a file remain distinct provenance even when their effective profiles
deduplicate. These field meanings follow the Clang compilation database format;
SSR's accepted subset below is deliberately smaller. [C1]

`arguments`, when present, must be a JSON array of nonempty strings. Use its
elements exactly; do not shell-unquote, join/resplit, expand variables, read
response files, or fall back to `command` after invalid arguments. A coexisting
`command` is unexamined metadata with `COMMAND_IGNORED_ARGUMENTS_PREFERRED`.
Otherwise tokenize `command` with the policy below. Source arguments are never
passed to a shell, build tool, driver process or target program.

## POSIX command-only tokenizer

Native macOS, Linux and Linux/WSL contexts use this same POSIX subset. WSL does
not imply Windows parsing: `cmd.exe`, PowerShell, MSVC/clang-cl quoting, drive
paths and UNC paths require an explicit future profile and are rejected here.
No platform autodetection or retry with a different parser is permitted.

Validate raw UTF-8 text, then scan quoting and escapes before Python 3.12
`shlex.split(command, posix=True, comments=False)`. Outside quotes, ASCII spaces
and tabs separate tokens; single/double quotes and backslash escaping follow
that tokenizer. Reject unmatched quotes and trailing escapes. `shlex` is a
Unix-shell lexer, not a shell executor or Windows command parser. [C2]

Reject dollar signs and backticks anywhere, including escaped/quoted occurrences:
this forbids command, arithmetic and parameter substitution, including `$()`,
`$((...))`, `${...}` and bare `$NAME`. Reject unquoted/unescaped characters
`; & | < > ( ) * ? [ ] { } ~ # !`, including pipelines, redirections, process
substitution, grouping, globs, brace/tilde expansion, comments and history forms.
There is no line continuation: raw CR/LF and other ASCII controls are rejected;
only separating tabs are allowed in the raw command. Quoted or escaped literal
operator characters may remain inside a macro value or captured path; they are
data. A standalone shell operator token is rejected even when quoted or supplied
through `arguments`. Do not silently truncate at a comment or operator.

Both input forms reject a token starting with `@` and any token containing a
dollar sign/backtick. Bound the command/aggregate argv to 262,144 UTF-8 bytes,
argv to 1,024 elements, and each resulting token to 8,192 bytes. Tokens cannot
contain U+0000–U+001F, U+007F or invalid Unicode; this also rejects tabs embedded
inside a quoted macro/path. These are profile limits, not Clang's limits.

## Exact accepted argument grammar

`argv := DRIVER OPTION* SOURCE`. Exactly one source operand must be last. No
`--` terminator, stdin `-`, multiple source files, environment assignments,
wrappers (`env`, `ccache`, `xcrun`, shells), link inputs or options after SOURCE.
The default exact driver-label set is `clang`, `clang++`, `/usr/bin/clang`,
`/usr/bin/clang++`. Trusted configuration may register exact canonical absolute
Clang paths or versioned Clang labels. Never accept an arbitrary path because
its basename happens to be `clang`; never resolve a label through `PATH`.

Spaces in the table separate argv elements; joined forms are one element.
This table is exhaustive. Unlisted aliases/forms are rejected even if Clang
itself accepts them. The selected spellings and meanings are grounded in Clang's
argument reference; the restricted value grammar is SSR policy. [C3]

| Option | Exact input forms | Operand and cardinality |
|---|---|---|
| Language | `-x c`, `-xc`, `-x c++`, `-xc++` | At most one; only `c` or `c++`. |
| Standard | `-std=STANDARD` | At most one; equals form only, from the sets below and compatible with the language. |
| Target | `-target TRIPLE`, `--target=TRIPLE` | At most one; exact member of the frozen toolchain target set. No prefix/wildcard matching. |
| Define | `-D NAME[=VALUE]`, `-DNAME[=VALUE]` | Repeatable and ordered; object macro name `[A-Za-z_][A-Za-z0-9_]*`; VALUE may be empty or contain literal spaces/quotes, subject to token safety checks. |
| Undefine | `-U NAME`, `-UNAME` | Repeatable and ordered; same identifier grammar, no `=VALUE`. |
| Include/search | `-I DIR`, `-IDIR`; `-isystem DIR`, `-isystemDIR`; `-iquote DIR`, `-iquoteDIR`; `-idirafter DIR`, `-idirafterDIR` | Repeatable and ordered; every DIR is mapped and verified. |
| Framework search | `-F DIR`, `-FDIR`; `-iframework DIR`, `-iframeworkDIR` | Same path rules; no implicit host SDK. |

C standards: `c89`, `c90`, `c99`, `c11`, `c17`, `gnu89`, `gnu90`, `gnu99`,
`gnu11`, `gnu17`. C++ standards: `c++98`, `c++03`, `c++11`, `c++14`, `c++17`,
`c++20`, `gnu++98`, `gnu++03`, `gnu++11`, `gnu++14`, `gnu++17`, `gnu++20`.
No other language, standard, function-like macro definition or option spelling
is accepted. Macro values are a single literal argv value; never parse their
contents as more options. For example `-D`, `TEXT="hello world"` becomes the
single compiler argument `-DTEXT="hello world"`, including its C string quotes.

A separated operand cannot be missing, empty, start with `-`, `=` or `@`.
The same leading-character restriction applies to joined operands. `-I=dir`
and `-I-` are rejected; neither is reinterpreted as the accepted directory form.
Missing singleton values such as `--target=` or `-std=` cannot consume the next
argument. Repeated singleton options are rejected, including identical repeats;
repeatable define/undefine/include flags retain their original relative order.

If `-x` is absent, infer C from `.c`, C++ from `.cc`, `.cpp`, `.cxx` or `.C`,
and record `LANGUAGE_FROM_SUFFIX`. Other suffixes require explicit `-x`; do not
invent standalone header contexts. An absent standard becomes `c17`/`c++20`
with `DEFAULT_STANDARD`. An absent target uses the frozen installed profile's
explicit default target with `DEFAULT_TARGET`, never ambient host discovery.
Without any captured command, the runtime may create the already specified
conservative context with explicit language/standard/target and the captured
root include path. Record `NO_CAPTURED_COMMAND` and default-profile uncertainty.
The reference sanitizer validates entries; it does not manufacture this fallback.

Everything else is rejected atomically, including `-c`, `-S`, `-E`,
`-fsyntax-only`, `-o`/`-oFILE`, `-M*`, `-MJ`, diagnostic/output files,
`-save-temps`, `-Xclang`, `-Xpreprocessor`, `-Wp,`, `-Wl,`, `-B`, plugins,
`-load`, `-fplugin=`, `--config`, response files, forced `-include`/`-imacros`,
PCH/modules/module caches, VFS overlays, target sysroots/resource overrides,
`-isysroot`, `--sysroot`, `-resource-dir`, toolchain discovery, unknown `-f*`,
optimization/debug/warning switches and unknown future options. Do not implement
a blacklist with pass-through for the remainder. Conventional compilation
databases containing `-c` or `-o` therefore produce invalid contexts in v1;
silently stripping those flags is not the specified accepted grammar.

## Rooted mapping and compiler isolation

Every original source path is interpreted in a virtual inventory frozen from
the captured snapshot. Toolchain resources have separate explicit original and
staged roots, frozen inventories and version identities. Roots are canonical
absolute POSIX paths other than `/`; original roots must not overlap each other,
and staged roots must not overlap each other. Root selection uses whole path
components: `/project-other` is not beneath `/project`. A directory/source
must select the source root; includes may select source or a declared resource.
Resource-only default includes cannot select the project root.

For relative paths, prepend the validated captured working directory. For an
absolute path, select a root by its exact original component prefix before
normalizing the remainder. Walk components against the inventory: collapse `.`
and empty components inside the root, permit `..` only after a known directory,
and reject leaving the selected root even if a later component re-enters it.
Reject missing/excluded entries, traversal through a file, wrong node kinds,
and directory/source paths reaching a resource or external tree. A path such as
`missing/../include` is invalid: lexical simplification must not manufacture a
directory. A regular source file is required; include operands require directories.

This compiler profile rejects every traversed symlink, including links whose
captured target is internal. The capture/read symlink rules remain valid; this
is an explicit compiler-context limitation, never permission to follow live
filesystem links. Trusted materialization validates all native ancestors and
uses no-follow traversal/handles to enforce the inventory without races; root
descriptors supplied to the pure model assert this already happened. Do not use
host `realpath`, `exists`, `expanduser` or the checkout to repair missing paths.
Rejected links produce `SYMLINK_PATH` and retain structural source visibility.

Pass only the mapped source as libclang's source argument, plus normalized
language/standard/target, ordered sanitized options, and trusted controls
`-nostdinc`, `-nostdinc++`, `-fno-modules`, `-fno-implicit-modules`.
Trusted default resource includes are explicit mapped `-isystem` pairs. Clang
documents `-nostdinc` as disabling standard system and builtin include searches;
the application supplies the allowed resource paths itself. [C3]

Flag validation alone is **not filesystem containment**: reviewed headers may
contain absolute includes or other frontend file requests. W09 must run the
selected library in an isolated worker whose file access permits only the
verified snapshot materialization, pinned toolchain resources and necessary
trusted runtime files. Source reads cannot fall back to arbitrary host paths.
The exact platform mechanisms, launch envelope/readiness and denial gates are
specified in [native-isolation.md](native-isolation.md); use its common runner,
not a compiler-specific unsandboxed subprocess path.
A VFS overlay that falls back to the host is insufficient. Deny source-derived
writes, executable/module/plugin loading and network access; clear inherited
include/SDK/toolchain/plugin environment variables and configuration discovery.
Do not claim this reference sanitizer implements OS isolation. Where the native
platform cannot enforce this boundary, compiler work fails with an explicit
adapter/isolation error rather than running without it. Never execute a target
command to discover flags, generate headers or build a compilation database.

Fingerprint the profile version, snapshot identity, toolchain/resource identity,
mapped source identity, effective ordered flags and default assumptions. Replace
temporary physical roots with stable root identities in the fingerprint; moving
the same immutable materialization must not change it. Preserve argv/command
origin, ignored metadata and original captured entry identity as provenance.
Installed backend conformance must validate all accepted flags and guards for
the pinned library; a lexical allowlist is not evidence of Clang correctness.

## Diagnostics, trust and reconciliation

`InvalidContext` is an expected validation result, carries a bounded code/field
without echoing raw untrusted strings, and yields `UNRESOLVED /
MISSING_BUILD_CONTEXT` for affected known references. Return no partial flag list
and stage no trusted compiler observations from a rejected context. Codes include
`INVALID_ENTRY`, `INVALID_FIELD`, `INVALID_ENCODING`, `CONTROL_CHARACTER`,
`INPUT_LIMIT`, `INVALID_ARGUMENT_ARRAY`, `ARGUMENT_COUNT`,
`UNSUPPORTED_COMMAND_PLATFORM`, `INVALID_COMMAND_QUOTING`, `SHELL_SYNTAX`,
`RESPONSE_FILE`, `UNAPPROVED_DRIVER`, `UNSUPPORTED_OPTION`, `MISSING_OPERAND`,
`INVALID_OPERAND`, `DUPLICATE_OPTION`, `INVALID_MACRO`, `UNSUPPORTED_LANGUAGE`,
`UNSUPPORTED_STANDARD`, `UNAPPROVED_TARGET`, `DIRECTORY_NOT_ABSOLUTE`,
`NON_POSIX_PATH`, `PATH_OUTSIDE_ROOT`, `PATH_TRAVERSAL`, `PATH_NOT_CAPTURED`,
`NOT_A_DIRECTORY`, `PATH_KIND_MISMATCH`, `SYMLINK_PATH`, `MISSING_SOURCE`,
`SOURCE_MISMATCH` and `SOURCE_NOT_FINAL_OR_MULTIPLE`. Record the first decisive
rejection; later tokens need not be diagnosed. Invalid trusted profile setup is
an adapter/configuration failure, not invalid reviewed source.

Structural extraction can still complete with honest limitations. A backend
startup failure, unexpected sanitizer exception, timeout, signal/crash or failed
isolation is FAILED work with normal lease/retry handling, never an unresolved
binding. Compiler error/fatal diagnostics with a successful parse invalidate
the entire translation-unit context for binding in v1; a future narrower scope
needs evidence and a profile change. Warnings are retained. Unknown/unused
argument or unsupported-target diagnostics invalidate the context even when
reported as warnings. Do not promote recovered AST/cursor guesses under these
errors. The real adapter obtains cursor/reference/USR information through the
libclang API, not parsed compiler stdout. [C4]

W09 stages observations keyed by context and mapped physical structural
reference ID, including raw-byte source/target ranges, cursor kind, USR,
diagnostics and validity. Match exact captured file/range/kind; macro expansion
and spelling positions must map uniquely. An unmapped or multiply mapped cursor
is diagnostic evidence, not a new guessed structural reference or a nearest-line
match. A known structural reference with no unique mapped evidence remains
`UNRESOLVED / UNSUPPORTED_BINDING`. Keep mapping evidence for diagnosis.

W12 waits for successful extraction and all expected context work, then groups
by the physical reference. Deduplicate only proven SAME_ENTITY target identities.
Expected contexts come from the frozen input census, never the observed subset.
Successful INVALID context outputs count as completed limitations; failed/missing
context work blocks finalization. The reference census and VALID complete file
visits/skipped ranges distinguish MISSING, NOT_IN_TU and INACTIVE without creating
placeholder compiler observations. See compiler-work.md for the exact state table.
All valid observations agreeing on one captured target may produce RESOLVED.
Two or more distinct supported captured candidates produce `AMBIGUOUS /
CONTEXT_DISAGREEMENT`; preserve all candidates. One supported candidate plus an
invalid, missing, unmapped or conflicting external context remains UNRESOLVED
with diagnostics, never a one-candidate AMBIGUOUS or a proven target. Two proven
candidates remain AMBIGUOUS even when additional contexts are invalid; record
the limitation. Final UNRESOLVED results have no target IDs; retain any single
unproven candidate only in staged evidence/diagnostics. A known context where the reference is preprocessor-inactive
is explicitly not applicable; an unprocessed context is pending, and a crashed
context blocks successful completion. Never count either as agreement.

Agreement on an external/toolchain identity retains the USR/name/provenance but
returns `UNRESOLVED / EXTERNAL_SOURCE_NOT_CAPTURED` without a captured target ID.
Mixed local/external or different external identities cannot manufacture local
candidates; retain disagreement diagnostics and return UNRESOLVED unless at
least two supported captured candidates exist. Preserve unsupported dynamic or
virtual-dispatch limitations; a compiler's referenced declaration alone does not
prove one runtime implementation. Worker completion order must not change results.

## Acceptance split and runnable evidence

W09 proves `auto obj = new Test(); obj->something();` in captured fixture files
produces a mapped member-call observation, the correct declaration USR and
matching staged definition identity/range under the supported profile. It also
proves invalid-context and mapping limits. W09 does not need public cross-file
association or `read_function` through an association to exist.

W12 owns the final success: reconcile the same observations, publish a proven
declaration/definition SAME_ENTITY association, navigate the member call and
read the exact captured method definition. Its release gate still includes
overloads, namespaces, virtual/inheritance limitations, reassignment, missing
headers and cross-context disagreement. Moving the staged observation check into
W09 does not weaken that final member-call requirement.

Run the pure specification regressions from the repository root:

```sh
uv run --no-project --python 3.12 --with-requirements stage-1-indexing/validation/requirements.txt python -m unittest discover -s stage-1-indexing/validation/regressions -p test_compiler_profile.py -v
```

These tests cover accepted grammar, quoting, hostile tokens, path inventories,
symlinks, context rejection and fingerprints without touching source files or
loading Clang. They do not claim a working W09/W12 adapter, compiler crash
recovery, native sandbox enforcement or final association/read integration.

## Primary references

- C1: [Clang JSON compilation database format](https://clang.llvm.org/docs/JSONCompilationDatabase.html).
- C2: [Python 3.12 shlex](https://docs.python.org/3.12/library/shlex.html).
- C3: [Clang command-line argument reference](https://clang.llvm.org/docs/ClangCommandLineReference.html).
- C4: [libclang cursor API tutorial](https://clang.llvm.org/docs/LibClang.html).
