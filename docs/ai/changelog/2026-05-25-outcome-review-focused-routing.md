# Outcome Review Focused Routing

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `check_harness_sample_outcome.py` 的 no-write report 现在输出当前 gap 的 focused planner command 和 focused intake command。
- JSON report 同步携带 `planner_command` 和 `intake_command`，便于后续工具或人工复核直接回到同一个 `--gap-id` scope。

## 修复问题

- 避免 outcome review 只显示 queue context，却仍要求复核者手写 planner / intake 命令来确认当前 lane。
- focused planner / intake command 现在显式携带 `--ledger-action review-existing-pending-slot`，且 intake command 额外携带 `--pending-state with-review-ready-pending`，避免默认 intake scope 返回空结果。
- 与 append / replacement no-write review report 的当前采集上下文输出保持一致。

## 行为变化

- 不写 ledger。
- 不接受样本。
- 不改变 readiness 或 upgrade decision。
- 不把 candidate 或 report 计为 accepted evidence。

## 破坏性变更

- 无。

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_harness_sample_outcome tests.test_tool_contracts`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --pending-state with-review-ready-pending`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Open Items](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
