# Phase 1 — operating model, agent autonomy, and tools

Status: IN DISCUSSION  
Specification: NOT YET DRAFTED  
Implementation plan: NOT YET DRAFTED

This is a discussion brief, not a replacement specification or an approved tool
schema. It keeps Phase 1 aligned with the user's already agreed direction.

## Already established

The system coordinates collaborating analysts alongside systematic coverage.
Existing continuous admission and useful source, evidence, tool, execution, and
publication infrastructure should be reused. The new design must not equate an
agent's assigned responsibility with a predetermined investigative route.

The tool-direction discussion identified broader discovery, contextual delegation,
incremental publication, and continuation as capabilities to develop. Their
exact authorization, input/output, and acceptance contracts remain to be agreed.

## Decisions this phase must settle

### Responsibility and authority

Define the distinction between an ongoing security question, canonical coverage
responsibility, and a worker attempt. Establish which analytical choices belong
to the agent and which admissions, permissions, validations, or state changes
belong to the host. Do not introduce extra managerial model roles by default.

### Research freedom

Specify how agents locate and inspect relevant context using the permitted
immutable project source. Decide how restrictions and additional authorization
are represented without silently making every cross-file detour a new task.
Preserve ownership of submitted results and coverage separately from navigation.

### Tool capability map

For each existing or proposed capability, record:

| Field | Meaning |
|---|---|
| Purpose | The concrete analyst question or action supported. |
| Baseline | Existing behavior and implementation owner, verified before relying on it. |
| Disposition | Retain, extend, replace, or add—with a reason. |
| Consumer | Which analytical responsibilities need access. |
| Authority | What the host validates and what the tool cannot authorize. |
| Result meaning | Navigation, evidence reference, contextual result, or accepted state change. |
| Failure behavior | Actionable denial, missing data, bounded result, or operational error. |
| Verification | Observable successful and negative cases for the proposed behavior. |

Cover source discovery/read/search; symbol and relationship navigation; retrieval
of accepted analysis; requests for further review; incremental result proposals;
continuation; and role-specific final submission. Do not create one tool per
vulnerability name merely to expand the catalogue.

### Implementation implications

After agreement, map these capabilities to existing/refactored owners, explicit
interfaces, required tests, and compatibility boundaries. Keep structural refactor
work separate from changed runtime behavior. Exact shared wire/storage contracts
will be reconciled in Phase 7; unresolved dependencies remain visible in the
Phase 1 plan rather than being filled with invented defaults.

## Decisions that belong elsewhere

Do not block this phase on whether an answer may publish mid-review: that is a
Phase 3–4 acceptance/publication decision. Do not settle coverage-credit rules,
complete operation-recognition catalogues, finding reassessment, scheduler ratios,
or database layouts here. Record the required capability and link the open choice
to its owning phase.

## Exit condition

The user has reviewed the ownership/autonomy/tool decisions and the resulting
`SPECIFICATION.md` and `IMPLEMENTATION_PLAN.md`. No future-phase restriction is
presented as an approved Phase 1 requirement. Open dependencies are explicit.

Return to the [roadmap](../PHASES.md) or [decision register](../DECISION_REGISTER.md).
