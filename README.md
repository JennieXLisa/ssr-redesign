# SSR redesign

Ground-up implementation specification for a researcher-directed source review tool.

Start with [AGENTS.md](AGENTS.md), then [Stage 1 implementation entry point](stage-1-indexing/IMPLEMENTATION.md). Stage 1 covers source intake, immutable Git snapshots, PostgreSQL indexing, supported reference resolution, reconnaissance flags and navigation. It makes no model calls and does not require whole-repository model review.

The implementation package contains capability-owned design documents, strict API models, the initial PostgreSQL schema, configuration and rule examples, reference checks, and 15 dependency-ordered work recipes. Start with W01; complete its acceptance checks and receipt before moving to W02. Historical approved requirements remain in `stage-1-indexing/requirements/`.

See [validation and implementation status](stage-1-indexing/VALIDATION.md) before interpreting any test claim. Passing the specification checks is not proof that the harness, parsers, compiler integration or scanner have been implemented.

## Previous design archive

The previous repository state is retained on [`archive/2026-09-12/main`](https://github.com/JennieXLisa/ssr-redesign/tree/archive/2026-09-12/main), at commit `29290fc9addf30e73db95b052a557e7b6f655470`. It is historical reference, not the active assignment for this restart. No legacy workflow or old-database migration is required.

Only this planning repository is changed. `source-review-harness` and `ssr-control` remain outside this documentation work.
