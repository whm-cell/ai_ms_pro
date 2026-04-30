---
name: repo-governed-coding
description: Optional behavioral coding guardrails for repositories using this Codex-first harness. Use when implementing, reviewing, or refactoring code and the task benefits from explicit assumptions, minimal diffs, document impact checks, REQ/WS traceability, verification closeout, and projection-surface boundaries. Prefer explicit invocation via `$repo-governed-coding`; do not treat it as an always-on replacement for `AGENTS.md`.
---

# Repo Governed Coding

## Overview

This skill adapts the MIT-licensed `forrestchang/andrej-karpathy-skills` guidelines to the Codex-first harness. It is intentionally a task-level behavior layer: repository rules, shared docs, hooks, and verification scripts remain the control plane.

Use it for non-trivial code, harness, or review work where the agent should slow down enough to make assumptions, scope, and verification explicit.

## Workflow

1. Ground the task in repo truth first.
- Read `AGENTS.md`, `docs/ai/index.md`, and `docs/ai/working-context.md` before editing.
- Read `docs/requirements/index.md` and `docs/requirements/traceability-matrix.md` when the task is requirement-driven or already bound to `REQ/WS`.
- Read the current stage `status`, relevant active `handoff`, and relevant `ADR` before deciding scope.

2. State assumptions and success criteria before editing.
- State assumptions explicitly instead of silently choosing an interpretation.
- Surface tradeoffs when there is a simpler or narrower path.
- Convert the request into checkable success criteria before implementing.
- If ambiguity would change the implementation, ask before writing code.

3. Implement the smallest direct change.
- Keep code simple and keep the diff narrow.
- Touch only lines that trace back to the request.
- Match local style instead of introducing a new abstraction style.
- Avoid incidental refactors, comment rewrites, or cleanup outside the requested scope.

4. Close the loop with governance.
- Run the document impact check after meaningful implementation or governance changes.
- Preserve or add `Requirement IDs` and `Workstream IDs` when the task is already bound; write `未绑定` when the mapping is unknown.
- Run repo verification before treating the task as complete.
- Keep current-state truth out of `plan` and `workstream` projection surfaces.

## Four Guardrails

### Think Before Coding

- Name assumptions.
- Ask when confusion would make the change unsafe.
- Present meaningful tradeoffs.
- Push back when the requested path is materially more complex than the goal requires.

### Simplicity First

- Solve only the requested problem.
- Avoid speculative abstraction, configurability, or impossible-case handling.
- Prefer boring code that fits the current repo over broad new framework shape.

### Surgical Changes

- Do not improve unrelated nearby code.
- Clean up only artifacts introduced by the current change.
- Mention unrelated dead code or risks instead of silently editing them.

### Goal-Driven Execution

- Define success as a checkable outcome.
- Prefer tests or smoke checks when they exist.
- Verify before declaring completion.
- Summarize changed files, checks run, and remaining risk.

## Repo-Specific Extensions

### Document Impact Check

- Use `implementation change -> document impact check -> update affected docs -> update docs/ai/index.md`.
- Update `handoff`, `status`, `changelog`, `ADR`, `working-context`, or requirements docs when the task changes shared project truth.
- Treat missing doc sync as incomplete work.

### Traceability Discipline

- Keep `Requirement IDs` and `Workstream IDs` aligned with `docs/requirements/traceability-matrix.md`.
- Update both the AI-side artifact and requirements-side mapping when a task becomes newly bound.
- Do not invent IDs; write `未绑定` when the mapping is unknown.

### Verification Finish Line

- Run `python3 scripts/check_ai_governance.py` before closing a meaningful task when applicable.
- Run `python3 scripts/check_code_shape.py --staged` when implementation or harness code is staged.
- Run task-specific tests or smoke checks needed to prove the request.

### Primary Truth Surface Boundary

- Primary truth belongs in `working-context`, active `handoff`, `status`, `ADR`, normalized requirements, and `traceability-matrix.md`.
- `plan` and workstream docs are projection surfaces, not duplicate status boards.
- Follow repository rules when this skill and repo policy ever disagree.

## Reference

- Read [governance-checklist.md](references/governance-checklist.md) when you need the closeout checklist.
