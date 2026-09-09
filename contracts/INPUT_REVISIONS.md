# Immutable inputs, issued tokens, and delivery binding

Contract: `input-v1` / `input-token-v1`. Resolves the identity portion of H03/H05. Exact objects are `$defs.InputRevision` and `$defs.InputTokenPayload` in `schemas/hardening-v1.schema.json`. All fields are required, nullable only where the schema says so. This contract supplies no analytical conclusions.

## Identity and storage

An input revision is immutable content for one logical task/review/snapshot. It includes generation, predecessor digest, assignment/policy digests, material and request manifest roots, checkpoint ID/hash (both null or both present), and required-delta root. Those manifests are host-owned immutable, paged collections of exact subject/artifact/request revisions. The revision hash is `SHA256(b"ssr.input.v1\0" + canonical_json(body))`; the revision ID is `in1:` plus that hash. Generation starts at 1 and increments exactly once per accepted material rebind. Generation alone is not identity.

Canonical JSON everywhere in the hardening contracts uses UTF-8, sorted object keys, compact separators, preserved Unicode (no NFC), no NaN/floats, integers within the schema bounds, no duplicate keys and no insignificant trailing bytes. JSON boolean and integer types are distinct. A field's logical order does not affect hashing; SDK DTO field order is frozen separately for Python equality. Every content-hash domain is distinct.

Store body and hash with an immutable-row trigger and unique `(task_id,generation)` and `(revision_id)` constraints. The work head may point to a newer revision, but old bodies/receipts cannot be rewritten. A material manifest root is built from a frozen, deterministically ordered set; a mutable query such as “latest evidence” is forbidden inside an immutable revision. The exact set may be large in storage without being repeated in a provider prompt.

## Issued model token

Use `i1.<base64url(payload)>.<base64url(HMAC-SHA256)>` without padding. The MAC input is `b"ssr.input-token.v1\0" + payload_bytes` and uses the established project host key. The payload includes full attempt identity, revision ID/hash, key_id and required-delta root. It is bounded to 4096 encoded bytes. Input tokens are attempt-bound, unlike source navigation cursors; a successor receives a new token for its own actual input. Key loss invalidates new submissions until explicit host recovery, not historical receipt hashes.

The host creates the token while building an outgoing request and records a source-free `request_input_binding` before dispatch: request_id, attempt identity, revision_id/hash, token hash, request hash, included mandatory-delta root and counter/policy digest. Its delivery status becomes OBSERVED only after a valid durable response to that exact request. A prepared/sent request with uncertain response is not proof of delivery. A model tool call in that response may use only the token bound to that request.

Validation order is: reject malformed/oversized token; authenticate its exact canonical bytes; resolve the immutable revision; match actual authenticated executing identity; match the originating request's input binding and mandatory deltas; then recheck current material validity and work authority. A revision newer than the request is never filled in mechanically. Updating the task's input head does not prove the model saw its contents.

## Material change and refresh

A required material change produces a new immutable revision and explicit delta manifest. Optional supplemental analysis does not automatically invalidate the current input. Before a new ordinary exchange, compose a bounded dossier containing the mandatory delta summary/references and new issued token; the same final-request context gate applies. Only its actual response enables submissions using that token.

A result using an older materially invalid revision returns STALE_INPUT and references the authorized refresh action; it does not get rebound to the current head. A harmless later optional artifact may leave the old revision valid. The candidate/request owner, not token code, decides material invalidation. Current visibility changes are always enforced independently.

A queued continuation keeps its exact checkpoint and requested answer revisions. On claim the host constructs a new revision only from current accepted compatible inputs, preserving predecessor lineage. If a chosen input became unavailable, keep the work blocked or return an explicit missing-input disposition; do not replace it with a similar document.

## Transactions and replay

Prepare immutable bodies and source-free manifests outside the write transaction. In a short owner transaction compare expected old revision/head and exact lease/control generation, insert the new revision/manifests if absent, CAS the head, and record the operation. Replaying the same semantic operation returns its old receipt before applying a fresh-head CAS. A different body with the same generation/digest claim is an integrity conflict.

Request/response receipts and accepted artifacts reference their original revision forever. Recovery can settle an already-committed original operation with its original producer proof, but an expired model cannot initiate a new effect. Two inputs produced for different tasks with identical prose are still different identities because ownership is inside the hash.

## Integration and tests

P1-F03 normalizers remove only the frozen mechanical identity fields. Domain validators still receive the complete internal analytical contract. P1-F05 refreshes material through this exact revision path; P1-F04 dossiers do not bypass it. Prefix receipts bind revision_hash and request_hash; synthesis manifests and yield intents bind revision_hash plus generation. The controller sees hashes/IDs, never raw lease tokens or a copy of source-containing provider inputs.

IRV-T01: changing any ownership/material/checkpoint field changes the digest. IRV-T02: reject changed payload/MAC, other attempt, other review and mismatched key. IRV-T03: an issued but unobserved token cannot authorize a result. IRV-T04: a response to Q1 cannot use Q2's token. IRV-T05: mandatory deltas omitted by context fitting block dispatch, not become “delivered.” IRV-T06: duplicate revision insertion returns the same receipt; competing different revisions have one CAS winner. IRV-T07: unchanged optional updates leave permitted old input valid; material changes do not. IRV-T08: original producer recovery cannot overwrite a successor. IRV-T09: digest/type/canonical-form tampering fails. IRV-T10: checkpoint_id/hash nullability must agree.
