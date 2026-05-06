# PRD To Skill Classification Checklist

Use this checklist when `$prd-to-project-skills` is active.

## Keep In Requirements

- Product behavior and user-facing acceptance criteria.
- Current requirement status, stage mapping, and traceability.
- Latest smoke evidence, validation results, blockers, and open questions.
- One-off business rules that are not expected to guide future implementation.

## Candidate Skill

- Stable module or architecture pattern repeated across tasks.
- API, data, testing, or review convention that future agents should load on demand.
- Dependency or framework usage rule backed by actual implementation evidence.
- PRD-to-implementation conversion method that reduces repeated context.

## Promote To ADR / Status / Check

- Long-lived architecture, delivery, testing, review, or dependency decision.
- Current-stage workflow change affecting multiple tasks.
- Rule that should become enforceable by script, hook, or CI check.
- Skill replacement, deprecation, or conflict that future agents must know.

## Reject Skillization

- Current progress or recent validation result.
- Unverified idea or speculative abstraction.
- Content already covered by `AGENTS.md`, ADR, or an active skill.
- Conflicting active workflow where the current effective entry is unclear.

## Required Closeout

- State the selected bucket for every candidate item.
- Name any governance docs that must be updated.
- Name any candidate skill directory only after confirming the content is stable enough.
- Write `未绑定` instead of inventing `REQ/WS` IDs when mapping is unknown.
