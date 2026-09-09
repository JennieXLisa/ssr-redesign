# Publication handoff — documentation only

Destination: `JennieXLisa/ssr-redesign`. The user already selected this repository and authorized saving design documents. Do not create another repository, modify implementation repositories or change visibility.

This task produced a complete local document tree. The connector exposed only read actions during this authoring pass; no GitHub commit/push is claimed. The last remote HEAD verified was `017bde3f0c1f59a01ca9d8b11273f5000676a7be`, while local approvals had advanced through v0.16. Use the full current tree, not an incremental patch against only one previous local version.

## Publishing agent steps

1. Read current remote HEAD and list existing files. Clone/use an authorized clean documentation worktree; preserve any intervening remote/user changes.
2. Compare the package with the remote. Copy current documentation/contracts/tools and the explicitly historical approval checkpoint into the repository. Do not copy archives, actual source code, credentials, local environments or implementation data.
3. Run `python tools/validate_docs.py` from the documentation root in its approved environment. Inspect all additions/changes. Record actual results; schema checks require jsonschema, and a missing dependency must be reported rather than silently skipped.
4. Commit only documentation/reference-schema/validation artifacts with an accurate message such as `docs: complete collaborative review design and feature delivery plans` and push using authorized credentials. Do not force-push or reset unrelated work.
5. Fetch the new remote commit/tree and verify changed-path/content hashes. Report the exact repository, branch and commit, with any unresolved merge/publication issue.

Application code, database migrations, dependency installation, model calls and deployment are outside this publication task. Reference schemas and documentation-validator code are not the harness implementation.
