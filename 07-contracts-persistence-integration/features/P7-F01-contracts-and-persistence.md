# P7-F01 — Cross-feature contracts and persistence integration

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P1-F03`, `P4-F01`, `P5-F03`, `P6-F04`

**Contract-hardening revision:** apply the concrete corrections in [P7-F01/IMPLEMENTATION_PLAN.md](P7-F01/IMPLEMENTATION_PLAN.md) and the [hardening index](../../CONTRACT_HARDENING.md). Earlier summary wording is not a substitute for the exact input, receipt, state, synthesis, context and cutover contracts.

## Purpose and concrete outcome

Turn the completed behavioral design into one consistent set of state, identity, tool and transaction contracts that developers can implement without inventing conflicting local variants.

## Existing implementation and ownership

Reuse existing contracts package, schema migrations/checksums, database ownership, task/candidate services and public DTO facades. The new records in STATE.md extend ssr.db, not a new side database for authoritative work.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P7-F01-R01.** Use collaborative-v1 as the feature-contract identity; the installed database migration number is allocated from its actual schema horizon. Never edit historical SQL migrations or pretend schema 55 is still latest without checking.

**P7-F01-R02.** Implement shared contract fields once and generate provider-supported schema projections from them. The full host validator remains strict even if a provider supports only a JSON Schema subset.

**P7-F01-R03.** Map each new logical record to an existing compatible table or one minimal append-only migration addition. Document why any new record is necessary; no table per feature just because a document exists.

**P7-F01-R04.** Review mode, tool/result contract hashes, configuration, producer input revisions and availability event versions are immutable provenance. New behavior cannot reinterpret old receipts.

**P7-F01-R05.** One owner commits each atomic result, lead/task intent, request wake, operation outcome and candidate validity hold. Do not move transaction boundaries into helper modules or hold write locks across I/O/inference.

**P7-F01-R06.** Compile the actual schema and migration constraints against historical fixtures built by replaying migrations, not by mutating a newest database into a pretend older one.

## Inputs, outputs, and state

Normative state fields/unique indexes are in STATE.md and tool fields in TOOLS.md. Migration plan: M-A adds version/mode and reference/operation infrastructure; M-B adds work requests/artifacts/availability/interests; M-C adds coverage adoption/current validity/material dependencies; M-D updates claim/closure guards and projections. These are logical batches, not reserved numeric filenames. A batch may combine compatible changes, but no intermediate mode may advertise unsupported capability.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Produce implementation mapping

At R0 record each logical row/type/API against actual modules and schema objects. Identify reused validators and facades and assign one rule owner.

### Step 2: Define additive schemas

Implement strict discriminated variants and tests using contracts/schemas/tool-inputs.schema.json plus existing role-specific result validators. Keep source-free ordinary DTOs distinct from sensitive content.

### Step 3: Write and verify migrations

Back up disposable fixtures, replay real old migrations to supported versions, apply new ones and compare schema/data invariants. Rollback for real state requires explicit operator procedure, not edited migration history.

### Step 4: Wire authoritative mutations

Use task/candidate/result owners and transactional intent records. Verify unique constraints and rejection of stale generations. Projection helpers do not mutate canonical state.

### Step 5: Check complete integration

Run tool request→result→availability→notice/dependency→candidate→closure traces; no feature-specific shortcut can bypass its shared authority.

## Failure, concurrency, and recovery

Unknown schema/contract versions fail before execution. A partial migration cannot activate collaborative mode. Crashes leave auditable pending intents/receipts for bounded owner recovery. Never fix schema mismatch by weakening integrity checks or broadly ignoring unknown fields.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P7-F01-T01 | Real historical DB migrated | All expected old data/identities retained. |
| P7-F01-T02 | Unknown contract sent | Explicit compatibility error. |
| P7-F01-T03 | Duplicate availability/operation | Unique canonical effect. |
| P7-F01-T04 | Half-complete migration | Mode not advertised. |
| P7-F01-T05 | Role-specific result schema | Analytical fields remain required. |
| P7-F01-T06 | Old execution receipt read | Exact original interpretation preserved. |

## Do not overengineer or expand scope

No migration number guessed from old notes, duplicated contract classes, distributed database transaction fiction, generic ORM rewrite or public API inferred from internal dataclass fields.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
