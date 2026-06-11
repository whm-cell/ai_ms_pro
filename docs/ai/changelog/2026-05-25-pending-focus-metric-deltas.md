# 2026-05-25 Pending Focus Metric Deltas

## 新增功能

- `check_harness_pending_samples.py --capture-focus` 的单张 next-capture 卡片现在会在存在 accepted-real/readiness metric 差异时显示 `Readiness metric delta`。
- JSON `next_capture_focus` entries 同步新增 `readiness_metric_delta` 字段，便于复制单个采集项时保留“账本 accepted real 粗计不等于 readiness source metric”的提醒。

## 修复问题

- 之前顶层 pending audit 已有 `accepted_real_readiness_metric_deltas`，但单张 capture-focus 卡片单独转发时只显示 `Metric` 和 `Current / target`，仍需要读顶层 map 才能看出 Stage Checkpoint / Local Trace 的粗计差异。

## 行为变化

- `GAP-RUNTIME-STAGE-CHECKPOINT-RESUME` 的 capture-focus 卡片会显示 `ledger accepted real=2; accepted cross-task resume samples=0/2`。
- `GAP-TRACE-LOCAL-SUMMARY-BURNIN` 的 capture-focus 卡片会显示 `ledger accepted real=3; accepted real local trace summary task classes=1/3`。

## 破坏性变更

- 无。该字段只读；不写 ledger、不生成样本、不接受 pending row、不改变 readiness 判定。

## 验证范围

- `tests/test_harness_pending_samples.py`
- `tests/test_tool_contracts.py`
- `scripts/check_harness_pending_samples.py --capture-focus`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
