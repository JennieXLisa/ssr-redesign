# P2-F04 — Host-first queries and trusted analyzer integration

Version: 1.0 · Authored: 2026-09-09  
Document status: DRAFT COMPLETE — delegated engineering detail; not an implementation claim.  
Decision basis: previously agreed behavior where applicable, plus [delegated choices](../../ENGINEERING_DECISIONS.md).  
Dependencies: `P2-F01`, `P4-F01`, `P6-F03`

**Contract-hardening revision:** apply the concrete corrections in [P2-F04/IMPLEMENTATION_PLAN.md](P2-F04/IMPLEMENTATION_PLAN.md) and the [hardening index](../../CONTRACT_HARDENING.md). Earlier summary wording is not a substitute for the exact input, receipt, state, synthesis, context and cutover contracts.

## Purpose and concrete outcome

Use code for mechanical questions and suitable trusted analyzers for supported static checks, reserving model workers for genuinely unresolved interpretation.

## Existing implementation and ownership

Reuse language adapters, parser diagnostics, source/evidence verification and observation registry. A new adapter is a host-owned provider of observations, never a fake model task/agent receipt.

Consult [BASELINE.md](../../BASELINE.md) before editing code. Verified paths locate current responsibilities; proposed new private helper names are not mandates for new services. Preserve existing public facades and accepted historical results.

## Detailed requirements

**P2-F04-R01.** Classify requests against a declared capability map: exact lookup/graph enumeration is host work; supported syntactic patterns are analyzer work; reachability/control sufficiency with gaps is model analysis.

**P2-F04-R02.** Trusted analyzer invocation uses an SSR-provisioned immutable executable and rule bundle, fixed argument builder and read-only snapshot input. Reject target-provided config/plugins/hooks and all network downloads.

**P2-F04-R03.** Normalize results to exact snapshot paths/ranges/hashes plus rule/version and limitations. A hit is an observation; a clean supported scan is not a canonical semantic coverage waiver.

**P2-F04-R04.** Every run distinguishes selected, examined, skipped, failed and unsupported files. Bound CPU, memory, wall time, stdout/stderr and result count. Do not silently ignore analyzer truncation.

**P2-F04-R05.** No scanner dependency is needed to start canonical review. The optional Semgrep adapter is disabled when unprovisioned; absence is visible and no target package manager is invoked.

**P2-F04-R06.** Host/analyzer answers have real producer receipts, not fabricated agent_run IDs or provider usage. Their assertions are limited to advertised capability semantics.

## Inputs, outputs, and state

AnalyzerRun: host operation ID, snapshot, executable/rule/options digests, input manifest selection digest, resources, result/limitation counts and status. Raw tool output is ephemeral or in explicitly governed diagnostics; normalized source-free observations enter ordinary metadata.

The shared [tool contracts](../../contracts/TOOLS.md), [state and storage contract](../../contracts/STATE.md), and [configuration contract](../../contracts/CONFIGURATION.md) define reusable fields. This feature owns the behavior below; it does not create a competing lifecycle or database.

## Ordered implementation

### Step 1: Implement capability dispatcher

Match typed mechanical query kinds first. Return a typed unsupported answer when the requested semantic property exceeds the host capability; no false security judgment.

### Step 2: Build optional scanner adapter

Use a trusted subprocess wrapper isolated from target environment/configuration, network disabled and outputs bounded. Keep scanner processes under host-resource admission.

### Step 3: Normalize and verify

Resolve every result path back to manifest, verify source span, strip copied source from persisted result, and reject foreign paths or inconsistent hashes.

### Step 4: Test absence and malicious input

Fixture malicious target config or executable names must never be invoked. Test invalid output ranges, partial scan, timeout and clean result with full canonical coverage still outstanding.

## Failure, concurrency, and recovery

Tool crash is an analyzer failure, not no vulnerabilities. A missing provisioned executable never triggers installation. Provider budgets and analyzer resources remain separately accounted; neither may overrun the host’s global limits.

## Acceptance tests

These are tests to implement and execute, not test results from document authoring.

| Test | Fixture or action | Required observable outcome |
|---|---|---|
| P2-F04-T01 | Exact symbol-binding query supported | No model call. |
| P2-F04-T02 | Requested control sufficiency unsupported | Explicit semantic escalation. |
| P2-F04-T03 | Target carries analyzer configuration | Ignored as execution authority. |
| P2-F04-T04 | Scanner points outside snapshot | Rejected normalized result. |
| P2-F04-T05 | Scanner clean but file not reviewed | Coverage stays incomplete. |
| P2-F04-T06 | Analyzer unavailable | Canonical review continues with explicit discovery limitation. |

## Do not overengineer or expand scope

No general shell exposed to agents, scanner rule downloads, target execution, scanning every alert with a separate model, or fabricated producer identity.

## Definition of done

Implement each requirement through its identified owner; run the tests above and the adjacent existing regressions. Record exact source/distribution identities and actual test collection. Update the requirement-to-test map, public-contract compatibility checks, and package-resource checks where affected. A missing integration or unavailable dependency is a named build/release gate, not a license to silently substitute behavior. No live installation, target execution, provider spend, or deployment is authorized by this document.
