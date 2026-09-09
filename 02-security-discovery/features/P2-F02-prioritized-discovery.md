# P2-F02 — Entrypoints, prioritization, and bounded inquiry creation

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P2-F01`, `P6-F01`

**Contract-hardening revision:** apply the concrete corrections in [P2-F02/IMPLEMENTATION_PLAN.md](P2-F02/IMPLEMENTATION_PLAN.md) and the [hardening index](../../CONTRACT_HARDENING.md). Earlier summary wording is not a substitute for the exact input, receipt, state, synthesis, context and cutover contracts.

## Purpose and concrete outcome

Begin useful analyst work early: user-facing handlers, sensitive effects and shared controls first, while all included files continue canonical review. Orientation is accumulated, not a repository-wide stage barrier.

## Existing implementation and ownership

Reuse manifest/index tasks, security tags and code-backed registration relationships. Existing canonical unit tasks can be reprioritized through the scheduler owner; only missing cross-component analysis becomes focused work.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P2-F02-R01.** Create a bounded project sketch from manifests, recorded routes/RPC/IPC consumers, module entrypoints and configuration references. No mandatory manager or orientation model must finish before coverage starts.

**P2-F02-R02.** Group adjacent observations belonging to the same source operation/question; prioritize canonical units that can answer them before creating duplicate focused tasks. Preserve untagged/no-hit systematic review.

**P2-F02-R03.** Initial deterministic score is exposure 0–3, effect authority 0–3, unresolved security boundary 0–2, shared-dependency benefit 0–2. Record component values and source/provenance; uncertainty is not invented reachability.

**P2-F02-R04.** Use score only for initial ordering; it is not severity, confidence or truth. Within equal score rotate subsystem/family buckets before exact stable ID, then apply scheduler aging/coverage fairness.

**P2-F02-R05.** Cap optional focused backlog through CONFIGURATION.md. Existing required dependencies/investigation are serviced before new speculative roots. Do not create a model job for mechanical symbol/file queries.

**P2-F02-R06.** An agent may revise its hypothesis, choose forward/backward/control/lifecycle reasoning or record additional leads. Source-supported unexpected business logic is not rejected for lacking a registered objective.

## Inputs, outputs, and state

InquirySeed: snapshot-bound subjects/observations, concrete question, motivation, unknowns, score components, suggested starting refs and producer identity. A seed is not a canonical candidate unless a specific source-backed suspicion is reported. Existing canonical task priority updates remain host-audited.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Extract inexpensive sketch incrementally

Publish host observations per completed inventory segment; schedule available canonical work without waiting for optional whole-project scanning.

### Step 2: Rank and group without model work

Use explicit deterministic grouping keys such as operation callsite+question facet, not broad file/CWE equality. Record dedup reasons and retain contributing observation refs.

### Step 3: Prefer required work first

If a queued unit covers the initial question, promote that task and attach advisory context. Otherwise admit a bounded FOCUSED_ANALYSIS root through shared scheduling.

### Step 4: Evaluate ordering separately

Compare original ordering, continuous pipeline only, reordered coverage and added discovery on the same corpus. Extra model activity is not automatically an improvement.

## Failure, concurrency, and recovery

A scanner timeout cannot prevent source review. High scores cannot override evidence gates or budget admission. Exhausted optional backlog keeps observations in the catalogue without hiding them as lost leads. No-hit files remain canonical obligations.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P2-F02-T01 | User-facing handler plus risky helper | Related required review promoted before duplicate focused pass. |
| P2-F02-T02 | No scanner hits | Canonical coverage still completes. |
| P2-F02-T03 | 1000 similar hits | Bounded grouped inquiries, not 1000 immediate workers. |
| P2-F02-T04 | New shared control discovered | Priority benefit attributed to source-backed consumers. |
| P2-F02-T05 | No exposure binding | Unknown remains visible rather than fabricated score proof. |
| P2-F02-T06 | Optional backlog full | Observations retained and eligible later, pool not exceeded. |

## Do not overengineer or expand scope

No learned ranker, reinforcement loop, giant initial architecture dossier, fixed sink-only workflow or automatic full-graph scan barrier.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
