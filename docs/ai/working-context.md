# 当前工作上下文

更新时间：2026-04-18
当前阶段：STAGE-00 真实场景验证与治理固化
当前模式：Codex-first harness engineering

## 作用

本文件只保留当前开发阶段最需要被下一次会话立即继承的真相。

它不是长期归档，不替代 `plan`、`status`、`handoff`、`adr`。

## 当前主目标

- 用 `WS-01 + WS-02` 证明当前 harness 已能支撑两个真实 repo-native 场景
- 保持 `docs/ai/` 与 `docs/requirements/` 的入口、模板、验证层一致
- 判断 Stage-00 是否已经完成“可用性验证”，以及还剩哪些 hardening 缺口

## 当前活跃队列

1. 判断 Stage-00 是否已满足“基础可用性已验证”，以及是否应进入下一阶段
2. 评估何时把治理检查接入 CI，并继续增加 metadata 与 traceability matrix 的一致性校验
3. 决定 `WS-01` 与 `WS-02` 哪些部分应该归档为样板，哪些继续演化
4. 用更真实的 observation 样本继续验证 reducer 压缩阈值

## 当前风险与阻塞

- 文档质量检查已上线，并已覆盖 `handoff` 模板中的有效/无效/候选路线结构；当前普通实现变更仍以 diff-aware warning 为主，但 `scripts/`、`.codex/hooks*`、`.githooks/` 等核心治理实现改动若未同步 `working-context` 或 `ADR`，已升级为阻断
- verification 层已新增 `working-context` 新鲜度 warning、活跃 `handoff` 堆积 warning 和 runtime session/observation staged 阻断；当前已接入 `Stop` 时的 runtime observation append-only 采集与 runtime session best-effort 自动写入，以及 `SessionStart / Resume` 时的最近 session 精简摘要读取
- `WS-01` 已具备 repo 内可复现的 deterministic smoke runner，能覆盖 `load -> eat -> game over -> restart`；但仍未覆盖自由输入路径、渲染质量、多尺寸和 CI 级自动执行
- `plan` 与 `workstream` 的 projection boundary 已明确，但 metadata 与 traceability matrix 的字段级一致性校验仍未自动化
- `WS-02` 已证明第二个 workstream 也能走通 runtime hook 与 reducer，但这次 metadata 仍通过显式环境变量传入，尚未证明任意调用方都能零配置带齐 IDs
- 当前两个 smoke 场景都偏 deterministic 行为验证，还未覆盖视觉回归或 CI 级长期稳定性

## 当前真实入口

