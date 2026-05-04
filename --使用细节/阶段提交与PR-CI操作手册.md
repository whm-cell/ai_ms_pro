# 阶段提交与 PR-CI 操作手册

更新时间：2026-05-02

## 这是什么

这份手册用于在一个业务小阶段完成、下班前保存进度、或准备让 GitHub CI 参与验证时，指导 harness 执行：

`建分支 -> 整理 staged 范围 -> 补 handoff/status -> 本地验证 -> commit -> push -> PR -> CI 观察`

它不是新功能开发提示词。进入这个流程后，默认停止扩展业务范围，只做收口、验证、提交和交接。

## 何时使用

适合使用：

- 一个业务小阶段已经完成
- 今天要下班，需要留下可恢复的提交点
- 准备把本地工作交给 GitHub CI 验证
- 工作区里混有代码、测试、文档和 harness 改动，需要分拣
- 准备从 `main` 上的本地改动切到 `codex/...` 分支提交

不适合使用：

- 需求还没跑通，仍在快速试错
- 你只是想看当前状态，不准备 commit
- 工作区里有明显不属于当前任务的删除或大范围改动，但还没决定是否保留
- 当前 CI 失败原因还没分析，继续堆新提交会掩盖问题

## 直接可用提示词

### 标准版

```text
按“阶段提交与 PR-CI”流程处理。现在我完成了一个业务小阶段/准备下班，请不要继续扩展新功能。

目标：
1. 先检查当前分支、staged/unstaged/untracked 状态，以及最近提交。
2. 如果我还在 main 上，请从当前状态创建一个 codex/<简短任务名> 分支；如果已经在合适的工作分支上，就继续使用当前分支。
3. 按语义整理 staged 范围：只包含本阶段相关代码、测试、治理文档和必要配置；不要使用 git add .；对不确定文件、删除项、runtime 文件、缓存文件列为“需要我确认”。
4. 如果本阶段有可恢复价值，请补充或更新 handoff/status，并检查 docs/ai/index.md 是否需要更新。
5. 运行本地验证：业务相关测试、harness governance、code shape；如涉及上下文/提交治理，额外运行 context budget。
6. 给出 commit 计划，包括将提交的文件、排除的文件、验证结果和 commit message。
7. 只有 staged 范围清楚且验证通过后再 commit。
8. commit 后 push 当前 codex/... 分支，并准备 PR 说明，让 GitHub CI 参与验证。

约束：
- 不要直接 push main。
- 不要回退我已有改动。
- 不要自动包含无关 untracked 文件。
- CI 如果失败，先分析失败原因并修复，不要继续开发新需求。
```

### 更严格版

```text
按“阶段提交与 PR-CI”流程处理，但先不要 commit。

请先输出一份提交前审查表：
- 当前分支和是否领先远端
- staged / unstaged / untracked / deleted 文件分组
- 本阶段应该提交的文件
- 不应该提交的文件
- 需要我人工确认的文件，尤其是删除项和 untracked 文件
- 需要补的 handoff/status/ADR/changelog
- 本地验证命令计划
- 建议 commit message

在我回复“确认提交”之前，只允许整理计划和运行只读检查，不要 stage、commit、push。
```

### 快速版

```text
我准备阶段性提交。按 PR CI 流程收口：检查状态，必要时建 codex/... 分支，整理 staged 范围，补 handoff/status，跑本地验证，commit，push 分支并准备 PR。不要直接 push main，不要包含无关文件。
```

## Harness 应执行的顺序

1. 检查当前状态：

```bash
git status -sb
git diff --cached --name-status
git diff --name-status
git log --oneline --decorate -5
```

2. 判断分支：

- 如果在 `main` 且有阶段性改动，创建 `codex/<task-slug>` 分支。
- 如果已经在 `codex/...` 或业务分支，继续使用当前分支。
- 如果当前分支领先远端，先说明已有本地 commit，避免重复提交或错误 push。

3. 分拣文件：

- `in-scope`: 本阶段业务代码、测试、必要配置、相关治理文档。
- `doc-sync`: `handoff/status/index/ADR/changelog` 等需要随本阶段同步的文档。
- `exclude`: runtime、本地缓存、`.venv`、`__pycache__`、临时日志、与任务无关文件。
- `needs-confirmation`: 大范围删除、旧资料迁移、无关 untracked、来源不明改动。

4. 更新治理文档：

- 小修复：通常不需要新增 handoff。
- 小阶段完成或下班交接：更新或新增 active handoff。
- 阶段判断、风险或 blocker 改变：更新 status。
- 长期技术决策改变：新增或更新 ADR。
- 新增/移动 handoff、status、ADR、changelog 后：检查 `docs/ai/index.md`。

5. 显式 stage：

```bash
git add path/to/file
git add path/to/other_file
```

不要默认使用：

```bash
git add .
```

只有当文件清单已经审查完并且没有无关文件时，才可以使用批量 add。

6. 本地验证：

POSIX/macOS：

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py
.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --staged
```

Windows PowerShell：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .codex/hooks/run_with_repo_python.ps1 scripts/check_ai_governance.py
powershell -NoProfile -ExecutionPolicy Bypass -File .codex/hooks/run_with_repo_python.ps1 scripts/check_code_shape.py --staged
```

按任务再补业务测试、smoke 或 context budget。

7. Commit：

```bash
git diff --cached --stat
git commit -m "<type>: <stage summary>"
```

推荐 message：

- `feat: complete order export stage`
- `fix: stabilize login retry flow`
- `docs: record stage handoff for payment setup`
- `harness: tighten staged PR workflow`

8. Push 和 PR：

```bash
git push -u origin codex/<task-slug>
```

PR 说明应包含：

- 本阶段完成了什么
- 验证命令与结果
- 有哪些文件被刻意排除
- 还剩什么风险或下一步
- GitHub CI 需要重点观察哪些 job

## GitHub CI 参与后有什么不同

- 本地 `commit` 主要通过 pre-commit 检查 staged 范围：governance 与 code shape。
- `push` 到远端分支后，GitHub Actions 才会跑远端环境验证。
- 当前仓库的 push/PR 会跑 governance、unit tests、code shape、Windows hook runtime 和 smoke。
- dependency review 只在 PR 上跑。
- 如果远端 branch protection / ruleset 已配置，PR 合并会被 required checks、CODEOWNERS review、conversation resolved 等规则约束。
- 如果远端规则还没配置，CI 只能提供反馈，不能自动阻止直接 push `main`。

## 人工确认点

harness 遇到这些情况应暂停并让用户确认：

- 要删除一批文件，且删除不是当前任务明确目标。
- untracked 文件很多，来源不清楚。
- staged 与 unstaged 混在同一个文件里，且需要 `git add -p` 分块。
- 当前分支是 `main`，用户却要求直接 push。
- 本地验证失败，但用户仍想提交。
- CI 失败原因与当前阶段无关，可能是远端环境或历史债。

## 成功标准

一次合格的阶段性提交应满足：

- commit 能被一句话解释清楚。
- staged 范围只包含当前阶段相关内容。
- 下次会话能从 handoff/status 恢复上下文。
- 本地验证结果清楚。
- push 后由 PR/CI 承接远端验证。
- 无关文件、runtime 文件和未确认删除没有混进提交。
