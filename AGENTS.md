# AGENTS.md

## Purpose

This repository uses Codex-first project governance for long-running, multi-stage development.

The goal is to keep AI work resumable, compressible, and auditable across multiple conversations.

## Document System

Project-progress and AI-handoff documents live under `docs/ai/`.

Requirement-source and requirement-normalization documents live under `docs/requirements/`.

Primary entrypoint:

- `docs/ai/index.md`
- `docs/requirements/index.md`

Core documents:

- `docs/ai/plan.md`
- `docs/ai/working-context.md`
- `docs/ai/handoffs/active/*.md`
- `docs/ai/status/*.md`
- `docs/ai/changelog/*.md`
- `docs/ai/adr/*.md`
- `docs/ai/templates/*.md`
- `docs/requirements/source/*.md`
- `docs/requirements/normalized/*.md`
- `docs/requirements/workstreams/*.md`
- `docs/requirements/traceability-matrix.md`

Local runtime memory:

- `.codex/runtime/sessions/*.md`
- `.codex/runtime/observations/*.jsonl`

These runtime files are local recovery artifacts. They are not canonical project memory and do not replace `docs/ai/*` or `docs/requirements/*`.

## Required Workflow

When work causes meaningful project progress, Codex must check whether documentation also needs to be updated.

Use this rule: `implementation change -> document impact check -> update affected docs -> update docs/ai/index.md`.

Detailed document-impact and closeout checklists live in `$repo-governed-coding` `references/governance-checklist.md`; keep this file as the always-on trigger layer.

## Reading Order

At the start of a new Codex task, prefer this order:

1. `docs/ai/index.md`
2. `docs/ai/working-context.md`
3. `docs/requirements/index.md` when the task is requirement-driven
4. `docs/ai/plan.md`
5. latest relevant `docs/ai/status/*.md`
6. active relevant `docs/ai/handoffs/active/*.md`
7. relevant `docs/ai/adr/*.md`
8. archive only if necessary

Runtime session files under `.codex/runtime/sessions/` are optional recovery inputs and should only be read when local session detail is needed.

## Task Discovery Protocol

Codex should classify each task before expanding context. The user does not need to label every task manually.

Use these default profiles:

1. Simple task: small explanation, local edit, single validation command, or narrow bugfix. Read `index -> working-context -> current status`, then open only directly relevant files.
2. Medium task: one module, one harness script, starter/root sync, or a small test set. Read the simple profile plus relevant active handoff, ADR, or implementation files.
3. Complex task: cross-module behavior, governance rule changes, traceability changes, architecture/API/storage/deployment decisions, or changes that affect future agent workflow. Read the medium profile plus relevant `requirements`, `traceability-matrix`, workstream docs, and ADRs.
4. 0-1 stage task: project initialization, first requirement import, new workstream, first vertical slice, or stage transition. Read `requirements index -> traceability matrix -> plan -> current status -> relevant workstream/templates`, then load handoff/ADR/archive only as needed.
5. Recovery or dispute task: resume, regression, conflicting state, or historical rationale. Read relevant active handoff first; enter archive only when current truth surfaces do not answer the question.

Before substantial work, state the selected profile briefly. Users do not need to add a task-type suffix to every prompt. Override phrases such as `按简单任务处理`, `按复杂任务处理`, `这是 0-1 阶段任务`, `不要读 archive`, or `需要深挖历史` are optional controls for correcting or narrowing the automatic classification.

## Harness Layers

This repository uses three harness layers:

- Runtime Harness: local session and observation state under `.codex/runtime/`
- Governance Harness: shared project memory under `docs/ai/*` and `docs/requirements/*`
- Verification Harness: lifecycle enforcement under `.codex/hooks.json`, `.githooks/*`, and `scripts/check_*`

Use these rules:

