# Session 到 Handoff 的提升规则

更新时间：2026-04-16
编号：ADR-002
标题：Runtime Session 到共享 Handoff 的提升规则
状态：已采纳

## 背景

- 项目已经引入 `.codex/runtime/sessions/` 作为本地 runtime harness 的会话恢复层。
- runtime session 文件只服务于本地恢复，不是 repo 内共享真相。
- 如果没有明确的提升规则，session 内容会长期停留在本地层，导致下一位 Agent 仍然无法只依赖仓库文档接力。
- 当前仓库的 canonical 接力面仍然是 `docs/ai/handoffs/active/*.md`。

## 决策

- 项目采用 “session 作为本地原料，handoff 作为共享交付物” 的分层规则。
- `.codex/runtime/sessions/_template.md` 作为 runtime session 的最小结构模板。
- 当 session 满足下列任一条件时，必须提升为 `handoff`：
  - 一个子任务已经完成
  - 任务被暂停且后续需要继续
  - 本次 session 产生了会影响下一位 Agent 判断的实现变化
  - 本次 session 形成了应被默认继承的有效路线、无效路线或关键风险
  - 本次 session 触发了需求、阶段或长期决策层面的共享更新
- 当 session 只包含局部探索、个人提示尝试、或没有 repo 级共享价值的临时过程时，可以停留在 runtime 层，不必提升为 `handoff`。
- canonical 的 `handoff` 由主 Agent 最终发布到 `docs/ai/handoffs/active/*.md`。
- subagent 可以返回 session 记录或 handoff 草稿，但不直接定义共享文档的最终版本。

## 备选方案

- 方案 A：所有 session 一律提升为 `handoff`
- 方案 B：只保留 runtime session，不维护 `handoff`
- 方案 C：让 hook 自动把 runtime session 直接改写成 `handoff`

## 决策理由

- 方案 A 会导致 `handoff` 文档膨胀，把大量本地恢复材料误升格为共享真相。
- 方案 B 会让项目治理过度依赖本地状态，不利于多 Agent 接力和 repo 内审计。
- 方案 C 无法稳定判断语义边界，例如“是否已形成共享结论”“是否需要压缩到 status 或 ADR”，且在并发场景下更容易造成文档覆盖。
- 当前决策保留了 runtime 层的轻量恢复能力，同时继续让 `handoff -> status -> adr/changelog` 作为共享治理链路。

## 影响

- `.codex/runtime/sessions/` 下的文件应优先使用模板结构，减少后续提炼成本。
- 主 Agent 在结束前需要显式判断：当前 session 是否已经触发 handoff 提升条件。
- 后续如果实现自动化 runtime hooks，也应只生成 session 原料，而不是跳过提升判断直接改写共享 handoff。
- `handoff` 模板中的“有效路线 / 无效路线 / 候选路线”成为 session 提升时的默认映射字段。

## 关联文档

- [项目规则 AGENTS.md](/Volumes/usd/codes/go_projects/ai_ms_pro/AGENTS.md)
- [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
- [ADR-001 Harness 分层决策](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-001-harness-layering.md)
- [Runtime Session 模板](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/runtime/sessions/_template.md)
- [Handoff 模板](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/_template.md)