- [项目规则 AGENTS.md](/Volumes/usd/codes/go_projects/ai_ms_pro/AGENTS.md)
- [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
- [需求文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/index.md)
- [项目计划](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/plan.md)
- [ADR-001 Harness 分层决策](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-001-harness-layering.md)
- [ADR-002 Session 到 Handoff 的提升规则](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-002-session-to-handoff-promotion.md)
- [ADR-003 Observation Reducer 顺序](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-003-observation-reducer-order.md)
- [ADR-004 Requirement Workstream Metadata](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-004-requirement-workstream-metadata.md)
- [ADR-005 Projection Surface Freshness Boundary](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-005-projection-surface-freshness.md)
- [Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
- [Three.js Snake MVP Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-threejs-snake-mvp.md)
- [Harness Trace Console Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-harness-trace-console.md)
- [Runtime Hooks Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-runtime-stop-session.md)
- [Observation Reducer Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-observation-reducer.md)
- [Requirement Workstream Metadata Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-requirement-workstream-metadata.md)
- [Projection Surface Freshness Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-projection-surface-freshness.md)

## 下一次会话先读

1. [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
2. [当前工作上下文](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)
3. [需求文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/index.md)
4. [项目计划](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/plan.md)
5. [ADR-001 Harness 分层决策](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-001-harness-layering.md)
6. [ADR-002 Session 到 Handoff 的提升规则](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-002-session-to-handoff-promotion.md)
7. [ADR-003 Observation Reducer 顺序](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-003-observation-reducer-order.md)
8. [ADR-004 Requirement Workstream Metadata](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-004-requirement-workstream-metadata.md)
9. [ADR-005 Projection Surface Freshness Boundary](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-005-projection-surface-freshness.md)
10. [Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
11. [Harness Trace Console Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-harness-trace-console.md)
12. [Projection Surface Freshness Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-projection-surface-freshness.md)
13. [Three.js Snake MVP Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-threejs-snake-mvp.md)
14. [Requirement Workstream Metadata Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-requirement-workstream-metadata.md)
15. [Observation Reducer Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-observation-reducer.md)
16. [Runtime Hooks Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-runtime-stop-session.md)

## 最近已固化的决策

- 项目采用 `AGENTS.md + Codex Stop hook + pre-commit + 脚本校验` 的治理方式
- 项目采用 `docs/requirements/` 与 `docs/ai/` 分层管理需求与执行上下文
- 新增 skill 的记录位置由 scope 决定，而不是全部写入 `AGENTS.md`
- 项目采用 `Runtime Harness + Governance Harness + Verification Harness` 的三层分工
- `.codex/runtime/` 只保存本地 session/observation 原料，不替代 `docs/ai/` 共享治理文档
- `handoff` 模板已强化为“任务结果 + 有效路线 + 无效路线 + 候选路线”的接力结构
- 治理脚本已新增 Phase-1 级 diff-aware warning，用于提示实现改动后未同步更新 `docs/ai/` 或 `docs/requirements/`
- 治理脚本已新增 runtime state 防误提交规则，并对 `working-context` 新鲜度和 `handoff -> status` 压缩节奏给出 warning
- 项目已定义 runtime session 最小模板，并已固化 “session 作为本地原料、handoff 作为共享交付物” 的提升规则
- Stop hook 分级策略已上线：普通实现变更缺文档更新时给 warning，核心治理实现变更缺 `working-context` 或 `ADR` 更新时直接失败
- `Stop` hook 已新增本地 runtime observation 采集能力，产物只追加到 `.codex/runtime/observations/*.jsonl`，用于后续 reducer 或手工提炼
- `Stop` hook 已新增本地 runtime session 快照写入能力，产物仅进入 `.codex/runtime/sessions/`，不会自动改写共享治理文档
- Observation reducer 已上线，默认顺序是 `observations -> handoff draft -> 主 Agent 审核 -> status/ADR`，并通过显式脚本而不是 hook 自动运行
- Requirement/workstream metadata 已进入 handoff、status、runtime session 和 reducer 输出；当前 canonical mapping 仍以 `docs/requirements/traceability-matrix.md` 为准
- `SessionStart` 恢复摘要在 session metadata 已知时，会一并带回 requirement/workstream 绑定，减少 resume 后的追踪断点
- Stage-00 已新增阶段级 status，用于压缩 `Runtime Hooks + Observation Reducer + Requirement Metadata` 的稳定成果
- `WS-01 / Three.js Snake MVP` 已完成首轮 requirements、implementation、handoff/status 闭环，证明当前 harness 可支撑真实场景
- `WS-01` 已新增 `python3 scripts/threejs_snake_smoke.py` 浏览器 smoke 入口，并通过 `?smoke=1` 下的 `window.__THREEJS_SNAKE_TEST__` namespaced API 提供低侵入、可重复的玩法断言
- `WS-02 / Harness Trace Console` 已完成第二个真实 workstream，且直接消费 `working-context`、stage `status` 与 `traceability-matrix` 这组 primary truth surface
- `WS-02` 已新增 `python3 scripts/harness_trace_console_smoke.py`，并通过 `?smoke=1` 下的 `window.__HARNESS_TRACE_CONSOLE_TEST__` namespaced API 验证加载、过滤、搜索与选择行为
- 已通过显式 `REQ-004~006 / WS-02` metadata 手工调用 Stop hooks 与 reducer，证明 runtime observation/session/reducer 在第二个 workstream 上也能贯穿
- repo-level smoke 已收紧 Playwright session 命名，避免在当前 macOS 环境中因 unix socket 路径截断导致本地重跑冲突
- 项目已明确 `plan/workstream` 作为 projection surface 的边界，当前完成度与验证证据默认集中到 `working-context`、`handoff`、`status`、`traceability-matrix`
- governance check 已新增 projection freshness 规则，但只针对显式状态字段，不做自由文本语义判断
- 当前 `working-context` 已与最新 stage status 对齐，后续应继续把新增治理能力优先回收到 primary truth surface
- 当前活跃 handoff 已扩展到 `Runtime Hooks + Observation Reducer + Requirement Metadata + Three.js Snake MVP + Projection Freshness + Harness Trace Console` 六个子任务；下一步应判断 Stage-00 是否可以压缩并进入下一阶段
- `SessionStart` hook 已新增最近 runtime session 摘要注入能力，会在 `startup|resume` 时 best-effort 提供本地恢复提示，但不会替代共享治理文档

## 更新规则

- 只保留当前阶段仍然有效的信息
- 当阶段切换或主目标变化时优先更新本文件
- 过期信息应进入 `status`、`adr` 或归档，而不是继续堆在本文件里
