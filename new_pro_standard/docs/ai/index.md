# AI 文档入口索引

更新时间：YYYY-MM-DD
当前状态：待导入首个真实场景
当前阶段：STAGE-00

## 入口说明

本文档是 `docs/ai/` 的稳定路由层，面向 AI 与人类执行者。

这里只保留共享治理控制面的默认入口，不在这里重复展开完整阶段目录。

`.codex/runtime/` 下的 session 与 observation 文件属于本地 runtime harness，不纳入默认共享阅读面，也不作为项目共享真相。

## 默认阅读顺序

1. [项目规则 AGENTS.md](../../AGENTS.md)
2. [当前工作上下文](./working-context.md)
3. [需求文档入口索引](../requirements/index.md)
4. [项目计划](./plan.md)
5. [Harness 可迁移清单](./harness-portability-guide.md)
6. [新项目 AGENTS 改写指南](./new-project-agents-rewrite-guide.md)
7. [传统项目接入 Harness 的标准起手式](./traditional-project-harness-kickoff.md)

## 默认治理控制面

- [项目规则 AGENTS.md](../../AGENTS.md)
- [当前工作上下文](./working-context.md)
- [需求文档入口索引](../requirements/index.md)
- [项目计划](./plan.md)
- [Harness 可迁移清单](./harness-portability-guide.md)
- [handoffs/active](./handoffs/active)
- [status](./status)
- [changelog](./changelog)
- [adr](./adr)
- 默认 active handoff 预算：`<=5`。超过预算时优先压缩到 `status` 或归档，而不是继续扩张默认恢复面。

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
