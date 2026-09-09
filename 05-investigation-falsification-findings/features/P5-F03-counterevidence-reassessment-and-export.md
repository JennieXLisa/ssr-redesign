# P5-F03 — Counterevidence, reassessment, and historical export

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P4-F03`, `P5-F01`, `P5-F02`

## Purpose and concrete outcome

Early findings remain revisable as background coverage discovers controls or contradictions. Preserve history while making current eligibility honest.

## Existing implementation and ownership

Extend CandidateService and artifact/evidence associations with current validity and successor links. Reuse immutable analysis packages and existing gate/export infrastructure.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P5-F03-R01.** Accepted source-backed counterevidence identifies exact candidate revision/facet and refs. It sets a conservative REVALIDATION_REQUIRED hold before affected current export can proceed; it does not automatically refute the candidate.

**P5-F03-R02.** Historical-target challenges apply to current revision only when the challenged material facet is explicitly reused. Otherwise route applicability analysis without blindly invalidating a different argument.

**P5-F03-R03.** Store source-visible negative-assumption domains and subject dependencies so newly accepted registrations/controls can trigger relevant review. Do not rely exclusively on previously cited byte spans.

**P5-F03-R04.** Schedule a canonical investigator/falsifier successor through existing roles. Create a new candidate revision linked to the same family; do not reopen or rewrite sealed terminal rows.

**P5-F03-R05.** Until revalidated, current finding count/export exclude held revision. Historical packages remain byte-identical with their original state-as-of metadata and clear supersession/current-validity labels.

**P5-F03-R06.** When resources are exhausted, retain an explicit unresolved reassessment blocker. Only a separately authorized limitation-closure action can finish a review with that limitation, never a silent dismissal or upheld reuse.

## Inputs, outputs, and state

Validity: CURRENT, REVALIDATION_REQUIRED, SUPERSEDED, REFUTED, UNRESOLVED. Revision linkage and material dependency records are in STATE.md. Export selection binds family, candidate/revision, argument digest, validity generation and accepted verdict identity. Operator audit label is not authority; authority is the existing authenticated control/coordinator action.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Add challenge producer path

Extend approved result/lead schemas with typed challenged-facet refs. Validate source/ownership and persist challenge with current-validity hold atomically.

### Step 2: Index affected material

Use exact artifacts/symbols/negative scope-domain refs. Reconcile delayed events before current export/closure; source-backed interpretation remains model-authored.

### Step 3: Create revision successors

Reuse CandidateService creation/maturity functions under a family CAS. Bind new argument and require fresh falsification; old verdict remains historical.

### Step 4: Preserve export history

Keep immutable artifacts, expose current status separately, and reject export racing with a validity hold. Test the read/commit boundary and generated package manifest identity.

## Failure, concurrency, and recovery

Duplicate counterevidence does not create endless successors. Export invalidation race fails or retries against the new validity generation; no stale package is labeled currently upheld. A stale author can record historical context only through valid host provenance, not mutate current state.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P5-F03-T01 | Later reviewer finds effective control | Current export held, historical result preserved. |
| P5-F03-T02 | Old revision challenged, current facet changed | No blind current refutation. |
| P5-F03-T03 | Identical challenged facet reused | Current revision held. |
| P5-F03-T04 | Budget exhausted before revalidation | Visible unresolved blocker. |
| P5-F03-T05 | Export races with hold | No stale currently-valid export. |
| P5-F03-T06 | Reassessment upheld | New revision/receipt, old package unchanged. |

## Do not overengineer or expand scope

No deletion of old findings, automatic refutation from any prose, latest-row overwrite or operator label treated as authorization.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
