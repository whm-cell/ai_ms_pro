# Godot PRD 首轮切片 Smoke 验证

更新时间：2026-05-21
需求编号：REQ-008
来源文档：REQDOC-003
需求标题：Godot PRD 首轮切片 Smoke 验证
状态：历史完成；当前不作为 active validation

## 背景

- REQDOC-003 的完整范围较大，若没有自动化验证，业务样本容易让 harness 失去可恢复性。
- Stage-00 的既有模式要求每个 repo-native 垂直切片都有可重复 smoke 入口。

## 目标

- 为 REQDOC-003 的首轮业务样本建立最小自动化验证，证明新增切片不是纯文档样例。

## 范围

### 包含

- 历史 smoke 自动启动静态服务器并打开 repo-native Godot browser slice。
- 历史 smoke 验证初始状态、冻结、投掷、连击计分、出口解锁、评级、完成与重置。
- 当前 Godot browser slice 和 smoke 脚本已退出 active validation；blocking browser smoke 由 WS-01 Three.js Snake 与 WS-02 Trace Console 承载。

### 不包含

- Godot headless、GUT、export preset 或构建产物。
- 性能基准、截图对比和多浏览器矩阵。

## 验收条件

- 历史 WS-03 smoke 曾覆盖 combo/rank 反馈。
- 需求追踪矩阵记录 WS-03 为历史完成 / 非 active validation，并记录当前 active smoke 边界。

## 依赖与前置条件

- 当前不再依赖 Godot browser slice smoke；若后续恢复 Godot 验证，需要新建 engine spike / ADR / smoke。

## 风险与待澄清项

- 浏览器 smoke 只能证明首轮玩法闭环和 harness 接线，不证明 Godot 引擎工程可构建。
- 后续 Godot 工程进入 repo 时，需要新增 Godot 专项验证命令。

## 关联工作流

- WS-03：Godot Platformer First Slice

## 关联阶段

- STAGE-00：真实场景验证与治理固化
