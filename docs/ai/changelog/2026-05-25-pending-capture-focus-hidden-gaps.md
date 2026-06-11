# Pending Capture Focus Hidden Gaps

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `scripts/check_harness_pending_samples.py` 的默认 bounded `next_capture_focus` 现在输出 `next_capture_focus_hidden_gap_ids`。
- 普通 text 输出和 `--capture-focus` cards 会显示 hidden gap ids；`--capture-focus-limit 0` 或空过滤范围显示 `<none>`。

## 修复问题

- 修复默认只显示前 5 条 capture focus 时，后排 gap 只能从 area / priority / ledger-action / capture-gate / readiness bucket count 间接推断的问题。

## 行为变化

- JSON / text / capture-focus cards 均能直接交接被截断隐藏的 gap id。
- 该变更只改善 pending audit 可读性；不写 ledger、不生成样本、不接受 pending row、不批准 future-work sampling。

## 破坏性变更

- 无。

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_harness_pending_samples tests.test_tool_contracts`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --include-future --include-accepted --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Open Items](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
