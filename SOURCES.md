# Reference baseline and evidence limits

These are implementation references, not a claim that the remote branch, local
worktree, installed distribution, or running controller is at this version today.

## Harness reference

Repository: `JennieXLisa/source-review-harness`  
Requested branch in the design conversation: `codex/0.1.2-investigation-tool-recovery`  
Inspected commit: `8b7ed0e335d4f4fb5ae53ef6e059334661279f20`

- [Broker authorization and construction](https://github.com/JennieXLisa/source-review-harness/blob/8b7ed0e335d4f4fb5ae53ef6e059334661279f20/src/ssr/tools.py#L590-L830): assigned-file checks, assignment symbol collection, scope/context-size coupling and attempt-local read state were re-read for this save.
- [Source access and verification](https://github.com/JennieXLisa/source-review-harness/blob/8b7ed0e335d4f4fb5ae53ef6e059334661279f20/src/ssr/source.py#L1-L240): `SourceScope`, `SourceResolver.resolve`, `read_verified_file`, captured classifications, coordinates, hashes and safe file reads were re-read for this save.

Other code references in this package identify paths inspected earlier in the
conversation. Before implementation, verify their refactored equivalents, callers,
contracts and tests. Code movement is not proof of changed or unchanged behavior.

## Document and conversation basis

The earlier `PHASES.md`, `DECISION_REGISTER.md`, and Phase 1 `DISCUSSION.md` were
read in full before this revision and copied unchanged to `history/roadmap-v1.0/`.
The current feature agreements are based on the user's explicit responses after
that checkpoint. They supersede earlier suggestions only where a decision was
actually made; open questions remain open.

No implementation repository or existing specification was changed. No runtime,
security, concurrency, or application test was executed during preparation of
this documentation package. File and link checks are documentation checks only.
