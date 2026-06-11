# Workflow Area Priority Focus Coverage

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `tests/test_governance_workflow_sample_outputs.py` now derives active real-sample area / priority pending-focus workflow commands and step-summary sections from the current inclusive readiness report.
- `.github/workflows/governance-and-smoke.yml` now appends active area and active priority pending capture-focus sections.
- `scripts/harness_collection_command_coverage.py` holds the shared area / priority command and section expectations used by workflow-output tests.

## 修复问题

- Prevents active area / priority routed command coverage from existing while the GitHub step summary still only exposes the full pending-focus queue.

## 行为变化

- 只强化 workflow-output 静态断言和 CI summary 可见性.
- 不运行 GitHub Actions workflow.
- 不写 ledger.
- 不生成或接受样本.
- 不改变 readiness / upgrade decision.

## 破坏性变更

- 无.

## 验证范围

- `python3 tests/test_governance_workflow_sample_outputs.py`
- `.codex/.venv/bin/ruff check scripts/harness_collection_command_coverage.py tests/test_governance_workflow_sample_outputs.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Remaining Work](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
