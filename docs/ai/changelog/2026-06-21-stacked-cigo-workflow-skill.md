# Stacked CIGO Workflow Skill

日期：2026-06-21
阶段：STAGE-00 Runtime Harness Foundation
Requirement IDs：未绑定
Workstream IDs：未绑定

## 新增功能

- 新增 `.agents/skills/stacked-cigo-workflow/`，把 CIGO-style PR 生命周期、stacked follow-up branch、独立 PR repair worktree、安全 `main` 同步和 runtime cleanup 固化为项目 skill。
- 新增分流参考：branch-base decision table、PR lifecycle、stacked branch、local sync / cleanup 和 failure modes。
- 新增 skill metadata：`.agents/skills/stacked-cigo-workflow/agents/openai.yaml`。

## 行为变化

- 将外部来源中的 `master` 口径调整为当前仓库的 `main`。
- 将 PR repair 入口绑定到当前仓库已有的 `scripts/report_pr_checks.py` 与 `scripts/start_pr_repair_worktree.py`，并保留 PowerShell / POSIX wrapper 示例。
- 明确 `UNKNOWN` remote check / branch-protection state 不得当作 green，也不得证明远端 required checks 或禁直推已强制。
- `docs/ai/index.md` 和 `AGENTS.md` 增加 `$stacked-cigo-workflow` 路由；旧中文操作手册增加 skill 指针。

## 修复问题

- 旧阶段提交 / PR-CI 手册是长文档提示词，不适合作为可发现、可压缩、可路由的项目 skill。
- 外部 skill 原始版本使用 `master` 与 `pnpm run pr:worktree` 口径，不匹配当前仓库的 `main` 与 Python helper。

## 破坏性变更

- 无。新增 skill 是 operator guidance，不修改 GitHub workflow、branch protection、helper 脚本或 runtime 行为。

## 边界

- 这是 operator workflow skill，不新增 hosted CI agent、remote enforcement、native sandbox、MCP/A2A、hosted trace/eval 或自动 merge 能力。
- `.codex/runtime/**` 仍是本地恢复材料，不能作为 canonical evidence 提交或提升。
- 旧中文操作手册只增加 skill 指针，暂不删除，避免丢失可读提示词。

## 验证范围

- `scripts/check_repo_skills.py`
- `scripts/check_ai_governance.py`
- `scripts/check_context_budget.py`
- `git diff --check`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Verification Minimums](../verification-minimums.md)
- [Commit / Push Workflow Optimization](./2026-06-20-commit-push-workflow-optimization.md)
