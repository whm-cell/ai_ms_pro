---
name: progressive-feature-development
description: Plan non-trivial feature work through progressive discovery, skill selection, technical-plan review, implementation guardrails, verification, and doc promotion without taxing simple tasks.
---

# Progressive Feature Development

## Current Status

Candidate

## Scope

Use this skill for non-trivial feature work: new feature modules, cross-module behavior changes, API / storage / architecture changes, testing strategy changes, or tasks where the user explicitly asks for a technical plan before implementation.

Do not use this skill for simple explanations, narrow one-file fixes, formatting, local typo edits, or single validation commands.

## Default Workflow

1. Classify the task.
- Confirm whether this is simple, non-trivial feature work, architecture-impacting work, or recovery / dispute work.
- If the task is simple, state that this skill is not needed and continue through the repository default short path.

2. Ground in minimum repo truth.
- Read `AGENTS.md`, `docs/ai/index.md`, `docs/ai/working-context.md`, and the current status source when those files exist.
- Read `docs/requirements/index.md` and `docs/requirements/traceability-matrix.md` when requirements or `REQ/WS` bindings are involved.
- Read only directly relevant source, tests, ADRs, handoffs, and workstream docs.

3. Select the minimum skill set.
- Use existing skills only when they directly reduce implementation risk.
- Prefer the repo's governed coding skill for implementation discipline when present.
- Do not keep multiple overlapping workflow skills active without choosing which one owns the task method.

4. Produce a technical plan before editing.
- Include task classification, assumptions, `REQ/WS` binding, selected skills, affected modules, interfaces / data flow, implementation boundary, tests / smoke checks, and doc impact.
- Include `NOT Building` to keep scope controlled.
- Keep the plan as a task artifact unless it needs handoff, status, ADR, or requirements promotion.

5. Run the plan gate.
- Check the plan against `references/technical-plan-checklist.md`.
- If the plan fails the gate, revise or ask the user before implementation.
- If the user already approved a concrete plan, record that and continue.

6. Implement with guardrails.
- Apply the smallest coherent change that satisfies the plan.
- Keep changed lines traceable to the plan and request.
- If implementation must deviate from the plan, record what changed and why.

7. Verify and promote.
- Run task-specific tests / smoke checks plus applicable governance checks.
- Decide whether results stay local, become an active handoff, update status, update ADR, update changelog, or update requirements / traceability.
- Update `docs/ai/index.md` only when new or changed shared truth affects routing.

## Required Output

When active, return or record these fields:

- Task Classification
- Requirement IDs / Workstream IDs
- Minimum Context Read
- Selected Skills
- Technical Plan
- Plan Gate Result
- Implementation Boundary
- Verification Commands
- Document Promotion Decision

## Escape Hatch

Skip or shorten this skill when:

- the task is simple and the overhead would exceed the implementation risk
- the user explicitly asks for a narrow direct edit
- current repo truth already contains an approved technical plan
- urgent recovery requires first stabilizing a broken state

If skipping changes the project workflow beyond one task, record the reason in `handoff`, `status`, or ADR.

## Promotion Rule

Keep this skill as Candidate until it has been used successfully in at least two non-trivial feature tasks. Promote to a stable default only if evidence shows it reduces rework without slowing simple tasks.

## Deprecation Rule

Deprecate or revise this skill if it causes routine tasks to carry planning overhead, conflicts with repository rules, or is replaced by a stronger verified workflow.

## Reference

- Use [technical-plan-checklist.md](references/technical-plan-checklist.md) for the plan gate.
