# Three.js Snake MVP Handoff

更新时间：2026-04-16
阶段：stage-00
任务：threejs-snake-mvp
状态：已完成

## 需求与工作流标识

- Requirement IDs：REQ-001, REQ-002, REQ-003
- Workstream IDs：WS-01
- 绑定关系已记录在 `docs/requirements/traceability-matrix.md`

## 本任务目标

- 在当前仓库中落一个真实可玩的 Three.js 贪吃蛇场景
- 用这个场景验证 `requirements -> implementation -> handoff/status` 的首条真实闭环
- 保持接入方式足够轻量，不先引入额外前端工具链

## 已完成内容

- 新增零构建静态应用 [apps/threejs-snake/index.html](/Volumes/usd/codes/go_projects/ai_ms_pro/apps/threejs-snake/index.html)、[style.css](/Volumes/usd/codes/go_projects/ai_ms_pro/apps/threejs-snake/style.css)、[main.js](/Volumes/usd/codes/go_projects/ai_ms_pro/apps/threejs-snake/main.js)
- 游戏已具备核心玩法：蛇按固定节奏移动、随机生成食物、吃到后增长并加分、撞墙/撞自己 game over、可通过按钮或 Enter 重开
- 游戏已具备最小三维表现：Three.js 场景、相机、基础光照、地面/网格、蛇与食物模型、HUD 和启动/失败 overlay
- 新增应用说明 [apps/threejs-snake/README.md](/Volumes/usd/codes/go_projects/ai_ms_pro/apps/threejs-snake/README.md)
- 已导入与该场景对应的 requirements / workstream / traceability 文档，并完成首轮 metadata 绑定
- 已进行基本验证：`node --check apps/threejs-snake/main.js` 通过；本地静态服务可打开页面；浏览器内可点击开始按钮并加载场景

## 修改文件

- [apps/threejs-snake/index.html](/Volumes/usd/codes/go_projects/ai_ms_pro/apps/threejs-snake/index.html)
- [apps/threejs-snake/style.css](/Volumes/usd/codes/go_projects/ai_ms_pro/apps/threejs-snake/style.css)
- [apps/threejs-snake/main.js](/Volumes/usd/codes/go_projects/ai_ms_pro/apps/threejs-snake/main.js)
- [apps/threejs-snake/README.md](/Volumes/usd/codes/go_projects/ai_ms_pro/apps/threejs-snake/README.md)
- [REQDOC-001-threejs-snake-harness-validation.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/source/REQDOC-001-threejs-snake-harness-validation.md)
- [REQ-001-threejs-snake-core-gameplay.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/normalized/REQ-001-threejs-snake-core-gameplay.md)
- [REQ-002-threejs-snake-3d-presentation.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/normalized/REQ-002-threejs-snake-3d-presentation.md)
- [REQ-003-harness-traceability-validation.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/normalized/REQ-003-harness-traceability-validation.md)
- [WS-01-threejs-snake-mvp.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/workstreams/WS-01-threejs-snake-mvp.md)

## 关键实现决策

- 应用以零构建静态方式接入，Three.js 通过 CDN ES module 加载，避免在首个真实场景中先引入新的包管理和构建复杂度
- 游戏视角采用俯视偏透视相机和基础灯光，优先保证可读性和可玩性，而不是追求复杂视觉效果
- 当前实现重点是桌面浏览器可玩的 MVP，用于验证 harness 和 traceability，而不是一次性完成产品化
- 要求与工作流绑定直接写入 handoff，保证这次实现不只是“做了个 demo”，而是进入 requirements 闭环

## 当前未完成项

- 尚未做更深入的浏览器自动化玩法验证，例如完整吃到食物和触发 game over 的自动 smoke test
- 尚未决定该场景后续是否会继续演化为更完整的前端样例或被归档为一次性验证案例
- 尚未接入部署或 CI 级前端校验

## 已知风险与注意事项

- 当前实现依赖 CDN 加载 Three.js，离线或受限网络环境下无法直接运行
- 当前浏览器验证已确认页面可打开和可开始，但没有完成全流程自动化玩法验证
- 当前仓库仍以 harness 骨架为主，应用目录只是首个真实垂直切片，不代表最终产品结构已定型

## 已验证有效的路线

- 先用轻量静态方式接入一个真实前端场景，比先引入完整工具链更适合验证 harness 本身
- 将 `REQ/WS` 绑定直接写进 handoff/status/session/reducer，能让这次实现真正进入 traceability 链路
- 选择贪吃蛇这类规则清晰的玩法，足以覆盖状态管理、渲染、交互和失败恢复等真实开发要素

## 已验证无效的路线

- 继续只做治理模板而不接入真实业务场景，无法证明当前 harness 在真实开发中可用
- 在首个验证任务里就引入完整构建链和复杂工程化，会让“验证 harness”这个目标失焦
- 只实现代码而不补 requirements / traceability / handoff/status，会让这次场景失去验证链路价值

## 尚未尝试但建议的路线

- 为游戏补一个更完整的浏览器 smoke test，至少覆盖开始、移动、得分变化或失败后的重开
- 若后续继续扩展前端样例，可评估是否引入构建工具，并把该决策升级为新的 ADR
- 以本次 `WS-01` 为样板，再导入第二个真实 workstream，验证 harness 的可复用性

## 下一位 Agent 的第一步动作

- 先打开 [apps/threejs-snake/README.md](/Volumes/usd/codes/go_projects/ai_ms_pro/apps/threejs-snake/README.md) 跑起页面，再根据 [Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md) 判断是继续补测试，还是推进下一个真实 workstream

## 建议同步更新

- 已同步 `docs/requirements/traceability-matrix.md`
- 已同步 `docs/ai/status/stage-00-runtime-harness-foundation.md`
- 检查 [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
