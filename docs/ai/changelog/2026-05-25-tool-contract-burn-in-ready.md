# 2026-05-25 Tool Contract Burn-In Ready

## 新增功能

- Candidate Check Burn-in Ledger 现在显示 `check_tool_contracts.py` 已达到 2/2 accepted real contract-change samples。
- `check_burn_in_ledger` tool contract 明确说明 `upgrade_eligible` 只表示样本目标达成，不自动升级或阻断。

## 修复问题

- 之前 `check_tool_contracts.py` 还停在 1/2，无法在 burn-in ledger 中暴露已有第二个 contract-change 样本已经完成。

## 行为变化

- `check_tool_contracts.py` 从仍需样本列表中移除，并进入 `upgrade_eligible_checks`。
- 当前决策仍为 `keep-candidate`；下一步是 upgrade decision review，而不是直接改为 blocking。

## 破坏性变更

- 无。该变更只更新 evidence ledger 和说明，不改变 `check_tool_contracts.py` 的实际阻断等级。

## 验证范围

- `tests/test_check_burn_in_ledger.py`
- `tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_burn_in_ledger.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_burn_in_ledger.py --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
