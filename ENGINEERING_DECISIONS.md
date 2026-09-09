# Delegated engineering decisions

Version: 2.0 · 2026-09-09 · Design choices, not implemented capabilities.

## Authorization and precedence

The user explicitly requested completing the remaining documentation without further consultation. This supersedes the earlier requirement to pause after each new design choice **for document authoring only**. Prior user-approved behavior remains controlling. Code modification, migration, live experiments, release installation, and deployment still require their own tasks.

This package supplies one buildable recommended design, not a menu of unresolved alternatives. New choices below are **DELEGATED_SELECTION**, not falsely recorded as individually user-approved. Exact local helper names may change without changing contracts. Empirical release gates and current-worktree verification are execution prerequisites, not undecided design.

The preserved decision register and prior F01/F02 documents are in `history/before-delegated-completion/`. The active phase/feature documents and `contracts/` replace their pending-detail statements. No previously approved behavioral rule is intentionally revoked. `contracts/` owns cross-feature wire/state details; phase features own their behavior; the traceability map links both.

## Decisions

| ID | Selection | Reason / limit |
|---|---|---|
| E01 | One harness process architecture and existing SQLite stores; extend existing task/attempt/candidate owners. | No broker service, vector store, manager-model bottleneck, or separate agent framework. |
| E02 | `collaborative-v1` is a new immutable per-review contract; legacy reviews retain their recorded semantics. | Do not reinterpret old receipts or turn a refactor into a workflow migration. |
| E03 | A long-lived inquiry uses a durable task ID; attempts are disposable executions. | No second scheduler or mandatory new inquiry subsystem. New task types are FOCUSED_ANALYSIS and CONTEXT_REVIEW; investigation/falsification reuse their canonical roles. |
| E04 | Accepted contextual answers may be published before completion of the larger assignment. | They have separate immutable artifacts, validation and turn-level acceptance receipts; no private-note shortcut or fake coverage credit. |
| E05 | A new independent lead is an existing-style SEEDED candidate plus canonical investigation work and explicit producer provenance. | No shadow lead database. Source-grounded suspicion is enough to request analysis; no proof required before investigation starts. |
| E06 | Dependency-free default orientation: deterministic project sketch plus reviewer discoveries; no mandatory orientation analyst. | Architecture questions can be ordinary bounded focused work when genuinely unresolved. |
| E07 | Route contextual requests first to compatible accepted answers, then canonical queued/running work, then supplementary review. | Never duplicate all-file review just to answer one missing fact. Running work sees an explicit request message, not a mutation of its original signed input. |
| E08 | Coverage credit requires an accepted result matching a complete canonical review unit contract. | Answers and partial focused reads do not count; full compatible results can be adopted without another mandatory model pass. |
| E09 | Exact request equivalence permits joining; semantic duplicate suggestions do not silently merge independent hypotheses. | Same file, CWE, sink or name is insufficient identity. |
| E10 | Durable result availability sequence, interests, and request-bound notices live in source-free harness metadata. | Notifications are optional reading hints; invalidation and blocking dependencies have separate authority. |
| E11 | Source/search/list cursors use versioned, domain-separated HMAC tokens with persistent project-local authentication keys. | Tokens locate data; they are never access grants or proof of source consumption. |
| E12 | `google-re2` official wrapper is the selected regex capability, using a bounded host-owned matcher process; literal case-sensitive matching uses standard-library search. | Pin tested artifacts in SSR's dependency/release lock; never install target tools or fall back to backtracking regex. |
| E13 | Strict UTF-8, ASCII and ISO-8859-1 text matching initially; no newline/Unicode normalization. | Other encoding support is an explicit extension; metadata and byte-based evidence remain usable where permitted. |
| E14 | Search continuation repeats the query and selection and authenticates their digests plus a safe file/position cursor. | No query text in cursor payload, per-search worker memory requirement, or per-page database session. |
| E15 | Work-conserving shared pool; every fourth dispatch services eligible canonical coverage when competing work exists. | Initial testable policy, not an empirically optimal ratio. Empty reservations are loaned; no healthy worker preemption. |
| E16 | Prioritize required unblocking and adjudication over opening optional new discovery. | Protect coverage and existing candidates from unbounded speculative fan-out. |
| E17 | Candidate current-validity is a separate authoritative projection; historical verdicts are immutable. | Source-backed material counterevidence holds current export and schedules revalidation without rewriting history. |
| E18 | Public SDK changes use explicit collaborative capability surfaces while preserving legacy methods/signatures. | Controller cannot guess or bypass strict SDK negotiation. |
| E19 | No full freeze of result visibility across listing pages. H bounds new arrivals; current access/status still applies. | Restore/re-availability gets a new epoch and new availability sequence. |
| E20 | No new runtime behavior is enabled before baseline, schema, publication, SDK and regression gates pass. | Documentation is complete even though application verification has not been performed. |

## Explicit exclusions

No source-target execution/build/tests/install, live migration, generic shell tool for review agents, network access beyond configured providers and separately provisioned trusted analyzers, generated PoC, automatic archive extraction, foundation-model training, microservices, generic event bus, inferred final findings, or model-manager approval for ordinary navigation.

Numeric values in CONFIGURATION.md are conservative **initial engineering defaults**, configurable per new review and requiring measurement before a scale claim. They are not universal findings about model efficiency.
