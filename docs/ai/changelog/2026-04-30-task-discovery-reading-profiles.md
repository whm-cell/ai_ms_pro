# 2026-04-30 Task Discovery Reading Profiles

更新时间：2026-04-30
阶段或版本：stage-00
状态：已确认

## 新增功能

- Added Task Discovery Protocol to root `AGENTS.md`.
- Synced the same protocol into `new_pro_standard/AGENTS.md`.
- Added ADR-011 to record automatic task classification and reading profiles.

## 修复问题

- Reduced the risk that complex or 0-1 stage tasks under-read context after the default context surface was slimmed.
- Clarified that task-type phrases are optional user overrides, not suffixes users must add to every prompt.

## 行为变化

- Codex should classify substantial tasks as simple, medium, complex, 0-1 stage, or recovery/dispute before expanding context.
- User overrides such as `按简单任务处理` or `这是 0-1 阶段任务` take precedence over automatic classification.

## 破坏性变更

- 无

## 验证范围

- `scripts/check_ai_governance.py`
- `scripts/check_archive_candidates.py`
- `scripts/check_code_shape.py --staged`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [ADR-011 Task Discovery Reading Profiles](../adr/ADR-011-task-discovery-reading-profiles.md)
