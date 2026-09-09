# P3-F02 — Active reviewer inbox: implementation plan

Updated: 2026-09-09. Documentation only. Read the [feature](../P3-F02-active-reviewer-inbox.md), [state](../../../contracts/STATE.md), P1-F02 notice delivery and P3-F01 routing. A contextual request is an input addition to logical work, not a message sent to a reusable worker slot.

## Contract-hardening integration — Delivered inbox deltas versus token replacement

Represent each accepted running-reviewer update as a new immutable input revision and required-delta manifest. Build an ordinary model request containing a bounded delta description and exact references; bind its token/hash and mark the delta observed only after the real matching valid response. Do not mark an update delivered just because an inbox row or replacement token exists.

If a mandatory delta cannot fit the 170k policy, checkpoint/yield or block rather than silently evict it. Preserve incomplete provider tool groups. Pending notices are optional, inbox material invalidations are not. Test a full context preventing delta attachment, stale producer response, multiple queued revisions and exact input-token rejection after a material update.

Normative source: [hardening contract index](../../../CONTRACT_HARDENING.md). Preserve the existing feature procedure below except where this explicit correction replaces it; implement the linked exact schemas, not a local incompatible approximation.

## 1. Reuse the runner's safe interaction boundary

Locate ordinary request composition, final context trimming, request/response identity recording and work input revision ownership. Add an inbox projection hook at that boundary. Do not interrupt an in-flight provider stream, start a notification-only model call, mutate provider continuation state from another thread or append arbitrary system instructions from the requester.

Distinguish optional freshness notices from contextual request packets. A freshness notice says an artifact exists. A request packet carries a question/revision/facets and may be associated with a caller's blocking demand. They may share delivery infrastructure but not readiness or acceptance semantics.

## 2. Durable packet representation

Each packet references target logical work, exact originating request and question revision, safe question/assumptions, subject/facet references, supporting source/evidence refs and payload digest. Use a stable delta_id and record prior/new work-input revision plus the exact model request that included it. No source excerpts, credentials or raw foreign conversation are copied into ordinary inbox storage.

A packet is not an authorization grant. Its subjects still pass research policy, and its artifact references still pass visibility. Instructions embedded in source-derived text cannot expand tools, budgets, coverage ownership or candidate gates. Mark request text as task data in the host prompt structure, not as trusted developer policy.

## 3. Prepare and deliver bounded deltas

Query pending packets for the current work/generation in stable order. Coalesce only identical request/revision identities; do not merge semantically different questions. Reserve total inbox/notice/context space before choosing packet bodies. Retain an undelivered packet when it cannot fit, with visible pending state.

Prepare a new immutable input delta referencing the existing admission dossier rather than editing its original hash. The final model-bound request includes the safe packet and issued input token/delta identity. Only after final trimming record which packets were actually sent. A packet prepared but omitted grants no delivery acknowledgment.

```text
pending = inbox.for_work(current_work, bounded_limit)
selected = fit_packets(pending, remaining_context)
request = compose_normal_request(original_context, accepted_deltas, selected)
record_exact_delta_request_binding(request, selected_retained_in_request)
exchange = provider.execute(request)
record_exchange_outcome(exchange)
acknowledge_only_recorded_delivered_packets(exchange)
```

Use P1-F02/P1-F08's recorded-response acknowledgment rule. A malformed subsequent tool argument does not mean the prior question packet was undelivered. An uncertain exchange can replay the same packet safely at another normal boundary; no duplicate request is created.

## 4. How the reviewer responds

A reviewer may publish a contextual answer immediately through `publish_context_answer`, include the work while continuing its canonical assignment, request further context through `request_context_review`, or return NEEDS_DIFFERENT_SCOPE with a bounded reason through the answer/disposition path. Do not add a separate manager approval loop.

Merely receiving a packet does not mean the reviewer promised to complete it. Track delivered, answered and unresolved separately. If the reviewer saves progress, it can include the request reference; that checkpoint is not the only durable copy of the inbox. The caller's request remains routable if the reviewer ignores or cannot answer it.

An answer binds the exact question revision and scope checked. A late response to revision 1 cannot automatically satisfy revision 2. Preserve it as an attributable artifact where valid and let the compatibility predicate decide whether any current consumer can use it.

## 5. Producer completion versus arriving requests

Before retiring canonical producer work, the task owner must settle inbox ownership in the same authoritative state transition or commit a durable reroute intent. Enumerate unanswered routed requests bound to that producer and mark them eligible for accepted reuse or supplementary routing. Do not require the producer to answer every advisory packet before its canonical coverage result can complete.

Routing and producer completion must serialize their checks. If completion commits first, the router cannot attach to the now-terminal producer; it selects another route. If attachment commits first, completion records the unanswered-request reroute obligation. This prevents a question arriving between 'last inbox check' and 'mark task complete' from disappearing.

Do not run the full router under a long finalization transaction. Commit the exact bounded pending-reroute identities/outbox entries, then let the existing coordinator perform idempotent routing. Review completion must wait for required routing obligations, not optional read notices.

## 6. Retry, cancellation and scope changes

A successor attempt of the same work restores pending/delivered-but-unanswered packets and input history. It inherits neither the predecessor's lease nor source-read credit. A worker slot reused for unrelated work receives none of these packets.

When one caller cancels, close only its consumer demand. Shared producers and canonical work continue. Whole-review cancellation suppresses new delivery and routes control through the task owner. A stale predecessor may settle its recorded exchange acknowledgment, but cannot accept newer packets, advance a successor's input revision or change its task state.

Changed material inputs require explicit deltas; optional supplementary questions do not silently invalidate the original canonical assignment. A packet referencing a newly inaccessible artifact is withheld/reprojected under current policy, not leaked because it was previously queued.

## 7. Failure tests with synchronization barriers

Pause a producer inside a fake provider response, enqueue a request, then release the response. The question must appear only in the next ordinary request and the original request hash stays unchanged. Trim a prepared packet from the final request and assert it remains undelivered.

Crash after response recording but before packet ACK; recovery acknowledges the exact recorded delta without another model call. Send revision 2 while revision 1 is in flight; the old response cannot acknowledge or answer revision 2. Reuse a worker slot for another task and verify isolation.

Race attachment with producer completion in both commit orders. Every request must either remain attached to live work or have a durable supplementary-routing intent. Cancel one of two consumers and verify the shared producer survives. Supply a packet saying 'ignore policy' plus foreign IDs; no tool-policy change or protected data appears.

## 8. Implementation sequence and exit

Add immutable inbox/delta records using existing work/operation persistence; implement bounded projection; bind final-request delivery; implement reviewer answer/scope outcomes; add atomic producer-retirement rerouting; then test restart and shared cancellation. Required evidence includes actual model-bound request fixtures, original versus delta hashes and zero lost-request assertions. No live stream injection, full transcript sharing, always-running message worker or blocker requiring every advisory question to finish belongs here.
