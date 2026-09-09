# P7-F02 — Public SDK and controller integration

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P7-F01`, `P6-F01`

## Purpose and concrete outcome

Expose collaborative work and early valid findings through the controller without allowing it to reproduce harness state or bypass strict compatibility negotiation.

## Existing implementation and ownership

Reuse public application/query/content SDK facades and controller compatibility, explorer, authenticated child dispatch, supervisor, admission and React API state. Find actual refactored owners before editing imports.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P7-F02-R01.** Add explicit CollaborativeReviewService/CollaborativeQueryService surfaces and versioned DTOs; preserve legacy method signatures and enum values. New capability is separately negotiated, not silently inferred from package version.

**P7-F02-R02.** The controller continues to use only supported SDK methods for project state/commands. It may persist its own job/evaluation data but cannot query harness ssr.db or private helpers.

**P7-F02-R03.** Expose real task types/states, blocking request refs, accepted answer/lead refs, partial coverage, current versus historical findings, required receipt gaps, budgets and readiness reasons. Never derive completion by counting visible UI rows.

**P7-F02-R04.** Mixed-role slice plans carry exact review/config/control identities and a provider-resource capacity vector. Controller admission grants an upper bound; harness revalidates actual task prerequisites/resources when claiming. Normal publications must not invalidate a plan merely because an unrelated task was added.

**P7-F02-R05.** Keep exact-task operator runs distinguishable from dynamic shared-pool plans. Preserve intended engine-import-free parent-side command DTOs and authenticated child-only engine dispatch.

**P7-F02-R06.** Frontend consumes typed status, bounds requests, cleans up streams and ignores stale asynchronous responses. Lazy historical transcripts remain lazy; new notices do not cause automatic source/transcript downloads.

## Inputs, outputs, and state

New methods: capabilities(context), plan_collaborative_slice(context, review_run_id, requested_capacity), drive_collaborative_slice(context, plan, admission_token), list_work(context, review_run_id, filters, cursor, limit), list_requests(...), list_artifacts(...), list_current_findings(...). Exact wire field table is in contracts/SDK.md. Existing sensitive source/transcript APIs remain separate explicit actions.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Add capability-negotiated facades

Keep public exports and DTO identities stable for old surfaces. Reject unsupported mode before creating jobs. Add new signatures to controller negotiated requirements only when enabling the paired capability.

### Step 2: Implement mixed capacity plan

Reuse harness readiness/resource owners. Bound by config/control generation and policy contract; verify exact-task restrictions, per-provider groups and actual lease admission.

### Step 3: Extend controller projections and child protocol

Use source-free typed conversion. Update every strict signature/enum check, command serializer, event projector, status view and package compatibility matrix coherently.

### Step 4: Add focused UI views

Show original work plus independent leads, requests/answers and blocking reasons. Preserve original task focus and explicit current-validity labels; no client-side authority.

### Step 5: Run four compatibility pairs

Baseline/baseline, refactored-harness/baseline-controller, baseline-harness/refactored-controller and refactored/refactored. New feature mode correctly refuses absent capability while old mode remains usable.

## Failure, concurrency, and recovery

An incompatible controller must fail explicitly rather than bypass check. A stale plan/control generation cannot start new work. Sensitive error/cursor data stays governed by existing access policy. Changes in UI filters cannot alter authoritative totals or evidence validity.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P7-F02-T01 | Old controller with new additive harness | Legacy mode continues under supported pair. |
| P7-F02-T02 | New controller with old harness | Collaborative mode unavailable explicitly. |
| P7-F02-T03 | Mixed backends in slice | Capacity vector respected. |
| P7-F02-T04 | New lead during running slice | Eligible refill without unrelated plan invalidation. |
| P7-F02-T05 | UI stale response after selection change | No wrong-project data/state overwrite. |
| P7-F02-T06 | Historical attempts collapsed | No eager transcript/source fetch fan-out. |

## Do not overengineer or expand scope

No controller SQL into project DB, CLI-output parsing, private imports, UI readiness inference or weakening compatibility to make a refactor pass.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
