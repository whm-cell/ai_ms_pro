# Pending Ready Next Evidence

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `scripts/check_harness_pending_samples.py` 现在在 text / JSON 输出 `ready_upgrade_decision_next_evidence_by_gap`。
- 该字段从当前 collection queue 的 `review-upgrade-decision` items 派生，复用 upgrade-decision ledger 的 `next_evidence_needed` 快照。

## 修复问题

- 修复 pending audit 已列出 ready upgrade-decision gaps 和 lane commands，但不能直接看到 keep-advisory 后续证据需求的问题。

## 行为变化

- 该变更只补齐 pending audit 控制面可见性；不写 ledger、不生成样本、不接受 pending row、不升级 blocking。

## 破坏性变更

- 无。

## 验证范围

- `.codex/.venv/bin/ruff check scripts/harness_pending_sample_report.py scripts/check_harness_pending_samples.py tests/test_harness_pending_samples.py tests/test_tool_contracts.py`
- `python3 tests/test_harness_pending_samples.py`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --include-future --include-accepted`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
