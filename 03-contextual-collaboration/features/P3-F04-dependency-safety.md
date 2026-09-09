# P3-F04 — Dependency cycles, joining, and finite collaboration

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P3-F01`, `P3-F03`, `P6-F03`

## Purpose and concrete outcome

Prevent a collaborating pool from deadlocking or expanding indefinitely while preserving useful cross-file questions and shared answers.

## Existing implementation and ownership

Reuse deterministic SCC knowledge for canonical same-file review, but maintain explicit dynamic request-consumer edges through the collaboration/task owner. Do not reuse canonical call-graph edges as if they proved request dependency.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P3-F04-R01.** Before inserting a blocking request edge, run bounded graph reachability from producer to consumer under a consistent transaction; a cycle cannot be added silently.

**P3-F04-R02.** If an answer would require its own waiting ancestor, prefer an independent targeted review with no inherited blocking edge, a local read by the consumer, or an explicit CYCLIC_CONTEXT outcome. Never fabricate a resolved answer.

**P3-F04-R03.** Joining requires exact snapshot/question/facet/assumption compatibility. Store all consumer links and independently track their revisions/cancellation.

**P3-F04-R04.** Enforce configured unresolved request/depth/revision caps. At the bound retain a visible question/limitation and return an actionable outcome; do not silently discard or count it as answered.

**P3-F04-R05.** No-progress is measured using new accepted evidence/facets/results or completed review obligations. Rephrasing the same question cannot reset an endless continuation budget.

**P3-F04-R06.** Cancelling an inquiry cancels only exclusive optional descendants; canonical coverage and shared producers remain required. Whole-review cancellation is the separate authoritative path.

## Inputs, outputs, and state

Explicit dispositions include JOINED, ROUTED, NEEDS_MAPPING, CYCLIC_CONTEXT, REQUEST_LIMIT, DEPTH_LIMIT, NO_PROGRESS and UNRESOLVED. These are request/routing outcomes, not vulnerability dispositions. Track cause and effect IDs for recovery.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Implement graph checks at the owner

Use indexed request-consumer edges with bounded traversal. Recheck at insertion to avoid two concurrent individually safe edges forming a cycle.

### Step 2: Add exact join semantics

Normalize only explicit fields and compare canonical digests; do not collapse source assumptions or caller contexts. Retain distinct request versions.

### Step 3: Add fallback routing

A cycle-breaking targeted task receives source context and the question but cannot depend on its blocked caller’s unfinished answer.

### Step 4: Apply finite accounting and cancellation

Record new-request/continuation counters against logical work. Shared producer cancellation requires no remaining consumers and no canonical obligation.

## Failure, concurrency, and recovery

Unexpected graph corruption is a visible integrity blocker; do not “fix” it by dropping edges without audit. Late canceled-consumer answers can remain valid producer artifacts but cannot resurrect canceled tasks. Limited graph checks must report an exceeded bound, not assume acyclic.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P3-F04-T01 | A waits B; B requests A | Cycle rejected or independent targeted route. |
| P3-F04-T02 | Concurrent reciprocal insertions | At most one blocking cycle-forming edge accepted. |
| P3-F04-T03 | Same function different caller assumptions | Not joined. |
| P3-F04-T04 | Depth limit reached | Question retained with explicit limitation. |
| P3-F04-T05 | Cancel one shared consumer | Producer and other consumer continue. |
| P3-F04-T06 | Repeated rewording without evidence | No-progress budget not reset. |

## Do not overengineer or expand scope

No general workflow-language engine, unlimited recursive spawning, dynamic SCC rewrite of canonical coverage or hidden queue deletion.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
