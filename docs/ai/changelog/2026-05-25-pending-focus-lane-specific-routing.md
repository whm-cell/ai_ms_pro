# Pending Focus Lane-Specific Routing

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `harness_collection_lane_commands.py` 现在集中生成 planner / intake 的 lane-specific 参数。
- pending `next_capture_focus` 的 planner / intake 命令现在会携带当前 `ledger_action`。
- append 和 placeholder replacement 的 no-write report 现在回显带当前 `ledger_action` 的 focused planner / intake 命令。
- `review-existing-pending-slot` lane 的下一步命令现在同时包含 intake summary，并显式使用 `--pending-state with-review-ready-pending`。

## 修复问题

- pending focus cards 不再交接通用 `--gap-id` 命令，避免后续跑到错误 lane 或空 scope。
- append / replacement review report 不再遗漏 `--ledger-action append-new-pending-slot` / `--ledger-action fill-existing-placeholder`。
- review-ready lane 不再只给 planner / outcome review，而遗漏可复现的 focused intake summary。

## 行为变化

- 不写 ledger。
- 不接受样本。
- 不改变 readiness 或 upgrade decision。
- 不生成真实样本。
- 不批准 future-work sampling。

## 破坏性变更

- 无。

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_harness_pending_samples tests.test_harness_sample_append tests.test_harness_placeholder_replacement tests.test_harness_burn_in_readiness tests.test_harness_sample_outcome tests.test_harness_upgrade_decision_candidate tests.test_harness_future_work_contract_candidate`
- `.codex/.venv/bin/ruff check scripts/harness_collection_lane_commands.py scripts/harness_pending_capture_focus.py scripts/harness_burn_in_readiness_routing.py scripts/harness_sample_review_context.py tests/test_harness_pending_samples.py tests/test_harness_sample_append.py tests/test_harness_placeholder_replacement.py tests/test_harness_burn_in_readiness.py tests/test_harness_sample_outcome.py tests/test_harness_upgrade_decision_candidate.py tests/test_harness_future_work_contract_candidate.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus --capture-focus-limit 2`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --include-future --include-accepted --json`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Open Items](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
