# Language profiles, fixture mapping and semantic identity

This supplies the missing connection between the authored language goldens and
the production `SemanticProfile` in [settings.py](../contracts/v1/settings.py).
It refines the profile key list in configuration-and-processes.md. Fixtures use
compact test metadata; pass them through `fixture_to_profile` in
[reference_profiles.py](../validation/reference_profiles.py), never directly to
`SemanticProfile` and never through an unknown-key-dropping adapter dictionary.
The existing language-fixtures.json bytes and benchmark pin remain unchanged.

## Production shape and selection

Retain `schema_version`, `language_overrides`, `encoding_overrides`,
`package_roots`, `module_aliases` and `compilation_database`. Add `file_options`
and `compiler_options`, both defaulting to empty arrays. All option models reject
unknown keys/coercion and attribute mutation. New option collections, include
roots and translation-unit lists become immutable tuples in Python; JSON uses
arrays. Planning stores canonical projection bytes, never a mutable reference to
caller-owned selectors, package-root lists or alias dictionaries.

Each `file_options` entry selects one exact canonical snapshot file `path` and
`language`. A duplicate path is invalid. Its fields are selected by language:

| Dialect | Additional fields and defaults |
|---|---|
| Python, C, C++, Java, Lua | None. Unsupported language options fail validation. |
| JavaScript, JSX, TypeScript, TSX | `mode`: `script`, `module`, or `commonjs`; `strict`: boolean. Omitted strictness is true in module mode and false otherwise. Module plus explicit false is invalid. |
| PHP | `input`: `mixed` (default) or `php-only`. This selects the PHP capsule without adding/removing source bytes. |
| Bash, Zsh | `cwd_snapshot`: canonical captured directory or null (default). Null means no proven relative source-path basis; it never means the host cwd. The `language` field is the frozen shell mode. |

The metadata planner first applies an exact `file_options.path` selection, then
the first matching `language_overrides` entry, then extraction.md's filename,
shebang and header rules. Encoding overrides retain their separate first-match
order. Exact path selection is independent of glob escaping. File options do not
exclude unlisted files. A configured nonexistent path is an input error, not an
unused option to ignore. Generic glob selectors may match no files; record that
fact with the plan rather than inventing source.

For a JS-family file without an exact option, `.mjs`/`.mts` select module mode,
`.cjs`/`.cts` select CommonJS, and the other supported JS-family suffixes select
script. `default_file_options` makes these choices explicit after dialect
selection. No package.json, tsconfig, loader, source `require` occurrence or
ambient executable switches modes. An exact mode overrides suffix defaults.
`strict=false` does not suppress a source strict directive; the syntax adapter
still processes directives. Unsupported sloppy block-function cases retain the
language-policy limitation. CommonJS enables only the finite unshadowed
require/module.exports recipe; it does not authorize transpilation or execution.
JSX/TSX capsule selection follows `language`, independently of module mode.

The snapshot root is `""` in production. `"."` is permitted only as the fixture
directory shorthand and is explicitly mapped to `""`. File paths cannot be
empty. Path-shape validation checks percent-decoded traversal/NUL/absolute forms;
the canonical-path owner additionally checks reversible display encoding,
decoded aliases, actual captured file/directory kind and no-follow containment.
No profile path denotes a native filesystem location. Selected languages must
match frozen metadata. `validate_profile_inventory` is the pure counterpart for
regular-file inventory checks; it is not filesystem isolation evidence.
Package/include roots and shell cwd must be captured directories; a module alias
may target a captured file or directory, as required by its import-path recipe.

## Exact fixture mapping

Each existing fixture has one dialect. The mapper rejects a mixed-dialect
shorthand fixture; production itself can select multiple dialects through
separate file options. Every source produces an exact-path file option, including
sources expected to fail parsing. An empty fixture profile uses the explicit
defaults above. A malformed source is still a valid configuration input.

| Fixture field | Production destination and validation |
|---|---|
| `mode` | JS-family `file_options[*].mode`, with explicit strictness derived from that mode. Other dialects reject it. |
| `package_root` | Singleton `package_roots`, with directory shorthand normalized. Python only. |
| `php_input` | PHP `file_options[*].input`; accepts exactly mixed/php-only. |
| `shell_mode` | `file_options[*].language`; must equal each source's Bash/Zsh dialect, including explicit settings identical to defaults. |
| `cwd_snapshot` | Shell `file_options[*].cwd_snapshot`; root shorthand is normalized. |
| `compiler` | `compiler_options[0].standard`; source dialect supplies `language=c` or `cpp`. Standard/dialect mismatch fails. |
| `include_root` | Singleton `compiler_options[0].include_roots`, normalized; requires compiler selection. |
| `translation_units` | Ordered `compiler_options[0].translation_units`; nonempty, unique, captured files of the selected dialect; requires compiler selection. |

