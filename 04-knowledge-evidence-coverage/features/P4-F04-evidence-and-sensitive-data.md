# P4-F04 — Evidence integrity and sensitive-data boundaries

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P1-F03`, `P4-F01`

## Purpose and concrete outcome

Keep precise source verification and producer provenance while allowing broader analytical collaboration. Neither new metadata nor convenience tools may leak raw sensitive data into ordinary stores.

## Existing implementation and ownership

Retain immutable snapshot worktrees, SourceResolver, EvidenceRepository, source-free prose guards, transcript.db and existing sensitive SDK paths. No change to the static-target policy.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P4-F04-R01.** All evidence refers to original snapshot bytes with half-open byte intervals, display coordinates and file/span hashes. Text normalization or preview markers cannot change evidence bytes.

**P4-F04-R02.** Ordinary ssr.db records, cursor metadata, knowledge and result summaries store refs and safe analysis, not source snippets, provider bodies, transport credentials or private reasoning.

**P4-F04-R03.** Legitimate sensitive source/tool/provider bytes remain only in the explicitly enabled transcript/content surfaces; do not redact a required exact capture merely to make an ordinary-storage test pass.

**P4-F04-R04.** Every material-source claim is checked for current scope, hash, symbol containment and actual source-delivery record when its role requires rereading. Host scanning a file is not model inspection.

**P4-F04-R05.** Shared contributions preserve who created evidence, who used it, and who accepted the resulting artifact. Do not repair producer conflicts by overwriting created_by or fabricating receipt identities.

**P4-F04-R06.** Exports are explicit sensitive actions. A valid finding becoming available does not itself export source, change retention, or reveal transcript content.

## Inputs, outputs, and state

Persistent records contain SourceRef/EvidenceRef/ArtifactRef associations and digests. Captured raw bodies remain in the existing transcript storage only under its contract. Cursor authentication secret is private host data, not included even in full transcript mode.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Trace all output paths

Review source tools, errors, event projection, checkpoints, notices, batch composition, artifacts and exports for content sensitivity. Preserve exact existing capture behavior.

### Step 2: Apply validation once at owning boundaries

Use the source/evidence service and prose guards in every new publication path. Retain metadata projection allowlists; do not globally prohibit legitimate typed fields containing words like source.

### Step 3: Record contribution use explicitly

Attach producer/consumer/acceptance refs without copying content. Cross-attempt read requirements are evaluated from current delivery records only.

### Step 4: Test source-free persistence and exact capture

Use unique synthetic sentinel source/secret strings and inspect all ordinary outputs for leakage while verifying required transcript bytes remain exact in a disposable test database.

## Failure, concurrency, and recovery

Integrity mismatch is a hard visible failure, not a pattern-search no-match. A missing snapshot cannot be replaced with current live source. Cross-database receipt reconciliation is explicit; no attach-database pseudo-atomicity.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P4-F04-T01 | Preview includes line labels | Evidence hash uses only original source. |
| P4-F04-T02 | Sentinel source in proposal prose | Guard rejects unsafe copying where required. |
| P4-F04-T03 | Full transcript configured | Required accepted bytes retained in separate store. |
| P4-F04-T04 | Transport key in headers | Secret never persisted. |
| P4-F04-T05 | Another attempt’s read refs reused | No inherited read credit. |
| P4-F04-T06 | Automatic new finding visibility | No implicit source export. |

## Do not overengineer or expand scope

No replacement filesystem, copied-source KB, generalized redaction weakening, direct SQL tools or target runtime access.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
