# AGENTS.md

## Purpose

This starter uses Codex-first project governance for long-running, multi-stage development.

The goal is to keep AI work resumable, compressible, and auditable across multiple conversations.

## Project Bootstrap Notes

Customize these items before large-scale implementation:

- project goal and scope in `docs/ai/plan.md`
- current execution truth in `docs/ai/working-context.md`
- repo-specific required docs in `.codex/harness.toml`
- repo-specific workflow defaults or constraints in this file

Do not keep old project truth when copying this starter to a new repository.

The default shared recovery surface should stay slim:

`docs/ai/index.md -> docs/ai/working-context.md -> latest stage status -> configured active handoff budget`

## AGENTS Rewrite Checklist

When this starter is copied into a new repository, rewrite `AGENTS.md` before large-scale implementation.

At minimum, replace or add these repo-specific facts:

- what the project is trying to build
- which directories are the real code entrypoints
- which documents are the real business or architecture truth surfaces
- which commands are the real verification commands
- which boundaries should not be edited casually
- what must be true before a task is considered complete

Do not turn `AGENTS.md` into a current-status board.

Current state, active backlog, and transient progress belong in:

- `docs/ai/working-context.md`
- active `handoff`
- `status`
- `docs/requirements/traceability-matrix.md`

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

Use this rule:

`implementation change -> document impact check -> update affected docs -> update docs/ai/index.md`

Update trigger summary:

- `handoff`: completed subtask, paused/resumable task, or implementation detail the next agent must inherit
- `status`: stage end, accumulated handoffs needing compression, or material risk/blocker change
- `changelog`: integration-ready stage, externally visible behavior change, or release-facing note
- `adr`: long-lived decision about architecture, API, storage, deployment, major constraints, testing, review, or delivery

After changing `plan`, `handoff`, `status`, `changelog`, or `adr`, check `docs/ai/index.md`.

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

This starter uses three harness layers:

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

Platform note:

- This starter includes POSIX and PowerShell hook runners; rerun bootstrap when moving host shells.

## Session Promotion

Runtime session files under `.codex/runtime/sessions/` are local recovery material and should follow the session template.

Promote a session into a `handoff` when any of the following are true:

- a subtask has completed
- a task is being paused and should be resumed later
- implementation changed in a way the next agent must understand
- the session established durable valid/invalid approaches or risks that should be shared by default
- the session created a change that should affect `status`, `adr`, `plan`, or requirements tracking

Do not promote a session when it only contains local scratch work, personal prompt experimentation, or exploratory notes without repo-level reuse value.

The main agent is responsible for deciding whether promotion is required and for publishing the canonical `handoff`.

## Requirement Traceability

When a task is already mapped to normalized requirements or workstreams, include those identifiers in runtime and governance artifacts.

Use these rules:

1. `handoff`, `status`, runtime session files, and observation-derived handoff drafts should carry `Requirement IDs` and `Workstream IDs` when the mapping is known.
2. If the mapping is not known yet, write `未绑定` instead of inventing IDs.
3. The canonical mapping still lives in `docs/requirements/traceability-matrix.md` and related workstream docs; AI-side metadata references that mapping and must not drift from it.
4. When a task is newly bound to a requirement or workstream, update both the AI-side artifact and the requirements-side traceability docs in the same change whenever feasible.

## Observation Reduction

Runtime observation files under `.codex/runtime/observations/*.jsonl` are local reduction inputs, not shared truth.

When changing reducer or runtime observation behavior, use `$harness-maintenance` and `references/runtime-observation-reduction.md`.

Default reduction order remains: `observations -> handoff draft -> main agent review -> status/adr if warranted`.

## Compression Rule

Project docs follow this lifecycle:

`handoff -> status -> changelog / adr -> archive old handoffs`

When a completed handoff has already been absorbed by `status` or `adr` and no longer has default resume value, move it into `docs/ai/handoffs/archive/`.

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

## Governance Surface Budget

Do not let the default shared recovery surface grow without bound.

`docs/ai/index.md` is a stable router; `docs/ai/working-context.md` is incremental truth. If active handoffs reach the configured budget, run `scripts/check_archive_candidates.py`, compress absorbed detail into `status` or ADR, then archive old handoffs. The check is warning-only; the main agent still decides what moves.

## Verification Layer

Preferred POSIX/macOS commands:

- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --staged`
- `.codex/hooks/run_with_repo_python.sh scripts/check_archive_candidates.py` when active handoffs reach budget or before stage compression
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py` when default context feels heavy

Preferred Windows PowerShell equivalents use `.codex/hooks/run_with_repo_python.ps1` with the same script paths.

This repository also includes a repo-local Codex `Stop` hook that runs the same governance check automatically when hooks are enabled.

Git hook setup:

`git config core.hooksPath .githooks`

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

## Project Skill Lifecycle

Architecture, style, and dependency skills are project-specific execution guidance, not default governance truth.

Use `docs/ai/templates/project-skill-lifecycle.md` when a task creates or changes a project architecture/style/dependency skill.

Keep these skills out of the default short context chain. If a skill changes long-lived architecture, style, dependency, testing, deployment, or delivery strategy, promote the durable decision to `status` or `adr`.

For non-trivial feature modules, cross-module/API/storage/architecture/testing-strategy changes, or explicit plan-first requests, use `.agents/skills/progressive-feature-development/`; when PRD, requirement, workstream, ADR, or repeated implementation material may contain stable project-skill candidates, use `.agents/skills/prd-to-project-skills/`. Skip both for simple tasks, and route outputs back into requirements, handoff, status, ADR, changelog, checks, or candidate skills instead of hidden canonical truth.

For harness-internal changes to runtime, hooks, reducers, GitHub guardrails, or code-shape checks, use `.agents/skills/harness-maintenance/`. Keep those mechanics out of the default short context unless the task touches that surface.

## Repo-local Skill Note

This starter carries an optional repo-local skill at `.agents/skills/repo-governed-coding/`.

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

A materially changing task is complete only after implementation, needed docs, `docs/ai/index.md`, governance check, and staged code-shape check are current.
