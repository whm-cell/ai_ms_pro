# Upgrade Decision Review Summary

日期：2026-05-25

## 新增功能

- Added read-only governance step-summary views for the ready-gap upgrade
  decision lane:
  `plan_harness_sample_collection.py --ledger-action review-upgrade-decision --capture-card`,
  `check_harness_sample_templates.py --ledger-action review-upgrade-decision`,
  `build_harness_sample_intake_bundle.py --ledger-action review-upgrade-decision --summary`,
  and `check_harness_burn_in_readiness.py --capture-gate upgrade-decision-review`.
- Updated follow-up coverage, change-triggered sample rules, tool contracts,
  check registry, roadmap, open items, and workflow tests so the new summary
  views are kept in sync.

## 修复问题

- Avoids hiding ready-gap upgrade decision replacement drafts behind the full
  queue, full intake bundle, or full readiness table.
- Keeps the four current ready gaps visible as decision-review work instead of
  suggesting another sample append path.

## 行为变化

- This is a read-only visibility change for CI summaries.
- No sample evidence rows or upgrade-decision rows were added, replaced,
  accepted, or rejected.
- Current ready-gap decisions remain keep-advisory.

## 破坏性变更

- None.

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_governance_workflow_sample_outputs tests.test_harness_sample_followup_coverage tests.test_change_triggered_followups tests.test_tool_contracts`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --ledger-action review-upgrade-decision --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --ledger-action review-upgrade-decision`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --ledger-action review-upgrade-decision --summary`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --capture-gate upgrade-decision-review`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
