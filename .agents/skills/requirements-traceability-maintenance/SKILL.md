---
name: requirements-traceability-maintenance
description: Maintain PRD, REQDOC, REQ, WS, traceability matrix, technical assumptions, and verification links without hiding requirement truth in skills.
---

# Requirements Traceability Maintenance

## Current Status

Stable

## Scope

Use this skill when importing a PRD, normalizing requirements, changing `REQDOC / REQ / WS`, editing `docs/requirements/traceability-matrix.md`, or checking whether technical stack statements are accepted facts, open assumptions, or rejected ideas.

Do not use this skill for ordinary code edits that only consume an existing `REQ/WS` mapping. Carry known IDs in those tasks and write `未绑定` when no mapping is known.

## Default Workflow

1. Preserve source truth.
- Keep the original PRD or requirement source in `docs/requirements/source/`.
- Assign or reuse stable `REQDOC` identifiers before creating normalized requirements.
- Do not rewrite uncertain technology statements into accepted architecture facts.

2. Normalize and bind.
- Create or update normalized `REQ-*` documents from the source.
- Create or update `WS-*` workstreams only for implementation-sized slices.
- Update `docs/requirements/traceability-matrix.md` in the same change when mappings change.

3. Classify technical assumptions.
- Use `references/technical-assumptions.md` when PRD text includes stack, architecture, storage, deployment, security, or integration claims.
- Promote only verified durable decisions to ADR, status, or checks.
- Keep exploratory or unverified claims as assumptions until evidence exists.

4. Verify shape.
- Use `references/requirements-traceability-checklist.md`.
- Run `scripts/check_requirements_shape.py` after PRD, `REQDOC`, `REQ`, `WS`, or matrix changes.
- Run governance checks before closeout when shared truth changed.

## Required Output

When active, return or record:

- Candidate Source IDs
- Normalized Requirement IDs
- Workstream IDs
- Traceability Matrix Changes
- Technical Assumption Status
- Verification Method
- Items Kept Out Of Skills
- Checks Run

## Truth Boundary

Requirements documents are the canonical source for current requirement truth. This skill is method guidance only. Stable reusable implementation patterns may become project skills, but acceptance criteria, current status, and traceability mappings stay in `docs/requirements/*` and `docs/ai/*`.

## References

- [requirements-traceability-checklist.md](references/requirements-traceability-checklist.md)
- [technical-assumptions.md](references/technical-assumptions.md)
