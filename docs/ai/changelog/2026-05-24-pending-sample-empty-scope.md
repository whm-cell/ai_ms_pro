# 2026-05-24 Pending Sample Empty Scope

## 新增功能

- `scripts/check_harness_pending_samples.py` 的普通 text 输出在过滤后既无 sample records、也无 collection queue entries 时，会打印显式 no-match 和边界说明。

## 修复问题

- 避免 `--gap-id GAP-DOES-NOT-EXIST` 这类空范围只输出一组 0，被人工或 CI 摘要误读为已完成 evidence 结论。
- 保持 future-work contract、ready upgrade-decision、local-only 等仍有 queue 状态的 gap 不会被误标为空。

## 行为变化

- JSON 输出结构不变。
- `--review-cards` 既有 empty-state 行为不变。
- 空 text scope 继续成功退出，但现在明确说明不会采集样本、改变 outcome 或证明 gap 完成。

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_harness_pending_samples.py`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --gap-id GAP-DOES-NOT-EXIST`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --include-future --gap-id GAP-TRACE-REMOTE-INTEROP`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
- `.agents/skills/harness-maintenance/references/verification-commands.md`
