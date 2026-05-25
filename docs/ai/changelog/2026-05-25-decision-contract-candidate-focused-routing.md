# Decision And Contract Candidate Focused Routing

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `check_harness_upgrade_decision_candidate.py` 的 no-write report 现在输出当前 gap 的 focused planner command 和 focused intake command。
- `check_harness_future_work_contract_candidate.py` 的 no-write report 现在输出当前 gap 的 focused planner command 和 focused intake command，即使 candidate 已经 stale 且当前 queue 已路由到 append lane。
- 两个 JSON report 同步携带 `planner_command` 和 `intake_command`，便于复核者回到同一个 `--gap-id` scope。

## 修复问题

- 避免 ready-gap decision 或 future-work contract candidate report 只显示 queue context，却仍要求复核者手写 planner / intake 命令。
- ready-gap decision 的 focused planner / intake command 现在显式携带 `--ledger-action review-upgrade-decision`，future-work contract candidate 则回显当前 queue lane（例如已获批后的 `append-new-pending-slot`），避免通用 `--gap-id` intake 命令返回空 scope。
- 让 decision / contract candidate review 与 append、replacement、outcome no-write review 的当前采集上下文输出保持一致。

## 行为变化

- 不写 ledger。
- 不接受样本。
- 不批准 future-work sampling。
- 不创建 ADR 或升级 blocking。
- 不把 candidate 或 report 计为 accepted evidence。

## 破坏性变更

- 无。

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_harness_upgrade_decision_candidate tests.test_harness_future_work_contract_candidate tests.test_tool_contracts`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --ledger-action review-upgrade-decision`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Open Items](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
