# Platformer Production Boundary

更新时间：2026-05-10
需求编号：REQ-013
来源文档：REQDOC-003
需求标题：素材、音频、AI 生产与发布边界
状态：已完成

## 背景

- 原始 PRD 包含 AI 图像、音频 cue sheet、本地化、移动端和发布流水线建议。
- 这些内容会显著扩大工程和外部依赖，不能因为 PRD 提到就自动视为当前已完成目标。

## 目标

- 明确当前 MVP 的生产边界：只落可审查的数据、占位视觉、占位反馈和验证入口。
- 将正式素材、音频、AI 生产流水线、Godot 导出和移动端发布保留为后续 workstream。

## 范围

### 包含

- 使用原创占位视觉和 UI，不复刻参考作品角色、地图或道具表达。
- 记录 AI/音频/素材流水线为 future scope，不把未审校生成物纳入最终资产。
- smoke 和文档明确当前验证的是产品闭环与 harness，不验证商业发布能力。

### 不包含

- AI 图像/音频生成脚本。
- 正式 sprite sheet、BGM/SFX、商店素材、Android/iOS/Steam 导出。
- 版权或法务审查结论。

## 验收条件

- MVP 仅使用原创占位视觉和文本。
- WS-04 文档列出未进入当前实现的 PRD 内容。
- traceability matrix 绑定 REQDOC-003、REQ-013 与 WS-04 / STAGE-01。

## 依赖与前置条件

- 依赖 code review / manual review 确认当前视觉为 canvas 原创占位绘制，而非导入正式或第三方素材。
- 依赖 requirements / workstream 明确记录 Godot、AI 图像、音频和发布流水线仍在后续范围。
- 后续如引入生成式素材，需要独立记录来源、审校状态和可发布边界。

## 风险与待澄清项

- 当前结论不是版权或法务审查结论，只是工程范围和素材来源边界。
- 正式商用素材、音频、移动端包体和商店发布仍需要单独验收。

## 技术假设

| Claim | Status | Verification Method |
| --- | --- | --- |
| 当前 MVP 的资产为原创占位实现，不构成最终商用素材 | accepted | code review / manual review |
| AI 图像、音频和发布流水线需要独立 workstream | deferred | pending future REQ / WS split |

## 关联工作流

- WS-04：Pixel Freeze Platformer MVP

## 关联阶段

- STAGE-01：Game MVP Development
