# 2026-05-25 Code Shape Follow-Up Rule Sample

## 新增功能

- Candidate Check Burn-in Ledger 现在把 follow-up rule wiring slice 记录为 `check_code_shape.py` 的第二个 accepted real changed-file sample。
- `check_code_shape.py` 达到 2/2 后仍保持 `keep-candidate`，并进入 check-level upgrade decision review。
- `docs/ai/standards/check-burn-in-upgrade-decisions.jsonl` 新增 `check_code_shape.py` 的 bounded keep-candidate 决策，后续证据指向非 harness changed-file 样本和误报 / reviewer cost 复核。

## 修复问题

- 本轮新增 check-level upgrade decision follow-up 规则时，`scripts/change_triggered_followup_rules.py` 一度超过 350 行预算；`check_code_shape.py --all` 暴露了这个 shape drift，随后通过压缩窄规则行恢复到预算内。

## 行为变化

- `check_code_shape.py` 从仍需样本列表中移除，并进入 `upgrade_eligible_checks` / `upgrade_review_needed_checks`。
- 该样本只证明 harness follow-up rule 改动下的 code-shape warning 有用；不证明应直接升级为 blocking。
- 当前决策仍为 `keep-candidate`；下一步不是改等级，而是继续收集更广泛的 changed-file 样本。

## 破坏性变更

- 无。该变更只更新 evidence ledger 和说明，不改变 `check_code_shape.py` 的实际阻断等级。

## 验证范围

- `tests/test_change_triggered_followups.py`
- `tests/test_check_burn_in_ledger.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `.codex/hooks/run_with_repo_python.sh scripts/check_burn_in_ledger.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_burn_in_ledger.py --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_burn_in_upgrade_decisions.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_burn_in_upgrade_decisions.py --json`
