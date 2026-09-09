# SSR collaborative review — decision register

Version: 1.0  
Recorded: 2026-09-08  
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

The pool of approximately 100 workers is the user's example of intended scale.
It is not a fixed default, a minimum, an entitlement to provider capacity, or a
measured result.

## Explicitly unresolved — do not promote to requirements

| ID | Open choice | Owning phase |
|---|---|---|
| O-001 | Exact agent research permissions, role-specific tool surfaces, host grants, and repair/return-to-analysis behavior. | 1 |
| O-002 | Whether any dedicated orientation analyst is needed. The earlier suggestion was not approved. | 2, informed by 1 |
| O-003 | Detailed operation catalogue, analyzer selection, recognition rules, binding support, and discovery policy. | 2 |
| O-004 | Contextual request identity, joining/routing, updates to running reviewers, shared answers, and cycle handling. | 3 |
| O-005 | When answers become shareable: completed sealed unit, completed targeted review, mid-review accepted answer, or another explicit contract. Sealed-unit-only delivery was a suggestion, not an accepted restriction. | 3–4 |
| O-006 | How focused/contextual work can satisfy canonical coverage, what adoption/revalidation is needed, and how canonical publication changes. Blanket no-credit/mandatory-duplication rules from the older proposal are not automatically retained. | 4 |
| O-007 | Incremental evidence/result publication, accepted-answer provenance, revisions, conflicts, and later corrections. | 4 |
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
