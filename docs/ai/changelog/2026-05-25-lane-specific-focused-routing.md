# Lane-Specific Focused Routing

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `harness_sample_review_context.focused_commands()` 现在可按 `ledger_action` 生成 lane-specific planner / intake command。
- `check_harness_burn_in_readiness.py` 的 per-gap next collection commands 现在也按 `ledger_action` 生成 lane-specific planner / intake command。
- `review-existing-pending-slot` 的 focused intake command 会带 `--pending-state with-review-ready-pending`，避免 outcome-review scope 被 intake bundle 默认的 `without-review-ready-pending` 过滤掉。
- Upgrade decision 和 future-work contract candidate report 现在使用当前 queue item 的 `ledger_action` 生成 focused planner / intake command。

## 修复问题

- 修复 ready-gap decision candidate report 里的通用 intake command 会返回空 scope 的问题。
- 修复 readiness handoff 中 ready-gap / append / replacement / contract lane 的 per-gap intake command 仍是通用 `--gap-id` scope 的问题。
- 修复 stale future-work contract candidate report 在当前已路由到 append lane 时无法直接复现当前 intake scope 的问题。
- 修复 outcome review report 里的 intake command 没有显式进入 review-ready pending scope 的问题。

## 行为变化

- 不写 ledger。
- 不接受样本。
- 不批准 future-work sampling。
- 不创建 ADR 或升级 blocking。
- 不把 candidate 或 report 计为 accepted evidence。

## 破坏性变更

- 无。

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_harness_sample_outcome tests.test_harness_upgrade_decision_candidate tests.test_harness_future_work_contract_candidate`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --gap-id GAP-WORKFLOW-TASK-PROFILE-AUDIT --ledger-action review-upgrade-decision --summary`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --gap-id GAP-TRACE-REMOTE-INTEROP --ledger-action append-new-pending-slot --summary`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Open Items](../harness-open-items.md)
- [Tool Contracts](../tool-contracts/README.md)
