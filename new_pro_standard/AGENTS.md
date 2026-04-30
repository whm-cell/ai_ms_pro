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

`docs/ai/index.md -> docs/ai/working-context.md -> latest stage status -> <=5 active handoff`

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

### Update triggers

Update or create a `handoff` when:

- a subtask is completed
- a task is paused but should be resumed later
- implementation changed in a way the next agent must understand

Update or create a `status` document when:

- a stage ends
- several handoffs have accumulated and need compression
- current risks or blockers materially changed

Update or create a `changelog` when:

- a stage is ready for integration
- externally visible behavior changed
- release-facing notes are needed

Update or create an `adr` when:

- a decision will remain relevant beyond the current stage
- architecture, API shape, storage strategy, deployment strategy, or major constraints changed

Always check `docs/ai/index.md` after adding or changing:

- `plan`
- `handoff`
- `status`
- `changelog`
- `adr`

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

Harness Python must prefer the repo-local virtual environment `.codex/.venv`.

Use these rules:

1. `scripts/bootstrap_harness.py` must support Windows and POSIX venv layouts.
2. Git hooks and Codex hooks must resolve Python through `.codex/hooks/` runners instead of hardcoding a system Python path.
3. Runners must verify that a Python candidate is actually runnable before using it.
4. If `.codex/.venv` exists but is not runnable, bootstrap may rebuild it in place without touching `.codex/runtime/*`.
5. On POSIX/macOS and Windows, fallback discovery must not stop at the first system Python when a later candidate provides Python 3.11+; prefer `.codex/.venv`, active envs, `CODEX_HARNESS_PYTHON`, then the best runnable Python before falling back to the launcher Python.
6. Do not commit `.codex/.venv`.

Platform note:

- This starter includes both POSIX and PowerShell hook runners.
- `scripts/bootstrap_harness.py` refreshes `.codex/hooks.json` for the current host shell during setup; if a repo later moves to a different host shell, rerun bootstrap or update only the hook entrypoint commands instead of rewriting the runtime scripts ad hoc.

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

Use these rules:

1. Reduce observations explicitly through the repo-local Python runner, for example `.codex/hooks/run_with_repo_python.sh scripts/reduce_runtime_observations.py` on POSIX/macOS or `powershell -NoProfile -ExecutionPolicy Bypass -File .codex/hooks/run_with_repo_python.ps1 scripts/reduce_runtime_observations.py` on Windows, when local observation material should be reviewed for promotion.
2. The default reduction order is `observations -> handoff draft -> main agent review -> status/adr if warranted`.
3. Reducer output is a candidate artifact. It does not replace the main agent's responsibility to decide whether canonical shared docs should change.
4. Only promote to `status` or `adr` when the reducer output has already been reviewed and the conclusion is stable beyond a single local observation batch.

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

Code shape is a harness-level constraint for implementation and harness scripts.

Use these rules:

1. The default scope is controlled by `.codex/code_shape.toml`.
2. Python file target is `<=300` lines; warning starts above `350`, and new files above `500` should be split before landing.
3. Function or method target is `<=60` lines; warning starts above `80`, and new definitions above `120` should be split.
4. Class target is `<=180` lines; warning starts above `250`, and new classes above `350` should be split.
5. Existing large files are legacy debt and may warn, but the rule is primarily intended to prevent new monoliths.
6. Keep shape checks separate from AI governance checks; do not keep expanding `scripts/check_ai_governance.py` with code-size rules.

## Governance Surface Budget

Do not let the default shared recovery surface grow without bound.

Use these rules:

1. `docs/ai/index.md` is a stable router, not a second stage report.
2. `docs/ai/working-context.md` should keep incremental truth, not a duplicate stage directory.
3. The default active handoff budget is `<=5`.
4. If active handoffs exceed that budget, compress absorbed detail into `status` or `adr`, then archive old handoffs.
5. Use `scripts/check_archive_candidates.py` through the repo-local Python runner when active handoffs reach the surface budget or before a stage compression pass.
6. The archive candidate check is warning-only: it lists candidates and reasons, but the main agent still decides whether to move files and update shared docs.
7. Small routing duplication is acceptable when it supports structure checks; large duplicated stage listings are not.

## Verification Layer

Preferred POSIX/macOS command:

`.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`

Preferred Windows PowerShell command:

`powershell -NoProfile -ExecutionPolicy Bypass -File .codex/hooks/run_with_repo_python.ps1 scripts/check_ai_governance.py`

Common POSIX/macOS supplement:

`.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --staged`

Common Windows PowerShell supplement:

`powershell -NoProfile -ExecutionPolicy Bypass -File .codex/hooks/run_with_repo_python.ps1 scripts/check_code_shape.py --staged`

Optional context-pressure check:

`.codex/hooks/run_with_repo_python.sh scripts/check_archive_candidates.py`

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

## Repo-local Skill Note

This starter carries an optional repo-local skill at `.codex/skills/repo-governed-coding/`.

Use these rules:

1. Use it only when explicitly invoked or when a task explicitly asks for Karpathy-style implementation guardrails inside this repository.
2. Treat it as method-level guidance for governed coding work, not as a replacement for `AGENTS.md`, `docs/ai/*`, `docs/requirements/*`, or verification rules.
3. If the skill and repository rules ever disagree, follow the repository rules and update stage docs if the skill pattern needs to change.

## Skill Escalation Policy

When a new skill is introduced, decide where it should be recorded based on scope and persistence.

### Task prompt only

Keep the skill only in the current task prompt when all of the following are true:

- it is one-off or narrowly scoped
- it does not change the repository's default workflow
- future tasks do not need to assume it by default

### Stage `status`

Record the skill usage in the current stage `status` when:

- it changes how the current stage is being executed
- several tasks in the same stage depend on it
- later work in the same stage would be confusing without noting the change

### `AGENTS.md`

Promote the skill usage pattern into `AGENTS.md` only when:

- it becomes a recurring default for this repository
- future Codex tasks should assume it without being reminded every time
- it is a stable workflow preference rather than a temporary tactic

### `ADR`

Record the skill-related decision in an `adr` when:

- it changes a long-lived workflow
- it changes architecture, testing, deployment, review, or delivery strategy in a lasting way
- the decision should remain true beyond the current stage

### Conflict rule

Do not keep a skill in both temporary task use and default repository rule without explicitly deciding which one is active.

## Completion Condition

A task that materially changed the project is not fully complete until:

1. implementation is updated
2. affected project docs are updated if needed
3. `docs/ai/index.md` is still accurate
4. `scripts/check_ai_governance.py` passes through the repo-local Python runner when applicable
5. `scripts/check_code_shape.py --staged` passes through the repo-local Python runner when implementation or harness code is staged
