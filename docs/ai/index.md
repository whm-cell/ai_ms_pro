# AI 文档入口索引

更新时间：2026-05-26
当前阶段：STAGE-00 Runtime Harness Foundation
当前判断：harness 可用；stopped burn-in session 已进入 closeout / split 阶段；context budget 是 strict gate；当前 capability validation 只以 WS-01 Three.js Snake（含 pause/resume 与 reset-best smoke）和 WS-02 Harness Trace Console 为准。

## 入口说明

本文件只做稳定路由。默认阅读链路保持短：`AGENTS.md -> working-context -> current status`。
requirements、handoff、ADR、archive、skills、runtime JSONL 和完整 diff 都按任务需要再进入。

## 默认短链路

1. [项目规则 AGENTS.md](/Volumes/usd/codes/go_projects/ai_ms_pro/AGENTS.md)
2. [当前工作上下文](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)
3. [Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)

## 按需入口

- [需求入口](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/index.md)：REQ、WS、traceability 或 0-1 workstream 任务再进入。
- [Traceability Matrix](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/traceability-matrix.md)：核对 `REQDOC -> REQ -> WS -> STAGE -> 验收`。
- [项目计划](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/plan.md)：阶段目标、范围或验收框架不清时再进入。
- [Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md)：查看 OPEN 项和完成定义。
- [Harness Real Sample Watchlist](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-real-sample-watchlist.md)：真实样本缺口的事件触发清单；平时不要反复主动覆盖。
- [Stage Checkpoints](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/checkpoints/README.md)：长任务 resume 前的 bounded checkpoint artifact，按需进入。
- [Active Handoffs](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active)：resume、recovery 或相关 profile 需要时再进入。
- [ADR 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr)：长期决策背景需要时再进入。
- Checks：[Registry](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/check-registry.md)、[Burn-in Ledger](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/check-burn-in-ledger.md)：确认等级、CI 覆盖和 blocking-candidate 升级证据。
- [Supply Chain And Provenance Plan](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/security/supply-chain-provenance-plan.md)：security evidence。
- [Security Evidence Triage](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/security/security-evidence-triage.md)：Scorecard、CodeQL、SBOM、dependency review 和 secret scanning advisory 的 triage / SLO。
- [Agentic Control Matrix](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/security/agentic-control-matrix.md)：agentic security control 映射。
- [Remote Merge Gates Evidence](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/security/remote-merge-gates.md)：private Free plan limit、CI evidence 和 future gates。
- [Agent Harness Security](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/security/agent-harness-security.md)：runtime redaction、source boundary、action matrix 和 samples 入口。
- Agentic standards：[standards](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/standards)、[evals](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/evals/README.md)、[tool contracts](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/tool-contracts/README.md)、[security samples](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/security/agentic-red-team-samples.md)；具体 trace / sample / sandbox / task-profile 检查按 `$harness-maintenance` 选择。
- [Candidate Skill Usage Samples](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/skill-usage-samples.md)：评估 Candidate skill 证据时再进入。
- [Candidate Skill Eval Protocol](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/skill-evals/README.md)：写详细 eval 或升级复核时再进入。

## 按需 Skills

- `$harness-maintenance`：bootstrap、hooks、runtime reducer、session compression、GitHub guardrails、supply-chain evidence 或 code-shape。
- `$requirements-traceability-maintenance`：REQDOC / REQ / WS、traceability-matrix 或技术假设状态变化。
- `$progressive-feature-development`：非平凡功能、跨模块变更、测试策略变化或显式 plan-first 任务。
- `$prd-to-project-skills`：从 workstream / 实现样本中判断是否沉淀稳定项目 skill。
- `$team-pr-conflict-control`：多人或多 AI 并行 PR、touch-set overlap、CODEOWNERS、merge queue / `merge_group` readiness。

## 常用检查

- Core：`check_ai_governance.py`、`ruff check .codex/hooks scripts tests`、`check_code_shape.py --all`、`git diff --check`、`check_context_budget.py`。
- Game/static：`check_threejs_snake_contract.py`，其他 smoke 按当前 workstream/status 选择。
- Harness/sample/security：按 changed-file follow-up、[check registry](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/check-registry.md) 或 [verification commands](/Volumes/usd/codes/go_projects/ai_ms_pro/.agents/skills/harness-maintenance/references/verification-commands.md) 选择，不把完整命令矩阵放在默认索引。

## 当前锚点

- 当前 status：[Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
- 当前 hardening backlog：[Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md)
- 当前真实样本 watchlist：[Harness Real Sample Watchlist](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-real-sample-watchlist.md)
- 当前 burn-in closeout：[Stage-00 Harness Burn-in Closeout Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-harness-burn-in-closeout.md)
- 当前 active handoff 精确集合：以 [working-context](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md) 的同步元数据为准。
- 最新 ADR：[ADR-017 Trace Remote Interop Boundary](./adr/ADR-017-trace-remote-interop-boundary.md)
- 最新 changelog：[Runtime Compression And Bounded Tool Output](./changelog/2026-05-26-runtime-compression-bounded-output.md)。当前重点集中在 runtime tool-output token pressure、starter-safe harness 同步、sample-gap evidence、readiness / pending / upgrade-decision accounting、burn-in closeout、context-surface compression 与 trace / cascade boundary；完整逐项记录以 changelog 目录为准，不在默认索引重复展开。

## 维护规则

- 本文件不展开完整阶段目录，也不维护第二套“下一次会话先读”。
- 新增或归档 `handoff`、`status`、`changelog`、`adr` 后，只更新稳定入口和当前锚点。
- 本地 runtime harness 文件不加入本索引；需要时通过 reducer、handoff 或 status 摘要进入共享 truth。
