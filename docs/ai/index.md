# AI 文档入口索引

更新时间：2026-04-18
当前状态：两个真实 workstream 已落地，且第二个场景已覆盖 runtime hook/reducer 验证
当前阶段：STAGE-00 真实场景验证与治理固化

## 入口说明

本文件是 `docs/ai/` 的轻量总入口，面向 AI 与人类执行者。

本索引只覆盖 repo 内共享真相。

`.codex/runtime/` 下的 session 与 observation 文件属于本地 runtime harness，不纳入这里的默认阅读顺序，也不作为项目主真相。

使用规则：

1. 开启新一轮工作时，先读本文件
2. 只把当前有效文档放在活跃入口区
3. 历史文档不要在这里全量展开，只保留归档入口

## 当前建议阅读顺序

1. [项目规则 AGENTS.md](/Volumes/usd/codes/go_projects/ai_ms_pro/AGENTS.md)
2. [当前工作上下文](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)
3. [需求文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/index.md)
4. [项目计划](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/plan.md)
5. [Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md)
6. [中型项目发现总结](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/medium-project-documentation-findings.md)
7. [轻量版大项目治理方案](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/lightweight-large-project-doc-governance.md)
8. [ADR-001 Harness 分层决策](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-001-harness-layering.md)
9. [ADR-002 Session 到 Handoff 的提升规则](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-002-session-to-handoff-promotion.md)
10. [ADR-003 Observation Reducer 顺序](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-003-observation-reducer-order.md)
11. [ADR-004 Requirement Workstream Metadata](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-004-requirement-workstream-metadata.md)
12. [ADR-005 Projection Surface Freshness Boundary](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-005-projection-surface-freshness.md)
13. [ADR-006 Harness 可迁移性与 Bootstrap 决策](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-006-harness-portability-bootstrap.md)

## 当前活跃文档

### 全局文档

- [项目规则 AGENTS.md](/Volumes/usd/codes/go_projects/ai_ms_pro/AGENTS.md)
- [当前工作上下文](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)
- [需求文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/index.md)
- [项目计划](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/plan.md)
- [Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md)
- [Harness 可迁移清单](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-portability-guide.md)
- [中型项目发现总结](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/medium-project-documentation-findings.md)
- [轻量版大项目治理方案](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/lightweight-large-project-doc-governance.md)
- [ADR-001 Harness 分层决策](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-001-harness-layering.md)
- [ADR-002 Session 到 Handoff 的提升规则](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-002-session-to-handoff-promotion.md)
- [ADR-003 Observation Reducer 顺序](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-003-observation-reducer-order.md)
- [ADR-004 Requirement Workstream Metadata](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-004-requirement-workstream-metadata.md)
- [ADR-005 Projection Surface Freshness Boundary](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-005-projection-surface-freshness.md)
- [ADR-006 Harness 可迁移性与 Bootstrap 决策](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-006-harness-portability-bootstrap.md)

### 当前阶段文档

- [Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
- [Harness Portability Template Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-harness-portability-template.md)
- [New Repo Rehearsal Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-new-repo-rehearsal.md)
- [Harness Trace Console Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-harness-trace-console.md)
- [Three.js Snake MVP Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-threejs-snake-mvp.md)
- [Runtime Hooks Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-runtime-stop-session.md)
- [Observation Reducer Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-observation-reducer.md)
- [Requirement Workstream Metadata Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-requirement-workstream-metadata.md)
- [Projection Surface Freshness Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-projection-surface-freshness.md)
- 暂无阶段 `changelog`
- [ADR-001 Harness 分层决策](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-001-harness-layering.md)
- [ADR-002 Session 到 Handoff 的提升规则](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-002-session-to-handoff-promotion.md)
- [ADR-003 Observation Reducer 顺序](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-003-observation-reducer-order.md)
- [ADR-004 Requirement Workstream Metadata](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-004-requirement-workstream-metadata.md)
- [ADR-005 Projection Surface Freshness Boundary](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-005-projection-surface-freshness.md)

## 活跃目录

- [handoffs/active](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active)
- [status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status)
- [changelog](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/changelog)
- [adr](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr)

## 归档入口

- [handoffs/archive](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/archive)
- [archive](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/archive)

## 维护规则

- 有实质性进展后，检查本文件是否仍然指向最新有效文档
- 新增 `handoff`、`status`、`changelog`、`adr` 后，更新活跃入口
- 阶段结束后，将失活 `handoff` 移入归档，并更新这里的链接
- 本地 runtime harness 文件不应加入本索引
