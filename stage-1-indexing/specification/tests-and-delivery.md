# Acceptance, integration and delivery

The inherited requirement documents retain their individual acceptance IDs. TRACEABILITY.json maps all 83 approved requirement IDs to bounded work tasks; it is not evidence that the implementation passed them. Run the inherited scenarios plus the gates below. Do not replace real Git/PostgreSQL/parser/scanner tests with the specification's pure reference checks.

## Fixture layout

Use `tests/fixtures/capture/`, `tests/fixtures/languages/<language>/`, `tests/fixtures/rules/`, and `tests/support/`. Helpers are shared support modules, not imported from other test cases. Every fixture has a short purpose and expected machine-readable output. Avoid relying on a developer's filesystem, credentials, locale, installed global ignore files or mutable remote branch. Use temporary roots/databases; never mutate live researcher storage.

## Required gates

| Gate | Required proof |
|---|---|
| G01 Local capture | Working vs staged/HEAD bytes, tracked/untracked/ignored files, deletions, no vendor-name exclusion, existing submodule edits; source Git state is byte-for-byte unchanged. |
| G02 Remote intake | Default and explicit revisions, HTTPS-only/public access, no ambient credentials, relative and nested submodule pins, explicit opt-out, no LFS download. |
| G03 Snapshot boundary | External/broken/cyclic links, included-target aliases, flattened submodules, raw filters/newlines preserved, no source lookup after original deletion. |
| G04 Capture crashes | Kill before/after Git objects, commit/ref and PostgreSQL READY; reconcile exactly one matching snapshot or report an integrity failure. |
| G05 Classification | Versioned encoding/language metadata and overrides; binary/unsupported treatment; query-ready totals match the frozen per-file plan. |
| G06 Adapter coverage | Every supported language/dialect and its specified construct matrix, Unicode/CRLF spans, valid-empty files and actual parse errors. |
| G07 Binding precision | C++ new-object/member call succeeds; aliases/imports/shadowing/overloads/virtual/context disagreements are not guessed; processing order does not change the final digest. |
| G08 Calls and ownership | Callback argument vs invocation, module commands, nested lambda bodies, multiple same-line callsites and multiple calls from one owner remain distinct. |
| G09 Rule selection | Built-in/custom combined and custom-only, invalid/empty selection, conflicts, identical duplicates and frozen rule definitions/provenance. |
| G10 Scanner accounting | All expected applicable files appear in completion evidence; large/generated/minified files and target ignore/suppression settings cannot silently disappear. |
| G11 Retry/replay | Crash after staging and after commit-before-ack; stale lease predecessor rejected; no duplicated records/completion or loss of successful independent steps. |
| G12 Byte reading | Every supported codec, original-byte offsets, inclusive line requests/exclusive source endpoints, character-safe fragments, empty files and exact direct-ID reads. |
| G13 Response budgets | 50,000 default, allowed overrides, escaping/framing, calculated insufficient-budget error, whole-response cap and metadata-growth reserve. |
| G14 Continuations | Session-independent fixed sections across replay/interleaving/default changes, validation of wrong source/type/range/token, no shared advancing position. |
| G15 Navigation | Names, content regex, one-hop references, flags, outlines, paths and occurrence subpages; unflagged/unsupported text remains accessible. |
| G16 Live pages | Insert-before/after cursor, merged symbol groups, changed query rejected, changed limit allowed; refresh after completion enumerates every matching record once. |
| G17 Errors | Batched independent errors, prerequisite-aware validation, source/input units, actionable correction, no secrets/stacks, no failed query disguised as no matches. |
| G18 Completion | Required file/component census equals published success census, zero outstanding applicable failures, explicit exclusions/limitations retained. |
| G19 Packaging | Fresh wheel/resource loading on Linux x86-64 and macOS arm64; actual supported tool probes. Windows is documented as WSL2 rather than untested native support. |
| G20 Restore/performance | PostgreSQL plus Git backup/restore, exact-source rereads; both pinned corpora below at 1/2/4/8 heavy slots, three fresh-storage repetitions each, with stage timings/RSS and normalized success/failure comparison. |

## Required consistency queries

The compiler context gates additionally audit both frozen censuses and the union
of file/context work families. Exercise missing context work, invalid-input
publications, failed attempts, proven inactive/nonvisited references, stale
publication reconstruction, all-context reconciliation and opposite-order
cross-family lock schedules as specified in compiler-work.md. The profile gates
must consume mapped SemanticProfile values through actual registry/adapter owners,
not merely compare authored fixture metadata. Native isolation gates use the
chosen macOS/Linux launch policies with positive controls, denied filesystem,
executable-mapping and network operations, readiness identity checks and actual
compiler/scanner tool probes. Pure regressions and the trusted C macOS smoke
receipt do not substitute for those runtime gates.

Audit work_units against the frozen applicable plan; count each file once per logical step. Join active publications and compare their result_count/digest against actual typed rows. Resolve every occurrence range against file size. Verify every binding target belongs to visible extraction records from the same snapshot/profile. Verify each successful dataset has no pending/running/failed required work and cannot accept new publication. Compare the full normalized extraction/binding/flag manifest between serial and parallel executions; exclude only nonsemantic timestamps/worker diagnostics from that comparison.

