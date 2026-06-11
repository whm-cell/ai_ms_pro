# Pending Next Capture Focus

更新时间：2026-05-24
阶段或版本：stage-01
状态：已确认

## 新增功能

- `scripts/check_harness_pending_samples.py` 的 stdout / JSON 报告现在输出 bounded `next_capture_focus`。
- `next_capture_focus` 默认列出前 5 个 actionable without review-ready pending gaps，并为每个 gap 绑定 focused planner、intake 和 lane review command。

## 修复问题

- 修复 pending audit 只能列出完整 actionable gap 队列，维护者仍需手动判断下一步从哪个 gap 开始采集的问题。

## 行为变化

- `--json` 输出会额外包含 `next_capture_focus` 字段。
- 普通 text 输出会额外包含 `- next capture focus:` 段落。
- 该输出只辅助真实事件采集和复核，不写 ledger、不接受样本、不改变 readiness 计数。

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_harness_pending_samples.py`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --include-future --include-accepted`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
