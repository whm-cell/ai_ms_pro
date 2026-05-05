# AGENTS Default Context Compression

更新时间：2026-05-05
阶段或版本：stage-00
状态：已确认

## 新增功能

- 将 root `AGENTS.md` 从 237 行压缩到约 190 行，保留读序、任务分类、truth boundary、skill 触发和完成条件。
- 同步 `new_pro_standard/AGENTS.md` 的轻量结构，保留 starter 专属 bootstrap / rewrite 说明。
- 将 projection、verification、GitHub guardrails、skill lifecycle 细则继续保持在 repo-local skills、references、templates 或 deterministic checks 中。

## 修复问题

- 修复 `AGENTS.md` 中部分已下沉机制仍以解释性长段落留在默认上下文的问题。
- 避免 projection、verification、GitHub 和 skill lifecycle 细则在 always-on 文档与 skill/reference 层重复维护。

## 行为变化

- `AGENTS.md` 更明确地作为 always-on trigger layer，而不是完整流程说明书。
- 详细机制仍按需进入 `$repo-governed-coding`、`$harness-maintenance`、`$team-pr-conflict-control`、`requirements-traceability-maintenance` 或 `project-skill-lifecycle` template。
- 远端 GitHub branch protection / rulesets 状态不变；`UNKNOWN` 仍不能被宣称为 OK。

## 破坏性变更

- 无。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `/Users/coolm/.pyenv/versions/3.11.13/bin/python3 scripts/check_ai_governance.py` from `new_pro_standard`
- `/Users/coolm/.pyenv/versions/3.11.13/bin/python3 scripts/check_context_budget.py` from `new_pro_standard`
- `git diff --check`

## 关联文档

- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Harness Maintenance Skill](../../../.agents/skills/harness-maintenance/SKILL.md)
- [Repo Governed Coding Governance Checklist](../../../.agents/skills/repo-governed-coding/references/governance-checklist.md)
