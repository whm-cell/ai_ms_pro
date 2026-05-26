# 当前工作上下文

更新时间：2026-05-26
当前阶段：STAGE-00 Runtime Harness Foundation
当前模式：Codex-first harness + Three.js capability sample + sample-gap advisory

## 作用

只保留下一次会话立即需要继承的当前真相；长期细节在 `status`、`handoff`、ADR、requirements 或 changelog。

## 同步元数据

- Current Stage: STAGE-00
- Active Status Source: docs/ai/status/stage-00-runtime-harness-foundation.md
- Active Handoff Sources:
  - docs/ai/handoffs/active/stage-00-harness-burn-in-closeout.md
- Requirement IDs: REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006
- Workstream IDs: WS-01, WS-02
- Last Synced From: status,handoff,manual
- Last Synced At: 2026-05-26

## 当前主目标

- Stage-00 主线是 harness closeout / split；不要继续扩大业务、hooks、CI、apps 或 sample collectors，除非任务明确要求。
- 当前 active validation sample 只有 WS-01 Three.js Snake（contract/browser smoke、pause/resume、reset-best）和 WS-02 Harness Trace Console（traceability 读取、筛选、详情）。
- `AGENTS.md` 保持 always-on 触发与边界；细则由 skills、references、templates 和 checks 承接，`.agents/skills` 不替代 canonical docs / checks。
- `new_pro_standard` 只同步 starter-safe 机制层；当前 repo 的 REQ/WS、accepted samples、runtime artifacts 和 demo apps 不复制。

## 当前活跃队列

1. 按 `stage-00-harness-burn-in-closeout.md` 拆分 review / stage / commit，先收敛 stopped burn-in session。
2. 真实样本采集走 `docs/ai/harness-real-sample-watchlist.md` 的 event-driven 触发；不要制造 synthetic evidence 或反复跑 readiness/planner 追不存在的场景。
3. 后续 PR 填写 `REQ/WS`、touch-set、overlap、verification 和 governance impact；多人 / 多 AI PR 用 `$team-pr-conflict-control`。

## 当前风险与阻塞

- GitHub private Free 下 main 保护 / ruleset 仍是 remote `UNKNOWN`；不得声明 required checks、review 或禁直推已强制。
- Candidate workflow skills 仍保持 Candidate；WS-01 simple-skip 达到 2/2 后已记录 keep-advisory，仍需要 cross-workstream / negative 样本。
- Agentic security / trace / sandbox / sample-gap 控制面只证明本地 bounded contract；不证明 secret scanning、远端审计、native/OpenAI sandbox、MCP/A2A、外部 OTLP 或 hosted trace。
- `GAP-TRACE-OTLP-PILOT-BURNIN` 只有 1 个 accepted local-interop sample；真实远端 collector / hosted trace 仍未完成。
- Source-boundary / control-matrix 均已有 2/2 keep-advisory；runtime drift、高影响动作、guardrail samples、security triage 和 runtime token pressure 仍是 warning/review-required，升级阻断需另做决策。
- Code-shape 主债务已清掉；context budget 已拆分 default surface、skill catalog、raw source 和 static task packet，继续用 checker 守住。
- starter/bootstrap 只初始化机制，不决定业务 truth；新项目仍需人工改写 `AGENTS.md` 和初始 REQ/WS。

## 下一次会话先读

1. [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
2. [Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
3. [Stage-00 Harness Burn-in Closeout Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-harness-burn-in-closeout.md)
4. [需求追踪矩阵](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/traceability-matrix.md)

仅在遇到真实样本事件或要做 sample-gap 审计时，再读 [Harness Real Sample Watchlist](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-real-sample-watchlist.md)。

## 最近已固化的决策

- 三层 harness 和 truth boundary 不变：runtime 是本地恢复材料，governance docs 是共享真相，verification scripts/hooks 做漂移检测；hooks 不自动改 canonical docs。
- 当前 truth 默认在 `working-context`、active `handoff`、stage `status` 和 `traceability-matrix`；`plan/workstream` 是 projection surface，按 Task Discovery profile 扩面。
- Skills、source evidence、subagents、full diff、transcript/runtime JSONL 都走 bounded/on-demand；`AGENTS.md` 保持轻量，长期规则见 ADR-010/011/014/015 和 check registry。
- Sample-gap 机制只记录真实 evidence 与 upgrade decisions；ready gaps 先走 `review-upgrade-decision`，不能用 synthetic evidence 补数。
- WS-01 / WS-02 是当前唯一 active capability validation boundary；WS-01 simple-skip 样本达到 2/2 后仍按 keep-advisory 处理。
- 2026-05-26 starter sync 与 bounded tool-output/runtime compression 已落地：starter 只拿机制，root 保留项目 truth；`capture_tool_output.py` 保留 raw artifact、摘要有界，Stop token-pressure 只写 runtime-only draft，仍 warning-only。

## 更新规则

- 只保留当前阶段仍然有效的信息
- 当阶段切换或主目标变化时优先更新本文件
- 过期信息应进入 `status`、`adr` 或归档，而不是继续堆在本文件里
