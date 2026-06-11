# Pending Capture Focus Cards

更新时间：2026-05-24
阶段或版本：stage-01
状态：已确认

## 新增功能

- `scripts/check_harness_pending_samples.py --capture-focus` 现在输出 compact read-only capture focus cards。
- 每张卡片包含 gap、ledger action、readiness、target artifact、target checker、planner、intake、lane review、trigger 和 boundary。

## 修复问题

- 修复 `next_capture_focus` 只能从完整 pending audit 中读取的问题，减少维护者在长队列输出中定位下一步采样面的成本。

## 行为变化

- `--capture-focus` 不写 ledger、不采集样本、不接受 pending row。
- 当过滤范围没有 capture focus entry 时，输出显式 no-match 消息并成功退出。

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_harness_pending_samples.py`
- `python3 tests/test_change_triggered_followups.py`
- `python3 tests/test_harness_sample_followup_coverage.py`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --gap-id GAP-WORKFLOW-TASK-PROFILE-AUDIT --capture-focus`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py --json`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
