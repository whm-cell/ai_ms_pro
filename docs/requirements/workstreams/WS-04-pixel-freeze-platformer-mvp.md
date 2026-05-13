# Pixel Freeze Platformer MVP

更新时间：2026-05-10
工作流编号：WS-04
工作流名称：Pixel Freeze Platformer MVP
文档定位：projection document

## 使用边界

- 本文档只描述本轮 MVP 的范围、模块和验收模型。
- 当前完成态、最新 smoke 证据和阻塞默认以 `working-context`、stage status、changelog 和 traceability matrix 为准。
- 本轮不把原始 PRD 全文放进默认上下文；`prd_game.md` 只作为 REQDOC-003 的 raw evidence attachment。

## 业务目标

- 基于 REQDOC-003 / `prd_game.md` 的核心产品意图，开发一个可打开、可操作、可 smoke 的单人 2D 平台闯关 MVP。
- 从 WS-03 的浏览器薄切片升级到多关卡、数据驱动、可保存进度的可玩样本。

## 覆盖需求

- REQ-010：2D 平台闯关可玩 MVP 基线。
- REQ-011：核心玩法系统与数据驱动关卡。
- REQ-012：MVP HUD、设置、存档与本地化种子。
- REQ-013：素材、音频、AI 生产与发布边界。

## 主要模块

- `docs/requirements/source/prd_game.md`
- `docs/requirements/source/REQDOC-003-godot-platformer-prd.md`
- `docs/requirements/normalized/REQ-010-platformer-playable-mvp-baseline.md`
- `docs/requirements/normalized/REQ-011-platformer-core-systems-and-levels.md`
- `docs/requirements/normalized/REQ-012-platformer-ui-save-localization.md`
- `docs/requirements/normalized/REQ-013-platformer-production-boundary.md`
- `apps/pixel-freeze-platformer/`
- `scripts/pixel_freeze_platformer_smoke.py`

## 阶段拆分建议

- STAGE-01A：source evidence 归并、REQ/WS 拆分、traceability 修复。
- STAGE-01B：repo-native 可玩 MVP，实现三关、核心系统、UI、存档和本地化种子。
- STAGE-01C：smoke / schema / governance 验证，并更新 status/changelog。
- STAGE-01D 候选：确认本机或 CI 可运行 Godot 后，另起 Godot engine spike。

## 验收模型

- 用户可打开 `apps/pixel-freeze-platformer/` 操作角色并完成 3 个房间式关卡。
- smoke 可验证 `load -> validate content -> clear level -> score/rank -> next level -> campaign complete -> locale/reset`。
- requirements shape、AI governance、code shape 和 task-specific smoke 检查通过。
- 未进入当前实现的 Boss、正式素材、音频、移动端和 Godot 导出范围被明确保留到后续 workstream。

## 风险与依赖

- 本轮不验证 Godot engine、GUT 或 export preset；当前本机没有可用 `godot` / `godot4` 命令。
- 浏览器 MVP 验证产品闭环和 harness 接线，不等于最终商业发布工程。
- PRD 中的 AI 生产、音频、本地化和移动端建议仍需后续独立验收。

## 关联文档

- 需求追踪矩阵：/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/traceability-matrix.md
- 当前阶段 status：/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-01-game-mvp-development.md