## Benchmark record

[`benchmark-corpus.json`](../contracts/v1/benchmark-corpus.json) fixes two inputs.
The real corpus is the entire `python/cpython` tree at `v3.12.0`: annotated tag
`0fb6e700c2f94ae0717ee1be7d4e50b2dd480d14`, peeled commit
`0fb18b02c8ad56299d6a2910be0bab8ad601ef24`. Prime verified those object IDs with
`git ls-remote`; this is pin evidence, not capture or benchmark evidence. Use
normal public-HTTPS remote intake and verify the resolved commit. Keep ordinary
source-intake accounting, with no benchmark subset or extra path exclusions.
Never build, import, install, test, source or otherwise execute target code.
CPython includes intentionally invalid test sources: retain actual terminal
failures and blocked downstream work, without weakening parsers or asserting
`index_complete`. Measure reachable phases; a phase blocked by the inventory
barrier is reported as blocked, not zero-time successful work.

The synthetic corpus uses exact UTF-8 source bytes from every language fixture
whose expected extraction files are **all** SUCCEEDED. It includes empty files,
preserves Unicode/CRLF, and repeats each entire eligible fixture 100 times at
`replica-NNNN/{fixture_id}/{source_path}`, starting with `replica-0001`.
The pin is 20 cases and 28 files / 2,557 bytes per replica; the default census is
2,800 unique paths / 255,700 bytes. Every path has its byte count and SHA-256;
the full sorted census has a pinned digest. Identical content does not collapse
distinct paths. This tiny-source volume workload is not real-world
representativeness. Check fixture semantics individually with their own profiles
using the language comparator; combined replication does not imply identical
bindings, compatible profiles or an all-success runtime result.

From the repository root, the default command emits manifest JSON only:

```sh
python3 -B stage-1-indexing/validation/reference_benchmark.py
python3 -B stage-1-indexing/validation/regressions/test_benchmark.py
```

For materialization, add `--output /absolute/trusted/parent/new-corpus`; the
parent must already exist and no component may be a symlink. The output must be
new, even if an existing directory is empty. The generator writes only source
bytes there and still emits the manifest on stdout; store that manifest outside
the captured tree. `--replicas 1` is the temporary-directory smoke test, not the
default benchmark. An I/O failure leaves an explicit error and possible partial
directory for inspection, never an overwrite or automatic cleanup. Generator
tests prove census/write behavior only; they run no parser or benchmark.

For **each** corpus, freeze one explicit semantic profile, tools and rule
selection, then run a serial baseline (1 heavy slot) and 2/4/8 heavy slots, with
three fresh-storage repetitions per configuration: 12 measurements per corpus.
Set `workers.scanner_slots=min(2, workers.heavy_slots)` before validating settings:
the serial run uses one scanner slot, and the other runs use two. Do not submit
scanner_slots=2 with heavy_slots=1; that violates the shared strict settings schema.
Compiler/scanner work also consumes heavy slots. Each
repetition gets a new disposable PostgreSQL database and managed Git store, with
no extraction/resolution/flagging dataset reuse. Record OS/tool-cache state;
fresh application storage does not claim cold filesystem caches. Do not execute
builds to obtain compiler inputs; missing context remains explicit. Freeze
per-path language overrides and any supplied build contexts in the profile.

Record repository locator and resolved commit or generated census digest,
managed snapshot/tree, included file/line/byte counts, language distribution,
excluded paths/reasons/counts, application commit and dependency lock, exact
installed parser/grammar/query/compiler/scanner versions and resource/executable
digests, rule mode/manifest/digest, resolved semantic profile digests,
hardware/runtime, PostgreSQL settings and worker budgets. Report every repetition
and capture, metadata planning, extraction, resolution, flagging, database
publication and representative query times separately, with peak RSS and
retry/error counts. Compare the full normalized success records **and** file/work
census, terminal failure classifications, blocked work and completeness state
against the serial baseline. Replace run-local IDs with stable physical locators;
retain semantic diagnostics and remove only documented timestamps, transient
attempt data and worker/runtime diagnostics. A missing or differing result fails
the comparison; terminal completion is not successful index completion. Report
warm dataset reuse separately with reused identities/counts. No performance claim
is established by these assets or by corpus generation; do not infer a universal
indexing SLA or count hidden skips as improvement.

## Task receipt

Use one rolling `IMPLEMENTATION_RECEIPT.md` with: task ID; scope/requirement IDs; owning package and changed files; exact test commands and exit/results; production entry point demonstrated; blockers/unrun gates; commit; next ready task. Keep development notes outside AGENTS.md. After two failed attempts at the same issue, attach a minimal reproduction and the revised diagnostic approach rather than issuing another speculative patch.

## Release receipt

W15 records every gate as PASS, FAIL or NOT RUN, with evidence. PASS requires the real dependency and entry-point path. A missing platform, compiler or Semgrep executable is NOT RUN, not pass-by-mock. A specification schema check is not a database migration test or a security-finding validation. Do not describe Stage 1 as implemented until all required runtime gates pass. No provider calls or target execution are needed to prove this stage.
