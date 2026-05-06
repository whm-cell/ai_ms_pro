# 2026-04-30 Context Surface Layering Hardening

更新时间：2026-04-30
阶段或版本：stage-00
状态：已确认

## 新增功能

- Added shared harness config loading in `scripts/harness_config.py`.
- Added `[context_surface]` to `.codex/harness.toml` for active handoff budget, archive candidate minimum score, and at-budget warning behavior.
- Added config/archive unit coverage and CI coverage for the new config path.

## 修复问题

- Removed duplicated TOML parsing from governance structure checks.
- Kept root, starter, and bootstrap-generated starter docs aligned on configured context-surface budgets instead of hardcoded threshold text.
- Preserved existing macOS/Windows Python resolution and hook-renderer regression coverage for this script-level change.

## 行为变化

- `check_ai_governance.py` warns when active handoffs or working-context-bound handoffs reach the configured default surface budget.
- `check_archive_candidates.py` now reads budget and minimum score from `.codex/harness.toml`; `--budget` and `--min-score` remain explicit overrides.
- Archive candidate checks remain warning-only and do not move files or update shared governance docs.

## 破坏性变更

- 无

## 验证范围

- `tests/test_harness_config.py`
- `tests/test_archive_candidate_monitor.py`
- `tests/test_python_resolution.py`
- `tests/test_hooks_config_sync.py`
- `scripts/sync_hooks_config.py --check`
- `scripts/check_ai_governance.py`
- `scripts/check_archive_candidates.py`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [ADR-010 Context Surface Layering](../adr/ADR-010-context-surface-layering.md)
