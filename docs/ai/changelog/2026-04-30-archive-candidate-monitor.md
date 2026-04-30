# 2026-04-30 Archive Candidate Monitor

更新时间：2026-04-30
阶段或版本：stage-00
状态：已确认

## 新增功能

- Added `scripts/check_archive_candidates.py` as a warning-only context-pressure monitor.
- Added the same script to `new_pro_standard/scripts/` so new harness starters can carry the monitor.
- Added regression coverage for completed handoff candidates and unbound active handoff candidates.

## 修复问题

- Reduced archive pressure handling from implicit manual inspection to a repeatable warning-only scan.
- Kept active in-progress handoffs out of default candidate output unless stronger pressure signals exist.

## 行为变化

- The monitor reports archive review candidates with reasons and cautions.
- It does not move files, update `index.md`, rewrite `working-context.md`, or publish canonical docs.
- It is intentionally not wired into the default `Stop` hook to avoid adding noise to simple development tasks.

## 破坏性变更

- 无

## 当前扫描结果

- 当前 active handoff 数量：`5`
- 当前候选：`stage-00-governance-surface-slimming.md`、`stage-00-harness-portability-template.md`、`stage-00-new-repo-rehearsal.md`
- 这些仍需要人工确认未完成项和下一步动作是否已经进入 `status` / backlog 后再归档。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_archive_candidates.py`
- `.codex/.venv/bin/python -m unittest tests/test_archive_candidate_monitor.py`
- `.codex/.venv/bin/python -m py_compile scripts/check_archive_candidates.py new_pro_standard/scripts/check_archive_candidates.py tests/test_archive_candidate_monitor.py`

## 关联文档

- [ADR-007 Governance Surface Budget](../adr/ADR-007-governance-surface-budget.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [当前工作上下文](../working-context.md)
