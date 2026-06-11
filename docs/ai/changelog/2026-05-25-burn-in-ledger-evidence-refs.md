# 2026-05-25 Burn-In Ledger Evidence Refs

## 新增功能

- `check_burn_in_ledger.py` 现在解析并输出 per-check `evidence_refs`。
- `Accepted samples` 大于 0 时必须有 `Evidence refs`，避免 blocking-candidate 样本计数不可审计。

## 修复问题

- 之前 blocking-candidate ledger 可以把 accepted sample 计数从 `0/2` 改成 `1/2`，但 checker 不要求同步记录可审计证据引用。

## 行为变化

- `check_burn_in_ledger.py` 的 markdown / JSON 输出现在会显示 evidence refs。
- accepted sample 大于 0 但缺少 evidence refs 时，checker 会失败。

## 样本进展

- `check_tool_contracts.py` 记录 1/2 accepted real contract-change sample。
- 样本证据引用本轮 `check_burn_in_ledger` tool contract 扩展、对应单测和 changelog。

## 破坏性变更

- 无。已存在的 `0/2` ledger 行可继续使用 `-` 作为 evidence refs。

## 行为边界

- 该变更不生成样本、不自动升级 blocking。
- `check_tool_contracts.py` 仍保持 `keep-candidate`；还需要 1 个新/变更 tool contract 的成功修复证据才进入升级讨论。

## 验证范围

- `tests/test_check_burn_in_ledger.py`
- `tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_burn_in_ledger.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_burn_in_ledger.py --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
