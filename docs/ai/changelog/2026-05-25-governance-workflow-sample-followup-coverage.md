# Governance Workflow Sample Follow-up Coverage

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `.github/workflows/governance-and-smoke.yml` now participates in `harness-sample-gap-evidence` change-triggered follow-up discovery.
- The routed sample-gap command package now includes `python3 tests/test_governance_workflow_sample_outputs.py`.
- Follow-up coverage discovery now audits the workflow file alongside sample-gap docs, scripts, and tests.

## 修复问题

- Fixed workflow sample-summary changes relying on full unittest rather than the sample-gap follow-up package to run workflow-output assertions.
- Prevents CI summary route changes from skipping the static workflow-output test.

## 行为变化

- 只强化 change-triggered follow-up coverage.
- 不运行 workflow.
- 不写 ledger.
- 不生成或接受样本.
- 不改变 readiness / upgrade decision.

## 破坏性变更

- 无.

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_change_triggered_followups tests.test_harness_sample_followup_coverage tests.test_governance_workflow_sample_outputs tests.test_tool_contracts`
- `.codex/.venv/bin/ruff check scripts/change_triggered_harness_sample_rules.py scripts/check_harness_sample_followup_coverage.py tests/test_change_triggered_followups.py tests/test_harness_sample_followup_coverage.py tests/test_governance_workflow_sample_outputs.py tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_change_triggered_followups.py --files .github/workflows/governance-and-smoke.yml`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Remaining Work](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
