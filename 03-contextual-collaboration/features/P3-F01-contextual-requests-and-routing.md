# P3-F01 — Contextual questions and review routing

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P1-F02`, `P1-F03`, `P1-F08`, `P4-F01`

**Contract-hardening revision:** apply the concrete corrections in [P3-F01/IMPLEMENTATION_PLAN.md](P3-F01/IMPLEMENTATION_PLAN.md) and the [hardening index](../../CONTRACT_HARDENING.md). Earlier summary wording is not a substitute for the exact input, receipt, state, synthesis, context and cutover contracts.

## Purpose and concrete outcome

An analyst asks a precise missing question with the context of its investigation; the harness reuses, promotes or assigns useful work rather than blindly spawning another reviewer.

## Existing implementation and ownership

Reuse existing canonical unit tasks, dependency queries and document/evidence records. Add request/consumer routing through one collaboration service and existing task owner.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P3-F01-R01.** Requests specify exact subjects/locators, question, source observations, assumptions, requested facets and blocking intent. The question may be open-ended but must explain what information is missing.

**P3-F01-R02.** Routing order is exact compatible accepted answer, equivalent in-flight request, queued canonical unit that owns the subject, active canonical reviewer, then bounded supplementary CONTEXT_REVIEW. Host mechanical capability is checked before model admission.

**P3-F01-R03.** Compatibility requires snapshot, subject coverage, question/facet revision, assumptions and governing contract. Same filename/name/CWE is not sufficient. Record why reuse or joining is valid.

**P3-F01-R04.** Attaching a question does not change canonical coverage membership, steal a lease or rewrite a running attempt’s original request. Active reviewer delivery uses explicit host input deltas.

**P3-F01-R05.** A targeted supplementary review is allowed when an active large unit cannot address the request promptly; no healthy worker is interrupted. Admission still respects shared capacity and backlog limits.

**P3-F01-R06.** Each consumer receives its own request identity/link and outcome. One consumer cancelling does not cancel a shared producer still needed by other consumers or canonical coverage.

## Inputs, outputs, and state

Request state: RECORDED, ROUTED, WAITING_FOR_ANSWER, ANSWER_AVAILABLE, INCONCLUSIVE, CANCELLED, CLOSED. These belong to requests; producer tasks use TaskService states. An available answer includes immutable artifact refs and answered/unresolved facets, never a raw conversation pointer.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Implement input normalization and exact equivalence

Use source/evidence refs and canonical assumptions; content digest comparison is deterministic. Natural-language similarity may only produce suggestions, never automatic reuse authority.

### Step 2: Map target to existing units

Use the existing inventory/review-unit membership, including SCCs. Promote required queued work through scheduler APIs, not direct priority SQL from the model.

### Step 3: Route active work through its inbox

Record a pending request message and the consuming relation. If the reviewer declines or finishes without covering it, create supplementary work with the same request identity.

### Step 4: Return nonblocking routing receipt

The original analyst may keep working. Only an explicit yield tied to unresolved blocking requests releases its slot.

## Failure, concurrency, and recovery

Unknown target locator is a mapping request, not a guessed symbol. A failed canonical unit remains visible; other requests continue. Race between matching and producer creation is serialized with request-equivalence uniqueness and task idempotency.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P3-F01-T01 | Queued owner exists | Attach context and reprioritize, no redundant whole-file task. |
| P3-F01-T02 | Matching answer accepted | Return answer refs with compatibility proof. |
| P3-F01-T03 | Two equivalent concurrent requests | One producer, two consumers. |
| P3-F01-T04 | Same symbol but different assumptions | Separate requests. |
| P3-F01-T05 | Reviewer finishes before inbox receipt | Supplementary review remains routable. |
| P3-F01-T06 | One consumer cancels | Shared remaining work unaffected. |

## Do not overengineer or expand scope

No manager-model router, universal natural-language dedup, duplicated file review by default or private transcript sharing.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
