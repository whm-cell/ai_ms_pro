---
name: repo-governed-coding
description: Optional coding guardrails for governed repo work. Use for non-trivial implementation, review, or refactor tasks needing assumptions, minimal diffs, doc sync, REQ/WS traceability, and verification.
---

# Repo Governed Coding

## Overview

Use this skill as a repo-local constraint layer for governed code changes in this repository. Keep the four Karpathy-style principles, then use the reference checklist for repo-specific document impact, traceability, verification, and primary truth surface details.

Inspired by the MIT-licensed `forrestchang/andrej-karpathy-skills` project and adapted for this repo's Codex-first harness.

## Workflow

1. Ground the task in repo truth first.
- Read `AGENTS.md`, `docs/ai/index.md`, and `docs/ai/working-context.md` before editing.
- Read `docs/requirements/index.md` and `docs/requirements/traceability-matrix.md` when the task is requirement-driven or already bound to `REQ/WS`.
- Read the current stage `status` and relevant active `handoff` before deciding what is in or out of scope.

2. State assumptions and success criteria before editing.
- State assumptions explicitly instead of silently choosing an interpretation.
- Surface tradeoffs when there is a simpler or narrower path.
- Convert the request into verifiable checks before implementing.
- State the scope boundary: what will be changed and what will be left alone.
- If ambiguity would change the implementation, ask before writing code.

3. Implement the smallest direct change.
- Keep code simple and keep the diff narrow.
- Touch only lines that trace back to the request.
- Avoid incidental refactors, comment rewrites, or cleanup outside the requested scope.

4. Close the loop with governance.
- Use `references/governance-checklist.md` for document impact, traceability, truth-surface, and verification closeout details.
- Use `$requirements-traceability-maintenance` when changing PRD, `REQDOC`, `REQ`, `WS`, traceability matrix, or technical assumptions.
- Use `$harness-maintenance` verification references when selecting repo checks.

## Four Principles

### Think Before Coding

- State assumptions explicitly.
- Ask instead of guessing when ambiguity would change the implementation.
- Surface simpler alternatives and tradeoffs.
- Stop when confusion would make the change unsafe.

### Simplicity First

- Solve only the requested problem.
- Avoid speculative abstraction, configurability, or impossible-case handling.
- Rewrite if the solution is obviously more complex than needed.

### Surgical Changes

- Match existing style.
- Do not improve unrelated nearby code.
- Clean up only artifacts introduced by your own change.
- Keep every changed line traceable to the request.

### Goal-Driven Execution

- Define success as a checkable outcome.
- Prefer tests or smoke checks when they exist.
- Verify before declaring completion.
- Summarize changed files, checks run, and remaining risk.

## Repo-Specific Extensions

Detailed repo-specific rules live in `references/governance-checklist.md` so this skill body stays small. Follow `AGENTS.md` if any rule conflicts, and promote durable workflow changes to status or ADR.

## Reference

- Read [governance-checklist.md](references/governance-checklist.md) when you need the repo-specific update and closeout checklist.
