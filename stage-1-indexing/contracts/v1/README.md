# Version 1 contract assets

`models.py` is the executable Pydantic reference for exact field types, strict input validation and cross-field checks. `api.schema.json` is its generated JSON Schema bundle; use the named model under `$defs` for an operation. Schema constraints alone do not perform database identity checks or prove a byte range maps to the claimed source.

`records.py` and generated `internal.schema.json` define the shared SourceUnit, ExtractionBundle and nested scope/import/declaration/type/property/provenance values. The original-byte publication validator rejects identity, position and reference-spelling mismatches; it is not a substitute for a real adapter proving syntax ownership. `extraction-fixtures.json` supplies authored valid/invalid bundles. `language-fixtures.json` supplies per-dialect source/output projections; its comparison support is `validation/reference_language_fixtures.py`.

`schema.sql` defines the initial PostgreSQL layout. The publication owner additionally enforces the cross-publication/snapshot/range/target predicates described in storage.md. Real PostgreSQL migration/transaction tests are required in W02/W06; they were not run while authoring the specification.

`defaults.toml` fixes operational defaults. `builtin-names.yaml` and `builtin-semgrep.yaml` provide the initial finite catalogue, with authored Semgrep positive/negative inputs in `rule-fixtures.json`. These rules require actual Semgrep validation and fixture execution in W13; YAML parsing is not equivalent to compiling a Semgrep pattern.

`settings.py` and generated `settings.schema.json` fix strict operational settings and explicit semantic profiles. `error_response_target_bytes` is a soft target; independent request errors are not truncated. Rule/semantic profile changes allocate new datasets rather than rewriting shared results.

Production adopts these types/resources in the owning packages. Do not keep a second competing copy in runtime code. Run `python stage-1-indexing/validation/run_checks.py` to regenerate schemas and execute the core and regression suites; then regenerate/check delivery hashes with `python stage-1-indexing/validation/refresh_manifest.py` and its `--check` mode. Use the Python 3.12 validation environment documented in VALIDATION.md. Runtime gates remain separate.
