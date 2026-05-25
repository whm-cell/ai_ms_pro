# 2026-05-25 Code Shape Burn-In Sample

## 新增功能

- `check_burn_in_ledger.py` 现在要求 accepted sample 的 `Evidence refs` 是存在的 repo-relative 文件引用。

## 修复问题

- 之前 ledger 只要求 accepted sample 有 evidence refs 文本，无法阻止不存在、绝对路径或逃逸仓库边界的引用。

## 行为变化

- `check_code_shape.py` 记录 1/2 accepted real changed-file sample。
- 本样本覆盖 `scripts/check_burn_in_ledger.py` 和 `tests/test_check_burn_in_ledger.py` 的本轮修改；`check_code_shape.py --all` 通过，未引入额外拆分或无关重构。

## 破坏性变更

- 无。`0/2` ledger 行仍可使用 `-` 作为 evidence refs；只有 accepted sample 大于 0 时才要求引用存在。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `tests/test_check_burn_in_ledger.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_burn_in_ledger.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_burn_in_ledger.py --json`
