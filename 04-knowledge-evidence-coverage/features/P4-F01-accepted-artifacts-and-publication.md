# P4-F01 — Independent artifact acceptance and publication

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P1-F03`, `P1-F08`

**Contract-hardening revision:** apply the concrete corrections in [P4-F01/IMPLEMENTATION_PLAN.md](P4-F01/IMPLEMENTATION_PLAN.md) and the [hardening index](../../CONTRACT_HARDENING.md). Earlier summary wording is not a substitute for the exact input, receipt, state, synthesis, context and cutover contracts.

## Purpose and concrete outcome

Make useful bounded answers and observations consumable before whole-file completion while preserving genuine semantic, evidence and runtime provenance gates.

## Existing implementation and ownership

Reuse existing documents, evidence preparation, typed result validators, distributed publication, execution contracts and separate transcript receipts. Add a small artifact reference/acceptance registry, not a second source or knowledge database.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P4-F01-R01.** Artifacts distinguish canonical unit result, contextual answer, host query answer, analyzer observation, lead registration and investigation/falsification output. Each variant has its own producer contract and acceptance checks.

**P4-F01-R02.** Model producer identity includes actual task/attempt/turn and recorded response. Host/analyzer producers have host-operation identity and capability/artifact digest; no fabricated agent or token use.

**P4-F01-R03.** Artifact semantic payloads are immutable, source-free and backed by exact evidence refs. Acceptance state is PREPARED, ACCEPTANCE_PENDING, AVAILABLE or REJECTED; availability and current validity are separate from candidate maturity.

**P4-F01-R04.** Mid-review artifact availability depends on a sealed contribution for its own completed exchange, including required transcript-turn receipt, not terminal completion of the larger task. Implement the new turn receipt explicitly before advertising these artifacts.

**P4-F01-R05.** Only the owning acceptance service publishes AVAILABLE and its review-local availability transition. All query, notice, dependency and candidate consumers use that service’s predicate; no task-completed shortcut.

**P4-F01-R06.** Revisions/supersession link immutable artifacts. A changed interpretation cannot overwrite a body under an existing artifact ID or erase counterevidence.

## Inputs, outputs, and state

Artifact registry and receipt fields are in STATE.md. Required receipt kinds are SEMANTIC_RESULT, SOURCE_DELIVERY (where material source is claimed), EXECUTION_EXCHANGE, and TRANSCRIPT_TURN when required. Registry points at existing typed result/document storage. A contribution can be valid even if later unrelated work in the same attempt fails.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Enumerate current producer contracts

Map each role’s semantic commit and receipt integration. Define a typed new contextual-answer result and exact host/analyzer variants with narrow assertions.

### Step 2: Implement immutable preparation

Verify refs/prose/current input, retain payload digest and origin operation. Preparation cannot publish half of the document/evidence graph.

### Step 3: Add contribution-level receipts

Introduce a per-turn transcript seal and source-free cross-store link. Reconcile crash windows without claiming a transaction spans ssr.db and transcript.db.

### Step 4: Publish through one availability transaction

Check all receipts, mark available and append the unique availability event. Consumers join against the registry’s active generation and current visibility.

### Step 5: Test downstream consumers

Verify query, notice, dependency wake and investigation readiness agree on identical pending/available fixtures.

## Failure, concurrency, and recovery

If raw transcript capture required for that exchange is incomplete, artifact remains pending. Preserve raw capture bytes and record any legitimate recovery attestation separately; do not edit history. A malformed analyzer result cannot be made usable by pretending it is a model summary.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P4-F01-T01 | Answer accepted before parent task completion | Usable with valid turn receipts; no file coverage completion. |
| P4-F01-T02 | Semantic commit without transcript receipt | Visible pending blocker, no consumer release. |
| P4-F01-T03 | Post-answer unrelated producer failure | Accepted answer not erased. |
| P4-F01-T04 | Retry publish transition | One availability event. |
| P4-F01-T05 | Host lookup result | Real host producer, no fake agent. |
| P4-F01-T06 | Body changed under existing ID | Integrity conflict. |

## Do not overengineer or expand scope

No private-note publication, duplicated source storage, auto-falsification credit, global publication manager model or relaxed receipt gates.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
