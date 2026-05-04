# AI 文档入口索引

更新时间：YYYY-MM-DD
当前状态：待导入首个真实场景
当前阶段：STAGE-00

## 入口说明

本文档是 `docs/ai/` 的稳定路由层，面向 AI 与人类执行者。

这里只保留共享治理控制面的默认入口，不在这里重复展开完整阶段目录。

`.codex/runtime/` 下的 session 与 observation 文件属于本地 runtime harness，不纳入默认共享阅读面，也不作为项目共享真相。

## 默认短链路

1. [项目规则 AGENTS.md](../../AGENTS.md)
2. [当前工作上下文](./working-context.md)

任务进入哪个更深入口，由 `AGENTS.md` 的 Task Discovery Protocol 判断。简单任务默认停在短链路；requirements、plan、handoff、ADR 与 archive 都是按需入口。

用户通常不需要手动标注任务类型。`按简单任务处理`、`按复杂任务处理`、`这是 0-1 阶段任务`、`不要读 archive`、`需要深挖历史` 只是可选覆盖指令，用来纠正或收窄 Agent 的默认判断。

## 按需深入入口

- [需求文档入口索引](../requirements/index.md)：需求驱动、traceability 或 0-1 stage 任务再进入
- [项目计划](./plan.md)：阶段目标、范围与验收框架需要确认时再进入
- [Harness 可迁移清单](./harness-portability-guide.md)
- [新项目 AGENTS 改写指南](./new-project-agents-rewrite-guide.md)
- [传统项目接入 Harness 的标准起手式](./traditional-project-harness-kickoff.md)
- [Project Skill Lifecycle Template](./templates/project-skill-lifecycle.md)：创建或调整 architecture/style/dependency skill 时再进入
- [Candidate Skill Eval Protocol](./skill-evals/README.md)：评估 Candidate skill with/without 样本时再进入
- `$progressive-feature-development`：非平凡功能、跨模块、API / storage / architecture、测试策略变化或显式 plan-first 任务再调用
- `$prd-to-project-skills`：PRD / requirements / workstream / ADR / 实现样本中出现稳定项目开发模式时再调用
- `scripts/check_context_budget.py`：默认上下文变重、stage compression 前或 skill/rule 膨胀排查时手动运行
- [handoffs/active](./handoffs/active)
- [status](./status)
- [changelog](./changelog)
- [adr](./adr)
- 默认 active handoff 预算由 `.codex/harness.toml` 的 `context_surface.active_handoff_budget` 控制，初始值为 `5`。达到预算时优先压缩到 `status` 或归档，而不是继续扩张默认恢复面。

## 当前阶段占位

- 暂无阶段 `status`
- 暂无活跃 `handoff`
- 暂无阶段 `changelog`
- 暂无正式 `adr`

## 活跃目录

- [handoffs/active](./handoffs/active)
- [status](./status)
- [changelog](./changelog)
- [adr](./adr)

## 归档入口

- [handoffs/archive](./handoffs/archive)
- [archive](./archive)

## 维护规则

- 本文件只做稳定路由，不维护第二套“当前阶段总表”或“下一次会话先读”的完整展开版。
- 新增或归档 `handoff`、`status`、`changelog`、`adr` 后，更新这里的稳定入口与占位状态。
- 当某个完成型 `handoff` 已被 `status` 或 `adr` 吸收且不再有默认恢复价值时，将其移入 `handoffs/archive`。
- 本地 runtime harness 文件不应加入本索引。
