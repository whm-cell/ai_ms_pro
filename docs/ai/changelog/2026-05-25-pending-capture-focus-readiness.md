# Pending Capture Focus Readiness Filter

日期：2026-05-25

## 新增功能

- `scripts/check_harness_pending_samples.py --capture-focus` 新增 `--capture-focus-readiness`，可只渲染指定 readiness state 的 next-capture 聚焦卡。
- pending JSON 报告新增 `next_capture_focus_readiness_filter`、`next_capture_focus_shown_readiness_counts` 和 `next_capture_focus_available_readiness_counts`。

## 修复问题

- 补齐 pending focus 与 planner / intake / template readiness 过滤能力的差距，避免 `needs-more-real-samples` lane 只能从完整 focus 或 bucket count 中人工查找。

## 行为变化

- 默认 `--capture-focus` 文本输出会显示 active readiness filter 和 shown/available readiness buckets。
- `--capture-focus-readiness needs-more-real-samples` 当前聚焦 Local Trace Summary 的 distinct task-class sample lane；该输出只读，不写 ledger，不接受样本。

## 破坏性变更

- 无。

## 验证范围

- `tests/test_harness_pending_samples.py`
- `tests/test_harness_sample_followup_coverage.py`
- `tests/test_change_triggered_followups.py`
- `tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus --capture-focus-readiness needs-more-real-samples --capture-focus-limit 0`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/check-registry.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
