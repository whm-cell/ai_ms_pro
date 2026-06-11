# Placeholder Replacement Summary Views

日期：2026-05-25

## 新增功能

- Governance workflow 现在把 `replace-placeholder-after-real-event` 的 planner capture-card、template drift、intake summary 和 pending capture-focus 视图写入 step summary。
- Sample follow-up coverage 与 change-triggered sample-gap follow-up bundle 现在要求同一组 placeholder replacement 聚焦命令。

## 修复问题

- 避免 PreToolUse preflight 与 Loop / Scope Monitor 的 pending placeholder 只藏在 full queue 或 readiness bucket count 中。
- 让 placeholder replacement 与已有 readiness / capture-gate 聚焦报告保持同一套 planner、template、intake、pending reporting surface。

## 行为变化

- 新增视图只读，只显示等待真实 warning 后替换占位行的 lane。
- 当前聚焦 `GAP-GUARDRAIL-PREFLIGHT-WARNING` 与 `GAP-RUNTIME-LOOP-SCOPE-WARNING`，两者仍为 `needs-first-real-sample` 且 accepted real warning samples 为 0。
- 真实事件补全后仍必须先跑 `check_harness_placeholder_replacement.py <candidate-jsonl>`，再单独做 outcome review。

## 破坏性变更

- 无。

## 验证范围

- `tests/test_governance_workflow_sample_outputs.py`
- `tests/test_harness_sample_followup_coverage.py`
- `tests/test_change_triggered_followups.py`
- `tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --capture-gate replace-placeholder-after-real-event --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --capture-gate replace-placeholder-after-real-event`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --capture-gate replace-placeholder-after-real-event --summary`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus --capture-focus-gate replace-placeholder-after-real-event --capture-focus-limit 0`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
