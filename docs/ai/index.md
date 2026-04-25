# AI 文档入口索引

更新时间：2026-04-25
当前状态：Stage-00 已补齐 starter 机制层同步；默认治理面进一步收敛为“稳定路由 + working-context 同步元数据”
当前阶段：STAGE-00 真实场景验证与治理固化

## 入口说明

本文件是 `docs/ai/` 的稳定路由层，面向 AI 与人类执行者。

本索引只覆盖 repo 内共享真相。

`.codex/runtime/` 下的 session 与 observation 文件属于本地 runtime harness，不纳入这里的默认阅读顺序，也不作为项目主真相。

使用规则：

1. 开启新一轮工作时，先读本文件
2. 只保留稳定入口，不在这里重复展开完整阶段目录
3. 当前精确的 active status / handoff 绑定以 `working-context.md` 的同步元数据为准，阶段压缩结论以 `status` 为准

## 默认阅读顺序

1. [项目规则 AGENTS.md](/Volumes/usd/codes/go_projects/ai_ms_pro/AGENTS.md)
2. [当前工作上下文](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)
3. [需求文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/index.md)
4. [项目计划](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/plan.md)
5. [Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
6. [Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md)
7. [当前活跃 handoff 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active)
8. [ADR 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr)

## 默认治理控制面

- [当前工作上下文](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)
- [Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
- [Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md)
- [当前活跃 handoff 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active)
- [已归档 handoff 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/archive)
- [当前 Changelog 目录](./changelog)
- [ADR 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr)
- [需求文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/index.md)
- 当前 active handoff 默认预算：`5`。超过时应优先压缩/归档，而不是继续扩展默认入口面。

## 当前阶段锚点

- 当前 stage status：[Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
- 当前 hardening backlog：[Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md)
- 当前 active handoff 精确集合：以 [当前工作上下文](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md) 的 `## 同步元数据` 为准
- 最新 changelog：[2026-04-25 Harness Starter Sync And Surface Trim](./changelog/2026-04-25-harness-starter-sync-and-surface-trim.md)

## 归档入口

- [handoffs/archive](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/archive)
- [archive](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/archive)

## 维护规则

- 本文件只做稳定路由，不维护完整阶段目录或第二套“下一次会话先读”
- active handoff / ADR 的精确当前集合，优先维护在 `working-context` 同步元数据与对应目录中，而不是在这里重复展开
- 新增或归档 `handoff`、`status`、`changelog`、`adr` 后，更新这里的稳定入口与阶段锚点
- 当 stage `status` 已吸收某个完成型 handoff 且其不再有默认 resume 价值时，将其移入 `handoffs/archive`
- 本地 runtime harness 文件不应加入本索引
