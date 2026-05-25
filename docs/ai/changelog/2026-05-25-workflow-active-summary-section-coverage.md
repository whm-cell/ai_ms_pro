# Workflow Active Summary Section Coverage

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `tests/test_governance_workflow_sample_outputs.py` now derives expected workflow step-summary section headings and `cat /tmp/...` outputs from the current inclusive readiness report.
- `scripts/harness_collection_command_coverage.py` now keeps shared workflow summary section expectations beside the workflow command expectations.

## 修复问题

- Prevents a new active real-sample capture gate, ledger action, or readiness state from having workflow commands but no visible GitHub step-summary section.
- Normalizes the burn-in readiness security-event temporary filename with the other sample summary surfaces.

## 行为变化

- 只强化 workflow-output 静态断言.
- 不运行 GitHub Actions workflow.
- 不生成模板.
- 不写 ledger.
- 不生成或接受样本.

## 破坏性变更

- 无.

## 验证范围

- `python3 tests/test_governance_workflow_sample_outputs.py`
- `python3 tests/test_harness_collection_config.py`
- `.codex/.venv/bin/ruff check scripts/harness_collection_command_coverage.py tests/test_governance_workflow_sample_outputs.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Remaining Work](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
