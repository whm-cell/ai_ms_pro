# Readiness State Filter

日期：2026-05-25

## 新增功能

- `scripts/check_harness_burn_in_readiness.py` 支持可重复的 `--readiness` 过滤器，可聚焦 `needs-first-real-sample` 等 readiness state。
- readiness report 的 text / JSON 输出新增 `readiness_filter`。
- governance workflow 会追加 needs-first-real-sample 聚焦 readiness section。

## 修复问题

- 剩余 first-real-sample blocker 现在可以直接从 readiness audit 或 CI summary 读取，不必从全量表格人工筛选。

## 行为变化

- `--readiness` 只改变只读审计范围；空过滤范围仍显示 no-match，不代表 evidence 结论。
- `ReadinessItem` / `ReadinessReport` 已拆到 `scripts/harness_burn_in_readiness_types.py`，避免主脚本继续贴近代码形状阈值。

## 破坏性变更

- 无。

## 验证范围

- `tests/test_harness_burn_in_readiness.py`
- `tests/test_harness_sample_followup_coverage.py`
- `tests/test_change_triggered_followups.py`
- `tests/test_governance_workflow_sample_outputs.py`
- `tests/test_tool_contracts.py`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
