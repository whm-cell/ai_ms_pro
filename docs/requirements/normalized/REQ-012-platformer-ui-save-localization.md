# Platformer UI Save Localization

更新时间：2026-05-10
需求编号：REQ-012
来源文档：REQDOC-003
需求标题：MVP HUD、设置、存档与本地化种子
状态：已完成

## 背景

- 原始 PRD 把 HUD、暂停、设置、存档和本地化列为首发必要或强建议能力。
- 当前 MVP 不做商业发布，但需要证明这些系统可以从一开始进入 harness 验证面。

## 目标

- 在可玩 MVP 中提供最小 HUD、暂停/重开、设置、本地进度保存和中英本地化种子。
- 使 UI 状态和保存状态可被 smoke 验证。

## 范围

### 包含

- HUD 显示生命、分数、连击、倒计时、剩余敌人、当前关卡、出口和评级。
- 暂停、重开关卡、重置进度。
- 本地保存已解锁关卡、最佳分数、设置和语言。
- 简体中文 / English 两套最小 UI 文案。

### 不包含

- 完整字体资产、全量剧情文本、多语言 QA。
- 手柄焦点完整矩阵或移动端触控布局深度调优。
- 云存档。

## 验收条件

- 用户可在 UI 中切换语言、暂停、重开和重置进度。
- smoke 能验证语言切换和进度重置 API。
- traceability matrix 绑定 REQDOC-003、REQ-012 与 WS-04 / STAGE-01。

## 依赖与前置条件

- 依赖浏览器 `localStorage` 保存 MVP 进度、最高分和语言设置。
- 依赖 `apps/pixel-freeze-platformer/content.js` 中的 `STRINGS` 作为中英本地化种子。
- 不依赖云存档、正式字体资源、完整手柄焦点矩阵或移动端触控布局。

## 风险与待澄清项

- 本地化仅覆盖 MVP UI 字符串，不覆盖完整剧情、字体回退、换行 QA 或多语言发布流程。
- `localStorage` 在受限浏览器环境可能不可用；当前实现已容错但不提供跨设备同步。

## 技术假设

| Claim | Status | Verification Method |
| --- | --- | --- |
| MVP 使用 `localStorage` 保存本地进度和设置 | accepted | browser smoke 调用 reset / locale API 验证 |
| Godot 版本应迁移到 ConfigFile / FileAccess 或 TranslationServer | proposed | pending Godot engine spike |

## 关联工作流

- WS-04：Pixel Freeze Platformer MVP

## 关联阶段

- STAGE-01：Game MVP Development
