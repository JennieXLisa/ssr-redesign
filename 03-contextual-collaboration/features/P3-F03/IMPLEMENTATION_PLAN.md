# P3-F03 — Answers and continuations: implementation plan

Updated: 2026-09-09. Documentation only. Read the [feature](../P3-F03-answers-and-continuations.md), [STATE.md](../../../contracts/STATE.md), P4-F01 publication and P6-F02 yield. This feature links accepted answer availability to an existing logical task without retaining an idle model slot.

## 1. Validate an answer for the exact question revision

`publish_context_answer` supplies request_id, request_revision, outcome, analysis, evidence/source refs, unresolved facets and scope_checked. Resolve the request under the producer's routed authority and current review/snapshot. Reject an unknown revision or unrelated producer; broad source permission alone is not permission to answer any hidden request.

Outcomes are ANSWERED, CONTRADICTED_ASSUMPTION, INCONCLUSIVE and NEEDS_DIFFERENT_SCOPE. The payload must identify which requested facets were checked and which remain unresolved. A contradicted assumption is useful analytical output, not validation failure. Malformed structure/reference is a rejection, not INCONCLUSIVE.

Prepare source-free analysis and verified references through P1-F03. Preserve producer authorship and source-delivery evidence. Do not use another worker's private notes as supporting evidence or infer complete scope from a generic summary.

## 2. Independent acceptance during an active review

Create an immutable contextual-answer artifact backed by the validated payload. Its producer receipt authenticates the completed exchange that requested publication; it must not wait for its own success ACK or the producer's whole canonical assignment. Required transcript mode needs a real immutable turn/prefix seal, not a forged full-attempt completion.

If required receipt material is absent, keep ACCEPTANCE_PENDING with explicit blockers. Once the receipt owner verifies all prerequisites, P4-F01's short availability transaction marks the artifact AVAILABLE and emits the review sequence event. Do not expose pending content through the request-status projection.

The same transaction records the exact request/revision-to-answer association and a durable wake/re-evaluation intent for compatible consumers. If these owners share the project database, commit them together through caller-owned primitives. If task scheduling is deferred, the intent is unique and restart-reconcilable. Never rely on an in-memory callback alone.

## 3. Determine which consumers can continue

For each live consumer, compare required request/facet revision, source/assumption/policy compatibility and accepted outcome. An answer to an old request can remain historical without satisfying a newer consumer. Consult exact recorded associations, not name similarity.

The default continuation predicate is 'at least one new relevant disposition is available to process'. A consumer may explicitly register a bounded ALL or ANY set of request/facet references; implement these as data, not an arbitrary expression interpreter. Contradictions and explicit unresolved/scope outcomes can enable a next action even when no positive answer was established.

Availability does not promote a candidate or assert that all prerequisites are true. The resumed analyst incorporates the answer and may refute its old hypothesis, request narrower work, or yield again. Ordinary freshness notices remain optional and are not automatic wake triggers for unrelated completed work.

## 4. Serialize yield against answer availability

The caller saves progress through P1-F04 and explicitly invokes yield_work. Within a short task transaction validate the exact checkpoint ID/hash, current lease/input generation and registered blocking requests. Re-evaluate answer dispositions before selecting the new task state.

```text
with task_transaction():
    require_owned_active_attempt_and_checkpoint()
    requests = load_registered_blocking_requests()
    if enabling_disposition_already_available(requests):
        transition_for_continuation(PENDING)  # or return explicit CONTINUE
    else:
        transition(RUNNING, WAITING_DEPENDENCY)
    persist_wait_predicate_and_checkpoint_binding()
    record_exact_yield_receipt()
```

The chosen CONTINUE versus yield-to-PENDING outcome must be explicit; do not put a task to sleep after the event that would wake it has already occurred. The answer-availability handler also checks current waiting state/generation under the same task authority. Thus either yield sees the answer or answer processing sees the waiter.

Release physical execution capacity only through P6-F02's exact-attempt settlement. Do not release the slot before a durable wait/continuation outcome exists, and do not keep it occupied merely to poll for an answer.

## 5. Idempotent wake application

A wake intent includes consumer logical task, relevant input/wait generation and exact available answer/request disposition. The task owner rechecks that work is still WAITING_DEPENDENCY, not terminal, and the predicate is satisfied by a new unprocessed disposition. Transition to PENDING once and persist the continuation input delta.

Duplicate availability events or intent retries are no-ops after the recorded transition. A late intent for an older wait generation cannot wake a newer incompatible wait, create a second task or claim two concurrent leases. A full pool leaves PENDING queued; it does not oversubscribe.

A consumer may finish or cancel while its producer is running. Its later answer can remain a valid producer artifact, but cannot reopen the terminal consumer. Shared remaining consumers are evaluated independently.

## 6. Construct the resumed context

At claim, keep the logical task/root identity and create a fresh attempt/lease. Bind its current input revision to the saved checkpoint plus explicit new answer refs and dispositions, outstanding requests and changed assumptions. Use compact recorded summaries, not whole transcripts or all prior source pages.

Label the original hypothesis and contradicting answer rather than silently rewriting history as if the analyst always knew the answer. The new attempt starts with empty source-delivery credit and must reopen material evidence where required. Author and receipt identities stay attached to their actual producer.

## 7. Failure and recovery matrix

Producer crash before answer commit: no available answer; router may recover or reassign required work. Crash after valid answer availability: answer survives independently of producer completion. Missing turn transcript: ACCEPTANCE_PENDING stays visible as a blocker; no fake wake. Consumer crash after durable wait: reconciliation restores waiting state and processes later intents. Crash after wake state change: the existing PENDING task is reused, not cloned.

Invalidated answer before consumer claim: re-evaluate its current availability and material compatibility. Do not put stale content into a new bound input silently. Repeated inconclusive answers count toward bounded continuation/request policy, not automatic success.

## 8. End-to-end tests

Build the primary trace: A reviews a sink, requests B's component with context, checkpoints and yields; B publishes a valid answer before finishing canonical coverage; A becomes PENDING and resumes while B's file remains incomplete. Assert source provenance, task states, slot counts and candidate non-promotion.

Run with all configured model slots occupied by waiting parents; after explicit yields, helpers must be admitted. Use barriers to publish an answer before yield validation, between yield preparation/commit, and after WAITING commit. Every order must result in either immediate continuation or one wake, never a permanently lost waiter.

Publish one contradiction among several requests and verify default ANY-style resumption; separately test ALL. Replay answer and wake transactions, cancel a consumer, expire a producer, and restart after each durable boundary. Assert one logical continuation, no duplicate lease, no inherited read credit and no terminal-work reopening.

## 9. Delivery slices

Implement typed answer preparation and pending/available artifact integration; add compatible request-answer associations; add durable wake intents; implement transactional yield recheck; add continuation dossiers and all race tests. Do not expose mid-review answer publication until real turn-level receipts work. No model polling, raw transcript answers, forced positive conclusions or separate persistent-agent framework belongs here.
