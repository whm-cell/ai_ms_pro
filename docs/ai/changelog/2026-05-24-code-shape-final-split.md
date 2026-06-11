# 2026-05-24 Code-shape Final Split

更新时间：2026-05-24
阶段或版本：stage-00 / harness maintenance
状态：已确认

## 新增功能

- 新增 `scripts/requirements_technical_assumptions.py`，承载 requirements 技术假设启发式检查。
- `check_change_triggered_followups.py` 现在会在 requirements shape helper 变化时提示 `requirements-traceability` follow-up。

## 修复问题

- 拆分 `check_code_shape.py` 的候选文件检查路径，消除 `check_candidate` 超过 warning 阈值的问题。
- 拆分 `check_requirements_shape.py` 的技术假设逻辑，消除 requirements checker 文件行数超过 warning 阈值的问题。
- 更新 working context、stage status、open items 和 burn-in ledger，移除已过期的既有 code-shape warning 描述。

## 行为变化

- `check_code_shape.py --all` 当前无 warning。
- Requirements shape CLI 和 code-shape CLI 入口保持不变。
- `check_code_shape.py` 仍是 `blocking-candidate`，本轮不做 blocking 升级。

## 破坏性变更

- 无。拆分只调整内部 helper 边界，不改变检查输入、输出或失败条件。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `.codex/hooks/run_with_repo_python.sh tests/test_code_shape_initial_commit.py`
- `.codex/hooks/run_with_repo_python.sh tests/test_requirements_shape.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_requirements_shape.py`
- `python3 tests/test_change_triggered_followups.py`
- `.codex/.venv/bin/python -m unittest discover -s tests`
- `.codex/.venv/bin/python -m ruff check .codex/hooks scripts tests`
- `git diff --check`

## 关联文档

- [Harness Remaining Work](../harness-open-items.md)
- [Working Context](../working-context.md)
- [Check Burn-in Ledger](../check-burn-in-ledger.md)
