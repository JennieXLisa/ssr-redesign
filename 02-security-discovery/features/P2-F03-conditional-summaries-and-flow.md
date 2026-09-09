# P2-F03 — Conditional summaries and cross-boundary reasoning

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P2-F01`, `P3-F01`, `P4-F03`

**Contract-hardening revision:** apply the concrete corrections in [P2-F03/IMPLEMENTATION_PLAN.md](P2-F03/IMPLEMENTATION_PLAN.md) and the [hardening index](../../CONTRACT_HARDENING.md). Earlier summary wording is not a substitute for the exact input, receipt, state, synthesis, context and cutover contracts.

## Purpose and concrete outcome

Reuse what reviewers learn about wrappers, data transformations, stored fields, queues and ownership decisions without converting summaries into global safe/unsafe labels.

## Existing implementation and ownership

Extend accepted symbol documents, knowledge/relationship records and conditional security tags. Existing PRODUCES/CONSUMES/FLOWS_TO/STATE_TRANSITION concepts are preferable to a call-only graph.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P2-F03-R01.** A function summary identifies parameter-to-effect influence, conditions, returned authority/data, exceptional paths, controls and unknowns with exact source references. Never store value_is_sanitized as a universal property.

**P2-F03-R02.** Controls identify a property, constrained subject, branch/configuration assumptions, failure behavior and later transformations. A parameterized SQL value does not imply tenant authorization; a length check must match actual units and signedness.

**P2-F03-R03.** Cross-boundary hypotheses can follow storage fields, queues, files, callbacks and IPC. Channel identity needs producer/consumer evidence, not a shared string name alone.

**P2-F03-R04.** A caller may consume a summary for navigation and request missing facets. Material investigation/falsification segments are reopened in source by the current attempt; summaries do not grant source-read credit.

**P2-F03-R05.** Discovery may proceed backward from effects, forward from input, through control callers, resource lifetime or a security invariant. Changing direction does not require a new hard-coded objective enum.

**P2-F03-R06.** Summarized assurance remains conditional and snapshot/contract-bound. Contradictory caller behavior creates a new question or revised assessment, not silent replacement of every caller’s conclusion.

## Inputs, outputs, and state

ConditionalSummary fields: subject, effects, parameter_influence[], constraints[{property,subject,conditions,failure_behavior,after_transforms,refs}], channels[{kind,identity_refs,role}], unknowns and provenance. Store within existing document schema extension and reference registry; no second global taint database.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Add conditional document fields

Version the symbol-result contract and host validation. Keep optional legacy reading but require explicit unknowns for missing new properties in new-contract results.

### Step 2: Link only evidenced channels

Create proposed relationships with producer identity and exact channel evidence; deterministic and model-proposed states remain distinguishable.

### Step 3: Use summaries in context requests

A sink analyst can ask writers of a field or users of a control rather than merely callers. Route unresolved channel mapping as a specific request, not a fabricated edge.

### Step 4: Validate caller-specific interpretation

Create fixtures where the same helper is safe under one caller restriction and unsafe or unknown under another. Test that summary reuse preserves its conditions.

## Failure, concurrency, and recovery

Summary contradiction can hold dependent claims under the material-dependency contract, but an unverified model statement is not automatic refutation. Unknown channel mapping cannot become a completed end-to-end path. No target importing or runtime behavior reconstruction is performed.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P2-F03-T01 | One helper, two differently constrained callers | Independent conditional conclusions retained. |
| P2-F03-T02 | Stored field reaches background command | Writer/consumer question carries exact field/channel evidence. |
| P2-F03-T03 | Two queues share display name | No automatic connection without identity evidence. |
| P2-F03-T04 | Size checked in elements, copied in bytes | Unit mismatch remains an explicit analytical question. |
| P2-F03-T05 | Control fails open on exception | Exceptional branch appears in summary. |
| P2-F03-T06 | Fresh falsifier uses summary | Still reopens material source. |

## Do not overengineer or expand scope

No universal sanitizer whitelist, model-generated global “safe” labels, automatic transitive vulnerability proof or whole-program symbolic execution rewrite.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
