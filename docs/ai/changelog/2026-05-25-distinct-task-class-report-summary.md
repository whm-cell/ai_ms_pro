# Distinct Task Class Report Summary Views

日期：2026-05-25

## 新增功能

- Governance workflow 现在把 `requires-distinct-task-class-report` 的 planner capture-card、template drift、intake summary 和 pending capture-focus 视图写入 step summary。
- Sample follow-up coverage 与 change-triggered sample-gap follow-up bundle 现在要求同一组 distinct task class report 聚焦命令。

## 修复问题

- 避免 `GAP-TRACE-LOCAL-SUMMARY-BURNIN` 只藏在 full queue 或 needs-more-real-samples 聚合视图中。
- 让 Local Trace Summary 不同任务类采集 lane 与 remote interop、workflow task event 和 cross-task resume 的 reporting surface 保持一致。

## 行为变化

- 新增视图只读，只显示需要不同任务类 local trace summary report 的 lane。
- 当前聚焦 `GAP-TRACE-LOCAL-SUMMARY-BURNIN`，该 gap 仍为 `needs-more-real-samples`，accepted real local trace summary task classes 为 1/3。
- 已有 3 条 accepted real local report 不能替代 distinct task-class readiness；当前 accepted class 仍只有 `harness-hardening`。
- 真实 distinct task-class report 补全后仍必须先跑 `check_harness_sample_append.py <candidate-jsonl>`，再单独做 outcome review。

## 破坏性变更

- 无。

## 验证范围

- `tests/test_governance_workflow_sample_outputs.py`
- `tests/test_harness_sample_followup_coverage.py`
- `tests/test_change_triggered_followups.py`
- `tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --capture-gate requires-distinct-task-class-report --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --capture-gate requires-distinct-task-class-report`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --capture-gate requires-distinct-task-class-report --summary`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus --capture-focus-gate requires-distinct-task-class-report --capture-focus-limit 0`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
