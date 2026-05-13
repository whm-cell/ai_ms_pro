# Stage-01 Game MVP Development Status

更新时间：2026-05-10
阶段：stage-01
状态：阶段完成

## 需求与工作流标识

- Requirement IDs：REQ-010, REQ-011, REQ-012, REQ-013
- Workstream IDs：WS-04
- 本阶段承接 REQDOC-003 / `prd_game.md`，以 repo-native 浏览器 MVP 验证 2D 平台闯关游戏的可玩闭环。

## 当前阶段目标

- 把原始 PRD 的“移动/跳跃 -> 冻结 -> 投掷连锁 -> 清场出口 -> 结算评级”落成可打开、可操作、可 smoke 的浏览器 MVP。
- 保留 Godot 4.6.2、GUT、导出 preset、正式素材、音频、移动端和发布流水线为后续独立 spike / workstream。
- 用 WS-04 再次验证 requirements -> implementation -> smoke -> governance docs 的 harness 闭环。

## 当前完成度

- 已完成：`apps/pixel-freeze-platformer/` 三关 MVP、数据驱动关卡、敌人/道具/评级、HUD、暂停/重开、localStorage 进度、中英本地化种子和 smoke-only 测试 API。
- 已完成：`scripts/pixel_freeze_platformer_smoke.py` 覆盖 load -> validate content -> controls -> clear level -> next level -> campaign complete -> locale/reset。
- 已完成：REQDOC-003 raw evidence attachment、REQ-010/011/012/013、WS-04 和 traceability matrix 已同步。
- 未纳入：完整 Godot 工程、Boss、正式美术音频、移动端触控深调、商店发布和 AI 素材生产流水线。

## 本阶段关键成果

- WS-04 从 WS-03 的薄切片升级为多关卡可玩 MVP，包含三关、至少三类敌人、多类道具、连锁计分、评级和本地进度。
- smoke API 仅在 `?smoke=1` 下暴露，普通页面保留用户向入口。
- `validateContent()` 能返回 requirement/workstream metadata、关卡数量、敌人/道具类型、本地化数量和原创占位素材边界。
- requirements checker 已支持 raw PRD evidence attachment，不再把 `prd_game.md` 误判为第二份 canonical REQDOC。

## 风险与阻塞

- 本阶段完成的是浏览器 MVP，不证明 Godot engine、GUT、导出模板、移动端、正式素材或商业发布能力。
- `pytest` 在当前系统 Python 和 repo-local venv 中不可用；requirements shape 相关单测需用 `unittest` 或先安装测试依赖。
- `scripts/check_requirements_shape.py` 仍有既有 code-shape warning：文件行数超过 350，后续维护时应拆分。

## 下一阶段重点

- 若继续产品化，先决策是否启动 Godot engine spike，并用 ADR 明确 Godot 版本、目录结构、导出和 smoke 策略。
- 若继续浏览器 MVP，优先补 Boss/精英战、触控输入、正式资源管线或更多关卡前，先拆新的 REQ/WS。
- 将 WS-04 smoke 接入 CI 需要按 team PR / workflow touch-set 边界另起变更。

## 验收判断

- STAGE-01 的 repo-native MVP 验收已达到：用户可打开页面玩三关，smoke 能验证内容、控制、通关、进度、本地化和重置链路。
- 未完成项属于明确排除或后续 scope，不阻塞 WS-04 当前 MVP 完成判断。

## 关联文档

- [项目计划](../plan.md)
- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [WS-04 Pixel Freeze Platformer MVP](../../requirements/workstreams/WS-04-pixel-freeze-platformer-mvp.md)
- [需求追踪矩阵](../../requirements/traceability-matrix.md)
