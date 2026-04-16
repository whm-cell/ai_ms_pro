# Requirement / Workstream 元数据约定

更新时间：2026-04-16
编号：ADR-004
标题：在 runtime 与治理文档中统一引用 Requirement IDs / Workstream IDs
状态：已采纳

## 背景

- 项目已经建立 `docs/requirements/` 体系，用于管理 `REQDOC`、`REQ` 和 `WS` 的来源与追踪关系。
- 当前 runtime session、observation reducer、handoff 和 status 已形成多层治理链，但还缺少统一的需求追踪元数据位点。
- 如果 AI 侧文档不引用 `REQ-XXX` / `WS-XX`，后续真实需求导入后会出现“代码推进了，但难以追溯到具体需求”的问题。
- 如果 AI 侧自己发明或漂移这些 ID，又会破坏 `docs/requirements/traceability-matrix.md` 的单一来源地位。

## 决策

- 项目统一使用 `Requirement IDs` 和 `Workstream IDs` 作为 AI 侧任务文档的追踪元数据。
- 以下文档类型默认应包含这组元数据：
  - `docs/ai/handoffs/active/*.md`
  - `docs/ai/status/*.md`
  - `.codex/runtime/sessions/*.md`
  - observation reducer 生成的 handoff 草稿
- 当任务已经绑定到需求或工作流时，必须填写真实的 `REQ-XXX` / `WS-XX`。
- 当任务尚未绑定时，明确写 `未绑定`，不允许编造 ID。
- `docs/requirements/traceability-matrix.md` 与相关 workstream 文档仍然是 canonical mapping；AI 侧文档只引用并同步该映射，不单独定义另一套真相。

## 备选方案

- 方案 A：仅在 `docs/requirements/` 中记录 `REQ` / `WS`，AI 侧文档不带任何追踪元数据
- 方案 B：让 handoff/status/session 自由写文本说明，不使用统一的 ID 字段
- 方案 C：让 runtime hook 自动推断并写死 requirement/workstream 绑定

## 决策理由

- 方案 A 会导致执行文档和需求文档脱节，后续阶段难以追踪“这个 handoff 对应哪组需求”。
- 方案 B 缺少稳定字段，无法被脚本、检查器或后续 reducer 可靠读取。
- 方案 C 自动化过强，但当前 hook payload 并没有可靠的 requirement/workstream 语义来源，容易写出错误绑定。
- 使用统一字段并允许显式写 `未绑定`，既能保留追踪位点，也能避免伪精确。
- 把 canonical mapping 继续留在 `docs/requirements/`，可以保持 repo-first 的单一来源和审计边界。

## 影响

- handoff、status、runtime session 模板和 observation reducer 输出都需要包含 `Requirement IDs` / `Workstream IDs`。
- 后续真实需求导入后，主 Agent 需要在 AI 侧文档与 `traceability-matrix.md` 之间同步这些字段。
- 若未来引入更强校验，可在此基础上检查 AI 侧元数据与 `traceability-matrix.md` 是否一致。
- runtime 层只记录被显式传入或环境中提供的 IDs；如果没有可靠绑定，继续写 `未绑定`

## 关联文档

- [项目规则 AGENTS.md](/Volumes/usd/codes/go_projects/ai_ms_pro/AGENTS.md)
- [需求文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/index.md)
- [需求追踪矩阵](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/traceability-matrix.md)
- [ADR-002 Session 到 Handoff 的提升规则](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-002-session-to-handoff-promotion.md)
- [ADR-003 Observation Reducer 顺序](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-003-observation-reducer-order.md)
