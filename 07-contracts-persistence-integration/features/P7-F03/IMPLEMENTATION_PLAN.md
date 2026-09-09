# P7-F03 — Configuration, versioning and rollout: implementation plan

Updated: 2026-09-09. Documentation only. Read the [feature](../P7-F03-configuration-versioning-and-rollout.md), [CONFIGURATION.md](../../../contracts/CONFIGURATION.md), [SDK.md](../../../contracts/SDK.md), P7-F01 migration and P8-F03 release.

## Contract-hardening integration — Collaborative-only cutover and immutable effective configuration

Apply CUTOVER.md: new release creates only collaborative-v1 reviews; explicit legacy execution is rejected, not an alternative default. Old reviews remain historical and cannot be resumed by rewriting their phase/mode. Preserve original bytes and optional read-only inspection separately. Require old writer/lease/provider settlement before storage cutover.

Freeze context/counter, limits, schema/ABI, prefix/runtime and state digests in effective review policy. Pin one new harness/controller pair and test mismatch refusal, clean installed packages and two-store activation failure. Cursor secret repair is an explicit operator action and does not reset budgets or promote old receipts. Rollback requires exact pre-cutover backup/binaries and exclusive writer proof, never an old executable opened on new schema.

Normative source: [hardening contract index](../../../CONTRACT_HARDENING.md). Preserve the existing feature procedure below except where this explicit correction replaces it; implement the linked exact schemas, not a local incompatible approximation.

## 1. Map parsing to immutable review identity

Locate current config models, parser/normalization/hash functions, review creation/resume, backend capability probes, execution-contract construction and controller config-revision services. Add the single-value `review.execution_mode` contract collaborative-v1 for new reviews. Existing rows retain historical mode identity and are not executable. Capability preflight and exclusive cutover are mandatory.

Keep operator configuration, normalized effective review configuration and per-attempt request overrides distinct. Resolve defaults once through the existing normalizer and bind the effective digest. No worker may reinterpret an omitted setting differently after a package upgrade. An invocation cannot switch an active legacy review to collaborative mode by supplying a tool argument.

## 2. Validate numerical and logical limits together

Implement CONFIGURATION.md's selected settings with exact units and bounds: page/result/cursor sizes, pattern/scan/preview limits, matcher process/memory limits, batch size, interests/notices/change-page limits, contextual fan-out/depth/revisions, coverage service cadence, optional backlog and no-progress policy. Do not duplicate defaults in a broker helper, UI form and scheduler.

Validate cross-field constraints, not just positive integers. A minimal result/error envelope must fit the allowed response size. Source preview/page and batch allowances cannot exceed the effective tool/context ceilings. Matcher memory includes decoded source, byte maps and native engine allocations. Request maximum output plus input/overhead must fit the probed context. A configured worker ceiling above a provider grant is a requested bound, not guaranteed capacity.

Reject booleans in integer fields, nonfinite numeric values, ambiguous units and unknown policy versions. Include effective values in source-free configuration projections so the developer/operator can see actual limits. Configuration validity does not prove measured performance.

## 3. Capability manifest and enablement

Build a host-generated capability manifest from installed code/schema support, backend protocol probes, producer receipt support, matcher/analyzer availability and public SDK contract versions. Bind its digest to the review/admission contract.

A feature is advertised only when its complete path exists: parser, authorization, handler, domain persistence/receipt acceptance, query projection, recovery and required tests. A new schema enum alone is not a supported capability. Missing mid-review transcript turn sealing disables early publication rather than fabricating receipts. Regex capability absence leaves literal search available with explicit regex-unavailable responses. Optional Semgrep absence does not block basic canonical review.

Backend probes must not be inferred from model/package names. A change in model/protocol/context support creates a new recorded route/capability result, not an invisible reinterpretation of an admitted attempt. Paid/live probes require separate explicit authorization where they invoke a provider.

## 4. Preserve historical identity without old execution

Keep original prompt text, tool names/order/descriptions/schema encodings, result schema versions, parser scope and execution hashes for old-contract attempts. Add separate collaborative schema/projection versions; do not mutate a shared global definition and then exempt old tests.

Old stored checkpoints/results/receipts are decoded through their exact contract owner. Unsupported future versions fail explicitly before execution/acceptance. Compatibility reexports preserve documented public import/class identity. Do not change public schema ranges to conceal that a migration or field is missing.

