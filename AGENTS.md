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
- `docs/requirements/source/*.md`
- `docs/requirements/normalized/*.md`
- `docs/requirements/workstreams/*.md`
- `docs/requirements/traceability-matrix.md`

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

## Compression Rule

Project docs follow this lifecycle:

`layer -> compress -> archive -> keep active entrypoints current`

More explicitly:

`handoff -> status -> changelog / adr -> archive old handoffs`

## Verification Layer

Verification is required, but it scales by project maturity.

Preferred command:

`python3 scripts/check_ai_governance.py`

This repository also includes a repo-local Codex `Stop` hook that runs the same governance check automatically when hooks are enabled.

### Phase 0: project start

Use manual verification only:

- after meaningful changes, check whether docs changed
- after doc creation, check whether `docs/ai/index.md` points to the right files

Codex should still run `python3 scripts/check_ai_governance.py` whenever the repository has enough structure for the script to be meaningful.

### Phase 1: early active development

Add a lightweight scripted verification step:

- warn when source files changed but `docs/ai/` did not
- warn when a new `status` or `changelog` exists but `index.md` was not updated

### Phase 2: multi-stage / multi-agent development

Add stronger verification:

- validate active handoff references
- validate archive moves
- validate latest-stage pointers

### Phase 3: release / CI maturity

Run verification in CI so documentation drift is caught before merge.

## Scope Discipline

Skills are allowed and useful, but they do not replace repository rules.

Use this division:

- `AGENTS.md`: always-on project rules
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
4. `python3 scripts/check_ai_governance.py` passes when applicable
