---
name: prd-to-project-skills
description: Convert stable PRD, requirement, or workstream patterns into candidate project skills while keeping current state and acceptance truth in governance docs.
---

# PRD To Project Skills

## Current Status

Candidate

## Scope

Use this skill when a PRD, normalized requirement, workstream, ADR, or repeated implementation pattern may contain reusable project execution guidance.

This skill does not implement features. It classifies project knowledge and proposes candidate skills only when the pattern is stable enough to reduce future context cost.

## Default Workflow

1. Identify candidate sources.
- Read the relevant PRD / source requirement, normalized requirement, workstream, ADR, or implementation evidence.
- Record the source path and whether it is product intent, current state, execution method, architecture rule, style rule, dependency rule, or validation rule.

2. Separate truth from method.
- Keep product requirements, acceptance state, latest validation evidence, blockers, and current progress in requirements / AI governance docs.
- Move only stable execution guidance, module patterns, architecture constraints, API conventions, testing patterns, or dependency rules into candidate skills.

3. Classify each item.
- `Keep in requirements`: product behavior, acceptance criteria, traceability, current stage mapping.
- `Candidate skill`: reusable method or pattern expected to help multiple future tasks.
- `Promote to ADR/status/check`: long-lived decision, current-stage workflow change, or enforceable verification rule.
- `Reject skill`: one-off note, unstable idea, duplicated governance rule, or stale current-state detail.

4. Draft candidate skill content.
- Use `docs/ai/templates/project-skill-lifecycle.md`.
- Include `Current Status`, `Scope`, `Default Rules`, `Escape Hatch`, `Evidence`, `Promotion Rule`, and `Deprecation Rule`.
- Keep the skill body focused; move large examples or checklists into `references/`.

5. Publish through governance.
- If a candidate skill is created or changed, update the appropriate handoff, status, ADR, or changelog.
- Keep `docs/ai/index.md` as a route only when the new skill changes an important on-ramp.
- Never let a skill become the canonical source for requirement truth.

## Required Output

When active, return or record these fields:

- Candidate Sources
- Stability Assessment
- Keep In Requirements
- Candidate Skill Content
- Promote To ADR / Status / Check
- Reject Skillization
- Governance Updates Needed

## Escape Hatch

Do not create or update a skill when:

- the source is a one-off requirement
- the pattern has not survived at least one real implementation or review
- the content is current state, latest evidence, or progress tracking
- it would duplicate an existing active skill or repository rule

If rejecting skillization affects current project execution, record the reason in handoff or status.

## Promotion Rule

Promote candidate skills only after repeated use proves that selective loading reduces context without hiding canonical truth.

## Deprecation Rule

Deprecate candidate skills when requirements change, architecture changes, evidence contradicts the pattern, or the content should become an ADR / check / `AGENTS.md` rule instead.

## Reference

- Use [classification-checklist.md](references/classification-checklist.md) to avoid turning PRD state into hidden skill truth.
