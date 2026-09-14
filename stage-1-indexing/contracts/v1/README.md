# Version 1 contract assets

`models.py` is the executable Pydantic reference for exact field types, strict input validation and cross-field checks. `api.schema.json` is its generated JSON Schema bundle; use the named model under `$defs` for an operation. Schema constraints alone do not perform database identity checks or prove a byte range maps to the claimed source.

`schema.sql` defines the initial PostgreSQL layout. The publication owner additionally enforces the cross-publication/snapshot/range/target predicates described in storage.md. Real PostgreSQL migration/transaction tests are required in W02/W06; they were not run while authoring the specification.

`defaults.toml` fixes operational defaults. `builtin-names.yaml` and `builtin-semgrep.yaml` provide the initial finite catalogue, with authored Semgrep positive/negative inputs in `rule-fixtures.json`. These rules require actual Semgrep validation and fixture execution in W13; YAML parsing is not equivalent to compiling a Semgrep pattern.

Production adopts these types/resources in the owning packages. Do not keep a second competing copy in runtime code. Regenerate the schema with `python stage-1-indexing/validation/export_schemas.py`; run specification checks with `python stage-1-indexing/validation/check_contracts.py`.
