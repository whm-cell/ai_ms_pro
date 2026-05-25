# Capture Gate Filters

日期：2026-05-25

## 新增功能

- `plan_harness_sample_collection.py` 支持 `--capture-gate`，可按真实事件前置条件聚焦 collection queue。
- `build_harness_sample_intake_bundle.py` 支持 `--capture-gate`，可按同一门槛生成只读 intake 草稿包或 summary。
- `check_harness_pending_samples.py --capture-focus` 支持 `--capture-focus-gate`，并在 text / cards / JSON 中输出 shown/available capture-gate counts。

## 修复问题

- 维护者现在可以直接聚焦 `requires-approved-remote-interop`、`requires-cross-task-resume` 等 lane，不必从完整队列里人工筛选。

## 行为变化

- 新过滤器只影响只读 planner、intake bundle 和 next-capture focus 输出，不改变 pending accounting、ledger totals 或样本状态。
- JSON 输出新增 `next_capture_focus_capture_gate_filter`、`next_capture_focus_shown_capture_gate_counts` 和 `next_capture_focus_available_capture_gate_counts`。

## 破坏性变更

- 无。

## 验证范围

- `tests/test_plan_harness_sample_collection.py`
- `tests/test_harness_sample_intake_bundle.py`
- `tests/test_harness_pending_samples.py`
- `tests/test_harness_sample_followup_coverage.py`
- `tests/test_tool_contracts.py`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/tool-contracts/README.md`
