# P3-F04 — Dependency safety: implementation plan

Updated: 2026-09-09. Documentation only. Read the [feature](../P3-F04-dependency-safety.md), [STATE.md](../../../contracts/STATE.md) and [CONFIGURATION.md](../../../contracts/CONFIGURATION.md). The implementation prevents actual wait dependencies from deadlocking; it does not reinterpret every call-graph edge as a runtime wait.

## 1. Define the graph being checked

Build adjacency from unresolved blocking request-consumer-to-producer relationships plus actual unsatisfied hard task prerequisites. Exclude advisory freshness interests, nonblocking requests, already settled prerequisites and ordinary semantic CALLS relationships that are not scheduling dependencies.

Reuse existing canonical SCC handling: recursive units already admitted together do not create invented mutual waits merely because their source calls are cyclic. Preserve the scheduler's actual prerequisite representation. Do not rewrite the canonical source graph to make dynamic collaboration convenient.

Each edge records consumer task, producer task/request, required revision/facets, generation, reason and active disposition. Index outgoing/incoming task relationships for bounded traversal. Work/root identity is for ownership/accounting; a shared producer may serve several roots.

## 2. Check and insert in one serialized authority

Before adding consumer C → producer P, search active wait adjacency from P for C. A direct self-wait is rejected. Perform the final cycle/depth check and insertion inside the same short serialized collaboration/task transaction so reciprocal concurrent insertions cannot both pass on an old view.

```text
with dependency_transaction():
    recheck_consumer_and_producer_generation()
    reachable, limit_hit = bounded_reachability(start=P, target=C)
    if limit_hit: return explicit DEPTH_LIMIT_OR_GRAPH_BOUND
    if reachable: return cycle_disposition_without_edge()
    require_request_and_revision_caps()
    insert_active_blocking_edge(C, P, exact_request_revision)
    commit_routing_receipt()
```

Bound traversal by configured depth/node work. Hitting the bound is not proof of acyclicity. Return a visible unresolved routing outcome and retain the question. Do not run an unbounded graph walk while holding the database write lock.

Two concurrent A→B and B→A requests must serialize: after the first commits, the second sees the path and cannot introduce the cycle. A read-only preflight can improve messages, but cannot replace this insertion-time check.

## 3. Cycle-breaking behavior

First consider whether the consumer can inspect the small dependency locally through its existing broad research tools. Otherwise route an independent targeted CONTEXT_REVIEW containing the source question and known facts without inheriting a blocking dependency on its waiting ancestor. The targeted reviewer must have enough independent source context to answer; removing an edge does not magically make an unavailable analytical prerequisite exist.

If no independent route exists, return CYCLIC_CONTEXT with authorized task/request references and a bounded explanation. Preserve the unresolved question and permit the analyst to revise scope or report a limitation. Never fabricate an answer, drop an edge silently, or mark coverage complete to break a deadlock.

Targeted routing still consumes ordinary capacity/budgets. It is not an exemption from depth/request limits or an unlimited recursive worker factory.

## 4. Exact joining and shared ownership

Join requests only when snapshot, subject set, question/facet revision, assumptions and policy contract match. Canonical normalization is deterministic; name/CWE similarity is not equivalence. Preserve each consumer's required revision, blocking intent and disposition.

A producer shared by A and B is not owned exclusively by whichever requested first. Cancellation of A closes A's consumer edge and demand, leaving B's demand intact. Canonical coverage demand remains independently represented. Cancel an optional producer only when no live consumer or canonical obligation requires it, through TaskService's normal cancellation path.

A later answer can remain a valid artifact even when one consumer cancelled. It must not wake that cancelled task. Shared billing/root attribution follows P6-F03; do not charge the producer's cost twice merely because two roots benefit.

## 5. Finite expansion and progress

Enforce the configured open-request, depth and request-revision caps at the work/root owner under transaction. Completed/joined consumers are counted according to CONFIGURATION.md; do not multiply producer tasks to escape a local cap. A bound returns a recorded limitation, not a successful answer or a hidden dropped request.

Normal continuations have separate accounting from operational retries. Measure progress from new accepted artifact/evidence/facet references, resolved question dispositions or completed canonical obligations. Rephrasing a question or increasing word count is not a reset. Maintain the consecutive no-progress state on logical work, not in an attempt-local counter that restarts every lease.

Changed source assumptions backed by new evidence can justify a revision. Keep its predecessor and reason. The root's hard resource budget still applies even with legitimate progress.

## 6. Recovery and graph consistency

A restart reconstructs active wait state from durable records. Do not infer it from which provider processes happen to be alive. Reconcile a missing producer/task association as an explicit integrity/routing blocker. A terminal producer with unresolved consumers must have the reroute disposition from P3-F02; process it idempotently.

Retire an edge when the consumer processes an enabling disposition, cancels, or supersedes the exact required revision. Keep history/provenance. A late event for an old edge cannot replace a new revision or decrement another consumer's counts. Whole-review cancellation is a separate authoritative traversal and must not be simulated by deleting the graph.

## 7. Tests with adversarial timing

Build A waiting on B; B requests A. Verify explicit rejection or independent targeted route with no inherited cycle. Add a canonical hard prerequisite path P→Q→A and request A→P to ensure the graph considers actual static waits too. Also include a recursive source SCC with no hard mutual wait and prove it is not falsely rejected.

Use two connections and barriers to attempt reciprocal edges simultaneously. Verify at most one cycle-forming insertion, correct request outcomes and no partial producer creation. Exceed depth/node/request bounds and ensure 'unknown due to bound' never becomes 'acyclic'.

Cancel one of two consumers of a shared producer; producer and remaining wait survive. Cancel all optional consumers and verify one normal cancellation without deleting a canonical task. Replay late answers/cancel events, supersede a request revision and restart before cleanup. No terminal task reopens, no counter underflows and no edge disappears without an attributable disposition.

## 8. Delivery and exit

Implement pure graph traversal over explicit edges with small fixtures; wire serialized insertion and unique identities; integrate router fallbacks; add cancellation/progress accounting; then test restart reconstruction. Avoid a workflow expression language, general graph service, semantic manager model, dynamic rewrite of coverage SCCs or silent queue deletion. Completion evidence must include reciprocal-race tests and every fallback's preserved question/ownership state.
