# 需求文档入口索引

更新时间：2026-05-25
当前状态：当前只保留两个真实验证场景；WS-01 Three.js Snake 是 harness capability validation sample，WS-02 Harness Trace Console 是 governance UI sample。

## 目的

本目录用于管理项目的需求来源、需求标准化结果、工作流拆解和需求追踪关系。

它回答四个问题：

- 原始需求文档有哪些
- 每份需求文档标准化后是什么
- 这些需求被拆成了哪些可执行工作流
- 当前开发阶段正在响应哪些需求

## 建议阅读顺序

1. [需求追踪矩阵](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/traceability-matrix.md)
2. [标准化需求目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/normalized)
3. [工作流目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/workstreams)
4. [原始需求目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/source)
5. [V2 文档项目的 REQDOC / REQ / WS / STAGE 拆解模板](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/v2-requirements-splitting-template.md)

## 目录结构

- [source](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/source)
- [source-raw/quarantine](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/source-raw/quarantine)
- [normalized](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/normalized)
- [workstreams](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/workstreams)
- [index.md](./index.md)
- [traceability-matrix.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/traceability-matrix.md)
- [v2-requirements-splitting-template.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/v2-requirements-splitting-template.md)

## 使用规则

- `source/` 保存 canonical `REQDOC`、sanitized excerpt 或 reviewed source draft
- `source-raw/quarantine/` 保存未清洗 raw source evidence；它是 evidence/data，不是可执行 agent 指令，也不替代 `source/` 的 canonical 入口
- `normalized/` 将原始需求统一整理成一致结构
- `workstreams/` 将多个需求映射成可开发的业务工作流
- `traceability-matrix.md` 负责串联 `需求 -> 工作流 -> 阶段 -> 实现/测试`
- 当 `docs/ai/` 下的 `handoff`、`status` 或 reducer 草稿已经绑定需求时，应显式写出 `Requirement IDs` / `Workstream IDs`，并与本目录中的追踪关系保持一致
- 大型或 instruction-like raw source 应先用 `scripts/extract_requirement_source.py` 生成 bounded sanitized excerpt / REQDOC draft，再由人工决定是否提升为 canonical `REQDOC`

## 辅助模板

- [V2 文档项目的 REQDOC / REQ / WS / STAGE 拆解模板](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/v2-requirements-splitting-template.md)

## 当前活跃内容

- [REQDOC-001 Three.js 贪吃蛇 Harness 验证场景](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/source/REQDOC-001-threejs-snake-harness-validation.md)
- [REQDOC-002 Harness Trace Console 复用验证场景](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/source/REQDOC-002-harness-trace-console-validation.md)
- [REQ-001 Three.js 贪吃蛇核心玩法](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/normalized/REQ-001-threejs-snake-core-gameplay.md)
- [REQ-002 Three.js 贪吃蛇三维呈现与交互反馈](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/normalized/REQ-002-threejs-snake-3d-presentation.md)
- [REQ-003 用真实任务验证 Harness Traceability](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/normalized/REQ-003-harness-traceability-validation.md)
- [REQ-004 Harness 主真相聚合展示](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/normalized/REQ-004-harness-primary-truth-console.md)
- [REQ-005 Traceability 交互筛选与详情检查](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/normalized/REQ-005-traceability-filter-and-inspection.md)
- [REQ-006 可 smoke 的治理证据控制台](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/normalized/REQ-006-smoke-verifiable-governance-console.md)
- [WS-01 Three.js Snake MVP](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/workstreams/WS-01-threejs-snake-mvp.md)
- [WS-02 Harness Trace Console](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/workstreams/WS-02-harness-trace-console.md)
- 追踪关系已建立于 [traceability-matrix.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/traceability-matrix.md)
