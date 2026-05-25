# Godot Platformer First Slice

更新时间：2026-05-21
工作流编号：WS-03
工作流名称：Godot Platformer First Slice
文档定位：projection document

## 使用边界

- 本文档只保留 workflow 目标、覆盖需求、阶段建议与验收模型。
- 不重复当前完成态、最新验证结果或 smoke 证据。
- 当前执行状态默认以 `working-context`、`handoff`、`status` 与 `traceability-matrix.md` 为准。
- 本 workflow 是历史薄切片 evidence；Godot browser slice 已退出 active validation，当前能力验证回到 WS-01 Three.js Snake。

## 业务目标

- 基于 REQDOC-003 建立首个可运行、可 smoke 的业务切片，验证核心平台闯关循环能被 harness 追踪和压缩。
- 保持 root repo 的 harness 研究定位，不在本轮引入完整 Godot 工程。

## 覆盖需求

- REQ-007：Godot 2D 平台闯关核心玩法闭环。
- REQ-008：Godot PRD 首轮切片 Smoke 验证。
- REQ-009：Godot PRD 技术边界与业务范围。

## 主要模块

- `docs/requirements/source/REQDOC-003-godot-platformer-prd.md`
- `docs/requirements/normalized/REQ-007-godot-platformer-core-loop.md`
- `docs/requirements/normalized/REQ-008-godot-platformer-smoke-verification.md`
- `docs/requirements/normalized/REQ-009-godot-platformer-technical-boundary.md`
- 历史实现证据：Godot browser slice app / smoke 已从 active worktree 与 CI 移除，不再作为当前模块。

## 阶段拆分建议

- STAGE-00：完成 repo-native 浏览器切片、smoke、traceability 和治理文档同步。
- STAGE-01 候选：若用户确认继续推进，再建立真实 Godot engine spike 和 Godot 专项 smoke。
- STAGE-02 候选：在 Godot spike 通过后，再考虑素材、本地化、存档和导出流水线。

## 验收模型

- 历史 browser slice 曾验证单屏平台闯关切片与 `load -> freeze -> throw -> combo/rank -> unlock exit -> complete -> reset`。
- 当前 active validation 不再要求打开 Godot browser slice；能力验证由 WS-01 Three.js Snake 和 WS-02 Trace Console 承载。
- requirements shape、AI governance 和 code shape 检查通过。
- REQDOC-003 不再停留在 source-only 未绑定状态。

## 风险与依赖

- 当前切片验证的是玩法与 harness，不验证 Godot 工程能力。
- 若下一阶段进入 Godot，需要确认 Godot 版本、工程路径、测试插件、导出平台和 CI runner 能力。
- PRD 中的素材、音频和本地化生产建议仍是候选范围，不进入首轮实现。

## 关联文档

- 需求追踪矩阵：/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/traceability-matrix.md
- 当前阶段 `status`：/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md
- 相关 `handoff`：本轮完成后由 status / changelog 吸收，不新增 active handoff
