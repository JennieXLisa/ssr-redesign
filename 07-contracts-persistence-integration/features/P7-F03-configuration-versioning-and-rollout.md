# P7-F03 — Configuration, versioning, and compatibility activation

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P7-F01`, `P7-F02`

**Contract-hardening revision:** apply the concrete corrections in [P7-F03/IMPLEMENTATION_PLAN.md](P7-F03/IMPLEMENTATION_PLAN.md) and the [hardening index](../../CONTRACT_HARDENING.md). Earlier summary wording is not a substitute for the exact input, receipt, state, synthesis, context and cutover contracts.

## Purpose and concrete outcome

Introduce the new behavior as an explicit immutable review contract with testable defaults and a safe compatibility boundary, not as accidental changes to running reviews.

## Existing implementation and ownership

Reuse current configuration validation/hash identity, capability probes, release pair pinning and backup-backed migration mechanisms. Preserve long-investigation profiles and original runtime limits.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P7-F03-R01.** Use CONFIGURATION.md selected defaults, validated overrides and a canonical effective digest. Detect unknown fields and bad combinations before any review/task mutation.

**P7-F03-R02.** Legacy reviews keep original eligibility, tool schemas and result interpretation. Collaborative-v1 may start only on a database and paired runtime that declares all required capability contracts.

**P7-F03-R03.** Do not add a public runtime mode for every implementation checkpoint. R0–R7 are development slices, not permanent user-facing half-pipelines.

**P7-F03-R04.** Provision cursor secrets and optional matcher/analyzer artifacts in explicit host setup, not as side effects of target source reads or failed cursors. Record nonsecret artifact/provisioning identity.

**P7-F03-R05.** Do not hard-code historical branch names, wheel hashes or new migration numbers in runtime authority. Release tooling emits tested exact artifact coordinates and source/contract manifest.

**P7-F03-R06.** Default enablement and live deployment are separate from passing deterministic implementation tests. Record actual tests, outstanding gates and unsupported platforms.

## Inputs, outputs, and state

EffectiveConfig includes execution_mode, capability contracts, source/egress policy, existing role profiles, navigation/freshness/collaboration limits and scheduling parameters. Config changes select a new review unless an existing explicit administrative operation is defined; they do not reinterpret active signed attempts.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Implement schema and canonical hashing

Validate all new settings without dropping unknowns. Preserve original historical config hashes on read-only inspection; reject legacy runtime activation.

### Step 2: Build capability preflight

Check schema horizon, public SDK contract, tool adapters and required execution/receipt support before creating collaborative work. Optional scanner absence is a declared limitation, not a mode failure.

### Step 3: Add explicit provisioning

Create/reconcile private cursor key and inspect installed matcher artifact in approved development/release setup. No network install during source review.

### Step 4: Package clean distributions

Build in isolated clean output, inspect package resource manifests and test installed imports and controller assets against exact paired engine wheels.

### Step 5: Document promotion/rollback

Release only with separately authorized action. For new-mode databases unsupported by old code, rollback means restore a verified backup in stopped/authorized state, not rewrite migrations or downgrade live rows.

## Failure, concurrency, and recovery

Missing key versus first initialization is distinguished by provisioning receipt. Invalid capacity/profile combinations fail fast. Default changes require new configuration identity and measured/reviewed acceptance, not a silent hot update.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P7-F03-T01 | Legacy configuration roundtrip | Original identity preserved. |
| P7-F03-T02 | Unknown new setting | Explicit error before work creation. |
| P7-F03-T03 | Required capability absent | Collaborative mode refused. |
| P7-F03-T04 | Optional analyzer absent | Mode can run with discovery limitation. |
| P7-F03-T05 | Restart key provisioning | Existing key reused or explicit loss error. |
| P7-F03-T06 | Clean wheel install | No sibling-checkout or stale assets dependency. |

## Do not overengineer or expand scope

No automatic in-place mode conversion, implicit dependency installation, release numbers in AGENTS.md, or forever-supported checkpoint modes.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
