---
name: repo-governed-coding
description: Optional coding guardrails for governed repo work. Use for non-trivial implementation, review, or refactor tasks needing assumptions, minimal diffs, doc sync, REQ/WS traceability, and verification.
---

# Repo Governed Coding

## Overview

This skill adapts the MIT-licensed `forrestchang/andrej-karpathy-skills` guidelines to the Codex-first harness. It is intentionally a task-level behavior layer: repository rules, shared docs, hooks, and verification scripts remain the control plane.

Use it for non-trivial code, harness, or review work where the agent should slow down enough to make assumptions, scope, and verification explicit. Use the reference checklist for repo-specific document impact, traceability, verification, and primary truth surface details.

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
- Use `references/governance-checklist.md` for document impact, traceability, truth-surface, and verification closeout details.
- Use `$requirements-traceability-maintenance` when changing PRD, `REQDOC`, `REQ`, `WS`, traceability matrix, or technical assumptions.
- Use `$harness-maintenance` verification references when selecting repo checks.

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

Detailed repo-specific rules live in `references/governance-checklist.md` so this skill body stays small. Follow `AGENTS.md` if any rule conflicts, and promote durable workflow changes to status or ADR.

## Reference

- Read [governance-checklist.md](references/governance-checklist.md) when you need the closeout checklist.
