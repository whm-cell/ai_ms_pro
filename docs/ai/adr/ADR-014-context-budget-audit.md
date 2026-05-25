# Context Budget Audit

更新时间：2026-05-21
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

## 2026-05-21 Runtime Token Budget 修订

- 保持 `check_context_budget.py` 负责静态默认面、skill catalog、raw source 和 static task packet。
- 新增 `scripts/check_runtime_token_budget.py`，负责按需审计 Codex rollout JSONL transcript 中的运行时 token 压力。
- 在 `.codex/harness.toml` 增加 `[runtime_token_budget]`：单次 tool output `5000`、单次 last input `100000`、单次 fresh input / cache miss `50000`、`task_complete` `8`、token snapshot `160`、session elapsed `90` 分钟。
- 该检查定级为 `blocking-candidate`：CI 只跑无 transcript 的 wiring check；真实 transcript audit 通过 `--transcript <rollout-jsonl>` 手动触发；`--strict` 只用于刻意验证 transcript gate。2026-05-23 起，Stop hook 复用同一阈值做 warning-only 当前 transcript 摘要，不升级为阻断。
- 运行时治理规则补入 `$harness-maintenance` `references/runtime-token-budget.md`，避免把完整执行细则塞回 always-on `AGENTS.md`。

## 备选方案

- 方案 A：直接接入 Stop hook，每轮结束自动跑 context budget。
- 方案 B：直接引入 strategic compact hook，按工具调用或 token 压力提醒 compact。
- 方案 C：只依赖 archive candidate monitor，不新增 budget audit。

## 决策理由

- 手动 warning-only 能暴露上下文膨胀来源，但不会在简单任务中增加默认上下文或 hook 噪音。
- Context budget audit 与 archive candidate monitor 分工不同：前者审计默认上下文成本，后者只审查 active handoff 归档候选。
- 真实 REQDOC-003 样本已经让默认短链路接近硬预算；因此需要 80/90 高水位提前报警，而不是等超过硬预算才发现。
- 当前仍没有足够样本证明自动 compact 应阻断任务，因此保留 warning-only，但把达到预算和高水位的提示变得更早、更明确。
- 2026-05-21 的长会话样本显示，默认文档面已经受控，但 broad `rg`、完整 skill 读取、完整 diff 和高 cache-miss turn 能把单次工具输出或单次 input 推到高水位；因此需要把 runtime token pressure 从静态文档预算中拆出单独审计。

## 外部依据

- OpenAI Codex subagents 文档说明 subagent 有自己的上下文窗口，适合把独立任务交给隔离上下文执行，而不是默认继承完整父会话：https://developers.openai.com/codex/concepts/subagents
- OpenAI Agents handoff / context 文档支持在 agent 交接时过滤或管理上下文输入，说明“传什么上下文”应被显式控制：https://openai.github.io/openai-agents-js/guides/handoffs/
- OpenAI compaction 文档把会话历史摘要化作为接近上下文上限时的标准处理方式：https://platform.openai.com/docs/guides/compaction
- OpenAI Codex agent loop 文档说明 tool output 会进入后续模型回合；这使单次大工具输出成为直接的 prompt-growth 风险：https://openai.com/index/unrolling-the-codex-agent-loop/
- OpenAI prompt caching 文档暴露 `cached_input_tokens`；当 `input_tokens` 很高而 cached 部分很低时，可以把它作为 cache miss / fresh input 高水位证据：https://openai.com/index/api-prompt-caching/
- Anthropic tool-context 文档把 tool result 清理和上下文管理作为 agent/tool-use 运行时问题，支持对过期或过大的工具结果做 trimming：https://platform.claude.com/docs/en/agents-and-tools/tool-use/manage-tool-context
- `Lost in the Middle` 论文指出长上下文模型在使用长输入中间位置的信息时会下降，说明“能放下”不等于“应该整包放入”：https://arxiv.org/abs/2307.03172
- `RULER` 论文把 nominal context window 与 effective context length 区分开，进一步支持不要只靠窗口大小容纳长 transcript：https://arxiv.org/abs/2404.06654

## 影响

- 当用户感觉 harness 对话变重，或 stage compression 前，可以运行 `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`。
- OPEN-10 首轮 triage 已完成：`AGENTS.md`、current status 和 `$repo-governed-coding` description 已瘦身；后续再次持续 warning 时，按 `--使用细节/上下文预算OPEN-10使用细节.md` 重新判断。
- Context budget audit 仍然是手动体检，不接 Stop hook，不触发自动 compact 或自动归档。
- 脚本退出码仍为 0，除非配置文件无法解析。
- Runtime token budget audit 默认也是手动 transcript 体检；无 `--transcript` 时只证明脚本和 CI wiring 可用，不读取本机历史会话。

## 关联文档

- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [Harness Remaining Work](../harness-open-items.md)
- [ADR-010 Context Surface Layering](./ADR-010-context-surface-layering.md)
- [ADR-013 Project Skill Lifecycle](./ADR-013-project-skill-lifecycle.md)
- [Runtime Token Budget](../../../.agents/skills/harness-maintenance/references/runtime-token-budget.md)
- [上下文预算 OPEN-10 使用细节](/Volumes/usd/codes/go_projects/ai_ms_pro/--使用细节/上下文预算OPEN-10使用细节.md)
