# 2026-05-25 Burn-In Ledger Structured Progress

## 新增功能

- `check_burn_in_ledger.py` 的 markdown / JSON 输出现在包含 `decision_counts`、`total_remaining_samples`、`checks_needing_samples` 和 `upgrade_eligible_checks`。
- JSON `rows` 现在按 blocking-candidate check 输出 `accepted_samples`、`sample_target`、`remaining_samples`、`current_decision`、`next_evidence`、`repair_path`、`cost`、`false_positives` 和 `upgrade_eligible`。

## 修复问题

- 之前 checker 只验证 markdown 表结构和 upgrade-decision consistency；自动化消费者若要知道还差哪些真实样本，必须重新解析 `docs/ai/check-burn-in-ledger.md`。

## 行为变化

- governance step summary 中的 burn-in ledger audit 会显示剩余样本槽位、仍需样本的 blocking-candidate checks 和逐项 next evidence。
- 当前状态仍是 7 个 blocking-candidate check 全部 `0/2`、`keep-candidate`，共 14 个剩余真实样本槽位。

## 破坏性变更

- 无。该改动只增加只读审计字段，不写 ledger、不生成样本、不升级 blocking。

## 验证范围

- `tests/test_check_burn_in_ledger.py`
- `tests/test_tool_contracts.py`

## 关联文档

- `docs/ai/check-burn-in-ledger.md`
- `docs/ai/check-registry.md`
- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
