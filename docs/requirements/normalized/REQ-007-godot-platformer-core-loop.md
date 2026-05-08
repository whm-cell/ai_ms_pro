# Godot 2D 平台闯关核心玩法闭环

更新时间：2026-05-08
需求编号：REQ-007
来源文档：REQDOC-003
需求标题：Godot 2D 平台闯关核心玩法闭环
状态：已完成

## 背景

- REQDOC-003 提出一个受单屏街机平台动作启发的原创 2D 闯关游戏。
- 为避免完整 Godot 工程、素材、导出和本地化一次性扩大上下文，本需求只抽取最小可验收玩法闭环。

## 目标

- 验证 “移动与跳跃 -> 冻结敌人 -> 投掷清屏 -> 出口解锁 -> 结算” 是否能作为后续业务 workstream 的核心闭环。

## 范围

### 包含

- 单屏平台场景。
- 玩家左右移动、跳跃、冻结、投掷。
- 至少 2 个敌人可进入冻结态并被投掷清除。
- 清屏后出口解锁。
- 分数、连击、评级、剩余敌人、出口状态和完成状态可见。

### 不包含

- 正式 Godot 工程。
- 9 关 MVP、Boss、存档、本地化、素材生产、音效和发布导出。
- 移动端、联机、排行榜或完整商业级内容。

## 验收条件

- 用户可在浏览器切片中完成核心闭环。
- smoke 可用稳定测试 API 验证冻结、投掷、连击计分、清屏、出口解锁、评级与完成状态。
- traceability matrix 绑定 REQDOC-003、REQ-007、WS-03 与 STAGE-00。

## 依赖与前置条件

- 使用 repo-native 静态浏览器切片作为首轮 spike，不要求本机安装 Godot。
- 后续若采纳 Godot，需要另行建立 engine spike、导出脚本和 Godot 专项 smoke。

## 风险与待澄清项

- Godot 4.6.2、Compatibility renderer、GUT、导出 preset 等仍是 proposed 状态；验证方式：后续 Godot engine spike / smoke 与 ADR 采纳，不因本浏览器切片自动变成已采纳架构事实。
- 玩法手感只能通过后续 Godot spike 或真实 Godot 工程进一步验证。

## 关联工作流

- WS-03：Godot Platformer First Slice

## 关联阶段

- STAGE-00：真实场景验证与治理固化
