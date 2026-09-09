# P1-F01 — Research access and assignment ownership

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: Shared baseline and contract preflight.

## Purpose and concrete outcome

An agent assigned unit A can investigate helper B without becoming B’s coverage owner. Analytical choice stays with the agent; current execution, permitted-source access and result acceptance remain host-enforced.

## Existing implementation and ownership

Keep BrokerScope execution identity and the source resolver. The observed refactor source_handlers receives explicit assigned-range callbacks; change their use for research tools, not the canonical result ownership validator. Keep useful public context/ownership boundaries; the executing SDK is the exact new contract, not a required old-mode facade.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P1-F01-C01.** Apply project-wide read-only permitted-snapshot research to background reviewers, focused analysts, investigators, falsifiers and file synthesizers. Do not copy all file/symbol IDs into every broker or confuse context capacity with permission.

**P1-F01-C02.** Resolve a known ID under the bound snapshot using manifest/index queries. Research permission is an on-demand check against classification and egress policy. No scope-expansion model conversation or new worker is required for an ordinary cross-file read.

**P1-F01-C03.** Assignment membership remains the sole basis of canonical coverage ownership. Broader reads do not grant mutation, publication, independent finding promotion or access to another review’s private artifacts.

**P1-F01-C04.** Revalidate live execution/lease/control generation at every operation and before authoritative writes. A stale attempt receives no new source even with a valid cursor. Terminated work cannot transfer grants through a reused slot.

**P1-F01-C05.** Keep falsifier source access broad, but its conversation fresh and result independent. Synthesizers use source for reconciliation, not mandatory duplicate review. Source comments and target AGENTS.md are untrusted data.

**P1-F01-C06.** Legacy attempts retain their exact prior surface and receipt interpretation. New attempts require collaborative capability negotiation and the new research-policy digest in execution provenance.

## Inputs, outputs, and state

Execution context has review/snapshot/task/agent/attempt/lease/control identity. Assignment has owned subject set, role and result contract. ResearchPolicy has snapshot, classification/egress policy version and capability set. These can be small immutable values behind one broker; they are not three databases. A validated per-read internal SourceScope can contain one resolved permitted path.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Locate and characterize owners

Map actual refactor facades and callbacks, all source/symbol/relationship/document checks, role exposure filters and final validators. Capture old denied/success cases and existing integrity tests before changing behavior.

### Step 2: Split permission from ownership

Add a focused policy function using the caller’s bound snapshot and indexed file identity. Remove assigned-byte clipping only from research navigation, retaining scope checks for the owned canonical submission. Resolve existing opaque file IDs through manifest locators if needed.

### Step 3: Wire every route consistently

Apply the same policy to source_read/search/stat, metadata discovery and actual source handles; do not only patch one read handler. Keep result visibility independent. Record actual bytes delivered after combined-result trimming.

### Step 4: Prove the boundary

Run tests for authorized cross-file source and rejected cross-file coverage completion, then legacy exact-surface and new-contract execution-receipt tests. Use a large inventory fixture to detect per-worker full catalogue construction.

## Failure, concurrency, and recovery

Do not cache an execution grant across lease replacement. Immutable manifest metadata may be cached within bounded host infrastructure but must be keyed by snapshot/policy. Publication and task status changes are not metadata-cache invalidation substitutes. No source or secret should enter denial text.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P1-F01-CT01 | A reads permitted B | B source succeeds, A’s assignment unchanged. |
| P1-F01-CT02 | A submits B coverage as its own | Ownership rejects; no partial rows. |
| P1-F01-CT03 | Expired attempt replays valid cursor | No bytes returned. |
| P1-F01-CT04 | Many files exceed context-item limit | Admission succeeds with bounded query results. |
| P1-F01-CT05 | Synthesizer checks a contradictory helper | Source access allowed without changing child ownership. |
| P1-F01-CT06 | Old-mode review opened for inspection | Original hashes remain historical; execution is rejected. |

## Do not overengineer or expand scope

No permissions server, generic RBAC product, whole-project prompt, new file store, target execution, or fabricated result visibility.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.

## Earlier approvals

Retain the [original approved requirements](P1-F01/APPROVED_REQUIREMENTS.md) and [original acceptance scenarios](P1-F01/APPROVED_TESTS.md). The complete source documents and checksums remain in the historical checkpoint.
