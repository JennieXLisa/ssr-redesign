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
| G20 Restore/performance | PostgreSQL plus Git backup/restore, exact-source rereads, pinned benchmark at 2/4/8 workers with stage timing/RSS/failures. |

## Required consistency queries

Audit work_units against the frozen applicable plan; count each file once per logical step. Join active publications and compare their result_count/digest against actual typed rows. Resolve every occurrence range against file size. Verify every binding target belongs to visible extraction records from the same snapshot/profile. Verify each successful dataset has no pending/running/failed required work and cannot accept new publication. Compare the full normalized extraction/binding/flag manifest between serial and parallel executions; exclude only nonsemantic timestamps/worker diagnostics from that comparison.

## Benchmark record

Record repository locator and resolved source commit, managed snapshot/tree, included file/line/byte counts, language distribution, excluded paths/counts, parser/compiler/scanner versions, rule digest, hardware/runtime, PostgreSQL settings and worker budget. Report capture, metadata planning, extraction, resolution, flagging, database publication and representative query times separately. Include peak RSS and retry/error counts. Do not turn a one-repository result into a universal indexing SLA or count hidden skips as performance improvement.

## Task receipt

Use one rolling `IMPLEMENTATION_RECEIPT.md` with: task ID; scope/requirement IDs; owning package and changed files; exact test commands and exit/results; production entry point demonstrated; blockers/unrun gates; commit; next ready task. Keep development notes outside AGENTS.md. After two failed attempts at the same issue, attach a minimal reproduction and the revised diagnostic approach rather than issuing another speculative patch.

## Release receipt

W15 records every gate as PASS, FAIL or NOT RUN, with evidence. PASS requires the real dependency and entry-point path. A missing platform, compiler or Semgrep executable is NOT RUN, not pass-by-mock. A specification schema check is not a database migration test or a security-finding validation. Do not describe Stage 1 as implemented until all required runtime gates pass. No provider calls or target execution are needed to prove this stage.
