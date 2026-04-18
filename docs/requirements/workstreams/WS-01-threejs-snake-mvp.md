# 工作流：Three.js Snake MVP

更新时间：2026-04-18
工作流编号：WS-01
工作流名称：Three.js Snake MVP
状态来源：当前完成度与验收证据以 `docs/requirements/traceability-matrix.md`、阶段 `status` 和相关 `handoff` 为准

## 使用边界

- 本文件只保留工作流目标、覆盖需求、阶段建议和验收模型。
- 当前状态、最新验证结论和 smoke 证据不在这里重复承载，避免与主真相文档漂移。

## 业务目标

- 用一个真实可玩的 Three.js 贪吃蛇场景验证当前 Codex-first harness 是否能支撑需求追踪、实现落地与阶段压缩

## 覆盖需求

- REQ-001：Three.js 贪吃蛇核心玩法
- REQ-002：Three.js 贪吃蛇三维呈现与交互反馈
- REQ-003：用真实任务验证 Harness Traceability

## 主要模块

- `docs/requirements/` 需求与追踪层
- `apps/threejs-snake/` 场景实现层
- `docs/ai/` 的 handoff/status/working-context 治理层
- `.codex/runtime/` 的 session / observation / reducer 验证层

## 阶段拆分建议

- STAGE-00：导入 requirements、建立 traceability、完成 Three.js Snake MVP 首个垂直切片
- STAGE-01：基于真实 observation 数据验证 reducer 压缩阈值，并收紧 metadata/traceability 校验
- STAGE-02：补 CI 或更强一致性检查，并按需要扩展玩法/表现

## 验收重点

- 游戏是否可运行且可玩
- requirement/workstream metadata 是否能贯穿 handoff/status/session/reducer
- requirements 与 docs/ai 文档是否能保持同步

## 风险与依赖

- 当前仓库没有既有前端脚手架，应用接入方式需要保持足够轻量
- traceability 只有在实现和文档都同时更新时才有验证意义

## 关联文档

- 需求追踪矩阵：[traceability-matrix.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/traceability-matrix.md)
- 当前阶段 `status`：[Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
- 相关 `handoff`：
  - [Three.js Snake MVP Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-threejs-snake-mvp.md)
  - [Requirement Workstream Metadata Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-requirement-workstream-metadata.md)
