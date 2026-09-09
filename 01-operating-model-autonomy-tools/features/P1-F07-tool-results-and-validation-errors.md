# P1-F07 — Actionable tool results and validation errors

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P1-F03`

**Contract-hardening revision:** apply the concrete corrections in [P1-F07/IMPLEMENTATION_PLAN.md](P1-F07/IMPLEMENTATION_PLAN.md) and the [hardening index](../../CONTRACT_HARDENING.md). Earlier summary wording is not a substitute for the exact input, receipt, state, synthesis, context and cutover contracts.

## Purpose and concrete outcome

The response delivered to the model identifies the actual problem and a valid next action. Rich host validation must not collapse to an opaque “invalid arguments” at the provider boundary.

## Existing implementation and ownership

Use existing tooling.diagnostics allowlists, ToolBrokerError, role validators and provider-neutral tool results. Preserve secret-safe projection and map internal paths back to compact model input fields.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P1-F07-R01.** Use the common outcome envelope with specific codes, JSON-pointer locations and bounded allowlisted details. Missing data, unsearchable input, partial pages, unknown outcome and explicit denial are different outcomes.

**P1-F07-R02.** Collect up to 16 independent issues per validation stage, plus omitted count. A prerequisite failure marks dependent checks NOT_EVALUATED instead of inventing derivative errors.

**P1-F07-R03.** Stop early for invalid execution identity, forbidden references, snapshot integrity and unparseable payloads. Do not disclose unauthorized IDs, paths, counts or raw provider/database exceptions through helpful-looking guidance.

**P1-F07-R04.** Repair actions must name available operations or ordinary input corrections. Never instruct an agent to run a tool unavailable to its role or to mark an analytical facet true merely to satisfy a schema.

**P1-F07-R05.** Always identify effect commitment: no accepted mutation, committed receipt, prepared safe retry, or unresolved outcome. An empty data list is not success after a failed search/query.

**P1-F07-R06.** Keep exact errors through normalization, broker, context composition and backend adapters. Output truncation must preserve code, actionable location and omission status before optional detail.

## Inputs, outputs, and state

Concrete initial codes include UNKNOWN_REFERENCE, REFERENCE_KIND_MISMATCH, STALE_INPUT, STALE_ATTEMPT, SOURCE_INTEGRITY_FAILURE, SOURCE_UNREAD, RESULT_UNREPRESENTABLE, PARTIAL_SCAN, MATCHER_UNAVAILABLE, UNSUPPORTED_PATTERN, ZERO_LENGTH_OCCURRENCE, SEARCH_PROGRESS_BLOCKED, INTEREST_LIMIT, INPUT_INVALID, OPERATION_OUTCOME_UNKNOWN. Legacy wire code aliases remain stable for legacy clients.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Inventory existing denial types

Retain exact lower-layer diagnostics where safe and identify where adapters replace them. Make an explicit mapping table; do not global-string-match exception prose.

### Step 2: Build stage-aware validation collection

Collect independent structural/type/ref checks, stop if authority fails, and label unevaluated semantic checks. Deduplicate repeated issues by code/location, not message text.

### Step 3: Validate recovery advice

Unit-test role/tool availability against every repair action. Include current limits and allowed values only from authoritative configuration.

### Step 4: Test final model request

Inspect the actual provider-normalized tool-result block with synthetic errors. Confirm secret-safe content and enough detail remain after output budgeting.

## Failure, concurrency, and recovery

Unexpected host errors use a fixed safe code plus correlation identity. Detailed host diagnostics stay in the authorized diagnostic surface. Partial result payloads cannot claim exhaustive validation or zero effects unless the transaction owner proves it.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P1-F07-T01 | Three independent bad fields | Three bounded, precise issues in one result. |
| P1-F07-T02 | Bad reference prevents source validation | Dependent hash/claim checks not falsely reported wrong. |
| P1-F07-T03 | Forbidden reference | No protected metadata disclosed. |
| P1-F07-T04 | Valid search times out | PARTIAL/UNAVAILABLE, not empty OK. |
| P1-F07-T05 | Repair action names absent tool | Contract test fails. |
| P1-F07-T06 | Provider adapter normalizes error | Model retains code/location/effect state. |

## Do not overengineer or expand scope

No generic catch-all error, retry-everything policy, logger-as-user-diagnostic substitute, raw stack trace to the model, or schemas weakened to achieve green tests.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
