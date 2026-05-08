# Projection Surface Freshness Boundary

更新时间：2026-04-18
编号：ADR-005
标题：收缩 plan 与 workstream 的当前状态承载面，并只对显式状态字段做 freshness 校验
状态：已归档；当前上下文面规则由 ADR-010、ADR-011、ADR-014 承接

## 背景

- 项目已形成 `working-context`、active `handoff`、`status`、`adr`、`traceability-matrix` 等多层共享文档面。
- 最近一次 `WS-01` 真实场景落地后，主真相文档已更新，但 `plan.md` 与 `workstream` 仍保留了部分容易过期的状态性句子。
- 现有校验脚本主要覆盖结构完整性、入口链接、`working-context` 新鲜度和治理实现漏更，不覆盖 projection 文档与 primary truth 之间的 freshness 依赖。
- 如果继续让 `plan` 与 `workstream` 自由承载当前状态，就需要维护更复杂的依赖图；如果不先划清边界，文档漂移会反复出现。

## 决策

- `docs/ai/working-context.md`、active `handoff`、`status`、`adr`、`docs/requirements/normalized/*.md`、`docs/requirements/traceability-matrix.md` 继续作为 primary truth。
- `docs/ai/plan.md` 与 `docs/requirements/workstreams/*.md` 定位为 projection surface，只承载稳定结构：
  - 目标
  - 范围
  - 阶段建议
  - 验收模型
- `plan` 与 `workstream` 默认不重复承载以下内容：
  - 当前完成度
  - 最新验证结论
  - smoke / test 证据
  - 阶段实时状态判断
- 如果 projection 文档中仍显式出现这类状态字段，verification 只对这些显式字段做 freshness 校验，不做自由文本语义推断。

## 备选方案

- 方案 A：继续让 `plan` 与 `workstream` 自由记录当前状态，再为它们补全面 freshness 依赖图
- 方案 B：把所有状态都压进 `working-context`，弱化 `status`、`handoff`、`traceability-matrix`
- 方案 C：让 hook 或 reducer 自动回写 projection 文档，保持表面同步

## 决策理由

- 方案 A 理论上可行，但会把 verification 复杂度抬得很高，还会引入大量文案级误报。
- 方案 B 会让 `working-context` 过载，也会削弱 `status`、`handoff` 和 requirements-side canonical mapping 的职责边界。
- 方案 C 仍然依赖自动化去判断语义层面的“当前状态是否应该投影出来”，风险和维护成本都偏高。
- 让 projection 文档回到更稳定的职责面，再只对显式状态字段做最小 freshness 检查，能用最低复杂度解决当前 drift 问题。
- 该决策与 ECC 的简化思路一致：减少 repo 内重复承载“当前状态”的文档面，把当前真相集中在更少、更清晰的 surface 上。

## 影响

- `docs/ai/plan.md` 需要显式声明自己的使用边界，并移除易过期的当前状态表述。
- `docs/requirements/workstreams/*.md` 需要改成“状态来源”链接，而不是自己维护完成态和验证证据。
- `scripts/check_ai_governance.py` 会新增 projection freshness 规则，但仅针对显式状态字段，不尝试理解自然语言状态句子。
- `scripts/check_ai_doc_quality.py` 会要求 `plan` 和 `workstream` 声明使用边界，避免后续回到隐式约定。
- 后续若确实需要某个 projection 文档携带状态字段，必须接受它进入 freshness 依赖校验范围。

## 关联文档

- [项目规则 AGENTS.md](/Volumes/usd/codes/go_projects/ai_ms_pro/AGENTS.md)
- [项目计划](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/plan.md)
- [当前工作上下文](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)
- [需求追踪矩阵](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/traceability-matrix.md)
- [工作流：Three.js Snake MVP](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/workstreams/WS-01-threejs-snake-mvp.md)
