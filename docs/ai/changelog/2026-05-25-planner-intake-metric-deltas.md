# 2026-05-25 Planner Intake Metric Deltas

## 新增功能

- `plan_harness_sample_collection.py` 的 queue / capture-card / JSON 输出现在会携带 `readiness_metric_delta`，当账本 accepted real 粗计和精确 readiness source metric 不一致时直接展示差异。
- `build_harness_sample_intake_bundle.py` 的 text / summary / JSON entry 同步携带 `readiness_metric_delta`，让 intake handoff 不会丢失 Stage Checkpoint / Local Trace 的差异提醒。

## 修复问题

- 之前 pending focus 单卡已有 `readiness_metric_delta`，但 planner 和 intake bundle 只显示 `Metric` 与 `Current / target`，复制 queue 或 intake summary 时仍可能把 accepted real row count 误读成 readiness 已满足。

## 行为变化

- Stage Checkpoint cross-task resume 和 Local Trace distinct task-class 这类 metric delta 会出现在 planner / intake handoff 面。
- 没有差异的 gap 保持空字段；markdown 表格显示 `none`。

## 破坏性变更

- 无。该改动只增加只读字段和展示列，不写 ledger，不生成或接受样本，也不改变 readiness / upgrade decision 判定。

## 验证范围

- `tests/test_plan_harness_sample_collection.py`
- `tests/test_harness_sample_intake_bundle.py`
- `tests/test_tool_contracts.py`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