When `compiler` is supplied without `translation_units`, select matching
non-header source suffixes in fixture source order (`.c` for C;
`.cc/.cpp/.cxx/.C` for C++). An empty selection fails. When include_root is
omitted, use the fixture root. For `c-prototype-pointer` this yields
`standard=c17`, `include_roots=[""]`, `translation_units=["unit.c"]`.
For `cpp-test-member`, the ordered units are Test.cpp and main.cpp; Test.hpp stays
a captured header, not an invented third unit. A missing included header does
not invalidate profile syntax or invent a captured file; compiler processing
later reports its context limitation.

The optional mapper `root` is the canonical mount of one complete fixture in the
snapshot. It prefixes source paths, package/include roots, shell cwd and TU paths
together. For example, mounting cpp-test-member at `examples/cpp` gives
`include_roots=["examples/cpp"]` and units `examples/cpp/Test.cpp` and
`examples/cpp/main.cpp`. Do not merge replica-local profiles into one assumed
binding environment. Synthetic benchmark volume and individual golden semantics
remain separate tests.

## Compiler owner handoff

`compiler_options` entries contain only `language`, `standard`, ordered
`include_roots` and ordered `translation_units`. Standards are exactly the C/C++
sets accepted by strict-posix-clang-v1. Multiple entries can cover distinct units;
duplicate unit membership is invalid. Explicit options and compilation_database
are mutually exclusive. A compilation database may itself contain multiple
accepted contexts for a unit, governed by the compiler work contract.

For an explicit entry, the compiler planner maps `cpp` to Clang's `c++`, constructs
data operands for `-x`, `-std` and ordered include roots under the controlled
materialization, and passes them through the shared sanitizer. It never treats a
standard as an executable name. Absence of both selectors requests resolution.md's
recorded conservative defaults from the captured inventory. Freeze the exact
default-unit/standard/include selection and invalid contexts in the compiler
input census before computing the resolution identity. No compiler output,
observation ID, context UUID or result enters these profile inputs. Assign
context UUIDs only after resolution identity exists. This preserves the W09
observation and W12 final-reconciliation boundary.

## Exact fingerprint projections

`extraction_projection` and `resolution_projection` supply concrete field owners.
They fail if the top-level SemanticProfile contract gains an unaccounted field.
Canonical JSON/SHA-256 uses records.py; defaults and nulls are explicit.

| Projection | Fields |
|---|---|
| Extraction | Version, ordered language/encoding overrides, and all exact file options except shell cwd. Exact file options are sorted by path UTF-8 bytes since their array order has no selection meaning. Dialect, JS mode/strictness and PHP input all change extraction identity. |
| Resolution | Version, ordered package roots, aliases, compilation-database selector, ordered compiler entries/includes/TUs, and shell path/dialect/cwd records sorted by path. |

The executable hash inputs are exactly:

```text
extraction = SHA256(canonical({snapshot_id, parser_resources_digest,
                             profile: extraction_projection(profile)}))
resolution = SHA256(canonical({extraction_fingerprint: extraction,
                             resolver_digest, compiler_inputs_digest,
                             profile: resolution_projection(profile)}))
```

`parser_resources_digest` covers the actual parser/grammar/query resources and
classification/decoding policy versions, including extension-default rules.
`resolver_digest` covers the installed finite resolver policies/resources.
`compiler_inputs_digest` covers the frozen sanitized/default/invalid input census,
compiler/toolchain resources and relevant input-content digests; a selected file
path alone never substitutes for its bytes. Runtime supplies actual receipts,
not the test module's clearly labeled sentinel digests. A no-C/C++ dataset uses
the canonical explicit empty compiler census, not a magic omitted value.

Roots, aliases, shell cwd and compiler changes therefore preserve extraction and
change resolution. Extraction changes also change resolution transitively.
Worker count, timeouts, retry delays, database connections and output formatting
are Settings, not SemanticProfile or FingerprintInputs. Hardware/operational
changes cannot enter this API. Tool/context-result nondeterminism remains a
publication failure, not an excuse to rehash successful results as fresh inputs.

## Adapter adoption and evidence

The worker/planner selects the immutable per-file options when constructing its
adapter; retain `extract(source: SourceUnit)` as the adapter call signature.
SourceUnit/profile identity must agree with that frozen adapter configuration
before extraction. No adapter consults the fixture JSON, current profile file,
target configuration or host cwd during parsing. Resolution receives its own
frozen projection. In tests, map the fixture once, plan/classify through the real
owner, then compare actual outputs through `assert_fixture`.

```sh
python stage-1-indexing/validation/reference_profiles.py --fixture cpp-test-member
python stage-1-indexing/validation/regressions/test_fixture_profiles.py -v
```

These are executable mapping, validation and hash regressions. They do not run
parsers, libclang, PostgreSQL or navigation. W07/W08/W10/W11 still must prove
installed grammar/capsule selection, actual frozen-option consumption, scope and
byte-accurate publication. W09/W12 must prove compiler census consumption and
reconciliation. Reference validation never upgrades those unrun runtime gates.
