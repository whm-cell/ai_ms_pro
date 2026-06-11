# Security Event Summary Views

日期：2026-05-25

## 新增功能

- Governance workflow 现在把 `requires-security-workflow-event` 的 planner capture-card、template drift、intake summary 和 pending capture-focus 视图写入 step summary。
- Sample follow-up coverage 与 change-triggered sample-gap follow-up bundle 现在要求同一组 security workflow event 聚焦命令。

## 修复问题

- 避免 scheduled security evidence run 与 PR / dependency evidence 两个 P1 缺口只藏在 full queue 或 readiness bucket count 中。
- 让 security evidence capture lane 与 placeholder replacement、readiness filter、template drift 和 intake bundle 的 reporting surface 保持一致。

## 行为变化

- 新增视图只读，只显示需要真实 PR、release、dependency、scheduled security、CodeQL、SBOM 或 dependency-review 事件的 lane。
- 当前聚焦 `GAP-SEC-SCHEDULED-RUN` 与 `GAP-SEC-PR-DEPENDENCY`，两者仍为 `needs-first-real-sample` 且 accepted real samples 为 0。
- 真实事件补全后仍必须先跑 `check_harness_sample_append.py <candidate-jsonl>`，再单独做 outcome review。

## 破坏性变更

- 无。

## 验证范围

- `tests/test_governance_workflow_sample_outputs.py`
- `tests/test_harness_sample_followup_coverage.py`
- `tests/test_change_triggered_followups.py`
- `tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --capture-gate requires-security-workflow-event --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --capture-gate requires-security-workflow-event`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --capture-gate requires-security-workflow-event --summary`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus --capture-focus-gate requires-security-workflow-event --capture-focus-limit 0`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
