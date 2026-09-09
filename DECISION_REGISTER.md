# SSR collaborative review — decision register

Version: 1.8  
Recorded: 2026-09-08  
Updated: 2026-09-09  
Basis: user-approved direction and constraints in the design conversation.

This register distinguishes agreed direction from implementation detail that has
not been settled. It does not claim that proposed features exist in code.

## Agreed direction

| ID | Decision or constraint | Owning phase |
|---|---|---|
| D-001 | Use the eight documentation phases recorded in PHASES.md. These are not sequential runtime stages. | Roadmap |
| D-002 | Discuss and agree each phase, then write and review its own detailed specification and implementation plan. Do not author all phases blindly. | All |
| D-003 | Develop the new design in separate files. Do not modify existing specifications or old design packages during this documentation work. | All |
| D-004 | The modular refactor and the two repository AGENTS.md files are a separate preparatory workstream. | All |
| D-005 | Understand the existing implementation and retain useful components even where workflow architecture changes. Do not assume a rewrite. | All |
| D-006 | Continuous worker admission already exists and is a baseline to preserve, not a new capability to invent. | 6 |
| D-007 | The system should work like collaborating analysts: prioritize useful security analysis while systematic whole-project review continues. | 1, 2, 6 |
| D-008 | An analyst can request another component's review with its actual context and continue its analysis when the answer arrives. | 3 |
| D-009 | Preserve whole-project coverage. Reuse useful review work where it satisfies the agreed contract; the exact coverage-credit policy remains open. | 4 |
| D-010 | Discovery must cover broad sensitive operations and actual usage semantics, including process execution and file operations—not only a short list of names or a single sink category. | 2 |
| D-011 | Retain useful broker, source-verification, retrieval, and validated-submission capabilities. Develop broader discovery, contextual delegation, incremental publication, and continuation. Exact interfaces and acceptance points remain open. | 1, 3, 4 |
| D-012 | Investigation and independent challenge remain part of reaching supported findings; an initial sink match or an agent's agreement is not enough. | 5 |
| D-013 | The controller remains a public-SDK consumer of harness-owned review authority. Do not introduce competing state or acceptance rules as an integration shortcut. | 7 |
| D-014 | State which requirements and plans are agreed, proposed, blocked, implemented, or tested. Do not conflate those statuses. | All |
| D-015 | Save each feature’s approved progress to the designated GitHub repository or local files after approval, and report the actual saved location. Partial approval must not be labeled a finished feature. | All |

The pool of approximately 100 workers is the user's example of intended scale.
It is not a fixed default, a minimum, an entitlement to provider capacity, or a
measured result.

## Phase 1 agreements added after the first roadmap save

The following records summarize explicit agreements in the conversation. They do
not assert that final schemas, module paths, or rollout behavior were approved.

