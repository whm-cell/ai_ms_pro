# Harness Upgrade Decision Evidence Refs

更新时间：2026-05-25
阶段或版本：STAGE-01
状态：已确认

## 新增功能

- `check_harness_upgrade_decisions.py` 现在校验 ready-gap upgrade decision 的 `evidence_refs` 必须是存在的 repo-relative 路径。

## 修复问题

- 过去只要求 `evidence_refs` 是非空字符串列表；缺失文件、绝对路径或逃出仓库的引用可能通过 shape 校验。

## 行为变化

- upgrade decision ledger 继续拒绝 `.codex/runtime` 原始材料，并新增拒绝 missing、absolute 或 escaping evidence refs。
- 当前四个 ready gap 仍保持 `keep-advisory`；本次不新增样本、不改 check level、不写 ADR。

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_harness_upgrade_decisions.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_upgrade_decisions.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_upgrade_decisions.py --json`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `check_code_shape.py --all`
- `unittest discover`
- `ruff`
- `check_ai_governance.py`
- `git diff --check`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
