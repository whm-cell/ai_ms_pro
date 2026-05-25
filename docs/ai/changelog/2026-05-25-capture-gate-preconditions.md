# Capture Gate Preconditions

日期：2026-05-25

## 新增功能

- `scripts/plan_harness_sample_collection.py` queue items now include `capture_gate` and `capture_gate_detail` so real-event blockers are machine-readable before an operator drafts sample evidence.
- `scripts/build_harness_sample_intake_bundle.py` propagates those fields into text, summary, and JSON output, including capture gate counts and a `Capture Gates` summary table.
- `scripts/check_harness_pending_samples.py` propagates capture gates into `next_capture_focus` text, cards, and JSON output.

## 修复问题

- 防止维护者把 `append-new-pending-slot` 或 `fill-existing-placeholder` 误读成当前会话可以直接补样本。
- 现在 Stage Checkpoint、Local Trace Summary、remote interop、cascade-stop 等 lane 会明确显示必须等待的真实事件或任务类型。

## 行为变化

- planner markdown summary 现在显示 capture gate counts。
- intake summary 现在显示 capture gate counts，并增加 `Capture Gates` 表。
- pending capture focus cards / JSON 现在显示每个 focus entry 的 `capture_gate` 和 `capture_gate_detail`。

## 破坏性变更

- 无。Capture gates are read-only routing metadata; they do not collect samples, accept pending rows, or prove readiness.

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_plan_harness_sample_collection tests.test_harness_pending_samples tests.test_harness_sample_intake_bundle tests.test_harness_sample_templates`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
