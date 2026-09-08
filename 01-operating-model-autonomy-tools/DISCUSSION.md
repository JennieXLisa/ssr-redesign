# Phase 1 discussion checkpoint

The overall Phase 1 behavior and nine-feature grouping are agreed. See the
[feature index](SPECIFICATION.md) and [decision register](../DECISION_REGISTER.md).

P1-F01's on-demand research policy, separate from execution identity and assignment
ownership, is saved in its detailed draft; refactored mapping and compatibility
questions remain open.

The current discussion is **P1-F02 — indexed navigation and information retrieval**.
The user approved symbol-ID or file-range selection through `source_read`, keeping
`symbol_get` metadata-only, and host-managed source pagination that preserves the
selection, authority checks, original bytes and actual-read accounting.
The user also approved self-contained, integrity-protected cursors with same-review
cross-attempt use and replay from a fixed position. No per-page position registry
or inherited read credit is implied. These decisions are saved in the
[feature document](features/P1-F02-indexed-navigation-and-retrieval.md).

Continue discussing the remaining P1-F02 interfaces and significant implementation
choices. Do not ask for reapproval of source selection or pagination without a
concrete reason to reopen them. The user has now approved HMAC-SHA-256 with a
persistent project-local host secret in owner-protected private storage, serialized
initial creation, shared worker loading and restart reuse. The secret authenticates
independent cursors; it is not a shared reading position. Missing/unverifiable
authentication fails explicitly rather than replacing a secret or trusting fields.

The user also approved extending `symbol_list` with exact local-name and qualified-
name lookup, optionally narrowed by file ID/relative path, containing symbol and
kind. Preserve direct ID retrieval, return distinguishable alternatives and query
completeness, apply authorization before paging, and never infer a callsite binding
from a unique declaration match. These requirements are now saved in R23–R28.

The user has now approved two-step analysis retrieval: compact discovery using
indexed subject IDs, then detail retrieval by exact result ID. Report usable
analysis separately from relevant task status; do not substitute newer results,
merge interpretations, expose private content, wait, or create tasks implicitly.
R29–R36 and guidance A1–A7 record this agreement; Phase 4 still owns acceptance.

The user additionally approved subject-specific freshness notices after asking how
automatic interest registration works. A lookup remembers the ongoing work's
interest; a relevant newly available result is advertised at the next ordinary
interaction without a separate subscribe call. No forced reload, worker interruption,
notice-only model call or task creation occurs. R37–R43 and N1–N6 record this detail.
Interests are attached to tasks/inquiries, not reusable worker slots.

Still open: the exact publication/change marker and changing-list pagination,
notice fields/bounds, coalescing and interrupted-delivery handling, persistence
across normal resumption, query filters, and result visibility integration. Do not
reopen the approved automatic-interest/optional-reload behavior merely to choose
these mechanics. A publication-bounded/keyset listing was proposed but is not yet
the selected algorithm. Other previously open navigation and cursor interfaces
remain open; P1-F02 is not ready for implementation.

Save feature progress after each approval to GitHub or local files and state where
it was saved. Do not wait for the whole phase to finish, and do not generate the
remaining feature designs blindly. The destination is `JennieXLisa/ssr-redesign`;
this checkpoint remains local while its public visibility is unresolved.
