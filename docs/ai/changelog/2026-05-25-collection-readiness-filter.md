# Collection Readiness Filter

日期：2026-05-25

## 新增功能

- `scripts/plan_harness_sample_collection.py` 支持可重复的 `--readiness` 过滤器。
- `scripts/build_harness_sample_intake_bundle.py` 支持 `--readiness`，并在 text / summary / JSON 中输出 `readiness_counts`。
- `scripts/check_harness_sample_templates.py` 支持 `--readiness`，用于只验证某个 readiness state 的模板草稿。

## 修复问题

- 维护者现在可以把 readiness audit 中的 state 直接带到 planner / intake / template drift check，不必在全量采集队列中人工筛选。

## 行为变化

- `--readiness needs-more-real-samples` 当前只聚焦仍需更多真实样本的 lane，不混入 first-sample blocker、local-only 或 ready upgrade-decision lane。
- 新过滤器只影响只读队列、草稿包和模板检查输出，不写 ledger、不接受样本。

## 破坏性变更

- 无。

## 验证范围

- `tests/test_plan_harness_sample_collection.py`
- `tests/test_harness_sample_intake_bundle.py`
- `tests/test_harness_sample_templates.py`
- `tests/test_harness_sample_followup_coverage.py`
- `tests/test_change_triggered_followups.py`
- `tests/test_tool_contracts.py`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
