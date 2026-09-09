# P4-F02 — Coverage adoption and canonical file synthesis

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P4-F01`, `P3-F03`

**Contract-hardening revision:** apply the concrete corrections in [P4-F02/IMPLEMENTATION_PLAN.md](P4-F02/IMPLEMENTATION_PLAN.md) and the [hardening index](../../CONTRACT_HARDENING.md). Earlier summary wording is not a substitute for the exact input, receipt, state, synthesis, context and cutover contracts.

## Purpose and concrete outcome

Preserve full project accounting while reusing analysis that genuinely satisfies a complete canonical review-unit obligation.

## Existing implementation and ownership

Keep existing review-unit inventory, same-file dependency/SCC rules, symbol_coverage, child authorship and atomic distributed_file_publication. Reuse dependency-result receipt validation rather than add parallel coverage bookkeeping.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P4-F02-R01.** Reading code, reporting a lead or answering one question grants no complete coverage. Only a full compatible unit-result artifact can satisfy a unit obligation.

**P4-F02-R02.** Adoption validates exact snapshot, subject membership, unit kind/content, review policy and output contract, complete required dispositions/documentation, evidence and producer receipts. Missing fields require supplementary completion, not invented defaults.

**P4-F02-R03.** Canonical review-unit owner records an explicit adoption receipt referencing original authorship. It does not create a fake new review attempt or claim the adopting agent re-read source.

**P4-F02-R04.** One canonical acceptance per unit is selected deterministically; other legitimate analyses remain attributable context. Same symbol name across snapshots is not identity reuse.

**P4-F02-R05.** File synthesis consumes accepted unit artifacts, reconciles contradictory/cross-symbol conclusions with authorized source access, and publishes full canonical coverage atomically. It does not automatically re-review every unit.

**P4-F02-R06.** Independent leads already registered from a contribution remain linked through exact origin IDs. Parent synthesis can reuse them without duplicate seeding, but semantic similarity alone cannot merge distinct findings.

## Inputs, outputs, and state

AdoptionReceipt: canonical task/unit, artifact ID, exact input/contract/content digests, validator version, original producer refs and contribution status. File-level completion remains the existing parent publication contract extended to these explicitly accepted inputs. Partial question answers never masquerade as full unit results.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Identify unit acceptance requirements

Extract a shared unit validator from existing commit path without changing its rules. Mark the distinction between acceptance preparation and canonical completion.

### Step 2: Implement compatible adoption path

Validate an existing complete artifact and create adoption receipt under the unit task owner. CAS prevents duplicate canonical acceptance when original reviewer and adopter race.

### Step 3: Extend parent input assembly

Allow exact adopted contribution refs alongside normal sealed child results. Preserve child-source evidence closure and provenance, including already registered lead origins.

### Step 4: Test no-duplicate-work behavior

A full compatible contextual reviewer can satisfy a unit; an incomplete answer cannot. Assert unchanged total canonical inventory/disposition requirements and atomic rollback on one invalid child.

## Failure, concurrency, and recovery

An active canonical reviewer is not forcibly terminated merely because an artifact appears. Coordinate adoption at safe task boundaries; duplicate computations can finish as supplementary evidence but never double-count coverage. Invalidation of an adopted source/contract requires explicit revalidation, not deletion of its provenance.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P4-F02-T01 | Complete compatible targeted unit result | Adopt without mandatory second model pass. |
| P4-F02-T02 | One-facet answer only | No coverage credit. |
| P4-F02-T03 | Original and adoption race | One canonical acceptance; both origins retained. |
| P4-F02-T04 | Child evidence from unrelated proposal | Cannot contaminate another candidate. |
| P4-F02-T05 | Cross-symbol contradiction during synthesis | Source verification allowed; unresolved state visible. |
| P4-F02-T06 | Same names in new snapshot | No reuse without explicit lineage/content proof. |

## Do not overengineer or expand scope

No blanket no-credit policy for all focused work, automatic credit for source reads, fake model runs, or another coverage database.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
