# OPEN-10 Context Budget Triage 使用细节

更新时间：2026-05-02

## 这是什么

OPEN-10 是一次默认上下文体检后的瘦身 triage，不是自动归档或自动 compact。

它解决的问题是：当 `scripts/check_context_budget.py` 提示默认短链路变厚时，人工判断应该调预算、压缩 always-on 文档、压缩 current status，还是缩短 skill metadata。

## 何时开始做

适合在这些时间点做：

- 一批 harness 改动已经稳定并通过 governance check
- 准备进入新的真实项目或新的 stage
- 准备做 stage compression
- 简单任务开始明显感觉默认上下文太厚
- `scripts/check_context_budget.py` 连续提示同一类 warning

不适合在这些时间点顺手做：

- 正在业务实现中途
- active handoff 还没有被 status / backlog / ADR 吸收
- 当前 stage status 还承担恢复必读信息
- 还没跑 governance check

## 当前决策

- `6500` token budget 保留为 starter / 新项目的默认目标。
- 当前 root repo 暂时使用 `8500` 作为 Stage-00 本地预算，因为它包含成熟阶段的 current status、ADR 历史和多个治理 hardening 结论。
- context budget audit 保持 warning-only，不接 Stop hook。
- 不做自动 compact；compact 应在计划完成、调试结束、阶段切换等语义点触发。
- 不做自动归档；归档仍需确认 handoff 的未完成项、风险和下一步动作已经进入 status / backlog / ADR。

## 本轮已处理

- 压缩 `AGENTS.md` 的长细则，保留 always-on 决策规则。
- 压缩 current stage status，把历史完成列表回收到成果摘要和关联文档。
- 缩短 `$repo-governed-coding` skill description。
- 保留 context budget audit 为手动命令。

## AGENTS 规则怎么搬

不搬走这些 always-on 规则：

- 任务入口与默认阅读顺序
- document impact check 的触发规则
- runtime / governance / verification 三层边界
- Python runtime resolution 规则
- handoff、status、ADR、changelog 的升级条件
- verification 命令入口
- skill 不替代 repo governance 的边界

可以搬到按需模板或使用细节的内容：

- 长解释、背景、例子和复查清单
- GitHub 远端设置步骤
- project architecture/style/dependency skill 生命周期细节
- context budget triage 细节
- 某个 stage 的历史完成列表

判断标准：如果简单任务也必须默认遵守，就留在 `AGENTS.md`；如果只有特定场景才需要展开，就放到 `docs/ai/templates/`、`--使用细节/`、ADR 或 status。

## 复查命令

POSIX/macOS：

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py
.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py
.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --staged
```

Windows PowerShell：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .codex/hooks/run_with_repo_python.ps1 scripts/check_context_budget.py
powershell -NoProfile -ExecutionPolicy Bypass -File .codex/hooks/run_with_repo_python.ps1 scripts/check_ai_governance.py
powershell -NoProfile -ExecutionPolicy Bypass -File .codex/hooks/run_with_repo_python.ps1 scripts/check_code_shape.py --staged
```

## 再次触发时怎么判断

- 如果只有当前 root repo 超过 `6500`，但低于本地预算，先不改 starter。
- 如果 `AGENTS.md` 超过 300 行，优先看是否有细则能移入 ADR、template 或 usage guide。
- 如果 current status 过长，优先压缩历史完成项，只保留当前判断、风险、下一步。
- 如果 skill description 过长，缩短触发说明，把细节留在 skill 正文。
- 如果重复 instruction 出现在 `working-context` 和 status 中，只保留一个 primary truth，另一个改成引用。
