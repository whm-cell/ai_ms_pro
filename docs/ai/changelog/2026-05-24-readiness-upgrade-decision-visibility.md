# 2026-05-24 Readiness Upgrade Decision Visibility

更新时间：2026-05-24
阶段或版本：stage-00 / agentic harness hardening
状态：已确认

## 新增功能

- `check_harness_burn_in_readiness.py` now surfaces ready-gap upgrade decision counts, per-gap decision status, decision refs, and missing-decision lists.
- The readiness table now shows `GAP-WORKFLOW-TASK-PROFILE-AUDIT` as `keep-advisory` with its `harness-upgrade-decisions.jsonl` ref.

## 修复问题

- 修复 readiness 输出只能看到 `ready-for-upgrade-discussion`，但不能直接判断该 gap 是否已有 bounded keep/promote/defer 决策的问题。

## 行为变化

- Readiness remains advisory and read-only.
- Strict decision validation still belongs to `check_harness_upgrade_decisions.py`.
- No sample counts, outcomes, or check levels changed.

## 破坏性变更

- 无。JSON report 只新增字段，不删除既有 readiness 字段。

## 验证范围

- `python3 tests/test_harness_burn_in_readiness.py`
- `python3 tests/test_harness_upgrade_decisions.py`
- `python3 tests/test_plan_harness_sample_collection.py`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --json`