| Decision | Owner | Agreed behavior or direction |
|---|---|---|
| P1-D01 | P1-F01 | Background reviewers, focused analysts, investigators, and falsifiers receive project-wide read-only research access within the authorized immutable snapshot. Assignment and publication authority remain separate. |
| P1-D02 | P1-F01 | File synthesis also receives source and index access for reconciliation and cross-symbol interactions, not a routine repeat of all completed review work. |
| P1-D03 | P1-F02 | Use the existing symbol/relationship index and IDs as the navigation foundation. Names/paths resolve through that index; source search complements gaps. Index-first is guidance, not a required sequence. |
| P1-D04 | P1-F05 | Agents choose when to submit and may return to research after a repairable rejection. Budgets do not reset; accepted history is not made editable. |
| P1-D05 | P1-F04 | Agents can save structured progress during ordinary work without ending the attempt. Host-requested and agent-requested checkpointing share one mechanism. |
| P1-D06 | P1-F06 | A source-grounded additional suspicion may be registered immediately through a nonterminal tool action, even outside a predefined category. The harness owns its independent follow-up; the proposer continues its original assignment. |
| P1-D07 | P1-F06 / Phase 6 | The harness records the lead and creates or associates follow-up work without waiting for the original task or file synthesis. A full pool means record and queue, not interrupt healthy workers or exceed the limit. Scheduling priority is still open. |
| P1-D08 | P1-F03 | For progress, observations and final submissions, the agent supplies analysis and explicitly chosen references. The host supplies execution identity and resolves indexed/source/evidence metadata from the attempt’s bound inputs. It does not invent missing analytical conclusions. |
| P1-D09 | P1-F07 | Model-visible tool results distinguish missing analysis, ambiguity, limits, invalid inputs, operational failures, and authorization/integrity failures, with field-specific explanations and usable next actions. |
| P1-D10 | P1-F07 | Collect independent validation errors in one bounded response where safe. Stop when prerequisites, authorization or integrity prevent meaningful further checks. Mark dependent checks not evaluated instead of fabricating extra errors. |
| P1-D11 | P1-F08 | Host-managed retries recover an action’s original outcome and acknowledgments without duplicating effects. Registration reliability is separate from lead investigation and from semantic duplicate detection. |
| P1-D12 | P1-F09 | Support optional grouped independent read-only retrieval with individually identified results, combined response limits and explicit partial outcomes. This is not batch-write atomicity. |
| P1-D13 | Phase 1 | Adopt nine feature documents, P1-F01 through P1-F09, each owning detailed specification, implementation guidance and tests. Phase documents integrate rather than duplicate them. |
| P1-D14 | P1-F01 | Separate execution identity, assignment ownership and research policy. Check snapshot-level research permission against the existing manifest/index on demand; do not copy every file/symbol into each worker or equate access size with context size. |
| P1-D15 | P1-F01 | Retain existing attempt/lease checks, source integrity and result ownership. Use a focused authorization component integrated with existing broker/resolver services; no separate permissions platform or second inventory is required. |
| P1-D16 | P1-F02 | Keep `symbol_get` metadata-only. Extend `source_read` to accept a known symbol ID or an explicit file/line selection through one authorization and verified-reading path; reject conflicting selectors. |
| P1-D17 | P1-F02 | A symbol read defaults to the indexed full-symbol range. Do not automatically include containing types, callers or helpers; include annotations only as supported by the indexed range. |
| P1-D18 | P1-F02 | Page valid oversized symbol and file-range selections with a host-generated continuation bound to the same snapshot, file, original selection and next position. Recheck current authority on every page. |
| P1-D19 | P1-F02 | Prefer full source lines but explicitly support partial long lines at valid character boundaries for supported encodings. Preserve original byte coordinates/hashes and keep presentation metadata separate. |
| P1-D20 | P1-F02 | The agent controls continuation; no automatic fetch-all or limit resets. Record only source actually delivered to the current attempt. Receiving a last page does not prove it received earlier pages. |
| P1-D21 | P1-F02 | Use a self-contained, host-generated, integrity-protected source cursor carrying version, review/snapshot, file/hash, original selection, next byte position and symbol identity when applicable. Do not depend on a per-page database row or the producing worker's pagination map. |
| P1-D22 | P1-F02 / P1-F04 | A valid cursor may be used by another independently authorized attempt in the same review. Bind navigation to review/source, not the original worker; recheck current authority and do not transfer read credit. Checkpoint integration must be explicitly implemented. |
| P1-D23 | P1-F02 / P1-F08 / P1-F09 | Cursor replay starts at the same source position and does not advance shared state. A tighter current allowance may shrink a page; derive the next cursor from actual returned bytes and preserve normal accounting. |
| P1-D24 | P1-F02 | Reuse a suitable existing host cursor utility or build a narrow codec/validator. Legitimate restart/cross-worker use must not rely on an ephemeral worker-only secret. Subsequent authentication and storage decisions are recorded in P1-D25–P1-D28; remaining details stay open. |
| P1-D25 | P1-F02 | Use HMAC-SHA-256 and standard-library support to authenticate complete cursor metadata; verify tags with `hmac.compare_digest`. The host keeps the secret; the model receives metadata plus its tag. Cursor authenticity is not source access or evidence validity. |
| P1-D26 | P1-F02 | Keep one persistent cursor-authentication secret per project in a dedicated owner-protected file within SSR-managed private project data, outside target/snapshot content. A serialized host initialization path creates it; workers load it and restarts reuse it. Do not expose it in ordinary state, model configuration, tool results, transcripts, logs or exports. |
| P1-D27 | P1-F02 / P1-F09 | Sharing that project secret does not share reading positions. Workers may hold independent cursors on different files or on the same function; one worker can retain several cursors. Each read returns a new continuation and preserves attempt-specific authorization, limits and delivered-source accounting. |
| P1-D28 | P1-F02 / P1-F07 | Missing/unavailable secret or unverifiable cursor produces an explicit safe continuation failure. Do not trust decoded fields, regenerate/replace the secret silently or rebind an old cursor. After explicit host repair, fresh authorized source reads may issue new cursors. Exact repair/rotation/expiry policy remains open. |
| P1-D29 | P1-F02 | Extend `symbol_list` for exact local-name and qualified-name lookup over the existing inventory, optionally narrowed by file ID/relative path, containing symbol and kind. Keep file listing and direct `symbol_get(symbol_id)`; do not require name lookup for known IDs or automatically return source/create tasks. |
| P1-D30 | P1-F02 | Return distinguishable existing declaration identities and metadata, explicit alternatives, query completeness and relevant inventory limitations. A one-item page with more results is not a unique match. No unsuccessful exact query may silently broaden its match or drop filters. |
| P1-D31 | P1-F02 | Name lookup does not resolve a callsite or establish a security path, even with one complete match. Do not create or upgrade relationship records from name-match uniqueness. |
| P1-D32 | P1-F02 / P1-F01 | Query the existing inventory in the execution-bound snapshot, apply research authorization before bounded deterministic pagination, and avoid full per-worker inventory loading or a second symbol store/model resolver. Exact wire, normalization, ordering and query-pagination details remain open. |
| P1-D33 | P1-F02 | Discover available analysis using existing symbol/file IDs and existing subject/result associations. Return a bounded compact result index with recorded summaries, producer/source identities and limitations; no new summarization model call or automatic source/document dump. |
| P1-D34 | P1-F02 | Retrieve a selected document/result by exact identity. Do not substitute a newly published result or silently merge analyses with different questions/assumptions. Current authorization and owning visibility rules still apply. |
| P1-D35 | P1-F02 | Report result availability separately from relevant work status, including unscheduled, queued, running, failed, pending acceptance, and usable prior analysis with supplementary work. Task completion alone is not result acceptance. |
| P1-D36 | P1-F02 / Phase 4 | Reuse owning accepted-result readers and visibility/provenance gates; source research access does not expose private child content. Summary consumption grants no source-read credit. Phase 4 still decides artifact publication and sharing. |
| P1-D37 | P1-F02 / Phase 3 | Analysis discovery/retrieval must not automatically wait, register leads, create tasks, or form blocking contextual dependencies. The earlier blanket no-subscription wording is amended by P1-D39–P1-D42 to allow lightweight subject-specific freshness interests. |
| P1-D38 | P1-F02 | The consistency of paging dynamically changing analysis lists must be explicit; source-cursor approval does not select a result-list pagination algorithm. Exact schema, ordering and consistency implementation remain open. |
| P1-D39 | P1-F02 | An authorized analysis lookup automatically registers interest in its subject/query for the ongoing task or inquiry, without a separate subscribe call. The interest does not belong to a reusable worker slot or broadcast every project update. |
| P1-D40 | P1-F02 / Phase 4 | Advertise relevant newly consumable analysis at the next ordinary tool-response/model-turn boundary, even after another tool call. Use current visibility and exact subject associations; do not expose private results, interrupt in-flight responses, or create a notice-only model call/task. |
| P1-D41 | P1-F02 | The agent may retrieve an advertised result by exact ID, refresh the listing, defer reading, or ignore the notice. Do not auto-load bodies, substitute a selected result, or reset the current listing. Notice receipt grants no result-consumption or source-read credit. |
| P1-D42 | P1-F02 / P1-F04 / P1-F08 | Keep notices bounded/coalesced and avoid repeating unchanged advertised updates each turn. Distinguish advertised from retrieved information and preserve work isolation. Durable interest ownership is refined by P1-D43–P1-D47. Exact schema/markers, delivery/replay, limits and pagination mechanics remain open; optional refresh never bypasses stale-input checks. |
| P1-D43 | P1-F02 / P1-F04 | Persist a small host-owned source-free interest per ongoing task/inquiry as part of completing a successful authorized analysis lookup. Do not rely solely on worker memory or the next model checkpoint; a replacement attempt continuing the same work restores it. |
| P1-D44 | P1-F02 | Reuse one equivalent interest keyed logically by review, ongoing work, existing subject and normalized query filters. Use an existing durable task identity where suitable; do not invent an inquiry subsystem or merge interests by worker slot/name similarity. Exact normalization and storage fields remain open. |
| P1-D45 | P1-F02 / P1-F04 / Phase 3 | Waiting and retryable attempt interruption preserve interest for normal same-work resumption. Stop advertising on logical-work completion/cancellation, not merely one attempt ending. Unrelated work inherits nothing; restored interests still require current authority/visibility and transfer no read credit. |
| P1-D46 | P1-F02 / P1-F07 / P1-F08 | Lookup contents and initial observed availability must agree: a racing relevant publication is represented by the lookup or remains eligible for notice. Distinguish observed, advertised, retrieved and source-read information; fetching a later result does not mark earlier results read. Exact markers, registration failure and delivery/replay protocols remain open. |
| P1-D47 | P1-F02 | Prefer a compatible existing durable-state extension, otherwise a small source-free persistence structure under existing owners. Do not copy source/results/conversations/publication history per interest, create a messaging service or notification workers, or hold transactions across model turns. No table/migration/retention scheme is selected by this approval. |

