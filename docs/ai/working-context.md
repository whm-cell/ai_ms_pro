# 当前工作上下文

更新时间：2026-06-03
当前阶段：STAGE-00 Runtime Harness Foundation
当前模式：Codex-first harness + bounded runtime capability

## 作用

只保留下一次会话立即需要继承的当前真相；长期细节在 `status`、`handoff`、ADR、requirements 或 changelog。

## 同步元数据

- Current Stage: STAGE-00
- Active Status Source: docs/ai/status/stage-00-runtime-harness-foundation.md
- Active Handoff Sources: docs/ai/handoffs/active/stage-00-harness-burn-in-closeout.md
- Requirement IDs: REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006
- Workstream IDs: WS-01, WS-02
- Last Synced From: status,handoff,manual
- Last Synced At: 2026-06-03

## 当前主目标

- Stage-00 从 harness closeout 转向 capability 增量建设，但三层边界不变：runtime 本地恢复、governance 共享真相、verification 漂移检测。
- 当前新增能力只限 `runtime durability`、`bounded observability / interop`、`task-quality eval`。
- 2026-06-03 capability artifacts 已进入结构化 state / evidence / aggregate 指标层。
- Active validation 仍只有 WS-01 Three.js Snake 与 WS-02 Harness Trace Console。
- `new_pro_standard` 只同步 starter-safe 机制，不复制本 repo 的 REQ/WS、accepted samples、runtime artifacts 或 demo apps。

## 当前活跃队列

1. 收敛 canonical change surface，避免 `.codex/runtime/*` 被当成共享 truth。
2. 压缩 context / ADR 预算，保持默认阅读链路短。
3. 只用真实 bounded evidence 补 cross-task resume、remote interop、高影响动作和 guardrail 样本。
4. 独立处理 legacy code-shape 大文件，不扩大 harness 产品边界。

## 当前风险与阻塞

- GitHub private Free 下 main 保护 / ruleset 仍是 remote `UNKNOWN`。
- Agentic security / trace / sandbox / sample-gap 控制面只证明本地 bounded contract；不证明 hosted trace、native sandbox、MCP/A2A 或外部 collector。
- `GAP-TRACE-OTLP-PILOT-BURNIN` 只有 1 个 accepted local-interop sample；`verified_remote=0`。
- `GAP-RUNTIME-STAGE-CHECKPOINT-RESUME` 尚无 accepted cross-task resume sample；不能用 harness-hardening 任务补数。
- 高影响动作、runtime drift、guardrail samples、security triage 和 runtime token pressure 仍是 warning / review-required。

## 下一次会话先读

1. [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
2. [Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
3. [Stage-00 Harness Burn-in Closeout Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-harness-burn-in-closeout.md)
4. [需求追踪矩阵](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/traceability-matrix.md)

仅在真实样本事件或 sample-gap 审计时，再读 [Harness Real Sample Watchlist](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-real-sample-watchlist.md)。

## 最近已固化的决策

- Runtime files、full diff、transcript、source evidence 和 subagent output 都是 bounded/on-demand 输入；稳定结论必须提升到 docs / checks / ADR。
- Sample-gap 机制只记录真实 evidence 与 upgrade decisions；synthetic evidence 不得补 accepted real sample。
- Capability summary 是 artifact-backed local summary，只支持后续决策，不自动升级 blocking、remote 或 hosted capability claim。
- 2026-06-01 至 2026-06-03 已完成 capability bootstrap、tightening、state/evidence/aggregate 增强；边界仍是 local-first。

## 更新规则

- 只保留当前阶段仍有效的信息。
- 阶段切换或主目标变化时优先更新本文件。
- 过期细节进入 `status`、`adr`、`changelog` 或 archive，不继续堆在本文件。
