# P1-F03 — Reference-based inputs and submissions

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P1-F01`, `P1-F07`, `P1-F08`

**Contract-hardening revision:** apply the concrete corrections in [P1-F03/IMPLEMENTATION_PLAN.md](P1-F03/IMPLEMENTATION_PLAN.md) and the [hardening index](../../CONTRACT_HARDENING.md). Earlier summary wording is not a substitute for the exact input, receipt, state, synthesis, context and cutover contracts.

## Purpose and concrete outcome

Let agents submit real analysis and selected references without reconstructing hashes, task identity, lease tokens or byte offsets already known to the host. Reduce accidental mismatch without weakening acceptance.

## Existing implementation and ownership

BrokerScope supplies execution identity. SourceResolver returns verified SourceSegment values. EvidenceRepository.prepare/insert_prepared/resolve and CandidateService remain the authoritative storage and gate paths; do not create replacement evidence semantics.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P1-F03-R01.** Host fills review/snapshot/task/agent/attempt identity from the actual execution. The model may select subjects and cite refs but cannot override execution identity or choose a different snapshot.

**P1-F03-R02.** SourceRef identifies exact verified bytes and is issued from host reads or authoritative indexed anchors. It is a domain-separated authenticated token, not an accepted claim or proof the current model received those bytes.

**P1-F03-R03.** For a new claim, resolve SourceRef, verify its hashes/ranges/containment, attach model-authored claim/kind, and prepare canonical evidence. Existing EvidenceRef reuse preserves its original claim, kind and authorship; new interpretations do not overwrite it.

**P1-F03-R04.** Keep source-anchor equality separate from claim equality. Exact existing canonical evidence can be referenced and a new usage/contribution recorded; never merge claims because spans, CWE labels or names match.

**P1-F03-R05.** Final submissions bind their host input_token to the frozen attempt input and explicitly accepted input-delta receipts. Reject a stale candidate/question revision instead of rebinding to latest. Mechanical defaults cannot assert control sufficiency or path completeness.

**P1-F03-R06.** Authenticate/resolve references before constructing an accepted artifact, recheck ownership before commit, and preserve atomic rejection. Distinct source_ref, evidence_id and artifact_id fields are typed and cannot silently coerce one another.

## Inputs, outputs, and state

SourceRef payload: contract kind SOURCE_REF, key generation, review/snapshot, file identity/hash, start/end bytes, span hash, optional contained symbol and issuing operation. It contains no source body or secret. New evidence use records current producer operation separately from original evidence author. Detailed source_ref token rules reuse the cursor codec with a different domain.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Audit role envelopes

Enumerate identity fields in every existing result contract and distinguish mechanical identity from semantic subject selection. Freeze legacy parsers; add the smaller envelope only under collaborative-v1.

### Step 2: Add one normalization adapter

Resolve typed references and produce the current domain proposal objects. Retain explicit error locations mapping normalized internal fields back to agent input JSON pointers. Do not use prose matching to select evidence.

### Step 3: Preserve producer identity

On exact evidence reuse, validate nonproducer canonical fields and preserve the existing row. Add an artifact/candidate evidence-usage link for the new producer; do not suppress a provenance conflict by changing created_by.

### Step 4: Bind actual source delivery

Use delivery_records for required source inspection. A metadata anchor or received notice alone has no credit; an investigator must reopen material ranges in its own accepted exchange.

### Step 5: Verify all submission roles

Test full normalization → existing validator → atomic commit, including stale inputs, mid-transaction cancellation, partial references and cross-file context without borrowed coverage ownership.

## Failure, concurrency, and recovery

Rotated SourceRefs can be reissued after a fresh authorized read. Durable evidence remains resolvable by original coordinates/hashes after key rotation. A receipt/identity failure is not repaired by guessing an alternative file. No raw source is persisted with the normalized proposal.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P1-F03-T01 | Valid host ref with new claim | One verified evidence claim and correct author linkage. |
| P1-F03-T02 | Same span, different interpretation | Distinct claims, no overwrite. |
| P1-F03-T03 | Existing evidence reused by another agent | Original author preserved plus current usage. |
| P1-F03-T04 | Notice ID supplied as evidence | Typed error with correct field location. |
| P1-F03-T05 | Candidate changes while inference runs | Stale-input rejection; no latest rebinding. |
| P1-F03-T06 | Cross-file source cited from a unit review | Context permitted; no foreign unit completion. |

## Do not overengineer or expand scope

No content-addressed whole-source database, embedding-based evidence lookup, opaque model memory, automatic analytical assertions, or duplicated evidence service.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
