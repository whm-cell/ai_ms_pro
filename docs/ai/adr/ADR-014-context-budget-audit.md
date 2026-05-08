# Context Budget Audit

更新时间：2026-05-07
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
- 默认上下文面达到 `80%` / `90%` 时先 warning；`90%` 视为继续增加 always-on 内容前必须 stage compression 的高水位。
- ADR 数量达到预算即 warning；`15/15` 不再视为正常余量。
- active stage `status` 达到 `stage_status_line_budget` 即触发 stage compression 检查。
- Subagent 默认使用精简任务包，不 fork 完整会话上下文；完整 PRD、完整 diff、完整 transcript/runtime JSONL 不直接进入对话或治理文档。
- `new_pro_standard` 同步脚本与配置，作为可迁移机制层。

## 备选方案

- 方案 A：直接接入 Stop hook，每轮结束自动跑 context budget。
- 方案 B：直接引入 strategic compact hook，按工具调用或 token 压力提醒 compact。
- 方案 C：只依赖 archive candidate monitor，不新增 budget audit。

## 决策理由

- 手动 warning-only 能暴露上下文膨胀来源，但不会在简单任务中增加默认上下文或 hook 噪音。
- Context budget audit 与 archive candidate monitor 分工不同：前者审计默认上下文成本，后者只审查 active handoff 归档候选。
- 真实 REQDOC-003 样本已经让默认短链路接近硬预算；因此需要 80/90 高水位提前报警，而不是等超过硬预算才发现。
- 当前仍没有足够样本证明自动 compact 应阻断任务，因此保留 warning-only，但把达到预算和高水位的提示变得更早、更明确。

## 外部依据

- OpenAI Codex subagents 文档说明 subagent 有自己的上下文窗口，适合把独立任务交给隔离上下文执行，而不是默认继承完整父会话：https://developers.openai.com/codex/concepts/subagents
- OpenAI Agents handoff / context 文档支持在 agent 交接时过滤或管理上下文输入，说明“传什么上下文”应被显式控制：https://openai.github.io/openai-agents-js/guides/handoffs/
- OpenAI compaction 文档把会话历史摘要化作为接近上下文上限时的标准处理方式：https://platform.openai.com/docs/guides/compaction
- `Lost in the Middle` 论文指出长上下文模型在使用长输入中间位置的信息时会下降，说明“能放下”不等于“应该整包放入”：https://arxiv.org/abs/2307.03172

## 影响

- 当用户感觉 harness 对话变重，或 stage compression 前，可以运行 `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`。
- OPEN-10 首轮 triage 已完成：`AGENTS.md`、current status 和 `$repo-governed-coding` description 已瘦身；后续再次持续 warning 时，按 `--使用细节/上下文预算OPEN-10使用细节.md` 重新判断。
- Context budget audit 仍然是手动体检，不接 Stop hook，不触发自动 compact 或自动归档。
- 脚本退出码仍为 0，除非配置文件无法解析。

## 关联文档

- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [Harness Remaining Work](../harness-open-items.md)
- [ADR-010 Context Surface Layering](./ADR-010-context-surface-layering.md)
- [ADR-013 Project Skill Lifecycle](./ADR-013-project-skill-lifecycle.md)
- [上下文预算 OPEN-10 使用细节](/Volumes/usd/codes/go_projects/ai_ms_pro/--使用细节/上下文预算OPEN-10使用细节.md)
