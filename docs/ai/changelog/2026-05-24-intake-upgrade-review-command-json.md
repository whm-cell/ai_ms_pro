# Intake Upgrade Review Command JSON

更新时间：2026-05-24
阶段或版本：stage-01
状态：已确认

## 新增功能

- `scripts/build_harness_sample_intake_bundle.py --ledger-action review-upgrade-decision --json` 现在为每个 ready-gap entry 输出 `upgrade_decision_review_command`。
- text / summary / JSON 三种输出都能直接指向 `check_harness_upgrade_decisions.py`，不需要消费者从通用 `review_command` 和 `ledger_action` 反推。

## 修复问题

- 修复 intake bundle 只有 replacement / append 专用 review command 字段，upgrade-decision lane 缺少对称机器字段的问题。

## 行为变化

- `append-new-pending-slot` entry 的 `upgrade_decision_review_command` 为 `not-applicable`。
- `fill-existing-placeholder` entry 的 `upgrade_decision_review_command` 为 `not-applicable`。
- `review-upgrade-decision` entry 的 `upgrade_decision_review_command` 指向 `.codex/hooks/run_with_repo_python.sh scripts/check_harness_upgrade_decisions.py`。

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_harness_sample_intake_bundle.py`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --ledger-action review-upgrade-decision --json`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