1. Runtime files are local-only recovery artifacts, not the canonical project truth.
2. Hooks may write `.codex/runtime/*`, but must not auto-edit `working-context.md`, `index.md`, `handoff`, `status`, `changelog`, or `adr`.
3. Shared governance documents are authored at explicit semantic checkpoints such as subtask completion, pause/resume boundaries, stage compression, and long-lived decisions.
4. The main agent owns canonical writes to `docs/ai/*` and `docs/requirements/*`.
5. Subagents may return structured results or handoff drafts, but the main agent publishes the canonical shared documents.
6. If a runtime finding remains relevant beyond the current local session, promote it into `handoff`, `status`, `adr`, `plan`, or requirements documents.

## Python Runtime Rule

Harness Python details are on-demand. When changing bootstrap, hook runners, hook sync, `.githooks`, `.codex/hooks/*`, or Python resolution, use `$harness-maintenance` and `references/python-runtime-and-hooks.md`.

Always preserve the repo-local `.codex/.venv` preference, verify runnable Python candidates, and never commit `.codex/.venv`.

## Session Promotion

Runtime session files are local recovery material, not shared truth.

Promote stable repo-level conclusions into `handoff`, `status`, `adr`, `plan`, or requirements documents. Use `$harness-maintenance` `references/runtime-governance-compression.md` for detailed promotion and compression rules.

## Requirement Traceability

Requirement mappings must not drift. Carry known `Requirement IDs` and `Workstream IDs`; write `未绑定` instead of inventing IDs when mapping is unknown.

For PRD import, `REQDOC / REQ / WS`, traceability-matrix, or technical-assumption changes, use `.agents/skills/requirements-traceability-maintenance/` and keep canonical mapping in `docs/requirements/*`.

## Observation Reduction

Runtime observation files under `.codex/runtime/observations/*.jsonl` are local reduction inputs, not shared truth.

When changing reducer or runtime observation behavior, use `$harness-maintenance` and `references/runtime-observation-reduction.md`.

Default reduction order remains: `observations -> handoff draft -> main agent review -> status/adr if warranted`.

## Compression Rule

Project docs follow this lifecycle: `handoff -> status -> changelog / adr -> archive old handoffs`.

When active surfaces reach budget or a stage is compressed, use `$harness-maintenance` `references/runtime-governance-compression.md`. The main agent still decides what becomes canonical or archived.

## Projection Surface Boundary

Not every document should carry current-state truth.

Use these rules:

1. `docs/ai/working-context.md`, active `handoff`, `status`, `adr`, `docs/requirements/normalized/*.md`, and `docs/requirements/traceability-matrix.md` are the primary truth surfaces.
2. `docs/ai/plan.md` is a projection document. It should keep goals, scope, stage breakdown, and acceptance framing, but should not repeat fast-changing completion state, latest validation results, or transient evidence.
3. `docs/requirements/workstreams/*.md` are projection documents. They should keep workflow goal, covered requirements, stage suggestions, and acceptance model, but should not become a second copy of the latest execution status or smoke evidence.
4. When current-state text appears in a projection document, it must either be removed or be explicitly synchronized with its primary truth source in the same change.
5. Current completion state, latest validation result, and canonical acceptance evidence should default to `working-context`, `handoff`, `status`, and `traceability-matrix.md`, not to `plan` or `workstream` docs.

## Code Shape Budget

Code shape is a harness-level constraint for implementation and harness scripts. The scope and thresholds live in `.codex/code_shape.toml` and are enforced by `scripts/check_code_shape.py`.

When changing the budget or the checker, use `$harness-maintenance` and `references/code-shape-budget.md`. Keep code-shape checks separate from AI governance checks.

## Verification Layer

Verification is required, but command selection scales by changed surface and project maturity.

Material governance changes must run the governance check. Staged code or harness changes must run code-shape. Use `$harness-maintenance` `references/verification-commands.md` for the command matrix and warning interpretation.

## GitHub Gatekeeping

GitHub repository settings are part of the verification harness, but not all of them live in the repo.

Keep workflow permissions minimal and verify remote branch protection / rulesets before claiming required checks are enforced.

When changing workflows, CODEOWNERS, Dependabot, dependency review, required checks, or remote guardrail scripts, use `$harness-maintenance` and `references/github-guardrails.md`.

