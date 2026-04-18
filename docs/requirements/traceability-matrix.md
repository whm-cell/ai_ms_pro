# 需求追踪矩阵

更新时间：2026-04-18
当前状态：已建立首个真实场景追踪

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
| REQDOC-001 | REQ-001 | WS-01 | STAGE-00 | 已完成 | `python3 scripts/threejs_snake_smoke.py` 已覆盖 `load -> eat -> game over -> restart` |
| REQDOC-001 | REQ-002 | WS-01 | STAGE-00 | 已完成 | Three.js 场景可见，包含分数/提示等基础反馈；smoke 已验证 HUD 与玩法主链路 |
| REQDOC-001 | REQ-003 | WS-01 | STAGE-00 | 已完成 | requirements -> implementation -> handoff/status 链路完成一次真实验证，且治理检查继续通过 |
