---
name: team-pr-conflict-control
description: Guide team or multi-agent PR collision control with touch-set overlap review, high-risk files, PR templates, CODEOWNERS, merge_group readiness, and governance writeback.
---

# Team PR Conflict Control

## Overview

Use this skill to prevent team or multi-agent work from colliding before merge time. It turns PR touch sets, high-risk paths, PR templates, CODEOWNERS, and merge queue readiness into a lightweight decision gate.

This skill does not replace GitHub settings or deterministic checks. It produces the coordination decision and points to scripts, workflows, PR templates, or governance docs that should carry enforcement.

## When To Skip

- Single-person local work with no PR, no shared governance files, and no overlapping branch concern.
- Already-materialized Git merge conflicts where the task is only to resolve conflict markers.
- Ordinary code review comments that do not involve changed-file overlap, ownership, or queue policy.

## Workflow

1. Classify the collaboration mode.
- `solo`: one active branch, no shared branch or open PR overlap risk.
- `team`: multiple developers or AIs may touch the repo concurrently.
- `high-risk team`: the change touches governance, CI, schema, migrations, shared routing, generated lockfiles, or platform-wide modules.

2. Build the current touch set.
- Prefer PR file lists when working on GitHub.
- Use local `git diff --name-only` only when PR metadata is unavailable.
- Include intended files when the implementation has not started yet.
- Carry known `Requirement IDs` and `Workstream IDs`; write `未绑定` if unknown.

3. Compare against active parallel work.
- Use GitHub PR metadata when available.
- Treat API/auth failure as `UNKNOWN`, not as safe.
- Separate same-file overlap from same-domain overlap.
- Escalate high-risk overlaps even when the textual diff is small.

4. Decide the coordination action.
- `continue`: no overlap or overlap is trivial and documented.
- `coordinate`: overlap exists but can be sequenced, split, or owner-reviewed.
- `block until resolved`: high-risk overlap exists, branch protection is unclear, or open PRs modify the same control-plane file.

5. Check PR hygiene.
- PR body should declare `REQ/WS`, touch set, high-risk files, overlap status, verification commands, and screenshots or smoke evidence when relevant.
- CODEOWNERS should cover control-plane and shared modules.
- Required workflows should include `pull_request`; if merge queue is enabled, required checks must also run on `merge_group`.

6. Write back durable decisions.
- One-off coordination belongs in PR body or review comments.
- Repeated conflict patterns belong in status, ADR, scripts, CODEOWNERS, PR templates, or a dedicated check.
- Do not put temporary branch coordination into requirements truth.

## Required Output

When active, return or record:

- Collaboration Mode
- Current Touch Set
- Open PR Overlap Result
- High-Risk Files
- Required Coordination Action
- PR Template Coverage
- CODEOWNERS / Merge Queue Readiness
- Governance Writeback Decision

## References

- [control-checklist.md](references/control-checklist.md)
- [evidence-and-boundaries.md](references/evidence-and-boundaries.md)
- [pr-template-minimum.md](references/pr-template-minimum.md)
