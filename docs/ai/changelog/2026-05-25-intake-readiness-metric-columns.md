# Intake Readiness Metric Columns

日期：2026-05-25

## 新增功能

- `scripts/build_harness_sample_intake_bundle.py` entry JSON 现在包含 `source_metric`、`accepted_count`、`upgrade_discussion_target` 和 `current_to_target`。
- intake text entry 和 `--summary` Queue 表现在显示 readiness source metric 与 current / target。

## 修复问题

- 防止 intake bundle 读者只看到 readiness 标签、模板数量或 ledger action，却看不到具体 readiness metric。
- Stage Checkpoint intake 行现在会显示 `accepted cross-task resume samples | 0/2`，避免把同一 harness-hardening 线程的 accepted rows 误读成跨任务样本满足。

## 行为变化

- `--summary` Queue 表新增 `Metric` 和 `Current / Target` 两列。
- JSON 新增字段是只读诊断字段，不改变模板内容、不写 ledger、不接受样本。

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_harness_sample_intake_bundle.py`

## 关联文档

- `docs/ai/standards/harness-sample-gap-evidence.md`
- `docs/ai/check-registry.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/agentic-harness-gap-roadmap.md`
