# 2026-05-04 Harness Maintenance Skill Downshift

更新时间：2026-05-04
阶段或版本：stage-00
状态：已确认

## 新增功能

- Added `$harness-maintenance` as an on-demand repo-local skill for bootstrap, hooks, runtime reducers, GitHub guardrails, and code-shape checks.
- Added references for Python runtime / hooks, runtime observation reduction, GitHub guardrails, and code-shape budget.

## 修复问题

- Reduced always-on `AGENTS.md` detail for harness internals while preserving trigger rules and canonical truth boundaries.
- Kept detailed mechanics in skill references instead of expanding default context.

## 行为变化

- Ordinary product tasks no longer need to carry Python runtime fallback, reducer, GitHub guardrail, and code-shape threshold details in the default context.
- Harness-internal tasks should invoke `$harness-maintenance` and the relevant reference.

## 破坏性变更

- 无

## 验证范围

- `python3 /Users/coolm/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/harness-maintenance`
- `python3 /Users/coolm/.codex/skills/.system/skill-creator/scripts/quick_validate.py new_pro_standard/.agents/skills/harness-maintenance`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`

## 关联文档

- [Harness Maintenance Skill](../../../.agents/skills/harness-maintenance/SKILL.md)
- [AI 文档入口索引](../index.md)
- [Harness 可迁移清单](../harness-portability-guide.md)
