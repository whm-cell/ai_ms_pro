# 2026-04-30 Context Surface Compression

更新时间：2026-04-30
阶段或版本：stage-00
状态：已确认

## 新增功能

- 无

## 修复问题

- Archived three completed active handoffs after confirming their durable conclusions were already absorbed by stage `status`, ADRs, changelogs, or remaining-work tracking.
- Reduced `working-context` active handoff bindings from 5 to 2.
- Reframed `docs/ai/index.md` as a short default chain plus Task Discovery based on-demand entrypoints.

## 行为变化

- Simple tasks should now read a smaller default surface before deciding whether deeper context is needed.
- Complex, 0-1 stage, recovery, and requirement-driven tasks still have explicit paths into requirements, plan, handoff, ADR, and archive material.

## 破坏性变更

- 无

## 验证范围

- `scripts/check_ai_governance.py`
- `scripts/check_archive_candidates.py`
- `scripts/check_code_shape.py --staged`

## 关联文档

- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [ADR-010 Context Surface Layering](../adr/ADR-010-context-surface-layering.md)
- [ADR-011 Task Discovery Reading Profiles](../adr/ADR-011-task-discovery-reading-profiles.md)
