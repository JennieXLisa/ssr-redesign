# Sources and interpretation

The design recommendations are original engineering choices. Repository facts below come from read-only inspection; external sources support specific mechanisms, not performance or correctness claims about SSR.

## Repository evidence

- [Original selected harness branch](https://github.com/JennieXLisa/source-review-harness/tree/8b7ed0e335d4f4fb5ae53ef6e059334661279f20): prior code inspection of broker, source/evidence, inventory, driver, worker, candidate and public SDK owners.
- [Observed modularization map](https://github.com/JennieXLisa/source-review-harness/blob/8f548f229dcac1c1d8aec2c5f8973353643ee99a/docs/refactoring/modularization/MODULE_MAP.md): retained owners, extraction boundaries and deferred concentrations.
- [Refactored source handlers](https://github.com/JennieXLisa/source-review-harness/blob/8f548f229dcac1c1d8aec2c5f8973353643ee99a/src/ssr/tooling/source_handlers.py): verified read assembly still receives assignment-range callbacks; this is an integration seam, not implemented broader research access.
- [Refactor comparison](https://github.com/JennieXLisa/source-review-harness/compare/8b7ed0e335d4f4fb5ae53ef6e059334661279f20...8f548f229dcac1c1d8aec2c5f8973353643ee99a): file-change inventory; not proof tests pass.
- [Controller selected earlier baseline README](https://github.com/JennieXLisa/ssr-control/blob/3c36f90777bbbd37a102e98d71b4560f02127d97/README.md): public SDK boundary, separate stores and packaged console.
- [Controller refactor documentation tree](https://github.com/JennieXLisa/ssr-control/tree/b7705ed35be54323fdf2a6d4a2ac8f2811d66745/docs): source of current owner-map discovery for implementation preflight; not fully audited here.
- [Remote redesign checkpoint](https://github.com/JennieXLisa/ssr-redesign/tree/017bde3f0c1f59a01ca9d8b11273f5000676a7be): remote v0.8; local conversation-approved v0.16 is preserved in this package.

## Primary technical references

- [SQLite isolation](https://www.sqlite.org/isolation.html): WAL read views and the failure of upgrading a stale read snapshot to a write. The prescribed H-read followed by original-H registration avoids that upgrade.
- [SQLite transaction control](https://www.sqlite.org/lang_transaction.html): explicit transaction ownership. Never hold a write transaction across model or analyzer work.
- [Python HMAC](https://docs.python.org/3/library/hmac.html): keyed tag generation and `compare_digest`; a valid tag authenticates cursor bytes, not source permission.
- [Google RE2](https://github.com/google/re2): non-backtracking matching, documented syntax/normalization limitations, and the official `google-re2` Python wrapper. Artifact pinning and supported-platform testing remain release work.
- [RE2 syntax](https://github.com/google/re2/wiki/Syntax): supported anchors, character classes and flags; look-around and backreferences are not silently emulated.
- [JSON Schema 2020-12](https://json-schema.org/draft/2020-12): format for the package's reference tool-input schema. Backend transport schemas may be a supported subset but the host validator remains strict.

Use the sources for their stated facts only. Numeric scheduling/resource defaults, result-publication choices and implementation slices are selected in this design and are not validated by these references. Do not fetch source from a user's connected repository through unauthenticated public search when a connector is available.
