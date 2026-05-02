# 2026-05-02 Project Skill Lifecycle

更新时间：2026-05-02
阶段或版本：stage-00
状态：已确认

## 新增功能

- Added a project architecture / style / dependency skill lifecycle template.
- Added ADR-013 to record the lifecycle rule and the boundary between skill guidance and canonical governance truth.
- Synced the template into `new_pro_standard` as portable harness mechanism.

## 修复问题

- Reduced the risk that early project architecture, style, or dependency constraints become permanent too early.
- Clarified that project skills reduce default context through on-demand loading, but do not replace `AGENTS.md`, ADR, status, requirements, or verification scripts.

## 行为变化

- Simple tasks should not load the project skill lifecycle template by default.
- 0-1 stage tasks and architecture/style/dependency skill changes may load the template on demand.
- Skill conflicts must use an escape hatch and promote durable changes to `handoff`, `status`, ADR, or requirements.

## 破坏性变更

- 无

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --staged`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Project Skill Lifecycle Template](../templates/project-skill-lifecycle.md)
- [ADR-013 Project Skill Lifecycle](../adr/ADR-013-project-skill-lifecycle.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