A source-only modular extraction should not change behavior hashes. New behavior changes are separate commits/versions with paired tests. Historical SQL migration bytes/checksums remain immutable.

## 5. Provision cursor secrets safely

Use the project-private `.host-secrets/cursor-key-v1.json` contract: format version, generation/key identity and encoded 32-byte secret. The existing coordinator/storage owner validates path containment, owner/permissions and absence of symlink substitution. Serialize initialization; create a protected temporary file exclusively, flush/fsync, publish without overwriting an established key, and fsync the directory where the platform requires it. Record source-free provisioning identity after verifying the file.

Handle the crash between file publication and provisioning receipt by verifying and adopting that exact valid established file. Handle a receipt with missing/corrupt key as an explicit repair condition. Never regenerate silently in ordinary reads, restart or a random worker. Multiple workers load the same established generation without sharing cursor positions.

Rotation is an authenticated operator action serialized against provisioning. Retain one active generation; explicitly invalidate old convenience tokens and advertise a fresh-read recovery path. Rotation does not alter durable evidence bytes or make old transcript content invalid. Backup/restore must preserve both key and source-free provisioning identity when continuation is intended; otherwise record that tokens cannot be resumed. Never include the secret in ordinary config exports or model context.

## 6. Additive rollout and compatibility gates

Allocate migration numbers from the actual current checkout and supported horizon. Apply new schema only through the existing coordinator command on isolated fixtures during development. Enable new-mode creation only after the full required migration batch and capability manifest are consistent. A partially migrated database cannot advertise collaborative-v1.

Keep new behavior disabled for existing reviews and unpaired controllers. R0–R7 are implementation gates, not permanent user-visible runtime modes. Do not create a separate experimental mode for every unfinished feature. Components may be developed behind an unavailable capability until their dependent receipt/worker paths exist.

Controller configuration revision updates produce new immutable revisions for future commands/reviews. An active dynamic plan binds the old config/control generation and is invalidated explicitly on relevant changes. Ordinary queue publications are not config changes.

## 7. Release artifact and rollback contract

Create a release manifest only from actual built artifacts: source commit and clean status, wheel/sdist names and SHA-256, schema horizon/checksums, SDK/tool/mode/producer versions, optional matcher/analyzer rule artifact identities, controller version and packaged frontend hash manifest. Do not use a moving branch or 'latest wheel' as immutable pairing coordinates.

An operator deploys only after separately authorized release gates. A rollback to code that cannot read new schema is not a simple pip downgrade. The procedure must restore a consistent backup into a compatible environment or keep a reader-compatible recovery version; stop mutation first through real control/liveness authority. No automatic destructive down-migration or historical migration edit is permitted.

Missing optional tools remain visible limitations. Missing mandatory integrity/receipt support prevents enablement, even when a benchmark looks faster.

## 8. Tests

Normalize equivalent explicit/default configurations and compare expected effective digests. Change one behavior setting and verify the relevant contract digest changes. Open an old review read-only after cutover: original mode/prompts/tool hashes remain unchanged and runtime resume is rejected. Reject an attempted in-place mode switch or stale dynamic plan.

Test all cross-field limits, unsupported enums, boolean integers and strict currency without sound provider pricing. Disable regex/analyzer dependencies and verify declared capability behavior without fallback engines or hidden installs. Remove the turn-seal support and verify early publication is not advertised.

Run concurrent secret initialization, crash after key publication before receipt, missing key after receipt, tampered generation and explicit rotation. Assert one established secret, no exposure and correct invalidation/recovery. Test backup restoration of matching/mismatched provisioning records.

Build clean artifacts and run the matching collaborative harness/controller pair and explicit incompatible-pair refusal tests; no legacy runtime emulation is supported. Simulate rollback incompatibility and ensure the documented restore/recovery path is required instead of opening new schema with an old writer.

## 9. Delivery sequence and exit

Implement typed config/normalization fixtures; add mode/capability pinning; preserve legacy serialization tests; implement safe secret provisioning; add preflight/upgrade gates and controller config projections; then build paired artifacts under separate authorization. Completion evidence includes exact effective configs/hashes, migration/probe results and actual artifact coordinates. No silent default upgrade, guessed installed versions, permanent partial-mode proliferation or automatic live restart is allowed.
