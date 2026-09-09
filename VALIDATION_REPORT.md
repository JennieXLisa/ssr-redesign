# Validation report — contract-hardening correction

Recorded:2026-09-09. Scope: the full design repository, generated contracts and executable specification/reference fixtures. **No harness/controller application tests, real database migrations, live gateway calls or reviewed-target execution were performed by these checks.**

## Checks actually run locally

| Check | Result and scope |
|---|---|
| `python tools/validate_docs.py` | PASS: 127 active Markdown documents; 34 features; eight specification/plan pairs; 779 local links; 96 tables; 30 input-schema fixtures |
| Earlier approval preservation | PASS: 113 approved requirements,156 approved scenarios and39 historical checkpoint files retain the validator's required original text/bytes |
| `python tools/test_contract_hardening.py` | PASS:60 unittest methods, including parameterized negative cases; exact generated schema/ABI,170k arithmetic, prefix/input/capture associations,10,000 staged decisions, quota rollback/replay, state fencing and Python IR pilot |
| Schema generation | `tools/build_hardening_schemas.py` generates55 closed object definitions, eight exact SDK methods, the ABI stub, total state/outcome matrices and combined tool inputs; repeated generation is byte-identical |
| `python tools/validate_hardening.py` | Runs the same reference suite, generated-file equality, all34 dedicated feature-plan membership and current manifest checks; machine result is hardening-validation.json |
| `python tools/refresh_manifest.py --check` | Compares the current design content set with MANIFEST.json, including dedicated plans and hardening files; its explicit exclusions avoid self-referential hashes |

The reference suite contains in-memory/small-SQL state models, not a disguised harness implementation. Its10,000-decision fixture proves bounded staged encodings/journal behavior, not actual production throughput. Context tests supply declared counts; the real gateway tokenizer/template must still be certified. Prefix tests check chain/identity/input rules on inert records; actual runtime reducers/capture persistence must pass their production fixtures. The Python callsite pilot proves selected structural cases without executing target imports; other language support is not claimed.

## Reproduce from the actual checked-out commit

```sh
python -m pip install 'jsonschema==4.23.0'
python tools/validate_docs.py
python tools/validate_hardening.py
python tools/refresh_manifest.py --check
```

After a deliberate source edit, regenerate the manifest with `python tools/refresh_manifest.py` before verification. Do not manually edit hashes or cite an earlier PASS as proof of the modified tree. The generator test fails when checked-in schemas/stubs differ from their generated contents; it does not bless an arbitrary schema because it parses.

## Publication and CI

The GitHub Validate design contracts workflow validates the exact pushed commit and retains commit/tree identity, source archive and reports. Consult that run's actual outcome; this static report does not embed its own final commit hash. Earlier v2 unpublished flags and stale manifests are retained only as historical metadata. Current source manifests deliberately exclude their own bytes and named generated validation outputs.

## Mandatory Codex implementation gates not run here

Real claim/finalizer interleavings with paused transcript seals; migrations of baseline0989172 with complete triggers/views/FKs/fingerprints; actual prefix/capture reconciliation; large-file canonical publication; exact installed SDK/controller reflection and serialization; provider-projected170k token counting and zero-dispatch over-limit tests; actual Python LanguageAdapter integration; protected data paths; failure/restart/usage settlement; and separately authorized quality/cost experiments. These are specified concretely by CONTRACT_HARDENING.md and the feature plans, not marked PASSED by document validation.
