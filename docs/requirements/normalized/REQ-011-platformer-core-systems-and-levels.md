# Platformer Core Systems And Levels

更新时间：2026-05-10
需求编号：REQ-011
来源文档：REQDOC-003
需求标题：核心玩法系统与数据驱动关卡
状态：已完成

## 背景

- 原始 PRD 强调“敌人状态机 + 可推动对象 + 连锁奖励 + 时间压力”四个支柱。
- MVP 需要比 WS-03 薄切片更接近真实游戏：多敌人类型、多关卡节奏、道具和可审查关卡数据。

## 目标

- 把核心战斗从脚本演示扩展为数据驱动关卡系统。
- 使关卡、敌人、道具、规则和评级目标可以被 smoke 和后续工具检查。

## 范围

### 包含

- 至少 3 类敌人行为：巡逻、跳跃/追击、飞行或护盾。
- 敌人状态：active / affected / packed / rolling / cleared。
- 关卡数据包含 id、名称、主题、时间、平台、敌人、道具、出口和评级目标。
- 道具至少覆盖攻击强化、跳跃/机动、防护或时间奖励中的 3 类。
- 连锁击倒影响分数、连击、评级或结算反馈。

### 不包含

- 程序化无尽生成。
- 复杂 Boss 行为树。
- 外部 AI 关卡生成服务接入。

## 验收条件

- MVP 的测试 API 能报告关卡 schema 校验结果。
- smoke 能确认 3 关数据存在，并能通过测试 API 清理至少一关敌人、解锁出口和进入下一关。
- traceability matrix 绑定 REQDOC-003、REQ-011 与 WS-04 / STAGE-01。

## 依赖与前置条件

- 依赖 `apps/pixel-freeze-platformer/content.js` 承载 MVP 关卡、敌人、道具和评级目标数据。
- 依赖 `window.__PIXEL_FREEZE_PLATFORMER_TEST__.validateContent()` 暴露可校验内容摘要。
- 后续迁移 Godot 时，需要把当前 JS 数据模型重新映射为 JSON / Resource / Scene 装配链。

## 风险与待澄清项

- 当前关卡数据足以验证三关 MVP，但还没有证明 9 关以上内容量、Boss 行为树或编辑器工作流。
- 敌人行为仍是浏览器 MVP 级简化实现，真实 Godot 物理和动画需另行验收。

## 技术假设

| Claim | Status | Verification Method |
| --- | --- | --- |
| 关卡数据先作为 JS module 固化，避免无构建静态应用的 local file fetch 限制 | accepted | browser smoke 加载应用并执行 `validateContent()` |
| 后续可迁移为 Godot JSON / Resource / Scene 三段式装配链 | proposed | pending Godot engine spike |

## 关联工作流

- WS-04：Pixel Freeze Platformer MVP

## 关联阶段

- STAGE-01：Game MVP Development
