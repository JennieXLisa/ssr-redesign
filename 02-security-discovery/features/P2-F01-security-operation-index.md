# P2-F01 — Security-operation catalogue and indexed observations

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P1-F02`, `P4-F04`

## Purpose and concrete outcome

Identify sensitive behavior using resolved API meaning and argument roles, including project wrappers and security decisions with no recognizable dangerous name. Produce navigable observations, never automatic vulnerability verdicts.

## Existing implementation and ownership

Reuse deterministic language adapters, symbols, relationships, security_tags and snapshot provenance. Store operation observations as typed accepted host/analyzer records associated with existing subject/range identities; do not rebuild parser inventory with a model.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P2-F01-R01.** Each operation model names language/framework/API binding, operation family, relevant receiver/argument roles, execution options and limitations. A bare token execute/fork/open is not a complete operation classification.

**P2-F01-R02.** Initial families include process execution, code/module loading, filesystem read/write/delete/rename/link/permission, archive extraction, queries, outbound network, parsing/deserialization, memory bounds/lifetime, output rendering, authorization and state/resource amplification.

**P2-F01-R03.** Resolve aliases, imported names and receiver types where the existing adapter can establish them. Record unresolved, ambiguous, external or unsupported binding explicitly; do not claim a clean scan for unknown syntax/frameworks.

**P2-F01-R04.** Separate shell-string interpretation, executable selection, option/argument injection, environment/CWD/privilege effects. POSIX fork is process creation, not shell interpretation; Node child_process.fork is a runtime-specific launch operation.

**P2-F01-R05.** For file operations track destination and contents independently, object authorization, links/check-use identity, mode/overwrite behavior and source-visible downstream consumers. A fixed filename alone cannot close a content-consumer concern.

**P2-F01-R06.** Operation observations never satisfy canonical coverage or candidate readiness. A deterministic match contributes source location and modeled semantics; models must verify control/reachability/impact.

## Inputs, outputs, and state

OperationObservation: existing subject/ref, model_id/version/hash, family, binding state, argument-role references, configuration-branch references, source anchors, producer kind, limitations. Models are SSR-owned data files shipped with a pinned digest; the target cannot supply executable model code.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Implement model registry over current adapters

Start with the languages already inventoried. Each adapter emits a bounded normalized callsite or decision observation; unsupported constructs remain diagnostics. Avoid per-operation new task creation.

### Step 2: Add argument-role extraction

Extract call modes, literal executable/options and argument positions where syntactically established. Record expressions by source reference, not raw strings copied into ordinary state.

### Step 3: Index observations by subject/family

Use existing metadata associations or a small derived operation table. Keys include snapshot/callsite/model identity; rerun is idempotent. Producer/version changes create a new observation generation.

### Step 4: Validate adversarial naming

Test aliased subprocess, shadowed system/execute, overloaded receivers, non-shell process launches, fixed-path writes with variable bytes, and an auth decision with no sink API.

## Failure, concurrency, and recovery

Parser failure blocks corresponding deterministic claims but not authorized source inspection. False positives remain observations with limits. Never evaluate target imports/configuration to discover receiver type. A model registry update does not silently reinterpret completed-review findings.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P2-F01-T01 | subprocess aliased as ps | Resolved adapter binding yields process operation. |
| P2-F01-T02 | Unrelated object exposes execute | No database/process classification from name alone. |
| P2-F01-T03 | fork without exec | Classify creation/lifecycle, not shell injection. |
| P2-F01-T04 | Fixed path and user-written contents | Two independent influence dimensions recorded. |
| P2-F01-T05 | Authorization omission without dangerous API | A security-decision observation can seed inquiry. |
| P2-F01-T06 | Unknown framework | Explicit model-support gap, canonical review remains required. |

## Do not overengineer or expand scope

No exhaustive list of magic strings treated as truth, remote model registry downloads, one worker per match, or target execution.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
