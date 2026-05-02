# Project Architecture / Style / Dependency Skill Lifecycle

更新时间：YYYY-MM-DD

适用范围：当项目架构、分层、样式规范、依赖选择或类似项目专属约束可能沉淀为 skill 时使用。

本模板是按需治理模板，不属于默认短链路。简单任务不需要读取它；0-1 阶段、架构变更、样式体系变更、依赖策略变更或创建/修改项目 skill 时再进入。

## 使用原则

- Skill 用来降低默认上下文，并按需加载项目执行指南。
- Skill 不替代 `AGENTS.md`、ADR、status、requirements 或 verification scripts。
- 早期项目规则应允许变化；只有经过真实任务验证后才进入稳定 skill 或 always-on 规则。
- 任何会长期改变架构、样式、依赖或交付策略的结论，都应提升到 ADR 或 stage `status`。

## 生命周期状态

| 状态 | 进入条件 | 存放位置 | 退出条件 |
| --- | --- | --- | --- |
| Draft | 尚未跑通首个垂直切片，约束仍在探索 | 当前任务、handoff 草稿、status 备注 | 首个切片证明这些规则会被重复使用，或被明确废弃 |
| Candidate Skill | 同类约束在多个任务中重复出现，但仍可能调整 | `.codex/skills/<project-skill>/SKILL.md` | 2-3 个非平凡任务验证有效，或出现冲突需要回退 |
| Stable Skill | 规则已稳定，适合按需复用 | repo-local skill + ADR/status 引用 | 需要所有任务默认遵守，或被新架构替代 |
| Promote | 规则成为长期默认治理或可验证约束 | `AGENTS.md`、ADR、checks、requirements | 已进入 always-on 规则或自动检查 |
| Deprecate | 规则被新证据、新需求或新架构替代 | status/ADR 记录，旧 skill 归档或标记废弃 | 旧入口不再被默认引用 |

## Candidate Skill 必填内容

- `description`：只描述触发场景，避免过长导致默认 skill metadata 变厚。
- `Current Status`：`Draft`、`Candidate`、`Stable`、`Deprecated`。
- `Scope`：适用目录、模块、技术栈或工作流。
- `Default Rules`：当前建议遵守的架构、样式或依赖约束。
- `Escape Hatch`：允许偏离的条件，以及偏离后必须写入的 ADR/status/handoff。
- `Evidence`：哪些真实任务、smoke、review 或实现验证过这些规则。
- `Promotion Rule`：何时升级到 `AGENTS.md`、ADR、requirements 或 check。
- `Deprecation Rule`：何时停止使用，如何避免新旧 skill 并存冲突。

## Escape Hatch

当出现以下任一情况时，允许偏离当前 skill：

- 新需求与现有架构约束冲突。
- 性能、安全、可维护性或用户体验证据推翻旧约束。
- 依赖生态、平台限制或部署条件发生变化。
- 旧 skill 会阻止更简单、更直接的实现。

偏离后必须选择一个共享真相位置记录原因：

- 单次任务影响：active `handoff`
- 当前阶段执行方式变化：stage `status`
- 长期架构、样式、依赖或交付策略变化：ADR
- 需求或验收口径变化：requirements / traceability 文档

## 不应该做

- 不要把尚未验证的项目想法直接写成 Stable Skill。
- 不要把 skill 当成绕过 `AGENTS.md` 或 governance check 的入口。
- 不要把当前阶段状态、最新验证日志或临时 TODO 写进 skill。
- 不要保留两个互相冲突的 active skill；必须明确一个为当前有效入口。
