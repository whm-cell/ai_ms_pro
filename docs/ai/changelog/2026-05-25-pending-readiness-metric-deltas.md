# Pending Readiness Metric Deltas

日期：2026-05-25

## 新增功能

- `scripts/check_harness_pending_samples.py` 的 JSON 输出新增 `queued_readiness_metrics_by_gap`。
- 同一报告新增 `accepted_real_readiness_metric_deltas`，用于暴露账本 `accepted_real_by_gap` 粗计和 readiness source metric 的差异。
- `--capture-focus` 卡片现在显示 `Metric` 和 `Current / target`。

## 修复问题

- 防止 pending audit 读者把 accepted real ledger row 数量误读为升级 readiness 已满足。
- 当前最直接的例子是 Stage Checkpoint：账本已有 2 个 accepted real resume rows，但 accepted cross-task resume samples 仍为 0/2。

## 行为变化

- text 输出会显示 queued readiness metric row count 和 accepted-real/readiness metric deltas。
- JSON 输出保留完整 per-gap readiness metric snapshot，便于 CI summary 或人工复核工具引用。

## 破坏性变更

- 无。新增字段是只读诊断字段。

## 验证范围

- `python3 tests/test_harness_pending_samples.py`

## 关联文档

- `docs/ai/standards/harness-sample-gap-evidence.md`
- `docs/ai/check-registry.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/agentic-harness-gap-roadmap.md`
