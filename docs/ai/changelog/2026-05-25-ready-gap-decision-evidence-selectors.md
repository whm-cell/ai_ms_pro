# Ready Gap Decision Evidence Selectors

更新时间：2026-05-25
阶段或版本：harness v1
状态：已确认

## 新增功能

- `check_harness_upgrade_decisions.py` 复用共享 `evidence_ref_utils` 校验 ready-gap upgrade decision 的 `evidence_refs`。

## 修复问题

- ready-gap upgrade decision ledger 现在允许 markdown anchor、pytest node id 和 JSONL 行号 selector，同时仍要求底层 repo-relative 路径存在。
- `scripts/evidence_ref_utils.py` 改动会触发 `harness-upgrade-decisions` follow-up，避免共享证据引用规则变化后遗漏 ready-gap decision audit。

## 行为变化

- ready-gap keep/promote/defer 决策可以精确引用章节、测试节点或 JSONL 行；该变更只提升决策证据可审计性，不新增样本、不接受样本、不升级 blocking。

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_harness_upgrade_decisions.py`
- `python3 tests/test_change_triggered_followups.py`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_upgrade_decisions.py`

## 关联文档

- [Check Registry](../check-registry.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Ready Gap Upgrade Decisions](../standards/harness-upgrade-decisions.jsonl)
