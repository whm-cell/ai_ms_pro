# Platformer Playable MVP Baseline

更新时间：2026-05-10
需求编号：REQ-010
来源文档：REQDOC-003
需求标题：2D 平台闯关可玩 MVP 基线
状态：已完成

## 背景

- 用户已要求基于 `prd_game.md` 原始 PRD 并结合 harness 进入实际游戏开发。
- 当前仓库没有可用 `godot` / `godot4` 命令，因此真实 Godot 工程验证仍不能声称已完成。
- 本需求先把 PRD 的产品闭环落成 repo-native 可玩 MVP，并保留后续 Godot engine spike 的技术边界。

## 目标

- 提供一个用户可打开、可操作、可重开、可完成多关流程的单人 2D 平台闯关 MVP。
- MVP 必须覆盖移动、跳跃、攻击冻结、投掷连锁、清场、出口、结算、失败与重试。

## 范围

### 包含

- 至少 3 个短房间式关卡。
- 玩家移动、跳跃、冻结攻击、投掷/滚动清敌。
- 生命、倒计时、分数、连击、评级、清屏出口和关卡推进。
- 可重复 smoke 的测试 API。

### 不包含

- 真实 Godot 工程、GUT、export preset 或导出模板。
- 完整 9 关/15 关商业内容。
- Boss 全量系统、正式美术音频、移动端发包或商店发布。

## 验收条件

- 用户可打开 MVP 应用并完整通关首批 3 关。
- smoke 覆盖 `load -> play/clear level -> score/rank -> next level -> campaign complete -> reset`。
- traceability matrix 绑定 REQDOC-003、REQ-010 与 WS-04 / STAGE-01。

## 依赖与前置条件

- 依赖 `apps/pixel-freeze-platformer/` 的无构建静态浏览器 MVP。
- 依赖 `scripts/pixel_freeze_platformer_smoke.py` 提供可重复主链路验证。
- 不依赖本机 Godot、GUT、导出模板或正式素材管线。

## 风险与待澄清项

- 浏览器 MVP 验证产品闭环和 harness 接线，不等于最终 Godot 工程或商业发布质量。
- 关卡手感、Boss、移动端输入和正式资源仍需后续独立 workstream 或 Godot spike 验证。

## 技术假设

| Claim | Status | Verification Method |
| --- | --- | --- |
| 当前阶段使用 repo-native browser MVP 验证产品闭环 | accepted | smoke test: `scripts/pixel_freeze_platformer_smoke.py` |
| Godot 4.6.2 / GUT / export preset 是后续 engine spike 候选 | deferred | pending Godot engine spike |

## 关联工作流

- WS-04：Pixel Freeze Platformer MVP

## 关联阶段

- STAGE-01：Game MVP Development
