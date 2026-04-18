# 工作流：Harness Trace Console

更新时间：2026-04-18
工作流编号：WS-02
工作流名称：Harness Trace Console
状态来源：当前完成度与验收证据以 `docs/requirements/traceability-matrix.md`、阶段 `status` 和相关 `handoff` 为准

## 使用边界

- 本文件只保留工作流目标、覆盖需求、阶段建议和验收模型。
- 当前状态、最新验证结论和 smoke 证据不在这里重复承载，避免与主真相文档漂移。

## 业务目标

- 用第二个 repo-native 垂直场景证明当前 harness 不只适用于 `WS-01`，而是能在新场景中复用 requirements、implementation、runtime 和 governance 链路。

## 覆盖需求

- REQ-004：Harness 主真相聚合展示
- REQ-005：Traceability 交互筛选与详情检查
- REQ-006：可 smoke 的治理证据控制台

## 主要模块

- `docs/ai/` 的 `working-context` 与阶段 `status`
- `docs/requirements/traceability-matrix.md`
- `apps/harness-trace-console/`
- `scripts/harness_trace_console_smoke.py`
- `.codex/runtime/` hooks 与 `scripts/reduce_runtime_observations.py`

## 阶段拆分建议

- STAGE-00：落地零构建控制台、完成 deterministic smoke，并用显式 metadata 跑一次 runtime hook/reducer
- STAGE-01：增加 metadata consistency 提示或 projection freshness 可视化
- STAGE-02：接入 CI、导出报告或更强的多 workstream 浏览能力

## 验收重点

- 页面是否直接消费 primary truth surface，而不是自造平行状态
- 筛选与详情检查是否足以定位 requirement/workstream 证据
- deterministic smoke 和 runtime promotion 是否都能在 `WS-02` 上跑通

## 风险与依赖

- 控制台解析依赖当前 Markdown 结构，后续文档格式变动需要同步维护
- runtime metadata 的自动携带仍依赖调用方传入，尚未形成零配置约束

## 关联文档

- 需求追踪矩阵：[traceability-matrix.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/traceability-matrix.md)
- 当前阶段 `status`：[Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
- 相关 `handoff`：
  - [Harness Trace Console Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-harness-trace-console.md)
