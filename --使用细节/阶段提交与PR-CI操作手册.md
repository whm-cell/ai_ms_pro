# 阶段提交与 PR-CI 操作手册

更新时间：2026-06-20

## 这是什么

这份手册用于把阶段性开发收口到 GitHub PR，同时避免把本地提交、PR 修复、合并 `main` 和同步开发分支混成一个高风险动作。

推荐总流程：

`fast local gates -> feature branch -> commit -> push -> draft PR -> PR CI -> isolated repair worktree -> user-confirmed merge -> safe local sync`

它不是新功能开发提示词。进入该流程后，默认停止扩展业务范围，只做收口、验证、提交、PR 修复和交接。

## 总提示词

```text
按本项目的「快本地门禁 + PR 异步重检查 + 独立 PR repair worktree」流程提交：
本地只跑 fast gates，不跑长 smoke，不直接推 main。
建/使用 codex/ 前缀 feature branch，整理 staged 范围，commit，push，开 draft PR。
PR checks 失败时，用独立 repair worktree 修复并 push 回 PR 分支，不污染当前开发工作区。
checks 全过后先问我，再合并到 main。
合并后不要自动同步我当前开发分支；先检查本地状态，再给同步方案。
```

## 阶段 1：开发完成，准备提交 PR

```text
按本项目的「快本地门禁 + PR 异步重检查」提交这次改动：
不要跑长 smoke，不要推 main。
检查当前改动范围，建/使用 codex/ 前缀 feature branch。
只跑必要 fast gates：git diff --cached --check、check_code_shape.py --staged、改动面对应 focused check，必要时补 typecheck。
commit、push 当前分支，创建 draft PR，让 GitHub Actions 异步跑 smoke / Windows / security evidence。
提交前不要重复跑 live provider 或生产级真实集成验证，除非我明确要求。
```

执行要点：

- 先看 `git status -sb`、`git diff --cached --name-status`、`git diff --name-status`、`git log --oneline --decorate -5`。
- 如果还在 `main` 且有阶段性改动，先创建 `codex/<task-slug>` 分支。
- staged 范围只包含本阶段相关代码、测试、治理文档和必要配置；不要默认 `git add .`。
- 删除项、来源不明 untracked、本地 runtime、缓存、`.codex/.venv` 和大文件必须单独确认。
- 本地 fast gates 至少包含 staged whitespace、staged code-shape 和 changed surface 的 focused check。

Windows PowerShell 示例：

```powershell
git diff --cached --check
powershell -NoProfile -ExecutionPolicy Bypass -File .codex/hooks/run_with_repo_python.ps1 scripts/check_code_shape.py --staged
```

POSIX 示例：

```bash
git diff --cached --check
.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --staged
```

## 阶段 2：只查看 PR checks

```text
查看 PR #<编号> 的 GitHub checks 状态。
只报告状态，不修改文件、不 push。
如果失败，指出失败 workflow/job，并摘取最关键失败日志。
区分：本地 fast gates、PR smoke、security evidence、live-provider-smoke 是否按设计跳过。
```

推荐只读入口：

```bash
.codex/hooks/run_with_repo_python.sh scripts/report_pr_checks.py <PR>
```

Windows PowerShell：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .codex/hooks/run_with_repo_python.ps1 scripts/report_pr_checks.py <PR>
```

## 阶段 3：PR checks 失败，用独立 worktree 修复

```text
PR #<编号> checks 失败了。按隔离修复流程处理：
不要在我当前开发工作区修 PR。
使用 scripts/start_pr_repair_worktree.py <编号> 创建或复用独立 PR repair worktree。
在 repair worktree 里定位失败日志、做最小修复、跑 fast gates、commit。
从 detached repair worktree push 到 PR head 分支。
不要修改或 staging 我当前主工作区里的业务改动。
```

推荐入口：

```bash
.codex/hooks/run_with_repo_python.sh scripts/start_pr_repair_worktree.py <PR>
```

Windows PowerShell：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .codex/hooks/run_with_repo_python.ps1 scripts/start_pr_repair_worktree.py <PR>
```

脚本会打印 repair worktree 路径和 push 目标。修复完成后，在 repair worktree 内使用它打印的命令，例如：

```bash
git push origin HEAD:codex/<pr-head-branch>
```

## 阶段 4：修复后继续监控 PR

```text
继续监控 PR #<编号> 的 checks。
如果仍失败，继续只在 PR repair worktree 中修复并 push。
如果 checks 全部通过，报告通过状态，但不要自动合并 main，先问我是否合并。
```

## 阶段 5：合并 PR 到 main

```text
可以合并 PR #<编号> 到 main。
合并前再次确认：PR 是 open、非 draft 或先 mark ready、head SHA 未变、checks 全部通过。
然后合并 PR 到 main。
合并完成后确认 PR merged=true，并检查远端 main 指针已经更新。
不要自动 pull 到我当前本地开发分支，除非我明确要求同步。
```

当前仓库是 private GitHub Free 边界：远端 branch protection、required checks、review gates、禁直推和 ruleset 仍可能是 `UNKNOWN`。即使本地流程要求先 PR，也不能宣称远端已经强制。

## 阶段 6：当前开发分支同步 main

```text
现在帮我把当前开发分支同步最新 main。
先检查 git status，不要覆盖未提交改动。
如果工作区有未提交改动，先说明风险，并建议 commit / stash / 新 worktree 三种方案。
确认安全后 fetch origin，再把 origin/main 合入当前开发分支，优先使用 rebase，除非当前分支不适合 rebase。
如果有冲突，停止并说明冲突文件、冲突原因和推荐解决策略。
合并/变基完成后跑 fast gates，不跑长 smoke。
```

## 阶段 7：出现冲突时

```text
同步 main 时出现冲突了。
请先不要强制覆盖、不要 reset --hard。
列出冲突文件，解释每个冲突大概来自 main 还是当前业务分支。
在保留我当前业务意图的前提下解决冲突。
解决后跑 fast gates，commit/rebase --continue 前先让我确认关键冲突处理结果。
```

## 阶段 8：清理 PR repair worktree

```text
PR #<编号> 已合并后，帮我检查是否可以清理对应 PR repair worktree。
先确认 worktree 没有未提交改动，再建议 git worktree remove <路径>。
不要删除当前主开发工作区。
```

## 人工确认点

- 当前分支是 `main`，用户却要求直接 push。
- 本地验证失败，但用户仍想提交。
- 要删除一批文件，且删除不是当前任务明确目标。
- staged 与 unstaged 混在同一个文件里，且需要分块 staging。
- PR checks 失败原因与当前阶段无关，可能是远端环境或历史债。
- 合并 PR 或同步本地开发分支前，当前工作区有未提交改动。

## 成功标准

- commit 能被一句话解释清楚。
- staged 范围只包含当前阶段相关内容。
- 本地只跑必要 fast gates，长 smoke 由 PR CI 或显式异步验证承接。
- PR 失败修复不污染当前开发工作区。
- PR 合并和本地分支同步分阶段、可确认、可回退。
- runtime 文件、缓存、`.codex/.venv`、无关 untracked 和未确认删除没有混进提交。
