# Readiness Area Priority Summary Coverage

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `scripts/harness_collection_command_coverage.py` now requires active real-sample area / priority readiness audit commands beside pending capture-focus commands.
- `.github/workflows/governance-and-smoke.yml` now appends active area and active priority burn-in readiness sections.
- `tests/test_governance_workflow_sample_outputs.py` derives those readiness commands and step-summary sections from the current inclusive readiness report.

## 修复问题

- Prevents roadmap area / priority buckets from being visible in pending focus but missing from burn-in readiness CI summary.

## 行为变化

- 只强化 read-only readiness audit command coverage 和 GitHub step-summary 可见性.
- 不运行真实采样.
- 不写 ledger.
- 不生成或接受样本.
- 不改变 readiness / upgrade decision.

## 破坏性变更

- 无.

## 验证范围

- `python3 tests/test_governance_workflow_sample_outputs.py`
- `python3 tests/test_harness_collection_config.py`
- `python3 tests/test_harness_sample_followup_coverage.py`
- `python3 tests/test_tool_contracts.py`
- `.codex/.venv/bin/ruff check scripts/harness_collection_command_coverage.py scripts/change_triggered_harness_sample_rules.py scripts/check_harness_sample_followup_coverage.py scripts/check_harness_collection_config.py tests/test_governance_workflow_sample_outputs.py tests/test_harness_collection_config.py tests/test_harness_sample_followup_coverage.py tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_collection_config.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Remaining Work](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
