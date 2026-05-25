# Bounded Real Incident Summary Views

日期：2026-05-25

## 新增功能

- Governance workflow 现在把 `requires-bounded-real-incident` 的 planner capture-card、template drift、intake summary 和 pending capture-focus 视图写入 step summary。
- Sample follow-up coverage 与 change-triggered sample-gap follow-up bundle 现在要求同一组 bounded real incident 聚焦命令。

## 修复问题

- 避免 tool / skill squatting、memory poisoning、A2A / handoff confusion 三个 P2 red-team 真实 incident 缺口只藏在 full queue、P2 readiness 或 needs-first-real-sample 视图中。
- 让 red-team incident capture lane 与 placeholder replacement、security workflow event、readiness filter、template drift 和 intake bundle 的 reporting surface 保持一致。

## 行为变化

- 新增视图只读，只显示需要真实 bounded incident 的 red-team lane。
- 当前聚焦 `GAP-AGENTIC-TOOL-SQUATTING`、`GAP-AGENTIC-MEMORY-POISONING` 与 `GAP-AGENTIC-A2A-HANDOFF`，三者仍为 `needs-first-real-sample` 且 accepted real incidents 为 0。
- 真实 incident 补全后仍必须先跑 `check_harness_sample_append.py <candidate-jsonl>`，再单独做 outcome review。

## 破坏性变更

- 无。

## 验证范围

- `tests/test_governance_workflow_sample_outputs.py`
- `tests/test_harness_sample_followup_coverage.py`
- `tests/test_change_triggered_followups.py`
- `tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --capture-gate requires-bounded-real-incident --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --capture-gate requires-bounded-real-incident`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --capture-gate requires-bounded-real-incident --summary`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus --capture-focus-gate requires-bounded-real-incident --capture-focus-limit 0`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
