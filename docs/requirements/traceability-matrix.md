# 需求追踪矩阵

更新时间：2026-05-21
当前状态：已建立四个真实场景追踪；WS-01 Three.js Snake 是当前 harness capability validation sample；WS-03 Godot browser slice 已退出 active validation；REQDOC-003 的 raw PRD evidence 已归并到 canonical source，WS-04 repo-native 游戏 MVP 已完成 smoke 验证

## 目的

本文件用于把原始需求文档、标准化需求、工作流、开发阶段和验证信息串联起来。

## 使用说明

- 每个原始需求文档应先有 `REQDOC-XX`
- 标准化后拆成 `REQ-XXX`
- 开发侧按 `WS-XX` 工作流组织
- 阶段执行按 `STAGE-XX` 推进
- `docs/ai/` 下的 `handoff`、`status`、runtime reducer 草稿若引用了 `REQ-XXX` / `WS-XX`，应与本矩阵保持一致

## 矩阵

| 原始文档 | 标准化需求 | 工作流 | 开发阶段 | 当前状态 | 验收/测试 |
| --- | --- | --- | --- | --- | --- |
| REQDOC-001 | REQ-001 | WS-01 | STAGE-00 | 已完成 | `python3 scripts/threejs_snake_smoke.py` 已覆盖 `load -> eat -> game over -> restart`；`python3 scripts/threejs_snake_blackbox_smoke.py` 覆盖真实页面 load -> keyboard turn -> game over -> Enter restart |
| REQDOC-001 | REQ-002 | WS-01 | STAGE-00 | 已完成 | Three.js 场景可见，包含分数/提示等基础反馈；deterministic smoke 与黑盒 smoke 已共同验证 HUD 与玩法主链路 |
| REQDOC-001 | REQ-003 | WS-01 | STAGE-00 | 已完成 | requirements -> implementation -> handoff/status 链路完成一次真实验证；governance checker 已校验 `working-context` 当前 stage 与 matrix 中 REQ/WS/STAGE 的一致性 |
| REQDOC-002 | REQ-004 | WS-02 | STAGE-00 | 已完成 | `apps/harness-trace-console/` 已直接读取 `working-context`、stage status 与 `traceability-matrix`，展示当前阶段、摘要卡片和活跃队列 |
| REQDOC-002 | REQ-005 | WS-02 | STAGE-00 | 已完成 | 控制台支持按 `stage/workstream/status/search` 过滤 traceability，并可查看单条 requirement 详情 |
| REQDOC-002 | REQ-006 | WS-02 | STAGE-00 | 已完成 | `python3 scripts/harness_trace_console_smoke.py` 已验证 load -> WS-02 filter -> REQ-006 search；runtime hooks 与 reducer 已用显式 metadata 跑通一次 |
| REQDOC-003 | REQ-007 | WS-03 | STAGE-00 | 历史完成；非 active validation | WS-03 曾用 repo-native browser slice 验证 move/jump -> freeze -> throw -> combo/rank -> clear enemies -> unlock exit -> complete 的玩法反馈闭环；当前 Godot slice 已从 active worktree / CI 移除，Godot 工程仍未采纳 |
| REQDOC-003 | REQ-008 | WS-03 | STAGE-00 | 历史完成；非 active validation | WS-03 曾用 browser smoke 验证 load -> freeze -> throw -> combo/rank -> unlock exit -> complete -> reset；当前 blocking browser smoke 改由 WS-01 Three.js Snake 与 WS-02 Trace Console 承载 |
| REQDOC-003 | REQ-009 | WS-03 | STAGE-00 | 已完成 | Godot 4.6.2、Compatibility renderer、GUT、导出 preset 等保持 proposed / 待确认；WS-03 历史 browser slice 不再作为当前 harness 验证样本；后续 Godot 需独立 engine spike / ADR / smoke |
| REQDOC-003 | REQ-010 | WS-04 | STAGE-01 | 已完成 | `apps/pixel-freeze-platformer/` 作为 repo-native 可玩 MVP；`scripts/pixel_freeze_platformer_smoke.py` 覆盖 load -> validate content -> controls -> clear level -> next level -> campaign complete -> locale/reset |
| REQDOC-003 | REQ-011 | WS-04 | STAGE-01 | 已完成 | MVP 关卡数据、敌人、道具和评级目标由 `validateContent()` 与 smoke 校验；后续 Godot JSON / Resource 迁移仍 proposed |
| REQDOC-003 | REQ-012 | WS-04 | STAGE-01 | 已完成 | MVP HUD、暂停、重开、本地保存和中英语言切换由 UI 与 smoke API 验证 |
| REQDOC-003 | REQ-013 | WS-04 | STAGE-01 | 已完成 | 当前只使用原创 canvas 占位视觉并记录素材/音频/AI/发布为后续 scope；验证方式为 code review / manual review |