## P1-F01 implementation choices still open

| Question | Kind | Where it is tracked |
|---|---|---|
| Actual owners and signatures after the modular refactor | Code verification | P1-F01 implementation steps and open decisions |
| Mapping all existing role/task identifiers, including legacy/link roles, to the named analytical responsibilities | Code verification; ask about any unmapped behavior | P1-F01 open decisions |
| Review/attempt contract compatibility and how new permissions are enabled without reinterpreting prior execution receipts | Design decision | P1-F01 and Phase 7 |
| Cross-file evidence use in terminal review results versus canonical coverage ownership | Cross-feature dependency | P1-F03 and Phase 4 |

Saving this document does not select defaults for these questions. The new-lead
registration decision is distinct from general mid-review answer publication,
which remains open in O-005/O-007.

## P1-F02 checkpoint

The [feature document](01-operating-model-autonomy-tools/features/P1-F02-indexed-navigation-and-retrieval.md)
is v0.8. It retains all source-read, authenticated-cursor, indexed-lookup,
exact-analysis-retrieval and automatic-notice agreements. P1-D43–P1-D47 now add
durable work-scoped interests, successful-lookup registration, equivalent-query
reuse, same-work restoration and logical-work lifecycle handling. No implicit
review task, blocking dependency or auto-resumption follows from a lookup/notice.

