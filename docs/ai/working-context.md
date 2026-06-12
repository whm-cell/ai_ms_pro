# 当前工作上下文

更新时间：2026-06-12
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
- Last Synced At: 2026-06-12

## 当前主目标

- Stage-00 从 harness closeout 转向 capability 增量建设，但三层边界不变：runtime 本地恢复、governance 共享真相、verification 漂移检测。
- 当前新增能力只限 `runtime durability`、`bounded observability / interop`、`task-quality eval` 和支撑性 advisory guardrails。
- 2026-06-06 已把五个 harness 反哺点落成 bounded 小切片：remote loopback hardening、CI agent contract、local execution policy wrapper、planner/executor/reviewer schema sample；cross-task resume 真实样本仍 open。
- 2026-06-07 source-backed external decisions 已入账；2026-06-08 已增加 evidence-backed default permission：证据充分且对当前 harness 正向时，bounded local/no-effect 小步默认许可，但四类外部运行面仍不声明完成。
- 2026-06-08 已从 `demo_txt_t_proto` 抽取 opt-in Prototype Design Brief / artifact review harness 机制；当前默认关闭，不复制目标项目业务 truth，不改变 active validation 范围。
- Active validation 仍只有 WS-01 Three.js Snake 与 WS-02 Harness Trace Console。
- `new_pro_standard` 只同步 starter-safe 机制，不复制本 repo 的 REQ/WS、accepted samples、runtime artifacts 或 demo apps。

## 当前活跃队列

1. 收敛 canonical change surface，避免 `.codex/runtime/*` 被当成共享 truth。
2. 压缩 context / ADR 预算，保持默认阅读链路短。
3. 只用真实 bounded evidence 补 cross-task resume、remote interop、高影响动作和 guardrail 样本；不能用 schema sample 或 local-only artifact 补数。
4. 独立处理 legacy code-shape 大文件，不扩大 harness 产品边界。

## 当前风险与阻塞

- GitHub private Free 下 main 保护 / ruleset 仍是 remote `UNKNOWN`。
- Agentic security / trace / sandbox / sample-gap 控制面只证明本地 bounded contract；不证明 hosted trace、native sandbox、MCP/A2A 或外部 collector。
- `GAP-TRACE-OTLP-PILOT-BURNIN` 只有 1 个 accepted local-interop sample；`verified_remote=0`。
- `GAP-RUNTIME-STAGE-CHECKPOINT-RESUME` 尚无 accepted cross-task resume sample；不能用 harness-hardening 任务补数。
- CI agent contract 与 local execution policy wrapper 都是 advisory / assistive，不创建真实 CI agent workflow，也不证明 native sandbox。
- Planner / executor / reviewer 目前只是 sample shape，不证明 scheduler runtime、A2A、hosted trace 或 red-team evidence。
- External harness decisions 只证明 source-backed operator-level choice 已入账；不证明 remote trace、hosted eval、native sandbox、MCP/A2A 或 CI agent runtime。
- `GAP-GUARDRAIL-CONFIRMATION` 已有 1 个 accepted real sample，但仍是 `needs-more-real-samples`，不能当成高影响动作覆盖完成。
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
- Task outcome eval command validation treats repo-local `.codex/.venv/bin/python` as an optional local interpreter entrypoint; CI must still validate referenced repo scripts/tests.
- External harness decision validation keeps the four previously manual choices source-backed, active, bounded, and default-permitted only for local/no-effect improvements; external effects still require explicit per-run confirmation.
- Prototype Design Brief validation is a disabled-by-default design projection gate; only enabled projects or slices get brief and artifact child checks in `check_ai_governance.py`.
- `.codex/hooks.json` uses the portable `.codex/hooks/run_hook.cmd` launcher; Windows routes to PowerShell and macOS / Linux routes to POSIX shell without host-specific resync.
- 2026-06-01 至 2026-06-06 已完成 capability bootstrap、tightening、state/evidence/aggregate 与 vnext advisory slices；边界仍是 local-first。

## 更新规则

- 只保留当前阶段仍有效的信息。
- 阶段切换或主目标变化时优先更新本文件。
- 过期细节进入 `status`、`adr`、`changelog` 或 archive，不继续堆在本文件。
