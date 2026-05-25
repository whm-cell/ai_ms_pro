# 2026-05-25 Burn-In Upgrade Review Needed

## 新增功能

- `check_burn_in_ledger.py` 现在输出 `upgrade_review_needed_checks`。
- 每个 row 现在带 `upgrade_review_needed`，用于标记 `2/2` 但仍为 `keep-candidate` 的 blocking-candidate check。

## 修复问题

- 之前 `upgrade_eligible_checks` 只能说明样本数达标，不能区分“已经进入 ready/promote 决策”与“仍停在 keep-candidate 但需要 upgrade decision review”。

## 行为变化

- `2/2` 且仍为 `keep-candidate` 的行必须在 `Next evidence` 中指向 upgrade decision review。
- 当前 `check_tool_contracts.py` 会出现在 `upgrade_review_needed_checks`，但仍不自动升级。

## 破坏性变更

- 无。该检查仍只读 ledger，不写状态、不生成样本、不升级 blocking。

## 验证范围

- `tests/test_check_burn_in_ledger.py`
- `tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_burn_in_ledger.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_burn_in_ledger.py --json`
