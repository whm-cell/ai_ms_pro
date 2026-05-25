# Planner Item Routing Split

更新时间：2026-05-24
阶段或版本：stage-01
状态：已确认

## 新增功能

- 无用户可见新功能。

## 修复问题

- 将 `plan_harness_sample_collection.py` 中的 `CollectionItem` 和 gap routing helper 拆到 `scripts/harness_sample_collection_items.py`，消除 planner 文件超过 code-shape 行数阈值的 warning。

## 行为变化

- `plan_harness_sample_collection.py` 继续保留原有公开导入面，现有 `build_queue()`、`CollectionItem` 和 `is_actionable_sample_item()` 调用保持兼容。
- 新 helper 已纳入 sample-gap change-triggered follow-up 覆盖。

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_plan_harness_sample_collection.py`
- `python3 tests/test_change_triggered_followups.py`
- `python3 tests/test_harness_sample_followup_coverage.py`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Tool Contracts](../tool-contracts/README.md)
