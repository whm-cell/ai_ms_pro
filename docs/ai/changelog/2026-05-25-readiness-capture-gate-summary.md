# Readiness Capture Gate Summary

日期：2026-05-25

## 新增功能

- Added CI step-summary readiness views for the remaining real sample capture gates:
  `requires-approved-bounded-incident`, `replace-placeholder-after-real-event`,
  `requires-security-workflow-event`, `requires-bounded-real-incident`,
  `requires-workflow-task-event`, `requires-cross-task-resume`,
  `requires-distinct-task-class-report`, and
  `requires-user-confirmed-high-impact-action`.
- Updated change-triggered follow-up coverage, tool contracts, check registry,
  roadmap, open items, and tests so readiness focused views match the existing
  planner, template, intake, and pending focus lanes.

## 修复问题

- Avoids leaving readiness capture-gate visibility narrower than planner,
  template, intake, and pending focus visibility.
- Avoids requiring maintainers to infer per-gate current / target readiness
  from the full readiness table or from JSON-only output.

## 行为变化

- This is a read-only visibility change.
- No sample ledger rows were added, accepted, replaced, or rejected.
- Readiness remains governed by real-event evidence and the target checker for
  each lane.

## 破坏性变更

- None.

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_governance_workflow_sample_outputs tests.test_harness_sample_followup_coverage tests.test_change_triggered_followups tests.test_tool_contracts`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --capture-gate requires-approved-bounded-incident`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --capture-gate replace-placeholder-after-real-event`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --capture-gate requires-security-workflow-event`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --capture-gate requires-bounded-real-incident`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --capture-gate requires-workflow-task-event`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --capture-gate requires-cross-task-resume`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --capture-gate requires-distinct-task-class-report`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --capture-gate requires-user-confirmed-high-impact-action`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
