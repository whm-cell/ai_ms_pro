# AI 文档入口索引

更新时间：2026-04-22
当前状态：Stage-00 已完成两个真实 workstream 验证；默认治理面已收敛为“轻量入口 + 小规模 active handoff”
当前阶段：STAGE-00 真实场景验证与治理固化

## 入口说明

本文件是 `docs/ai/` 的稳定路由层，面向 AI 与人类执行者。

本索引只覆盖 repo 内共享真相。

`.codex/runtime/` 下的 session 与 observation 文件属于本地 runtime harness，不纳入这里的默认阅读顺序，也不作为项目主真相。

使用规则：

1. 开启新一轮工作时，先读本文件
2. 只保留稳定入口，不在这里重复展开完整阶段目录
3. 当前增量真相以 `working-context.md` 为准，阶段压缩结论以 `status` 为准

## 默认阅读顺序

1. [项目规则 AGENTS.md](/Volumes/usd/codes/go_projects/ai_ms_pro/AGENTS.md)
2. [当前工作上下文](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)
3. [需求文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/index.md)
4. [项目计划](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/plan.md)
5. [Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
6. [Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md)
7. [当前活跃 handoff 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active)
8. [ADR 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr)

## 当前控制面

- [当前工作上下文](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)
- [Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
- [Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md)
- [当前活跃 handoff 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active)
- [已归档 handoff 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/archive)
- [ADR 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr)
- [需求文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/index.md)
- 当前 active handoff 默认预算：`5`。超过时应优先压缩/归档，而不是继续扩展默认入口面。

## 当前活跃 Handoff

- [Governance Surface Slimming Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-governance-surface-slimming.md)
- [Runtime Hooks Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-runtime-stop-session.md)
- [Observation Reducer Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-observation-reducer.md)
- [Harness Portability Template Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-harness-portability-template.md)
- [New Repo Rehearsal Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-new-repo-rehearsal.md)

## 当前 ADR 文档

- [ADR-001 Harness 分层决策](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-001-harness-layering.md)
- [ADR-002 Session 到 Handoff 的提升规则](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-002-session-to-handoff-promotion.md)
- [ADR-003 Observation Reducer 顺序](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-003-observation-reducer-order.md)
- [ADR-004 Requirement Workstream Metadata](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-004-requirement-workstream-metadata.md)
- [ADR-005 Projection Surface Freshness Boundary](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-005-projection-surface-freshness.md)
- [ADR-006 Harness 可迁移性与 Bootstrap 决策](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-006-harness-portability-bootstrap.md)
- [ADR-007 Governance Surface Budget](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-007-governance-surface-budget.md)
- [ADR-008 Cross-Platform Hooks And Code Shape Budget](./adr/ADR-008-cross-platform-hooks-and-code-shape.md)

## 当前 Changelog

- [2026-04-24 Harness Portability Hardening](./changelog/2026-04-24-harness-portability-hardening.md)

## 归档入口

- [handoffs/archive](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/archive)
- [archive](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/archive)

## 维护规则

- 本文件只做稳定路由，不维护完整阶段目录或第二套“下一次会话先读”
- 新增或归档 `handoff`、`status`、`changelog`、`adr` 后，更新这里的稳定入口
- 当 stage `status` 已吸收某个完成型 handoff 且其不再有默认 resume 价值时，将其移入 `handoffs/archive`
- 本地 runtime harness 文件不应加入本索引
