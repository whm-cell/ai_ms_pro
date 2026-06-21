---
name: stacked-cigo-workflow
description: Manage repo CIGO-style PRs, stacked follow-up branches, repair worktrees, safe main sync, and runtime cleanup without expanding remote-enforcement claims.
---

# Stacked CIGO Workflow

## Overview

Use this skill to keep PR publishing, stacked follow-up branches, isolated PR repair, local `main` sync, and cleanup as separate operator phases.

CIGO here is an operator workflow label for Codex-assisted Git operations. It does not create a hosted CI agent workflow, replace GitHub branch protection, or replace `AGENTS.md`, `docs/ai/*`, deterministic checks, or user confirmation for high-impact actions.

## First Checks

1. Read `AGENTS.md`, `docs/ai/index.md`, `docs/ai/working-context.md`, and `docs/ai/verification-minimums.md`.
2. Classify the task profile before editing.
3. Check whether `$team-pr-conflict-control` also applies when there are parallel PRs, shared governance files, CODEOWNERS, or merge-readiness questions.
4. Confirm whether the task is one of:
- `cigo-pr`: submit, monitor, repair, or merge a PR.
- `stacked-followup`: start or maintain a child branch that depends on an unmerged parent PR.
- `sync-main`: update a local branch or worktree after `main` moves.
- `cleanup`: remove repair worktrees, temporary runtime output, or duplicated prompt docs.

## Decision Router

- For branch-base choices, read [decision-table.md](references/decision-table.md).
- For PR submission, check monitoring, repair, and merge, read [cigo-pr-lifecycle.md](references/cigo-pr-lifecycle.md).
- For branch A -> branch B stacked development, read [stacked-branches.md](references/stacked-branches.md).
- For local sync and cleanup after merge, read [local-sync-and-cleanup.md](references/local-sync-and-cleanup.md).
- For common failure patterns, read [failure-modes.md](references/failure-modes.md).

## Hard Rules

- Use `codex/` branch names by default.
- Do not push directly to `main`.
- Do not merge a PR until checks are green or explicitly confirmed as acceptable by the user; treat unknown check or branch-protection state as `UNKNOWN`, not green.
- Confirm the PR head SHA before merging when a connector or GitHub metadata can provide it.
- Do not run long smoke, live provider, or production integration checks locally unless the user explicitly asks; use local fast gates plus PR/GitHub Actions for longer checks.
- If PR checks fail while local development may continue, repair only in an isolated PR repair worktree created by the repo helper.
- Do not stage or promote `.codex/runtime/**` as canonical evidence. Durable truth belongs in `docs/ai/*`, `docs/requirements/*`, ADRs, status, handoffs, checks, or code.
- Do not auto-sync the user's current development branch after merge. Inspect `git status` first and choose commit, stash, worktree, rebase, merge, or no-op intentionally.
- Use `git reset --hard` only for an explicitly requested clean sync after verifying the target branch/worktree and local dirty state.

## Verification

Select the smallest defensible check bundle from `docs/ai/verification-minimums.md`.

For skill/doc-only changes, normally run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .codex/hooks/run_with_repo_python.ps1 scripts/check_repo_skills.py
powershell -NoProfile -ExecutionPolicy Bypass -File .codex/hooks/run_with_repo_python.ps1 scripts/check_ai_governance.py
powershell -NoProfile -ExecutionPolicy Bypass -File .codex/hooks/run_with_repo_python.ps1 scripts/check_context_budget.py
git diff --check
```

Use the POSIX `.codex/hooks/run_with_repo_python.sh` wrapper when working outside PowerShell.

## Required Output

When active, return or record:

- Workflow Type
- Branch / Worktree State
- PR Base Decision
- Repair Isolation Decision
- Verification Commands
- Merge / Sync Confirmation State
- Governance Writeback Decision
