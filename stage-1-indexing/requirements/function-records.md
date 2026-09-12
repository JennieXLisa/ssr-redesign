# Stage 1 — Function records

Status: approved behavior from the researcher discussion. This records the function information agreed for Stage 1; it is not a complete database schema, implementation plan, or test-results report.

Read with [source-intake.md](source-intake.md) and [indexing-progress.md](indexing-progress.md). Git owns immutable source contents; PostgreSQL owns the searchable records. Available records and their processing completeness follow the existing partial-query requirements.

## Approved requirements

**S1-FN-R01 — Identity and source association.** Give each function entry a unique symbol identity, its indexing-run association, snapshot/file references, and language. A name alone is not an identity. Lookups must distinguish entries with the same local name in different scopes or files and must not mix snapshots or indexing runs. The identity algorithm and any cross-run identity guarantees remain to be specified.

**S1-FN-R02 — Names, kind, and ownership.** Record the local and qualified names, the applicable kind such as function, method, or constructor, and the enclosing class, module, or function where applicable. Preserve nested scope rather than reducing all entries to a flat collection of names. The complete kind vocabulary and treatment of anonymous constructs remain implementation-design questions, not silently selected conventions.

**S1-FN-R03 — Signature information.** Record signature text, parameter names, available parameter type information, and return type where known. Preserve source locations for default-value expressions. Distinguish types declared in source from types inferred by a semantic backend. Missing information remains explicitly unknown; parsing a language does not authorize inventing its semantic types. Exact representations and unavailable-field conventions will be agreed with the schema.

**S1-FN-R04 — Source locations.** Retain exact declaration, definition, and body ranges where available, with byte offsets and readable line positions identifying the captured file. Source retrieval must use the corresponding immutable snapshot, not the original checkout or a newly resolved branch. Do not fabricate a body for a declaration without one. Range conventions and encoding rules will be fixed in the source-location contract.

**S1-FN-R05 — Applicable properties.** Record available visibility and modifiers, such as public, static, virtual, and async, where they apply. Distinguish an established property from unknown information and from a property not applicable to that language or construct. Do not treat unavailable visibility or type information as a known default merely to populate a field.

**S1-FN-R06 — Extraction provenance.** Retain which parser or semantic backend produced the information, its version, and relevant limitations. When semantic enrichment supplies type or linkage information, its origin must remain distinguishable from syntax-derived information. Preserve the indexing configuration association required by S1-IN-R07. This does not select a semantic backend or promise identical resolution capabilities for every language.

**S1-FN-R07 — Multiple occurrences and overloads.** Support multiple source locations associated with one function when resolution establishes they identify that function. In particular, link a C/C++ declaration in a header to its definition elsewhere when the evidence supports that association. Keep same-name overloads distinct. Do not merge records solely because their names match; where identity is not established, preserve the occurrences and unresolved or ambiguous association rather than inventing equivalence. Exact occurrence tables and record-linking/publication behavior remain to be designed.

**S1-FN-R08 — Linked records, not embedded growing lists.** Store references, callsites, and security signals separately and link them to function entries. Queries assemble the requested view of a function, its declarations/definition, callers/callees, reference occurrences, and flags, using bounded results and the existing partial-coverage indicators. Do not require a model-generated function summary, a vulnerability score, or a duplicate complete function body in PostgreSQL. Retrieve the body from Git when requested; storing the agreed signature metadata does not change that source-storage boundary.

## Derived acceptance scenarios

These are required observations for future tests, not tests executed here.

| ID | Scenario | Required observation |
|---|---|---|
| S1-FN-T01 | Index same-name functions in different modules/classes and in separate snapshots or runs. | Names do not collapse identities; each result retains the correct scope, file, snapshot, and run association. |
| S1-FN-T02 | Index a method and a nested function with available signatures, parameters, default expressions, and modifiers. | Applicable information and enclosing scope are retrievable, with source locations for defaults and no invented unavailable properties. |
| S1-FN-T03 | Enrich a parsed function with inferred type information while another type remains unknown. | Declared, inferred, and unknown information remain distinguishable with their producing backend/version and limitations. |
| S1-FN-T04 | Index declarations with and without definitions, then alter or remove the original working directory. | Available declaration/definition/body locations retrieve the captured source; absent bodies are not fabricated and no live-source fallback is used. |
| S1-FN-T05 | Provide a C/C++ header declaration, a matching definition in another file, same-name overloads, and an unresolved candidate association. | Established declarations/definitions are linked; overloads stay distinct; uncertain associations are not merged by name alone. |
| S1-FN-T06 | Add references and flags after a function record becomes queryable. | Linked records can become available without embedding growing lists or duplicating the function body; queries disclose unfinished relationship/flag processing. |

## Decisions still requiring discussion

- Exact PostgreSQL tables, field types, nullability, enums, constraints, and identifiers.
- Source-range conventions, signature representation, anonymous constructs, and language-specific property mapping.
- Semantic backends, declaration/definition identity proofs, enrichment conflict handling, and safe publication while indexing continues.
- Reference/callsite record shapes, resolution records, pagination, and the shared CLI/model-tool query contract.

Record these mechanisms with the researcher before assigning implementation. Do not turn an approved information requirement into an assumed backend capability or a new whole-repository model-review workflow.
