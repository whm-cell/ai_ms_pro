# Planner Lane Review Command JSON

更新时间：2026-05-24
阶段或版本：stage-01
状态：已确认

## 新增功能

- `scripts/plan_harness_sample_collection.py --json` 现在为每个 queue item 输出 lane-specific review command 字段：
  `replacement_review_command`、`append_review_command`、`outcome_review_command`、`upgrade_decision_review_command`、`contract_precondition_review_command`。
- markdown queue table 和 capture card 会显示当前 ledger lane 的 active review command。

## 修复问题

- 修复 planner 消费者需要从 `ledger_action` 反推 no-write review command 的问题。
- future-work contract precondition lane 现在能在 planner JSON / capture-card 中直接指向 `check_harness_future_work_contracts.py`。

## 行为变化

- `fill-existing-placeholder` item 的 `replacement_review_command` 指向 `check_harness_placeholder_replacement.py <candidate-jsonl>`，其他 lane command 为 `not-applicable`。
- `append-new-pending-slot` item 的 `append_review_command` 指向 `check_harness_sample_append.py <candidate-jsonl>`，其他 lane command 为 `not-applicable`。
- `review-existing-pending-slot` item 的 `outcome_review_command` 指向 `check_harness_sample_outcome.py <candidate-jsonl>`，其他 lane command 为 `not-applicable`。
- `review-upgrade-decision` item 的 `upgrade_decision_review_command` 指向 `check_harness_upgrade_decisions.py`，其他 lane command 为 `not-applicable`。
- `define-contract-precondition` item 的 `contract_precondition_review_command` 指向 `check_harness_future_work_contracts.py`，其他 lane command 为 `not-applicable`。

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_plan_harness_sample_collection.py`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --json`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --gap-id GAP-GUARDRAIL-PREFLIGHT-WARNING --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --include-future --ledger-action define-contract-precondition --json`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --include-future --ledger-action define-contract-precondition --capture-card`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
