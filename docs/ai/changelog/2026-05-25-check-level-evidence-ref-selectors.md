# Check-Level Evidence Ref Selectors

更新时间：2026-05-25
阶段或版本：harness v1
状态：已确认

## 新增功能

- `check_burn_in_ledger.py` 与 `check_burn_in_upgrade_decisions.py` 复用共享 `evidence_ref_utils` 校验 check-level evidence refs。

## 修复问题

- check-level burn-in ledger 和 check-level upgrade decision ledger 现在允许 markdown anchor、pytest node id 和 JSONL 行号 selector，同时仍要求底层 repo-relative 路径存在。
- `scripts/evidence_ref_utils.py` 改动会触发这两个 checker 的 changed-file follow-up，避免共享引用规则变化后遗漏 check-level 决策账本。

## 行为变化

- 证据引用可以更精确地指向具体章节、测试节点或 JSONL 行；该变更只提升可审计性，不新增样本、不接受样本、不升级 blocking。

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_check_burn_in_ledger.py`
- `python3 tests/test_burn_in_upgrade_decisions.py`
- `python3 tests/test_change_triggered_followups.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_burn_in_ledger.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_burn_in_upgrade_decisions.py`

## 关联文档

- [Check Burn-in Ledger](../check-burn-in-ledger.md)
- [Check Registry](../check-registry.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
