# Intake Outcome Review Command JSON

更新时间：2026-05-24
阶段或版本：stage-01
状态：已确认

## 新增功能

- `scripts/build_harness_sample_intake_bundle.py --json` 现在为每个 entry 输出 `outcome_review_command`。
- text / summary / JSON 输出现在能为 `review-existing-pending-slot` lane 直接指向 `check_harness_sample_outcome.py <candidate-jsonl>`。
- intake bundle 复用 `harness_collection_lane_commands.py` 的 lane review command 字段，和 planner / pending audit 保持同源。

## 修复问题

- 修复 intake bundle 只有 replacement / append / upgrade-decision / contract-precondition 专用字段，缺少 pending outcome review 专用机器字段的问题。

## 行为变化

- `append-new-pending-slot` entry 的 `outcome_review_command` 为 `not-applicable`。
- `fill-existing-placeholder` entry 的 `outcome_review_command` 为 `not-applicable`。
- `review-upgrade-decision` entry 的 `outcome_review_command` 为 `not-applicable`。
- `define-contract-precondition` entry 的 `outcome_review_command` 为 `not-applicable`。
- `review-existing-pending-slot` entry 的 `outcome_review_command` 指向 `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_outcome.py <candidate-jsonl>`。

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_harness_sample_intake_bundle.py`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --json`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --summary`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
