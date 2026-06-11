# Workflow Task Event Summary Views

日期：2026-05-25

## 新增功能

- Governance workflow 现在把 `requires-workflow-task-event` 的 planner capture-card、template drift、intake summary 和 pending capture-focus 视图写入 step summary。
- Sample follow-up coverage 与 change-triggered sample-gap follow-up bundle 现在要求同一组 workflow task event 聚焦命令。

## 修复问题

- 避免 cross-workstream skill load / skip、simple skip 和 PR overlap 三个 P2 workflow-skill 缺口只藏在 full queue、P2 readiness 或 needs-first-real-sample 视图中。
- 让 workflow task event capture lane 与 placeholder replacement、security workflow event、bounded real incident、readiness filter、template drift 和 intake bundle 的 reporting surface 保持一致。

## 行为变化

- 新增视图只读，只显示需要真实 workflow task 的 workflow-skill lane。
- 当前聚焦 `GAP-WORKFLOW-CROSS-WS`、`GAP-WORKFLOW-SIMPLE-SKIP` 与 `GAP-WORKFLOW-PR-OVERLAP`，三者仍为 `needs-first-real-sample` 且 accepted real workflow task samples 为 0。
- 真实 workflow task 补全后仍必须先跑 `check_harness_sample_append.py <candidate-jsonl>`，再单独做 outcome review。

## 破坏性变更

- 无。

## 验证范围

- `tests/test_governance_workflow_sample_outputs.py`
- `tests/test_harness_sample_followup_coverage.py`
- `tests/test_change_triggered_followups.py`
- `tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --capture-gate requires-workflow-task-event --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --capture-gate requires-workflow-task-event`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --capture-gate requires-workflow-task-event --summary`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus --capture-focus-gate requires-workflow-task-event --capture-focus-limit 0`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