The observed listing and its initial availability position must not lose a racing
publication. This is an approved invariant, not an approved publication sequence,
transaction protocol, or dynamic-list paging algorithm. Interest state is durable;
its exact schema, filters/owner mapping, marker, delivery acknowledgment and
physical retention remain open. Publication-bounded/keyset listing was proposed
but not separately selected. Final wire contracts, cursor provisioning details,
remaining navigation interfaces and refactored integration also remain open.
The detailed direct-relationship proposal is not an approved requirement.

R44-R48, steps I1-I6 and scenarios T62-T69 record this approval. They are written
guidance and specified tests, not implemented behavior or executed application
tests. P1-F02 remains partial and not ready for implementation. Earlier approvals
are preserved; publication of this amendment does not change that status.

## Explicitly unresolved — do not promote to requirements

| ID | Open choice | Owning phase |
|---|---|---|
| O-001 | Partially resolved by P1-D01–P1-D47 above: access, synthesis, return to research and tool directions are agreed. Exact feature contracts and role-to-code mapping remain open. | 1 |
| O-002 | Whether any dedicated orientation analyst is needed. The earlier suggestion was not approved. | 2, informed by 1 |
| O-003 | Detailed operation catalogue, analyzer selection, recognition rules, binding support, and discovery policy. | 2 |
| O-004 | Contextual request identity, joining/routing, updates to running reviewers, shared answers, and cycle handling. | 3 |
| O-005 | When answers become shareable: completed sealed unit, completed targeted review, mid-review accepted answer, or another explicit contract. Sealed-unit-only delivery was a suggestion, not an accepted restriction. | 3–4 |
| O-006 | How focused/contextual work can satisfy canonical coverage, what adoption/revalidation is needed, and how canonical publication changes. Blanket no-credit/mandatory-duplication rules from the older proposal are not automatically retained. | 4 |
| O-007 | General incremental evidence/answer acceptance, revisions, conflicts, and corrections remain open. The independently accepted new-lead registration behavior is agreed in P1-D06; it must not wait for its proposer’s terminal result. | 4 |
| O-008 | Exact candidate producer/handoff rules, current-finding validity, and reassessment implementation. | 5 |
| O-009 | Scheduling allocations, numeric budgets, time quanta, queue order, request fan-out limits, and continuation accounting. Old 50/50 or other proposal defaults are not approved here. | 6 |
| O-010 | Exact module layout after refactoring, schemas, migrations, versioning, and paired SDK changes. | 7 |
| O-011 | Implementation order, release increments/modes, full evaluation protocol, and enabling defaults. Older M0–M3 milestones are not automatically adopted. | 8 |

## Rules for maintaining this register

Use a named decision with scope and rationale when recording approval. Link it
to its owning phase and relevant requirements once those documents exist. Do not
mark an assistant recommendation accepted without agreement. When reopening an
accepted decision, preserve its history, explain the conflict, and identify the
requirements and implementation slices affected.

Statements about current source must be supported by inspection of the actual
baseline used. Earlier inspected commit references are navigation aids, not
proof of the current remote branch, local worktree, installed package, or live
process state. Reconcile the future implementation plan against the delivered
refactor instead of assuming the old file layout is still current.

See [PHASES.md](PHASES.md) for the approved phase sequence and current checkpoint.
