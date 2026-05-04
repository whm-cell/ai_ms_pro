---
name: repo-governed-coding
description: Optional coding guardrails for governed repo work. Use for non-trivial implementation, review, or refactor tasks needing assumptions, minimal diffs, doc sync, REQ/WS traceability, and verification.
---

# Repo Governed Coding

## Overview

Use this skill as a repo-local constraint layer for governed code changes in this repository. Keep the four Karpathy-style principles, then extend them with this repo's requirements for doc sync, traceability, verification, and primary truth surface boundaries.

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
- Run document impact check after meaningful implementation or governance changes.
- Preserve or add `Requirement IDs` and `Workstream IDs` when the task is already bound; write `未绑定` when the mapping is unknown.
- Run repo verification before treating the task as complete.
- Keep current-state truth out of `plan` and `workstream` projection surfaces.

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

### Document Impact Check

- Run `implementation change -> document impact check -> update affected docs -> update docs/ai/index.md` as the default rule.
- Update `handoff`, `status`, `changelog`, `adr`, `working-context`, or `traceability-matrix` when the task meaningfully changes shared project truth.
- Treat missing doc sync as incomplete work, not as an optional polish step.

### Traceability Discipline

- Keep `Requirement IDs` and `Workstream IDs` aligned with `docs/requirements/traceability-matrix.md`.
- Update both AI-side artifacts and requirements-side mapping in the same change when the task becomes newly bound.
- Do not invent IDs; write `未绑定` when the mapping is unknown.

### Verification Finish Line

- Run `python3 scripts/check_ai_governance.py` before closing a materially meaningful task when the repo state makes the check applicable.
- Run task-specific tests or smoke checks needed to prove the request.
- Treat "code written" as incomplete if verification or required doc sync is missing.

### Primary Truth Surface Boundary

- Keep current-state truth in `docs/ai/working-context.md`, active `handoff`, `status`, `adr`, `docs/requirements/normalized/*.md`, and `docs/requirements/traceability-matrix.md`.
- Keep `docs/ai/plan.md` and `docs/requirements/workstreams/*.md` as projection surfaces, not duplicate status boards.
- Follow repository rules if this skill and repo policy ever disagree.

## Reference

- Read [governance-checklist.md](references/governance-checklist.md) when you need the repo-specific update and closeout checklist.
