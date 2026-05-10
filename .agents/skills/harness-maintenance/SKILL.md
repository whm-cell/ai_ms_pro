---
name: harness-maintenance
description: Maintain Codex harness runtime, hooks, reducers, GitHub guardrails, agentic standards, trace/eval/tool contracts, and code-shape checks through scoped references without expanding always-on AGENTS guidance.
---

# Harness Maintenance

## Current Status

Stable

## Scope

Use this skill when changing the harness itself: Python runtime discovery, bootstrap, hook runners, runtime observation/session reducers, handoff compression, GitHub workflows or repository guardrails, agentic standards, trace/eval/tool contracts, code-shape budgets, or related verification scripts.

Do not use this skill for ordinary product features, simple edits, PRD normalization, or task implementation that only consumes the harness.

## Default Workflow

1. Classify the harness area.
- Python runtime / hooks: use `references/python-runtime-and-hooks.md`.
- Runtime observation / reducer: use `references/runtime-observation-reduction.md`.
- Session promotion / compression: use `references/runtime-governance-compression.md`.
- GitHub guardrails: use `references/github-guardrails.md`.
- Supply-chain evidence: use `references/supply-chain-security.md`.
- Agentic standards / trace / eval / tool contracts: use `references/agentic-standards.md`.
- Code shape: use `references/code-shape-budget.md`.
- Verification commands: use `references/verification-commands.md`.

2. Keep AGENTS light.
- Put recurring detailed mechanics in this skill or deterministic scripts.
- Keep `AGENTS.md` limited to trigger rules, canonical truth boundaries, and required verification.

3. Preserve truth boundaries.
- Runtime files are local recovery artifacts.
- `docs/ai/*` and `docs/requirements/*` remain canonical shared truth.
- Scripts and hooks detect drift; they do not silently rewrite governance docs.

4. Verify the changed surface.
- Run the specific script or test for the changed harness area.
- Run `scripts/check_ai_governance.py` after governance-surface changes.
- Run `scripts/check_context_budget.py` after adding always-on text or skills.
- Run `scripts/check_code_shape.py --staged` when harness code is staged.

## Required Output

When active, return or record:

- Harness Area
- Reference Used
- Always-On Surface Impact
- Verification Commands
- Governance Update Decision

## Escape Hatch

Skip this skill when the task only uses existing harness commands without changing harness behavior.

## Revision Rule

Revise this skill through status, ADR, or changelog when harness maintenance tasks show that a reference is outdated, too broad, or should be enforced by a deterministic check instead.

## References

- [python-runtime-and-hooks.md](references/python-runtime-and-hooks.md)
- [runtime-observation-reduction.md](references/runtime-observation-reduction.md)
- [runtime-governance-compression.md](references/runtime-governance-compression.md)
- [github-guardrails.md](references/github-guardrails.md)
- [supply-chain-security.md](references/supply-chain-security.md)
- [agentic-standards.md](references/agentic-standards.md)
- [code-shape-budget.md](references/code-shape-budget.md)
- [verification-commands.md](references/verification-commands.md)
