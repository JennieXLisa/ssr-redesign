# Executable contract schemas

`hardening-v1.schema.json` contains closed typed input/revision/prefix/synthesis/role/IR/SDK contracts. `sdk-abi.json` and `../reference/public-api.pyi` freeze exact public callable/DTO surfaces. `state-transitions.json` freezes state domains and total outcome tuples. `tool-inputs.schema.json` combines retained navigation inputs with the exact new role/staging tools; it is generated using local refs, not network schema lookup.

Run `python tools/build_hardening_schemas.py` from the repository root to regenerate. Do not edit generated definitions independently. `tools/validate_hardening.py` checks byte equality and executable positive/negative fixtures. JSON Schema validation does not replace whole-envelope byte/token limits, exact source/ownership checks, facet coverage, receipt replay, state guards or analytical validation.

The old semantic contracts for existing role analyses remain with their owning validator and are projected mechanically without deleting analytical fields. The new runtime does not maintain an old-mode tool interface. New FOCUSED_ANALYSIS/CONTEXT_REVIEW and file-synthesis stage/seal inputs are specified here rather than left as generic analysis dictionaries. Historical original schemas are provenance only.
