# P4-F03 — Knowledge reuse, revision and conflict handling

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P4-F01`, `P5-F03`

## Purpose and concrete outcome

Keep reusable project understanding accurate and attributable as new reviewers add facts, hypotheses and counterevidence.

## Existing implementation and ownership

Reuse current documents/knowledge/relationships and repeated-review lineage/reuse services. Add explicit material-dependency and revision links rather than overwrite accepted prose.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P4-F03-R01.** FACT means a bounded source observation with provenance, not a host-certified security theorem. HYPOTHESIS and QUESTION retain uncertainty and cannot be promoted by schema validation alone.

**P4-F03-R02.** Reuse requires compatible snapshot/content, contract, assumptions and subject domain. Queries return exact results and recorded supersession/contradiction relationships, not an automatically synthesized consensus.

**P4-F03-R03.** New contradictory analysis is an immutable artifact linked to the challenged claims/facets and supporting refs. Preserve both versions and route material effects through the candidate validity owner.

**P4-F03-R04.** Negative findings such as no applicable guard must state the searched scope and limitations. Store relevant domain/registration subject dependencies so later accepted discoveries can trigger revalidation.

**P4-F03-R05.** Repeated-review reuse uses existing file/symbol lineage and exact policy/hash proofs. Changed sources and affected material neighbors are requeued; prior producer identity and result epoch remain historical.

**P4-F03-R06.** Knowledge corrections publish a new availability generation; optional freshness notices advertise them, while mandatory invalidation separately gates affected current findings.

## Inputs, outputs, and state

Add explicit relations SUPERSEDES, CONTRADICTS and APPLIES_UNDER to immutable artifact references where the existing schema can represent them. Record role and exact facet IDs. Avoid relying on string equality of claims to propagate material validity.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Version structured knowledge fields

Capture assumptions, searched scope and negative-claim domains in accepted result schema. Existing older summaries remain readable with limitations.

### Step 2: Implement revision associations

Use one owner to create immutable successors and relation refs. Do not change old hashes or rewrite prior artifacts.

### Step 3: Build material dependency index

Track exact evidence, artifacts and source-visible registration/domain assumptions used by candidate revisions. Bounded inverse queries identify affected work when new material appears.

### Step 4: Extend reuse validation

Use current reuse.py lineage/policy checks, add new contract and assumption digests, and test that old provenance is preserved instead of inventing rerun agents.

## Failure, concurrency, and recovery

Unrelated new analysis does not invalidate every project candidate. Unsupported dependencies remain explicit uncertainty. Old partial summaries cannot be treated as full new-contract results merely because source bytes match.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P4-F03-T01 | Two analyses conflict | Both visible with refs; no silent winner. |
| P4-F03-T02 | Negative auth claim plus new middleware relation | Affected candidate applicability is reevaluated. |
| P4-F03-T03 | Unrelated subsystem result | No blanket invalidation. |
| P4-F03-T04 | Unchanged repeated review with compatible policy | Explicit original-result reuse. |
| P4-F03-T05 | Same source changed contract | Reuse denied or limited, not silently upgraded. |
| P4-F03-T06 | Corrected artifact exact ID fetched | Original immutable content and current status returned. |

## Do not overengineer or expand scope

No automatic LLM consensus merger, universal semantic cache, whole-project invalidation on any event, or unverifiable negative safety claims.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
