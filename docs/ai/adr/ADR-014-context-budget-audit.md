# Context Budget Audit

更新时间：2026-05-02
编号：ADR-014
标题：默认上下文预算体检
状态：已采纳

## 背景

- Context surface、Task Discovery、archive candidate monitor 和 project skill lifecycle 已经让默认阅读链路变小，但 harness 仍会随着 ADR、status、skill 和检查脚本增长而重新变厚。
- 参考 `everything-claude-code` 的 context-budget 思路，预算治理需要先量化 always-on 文件、skill metadata、重复规则和 MCP 入口，再决定是否压缩。
- 自动 compact 或自动归档会改变会话语义，当前阶段更适合 warning-only 体检。

## 决策

- 新增 `scripts/check_context_budget.py`，手动审计默认上下文面，不接入 Stop hook，不阻断任务。
- 在 `.codex/harness.toml` 增加 `[context_budget]`，配置默认面 token 预算、always-on 文档行数、skill description/body、ADR 数量和 MCP server 数量阈值。
- 审计范围包括默认短链路、active handoff 数量、ADR 数量、repo-local skills、重复 instruction 行和 MCP server 数量。
- `6500` 作为 starter/new-project 初始目标保留；当前 root 仓库处于 Stage-00 hardening 后期，默认短链路承载更多治理真相，局部预算调为 `8500`。
- `new_pro_standard` 同步脚本与配置，作为可迁移机制层。

## 备选方案

- 方案 A：直接接入 Stop hook，每轮结束自动跑 context budget。
- 方案 B：直接引入 strategic compact hook，按工具调用或 token 压力提醒 compact。
- 方案 C：只依赖 archive candidate monitor，不新增 budget audit。

## 决策理由

- 手动 warning-only 能暴露上下文膨胀来源，但不会在简单任务中增加默认上下文或 hook 噪音。
- Context budget audit 与 archive candidate monitor 分工不同：前者审计默认上下文成本，后者只审查 active handoff 归档候选。
- 当前还没有足够样本证明自动 compact 提醒的阈值，因此先保留为手动体检。

## 影响

- 当用户感觉 harness 对话变重，或 stage compression 前，可以运行 `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`。
- OPEN-10 首轮 triage 已完成：`AGENTS.md`、current status 和 `$repo-governed-coding` description 已瘦身；后续再次持续 warning 时，按 `--使用细节/context-budget-open-10.md` 重新判断。
- Context budget audit 仍然是手动体检，不接 Stop hook，不触发自动 compact 或自动归档。
- 脚本退出码仍为 0，除非配置文件无法解析。

## 关联文档

- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [Harness Remaining Work](../harness-open-items.md)
- [ADR-010 Context Surface Layering](./ADR-010-context-surface-layering.md)
- [ADR-013 Project Skill Lifecycle](./ADR-013-project-skill-lifecycle.md)
- [OPEN-10 Context Budget 使用细节](/Volumes/usd/codes/go_projects/ai_ms_pro/--使用细节/context-budget-open-10.md)
