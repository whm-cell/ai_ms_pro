# Workflow Active Sample Summary Coverage

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `tests/test_governance_workflow_sample_outputs.py` now derives expected workflow summary commands from the current inclusive readiness report.
- The workflow-output test checks every active real-sample capture gate, real-sample ledger action, and real-sample readiness state has its planner/template/intake/readiness/pending-focus summary command in `.github/workflows/governance-and-smoke.yml`.
- Workflow summary command templates live in `scripts/harness_collection_command_coverage.py` beside the follow-up command templates.

## 修复问题

- Prevents the command package from staying complete while the GitHub step summary silently misses a newly active real-sample lane.
- Reduces hand-maintained drift between collection config audit, follow-up coverage, and governance workflow sample summaries.

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
- `.codex/.venv/bin/ruff check scripts/harness_collection_command_coverage.py tests/test_governance_workflow_sample_outputs.py tests/test_harness_collection_config.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_collection_config.py`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Remaining Work](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
