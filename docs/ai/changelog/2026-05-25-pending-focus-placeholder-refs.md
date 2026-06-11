# Pending Focus Placeholder Refs

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `scripts/check_harness_pending_samples.py` 的 `next_capture_focus` entries 现在为 placeholder replacement lane 输出 `pending_slot_refs` 和 `pending_review_blockers`。
- `--capture-focus` cards 现在显示 `Pending refs` 和 `Pending blockers`，直接指出要替换的 pending sample id、ledger ref 和当前 review blockers。

## 修复问题

- 修复采集者看到 `fill-existing-placeholder` focus card 后，还需要再打开 `--review-cards` 才知道具体替换哪一行的问题。

## 行为变化

- 该变更只让 placeholder replacement handoff 自包含；不写 ledger、不生成样本、不接受 pending row、不把 placeholder 计为 burn-in evidence。

## 破坏性变更

- 无。

## 验证范围

- `.codex/.venv/bin/ruff check scripts/harness_pending_capture_focus.py scripts/harness_pending_capture_focus_filters.py scripts/harness_pending_capture_focus_slots.py scripts/harness_pending_capture_focus_render.py scripts/harness_pending_sample_report.py scripts/check_harness_pending_samples.py tests/test_harness_pending_samples.py tests/test_tool_contracts.py`
- `python3 tests/test_harness_pending_samples.py`
- `python3 tests/test_tool_contracts.py`
- `python3 tests/test_change_triggered_followups.py`
- `python3 tests/test_harness_sample_followup_coverage.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus --capture-focus-limit 1`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
