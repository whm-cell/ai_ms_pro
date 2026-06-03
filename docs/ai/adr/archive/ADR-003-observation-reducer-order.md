# Observation Reducer 的 Handoff 优先顺序

更新时间：2026-04-16
编号：ADR-003
标题：Runtime Observation Reducer 先产出 Handoff 草稿
状态：已归档；当前规则由 `$harness-maintenance` runtime governance compression reference 与 reducer/checks 承接

## 背景

- 项目已经引入 `.codex/runtime/observations/*.jsonl` 作为本地 runtime observation 原料。
- observation 是 append-only 的 Stop hook 产物，适合保留原始线索，但不适合作为 canonical 项目记忆直接发布。
- 如果没有 reducer，observation 只能停留在本地层，无法形成稳定的共享接力面。
- 如果 reducer 直接生成 `status` 或 `ADR`，容易把尚未稳定的局部线索过早提升为长期真相。

## 决策

- 项目采用 “observations 先归纳为 handoff 草稿，再决定是否压缩到 status 或 ADR” 的顺序。
- 默认 reducer 入口为显式脚本 [reduce_runtime_observations.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/reduce_runtime_observations.py)，而不是 lifecycle hook 自动发布共享文档。
- reducer 的默认目标是生成 handoff-compatible 草稿结构，供主 Agent 审核后决定是否发布为 canonical `docs/ai/handoffs/active/*.md` 文档。
- 只有当 observation 线索已经跨 session 稳定重复出现，或已经被主 Agent 判断为阶段/长期结论时，才继续提升到 `status` 或 `ADR`
- reducer 可以帮助识别共享层文件、重复 prompt 线索和 promotion reason，但这些结果仍然是候选，不直接替代语义判断。

## 备选方案

- 方案 A：不做 reducer，只保留 observation 原料
- 方案 B：让 hook 自动把 observations 直接改写为 canonical handoff
- 方案 C：让 reducer 直接产出 `status` 或 `ADR`

## 决策理由

- 方案 A 无法形成闭环，observation 会长期停留在本地层，下一位 Agent 仍然需要自己重新整理。
- 方案 B 自动化更强，但会越过主 Agent 的语义判断边界，不适合当前 repo-first 治理模型。
- 方案 C 容易把短期、局部、噪音较大的 observation 过早提升为长期真相。
- handoff-first 能保留任务上下文和接力结构，同时继续遵守现有的 `handoff -> status -> adr/changelog` 压缩链路。
- 显式 reducer 脚本便于后续引入 requirement/workstream metadata、去重规则和阶段压缩规则，而不必修改 hook 的默认职责边界。

## 影响

- `.codex/runtime/observations/` 的 append-only 原料将通过显式脚本提炼，而不是由 hook 自动发布共享文档。
- 主 Agent 需要在需要共享时运行 reducer、审查草稿，并决定是否落地 canonical handoff。
- `status` 与 `ADR` 的形成继续建立在主 Agent 审核和稳定重复性判断之上，不直接从单次 observation 自动升级。
- 后续若需要把 reducer 产物接入 requirements、workstream 或 CI，可以在 handoff-first 路径上继续扩展，而不破坏当前分层。

## 关联文档

- [项目规则 AGENTS.md](/Volumes/usd/codes/go_projects/ai_ms_pro/AGENTS.md)
- [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
- [ADR-001 Harness 分层决策](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-001-harness-layering.md)
- [ADR-002 Session 到 Handoff 的提升规则](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/archive/ADR-002-session-to-handoff-promotion.md)
- [Runtime Observations README](/Volumes/usd/codes/go_projects/ai_ms_pro/.codex/runtime/observations/README.md)
- [Observation Reducer 脚本](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/reduce_runtime_observations.py)
