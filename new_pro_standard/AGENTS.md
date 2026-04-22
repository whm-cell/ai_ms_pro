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

## Harness Layers

This starter uses three harness layers:

- Runtime Harness: local session and observation state under `.codex/runtime/`
- Governance Harness: shared project memory under `docs/ai/*` and `docs/requirements/*`
- Verification Harness: lifecycle enforcement under `.codex/hooks.json`, `.githooks/*`, and `scripts/check_*`

Use these rules:

1. Runtime files are local-only recovery artifacts, not the canonical project truth.
2. Hooks may write `.codex/runtime/*`, but must not auto-edit shared governance docs.
3. Shared governance documents are authored at explicit semantic checkpoints such as subtask completion, pause/resume boundaries, stage compression, and long-lived decisions.
4. The main agent owns canonical writes to `docs/ai/*` and `docs/requirements/*`.

## Python Runtime Rule

Harness Python should run from a repo-local virtual environment at `.codex/.venv`.

Use these rules:

1. `scripts/bootstrap_harness.py` should create `.codex/.venv` with the current environment's Python unless `--python` overrides it.
2. Git hooks and Codex hooks should call `.codex/hooks/run_with_repo_python.sh` or `.codex/hooks/run_hook.sh` instead of hardcoding `/usr/bin/python3`.
3. Do not commit `.codex/.venv`.

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

## Governance Surface Budget

Do not let the default shared recovery surface grow without bound.

Use these rules:

1. `docs/ai/index.md` is a stable router, not a second stage report.
2. `docs/ai/working-context.md` should keep incremental truth, not a duplicate stage directory.
3. The default active handoff budget is `<=5`.
4. If active handoffs exceed that budget, compress absorbed detail into `status` or `adr`, then archive old handoffs.
5. Small routing duplication is acceptable when it supports structure checks; large duplicated stage listings are not.

## Verification Layer

Preferred command:

`python3 scripts/check_ai_governance.py`

This repository also includes a repo-local Codex `Stop` hook that runs the same governance check automatically when hooks are enabled.

Git hook setup:

`git config core.hooksPath .githooks`

## Completion Condition

A task that materially changed the project is not fully complete until:

1. implementation is updated
2. affected project docs are updated if needed
3. `docs/ai/index.md` is still accurate
4. `python3 scripts/check_ai_governance.py` passes when applicable
