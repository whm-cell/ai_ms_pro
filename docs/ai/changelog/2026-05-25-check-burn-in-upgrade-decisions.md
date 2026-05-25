# 2026-05-25 Check Burn-In Upgrade Decisions

## 新增功能

- 新增 `scripts/check_burn_in_upgrade_decisions.py`，校验 blocking-candidate burn-in ledger 中 `upgrade_review_needed_checks` 是否都有 bounded check-level upgrade decision。
- 新增 `docs/ai/standards/check-burn-in-upgrade-decisions.jsonl`，记录 `check_code_shape.py` 与 `check_tool_contracts.py` 达到 2/2 accepted samples 后仍保持 `keep-candidate` 的复核决策。
- `check_burn_in_upgrade_decisions` 已登记 tool contract 并接入 governance workflow / changed-file follow-up，覆盖 no-write 审计、JSON 输出、step summary、快照校验、existing repo-relative evidence refs 和本地 runtime 引用边界。

## 修复问题

- 之前 `check_burn_in_ledger.py` 可以暴露 `upgrade_review_needed_checks`，但缺少独立账本校验这些 check 是否已经完成人工可审计的 keep / promote / demote 决策。

## 行为变化

- `check_code_shape.py` 与 `check_tool_contracts.py` 当前仍保持 `keep-candidate`；2/2 sample target 只触发 upgrade decision review，不触发 level change。
- 新 checker 会拒绝缺失决策、重复 check、过期 accepted/sample/current-decision 快照、缺失后续证据、缺失/越界/不存在的 evidence refs，以及 `.codex/runtime/` 本地原料引用。

## 破坏性变更

- 无。该变更只增加 no-write 决策审计和文档账本，不改变任何 check 的阻断等级，不生成样本，不写 ADR。

## 验证范围

- `tests/test_burn_in_upgrade_decisions.py`
- `tests/test_tool_contracts.py`
- `tests/test_governance_workflow_sample_outputs.py`
- `tests/test_change_triggered_followups.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_burn_in_upgrade_decisions.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_burn_in_upgrade_decisions.py --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
