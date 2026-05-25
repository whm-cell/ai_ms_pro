# Pending Ready Upgrade Gap List

更新时间：2026-05-24
阶段或版本：stage-01
状态：已确认

## 新增功能

- `scripts/check_harness_pending_samples.py` 的 stdout / JSON 报告现在显式输出 `ready_upgrade_decision_gaps`，当前列出 `GAP-WORKFLOW-TASK-PROFILE-AUDIT`。
- pending sample audit 的 QueueState / PendingSampleReport 现在保留 ready gap 的 upgrade-decision 列表，避免 ready gap 只出现在 next lane commands 里。

## 修复问题

- 修复 pending sample audit 文档已经宣称区分 ready upgrade-decision gap，但机器输出缺少独立 gap list 的漂移。

## 行为变化

- `--include-future --include-accepted` 输出会额外显示 `- ready upgrade-decision gaps: [...]`。
- `--json` 输出会额外包含 `ready_upgrade_decision_gaps` 字段。

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_harness_pending_samples.py`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --include-future --include-accepted`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --include-future --include-accepted --json`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
