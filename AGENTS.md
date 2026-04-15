# AGENTS.md

## Purpose

This repository uses Codex-first project governance for long-running, multi-stage development.

The goal is to keep AI work resumable, compressible, and auditable across multiple conversations.

## Document System

All project-progress and AI-handoff documents live under `docs/ai/`.

Primary entrypoint:

- `docs/ai/index.md`

Core documents:

- `docs/ai/plan.md`
- `docs/ai/handoffs/active/*.md`
- `docs/ai/status/*.md`
- `docs/ai/changelog/*.md`
- `docs/ai/adr/*.md`

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
2. `docs/ai/plan.md`
3. latest relevant `docs/ai/status/*.md`
4. active relevant `docs/ai/handoffs/active/*.md`
5. relevant `docs/ai/adr/*.md`
6. archive only if necessary

## Compression Rule

Project docs follow this lifecycle:

`layer -> compress -> archive -> keep active entrypoints current`

More explicitly:

`handoff -> status -> changelog / adr -> archive old handoffs`

## Verification Layer

Verification is required, but it scales by project maturity.

Preferred command:

`python3 scripts/check_ai_docs.py`

This repository also includes a repo-local Codex `Stop` hook that runs the same governance check automatically when hooks are enabled.

### Phase 0: project start

Use manual verification only:

- after meaningful changes, check whether docs changed
- after doc creation, check whether `docs/ai/index.md` points to the right files

Codex should still run `python3 scripts/check_ai_docs.py` whenever the repository has enough structure for the script to be meaningful.

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
- skills: task-specific execution guidance
- scripts/checks: enforcement and drift detection
- `.codex/hooks.json`: Codex lifecycle enforcement

## Completion Condition

A task that materially changed the project is not fully complete until:

1. implementation is updated
2. affected project docs are updated if needed
3. `docs/ai/index.md` is still accurate
4. `python3 scripts/check_ai_docs.py` passes when applicable
