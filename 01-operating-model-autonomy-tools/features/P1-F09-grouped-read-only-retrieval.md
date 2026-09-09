# P1-F09 — Grouped read-only retrieval

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P1-F02`, `P1-F07`, `P1-F08`

## Purpose and concrete outcome

An agent may collect several already-known independent source or metadata results in one turn, without multiplying budgets or surrendering control over its next analytical step.

## Existing implementation and ownership

Reuse the current agent runner’s parallel-tool negotiation, query readers and per-attempt accounting. A read_batch handler is a narrow composition of existing read-like tools, not a second tool executor.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P1-F09-R01.** Allow only the read-like whitelist in TOOLS.md; no submission, lead, checkpoint, context request, yield or operator control. document_query may create its specified interest metadata but not analytical work.

**P1-F09-R02.** Each item has a unique caller-local key and independent validated arguments. Do not allow an item to depend on a result from another item in the same batch; the host cannot guess missing IDs.

**P1-F09-R03.** Enforce one combined response/source/context allowance before dispatch and before final delivery. Return stable item-key order regardless of completion order. A partial/failed item does not make other items empty successful results.

**P1-F09-R04.** Use separate read connections per truly parallel operation; otherwise execute sequentially. Bound host I/O and matcher capacity independently of analytical worker count.

**P1-F09-R05.** Record only source actually included in the final outgoing message for each item and retain per-item errors/continuations. Never mark an entire batch read because it was requested.

**P1-F09-R06.** Cancellation stops not-yet-started items and marks them NOT_EXECUTED. Completed safe bookkeeping keeps its actual receipt; no implied rollback or batch write atomicity.

## Inputs, outputs, and state

Input `{items:[{key,tool,arguments}]}` has a configurable maximum of 8. Per-item status and data use the same single-tool contracts. Host applies conservative preflight allocation in input order, then fills remaining space in that same order; no hidden fetch-all or surplus provider call.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Define registry whitelist

Reference the actual tool registry and capability matrix; no string dispatch to unregistered arbitrary tools.

### Step 2: Implement bounded planning

Reserve combined output and host resources, validate independent IDs, and schedule through existing executors with correct DB ownership. Keep a serial fallback when concurrency is not supported.

### Step 3: Compose deterministically

Budget actual encoded result size, preserve minimum error/completeness envelopes and provide continuation for deferred data. Do not drop a discovered hit and advance its cursor.

### Step 4: Integrate request delivery

Associate each surviving source interval/artifact with the real outgoing request. Propagate notices through the common hook without duplicating them in every batch item.

## Failure, concurrency, and recovery

A stale lease during a batch denies later operations; already delivered source remains accounted. Timeout of one matcher cannot kill sibling work. Duplicate item keys or attempting a write is a structural rejection before that action starts.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P1-F09-T01 | Three known symbols requested together | Stable individually identified results. |
| P1-F09-T02 | One missing subject | Other outcomes preserved; missing item explicit. |
| P1-F09-T03 | Combined budget smaller than sum | Bounded partial data with no false read credit. |
| P1-F09-T04 | Write tool in batch | Rejected before mutation. |
| P1-F09-T05 | Concurrent DB reads | No shared SQLite connection across threads. |
| P1-F09-T06 | Cancel halfway | Remaining items NOT_EXECUTED; no fake rollback. |

## Do not overengineer or expand scope

No automatic task graph within a batch, transactional writes, unbounded thread spawning, or assumption that optional provider parallel tools are universally available.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