When team development, multiple AIs, open-PR changed-file overlap, PR templates, CODEOWNERS ownership, or merge queue readiness is part of the task, use `.agents/skills/team-pr-conflict-control/` and keep durable outcomes in PR metadata, checks, status, ADR, or requirements docs as appropriate.

## Scope Discipline

Skills are allowed and useful, but they do not replace repository rules.

Use this division:

- `AGENTS.md`: always-on project rules
- `.codex/runtime/*`: local runtime harness memory
- `docs/ai/*`: persistent project memory
- `docs/requirements/*`: requirement source, normalization, and workstream tracking
- skills: task-specific execution guidance
- scripts/checks: enforcement and drift detection
- `.codex/hooks.json`: Codex lifecycle enforcement

## Skill Coordination

Skills do not coordinate themselves. Codex coordinates them using repository rules and document layers.

Use these rules:

1. Existing skills are not "always running". They are loaded when relevant to the current task.
2. New skills may be introduced mid-project, but they must write their results into the existing document system.
3. Repository rules and `docs/ai/index.md` remain the stable control plane even when skills change.

When adding new skills in a later stage:

- keep `AGENTS.md` as the persistent source of workflow rules
- use `plan`, `handoff`, `status`, `changelog`, and `adr` as the shared memory surface
- let task skills produce task outputs, not governance decisions
- update `adr` if a new skill changes a long-lived workflow or architecture decision

If a new skill supersedes an old approach:

- record the change in `status` or `adr`
- archive old task-specific notes if they are no longer active
- do not keep two conflicting active workflows in parallel

## Project Skill Lifecycle

Architecture, style, and dependency skills are project-specific execution guidance, not default governance truth.

Use `docs/ai/templates/project-skill-lifecycle.md` when a task creates or changes a project architecture/style/dependency skill.

Keep these skills out of the default short context chain. If a skill changes long-lived architecture, style, dependency, testing, deployment, or delivery strategy, promote the durable decision to `status` or `adr`.

For non-trivial feature modules, cross-module/API/storage/architecture/testing-strategy changes, or explicit plan-first requests, use `.agents/skills/progressive-feature-development/`; when PRD, requirement, workstream, ADR, or repeated implementation material may contain stable project-skill candidates, use `.agents/skills/prd-to-project-skills/`; when changing PRD imports, `REQDOC / REQ / WS`, traceability matrix, or technical assumptions, use `.agents/skills/requirements-traceability-maintenance/`. Skip workflow skills for simple tasks, and route outputs back into requirements, handoff, status, ADR, changelog, checks, or candidate skills instead of hidden canonical truth.

For harness-internal changes to runtime, hooks, reducers, compression, verification commands, GitHub guardrails, or code-shape checks, use `.agents/skills/harness-maintenance/`. For multi-person or multi-AI PR collision control, use `.agents/skills/team-pr-conflict-control/`. Keep those mechanics out of the default short context unless the task touches that surface.

## Repo-local Skill Note

This repository also carries an optional repo-local skill at `.agents/skills/repo-governed-coding/`.

Use these rules:

1. Use it only when explicitly invoked or when a task explicitly asks for Karpathy-style implementation guardrails inside this repository.
2. Treat it as method-level guidance for governed coding work, not as a replacement for `AGENTS.md`, `docs/ai/*`, `docs/requirements/*`, or verification rules.
3. If the skill and repository rules ever disagree, follow the repository rules and update stage docs if the skill pattern needs to change.

## Skill Escalation Policy

When a new skill is introduced, decide where it should be recorded based on scope and persistence.

Use this escalation ladder:

- task prompt only: one-off, narrow, or not needed by future tasks
- stage `status`: affects current-stage execution or several tasks in the same stage
- `AGENTS.md`: stable recurring default future tasks should assume
- `ADR`: long-lived workflow, architecture, testing, deployment, review, or delivery decision

Do not keep a skill in both temporary task use and default repository rule without explicitly deciding which one is active.

## Completion Condition

A material task is complete only when implementation, affected docs, `docs/ai/index.md`, traceability, and applicable verification are current.
