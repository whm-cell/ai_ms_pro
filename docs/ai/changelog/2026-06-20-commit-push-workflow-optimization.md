# Commit / Push Workflow Optimization

日期：2026-06-20
阶段：STAGE-00 Runtime Harness Foundation
Requirement IDs：未绑定
Workstream IDs：未绑定

## 新增功能

- 新增 `scripts/report_pr_checks.py`，用于只读报告 PR 状态、draft 状态、branch、failed / pending / unknown checks。
- 新增 `scripts/start_pr_repair_worktree.py`，用于创建或复用 sibling detached PR repair worktree，并打印更新 PR head branch 的 push 命令。
- pre-commit fast gate 增加 `git diff --cached --check`，在本地 commit 前拦截 staged whitespace 问题。

## 行为变化

- 阶段提交 / PR-CI 操作手册改为分阶段流程：本地 fast gates、feature branch / draft PR、只读 checks、独立 repair worktree、用户确认后合并 `main`、再按本地状态同步开发分支。
- `docs/ai/verification-minimums.md` 增加 commit / push / PR checks / PR repair worktree 的最小验证路由。
- `docs/ai/check-registry.md` 将两个新 helper 记录为 advisory 操作辅助，不升级为 blocking。

## 修复问题

- 旧阶段提交手册把 commit、push、PR checks、PR 修复、合并 `main` 和本地同步放在同一条流程里，容易让操作者把高影响动作连在一起执行。
- 当前仓库缺少独立 PR repair worktree helper，PR checks 失败时容易污染正在继续开发的主工作区。
- pre-commit fast gate 没有显式执行 staged whitespace 检查，主要依赖 CI 的 `git diff --check` 才发现空白错误。
- root 与 starter 的 local execution policy wrapper 单测不再要求 Windows 存在 POSIX `env` 可执行文件；测试保留 sensitive-output policy 语义并 mock 实际执行。

## 破坏性变更

- 无。新增 helper 默认不 merge、不 push、不清理 worktree；pre-commit 只新增 staged whitespace fast gate。

## 边界

- 不新增真实 CI agent workflow、hosted trace/eval、native sandbox、MCP/A2A runtime、远端 required-check enforcement 或禁直推证明。
- `report_pr_checks.py` 只读 GitHub PR metadata；若 token 不能读 check rollup，会报告 unavailable，而不是把未知状态写成 OK。
- `start_pr_repair_worktree.py` 可以创建本地 worktree，但不自动修改当前开发工作区、不自动 merge、不自动清理 worktree、不证明 PR checks 通过。
- main push branch hygiene 仍保持 advisory summary；PR branch hygiene 仍保持 strict。

## 验证范围

- `tests/test_pr_workflow_helpers.py`
- `tests/test_execution_sandbox_wrapper.py`
- `new_pro_standard/tests/test_execution_sandbox_wrapper.py`
- `.githooks/pre-commit`
- `new_pro_standard/.githooks/pre-commit`
- `scripts/report_pr_checks.py`
- `scripts/start_pr_repair_worktree.py`
- `docs/ai/verification-minimums.md`
- `docs/ai/check-registry.md`

## 关联文档

- [Verification Minimums](../verification-minimums.md)
- [Check Registry](../check-registry.md)
- [Remote Merge Gates](../security/remote-merge-gates.md)
