# Pending Report Code Shape Split

日期：2026-05-25

## 新增功能

- 新增 `scripts/harness_pending_review_cards.py`，把 pending review card 数据类、复核命令绑定和边界文案组装从 pending sample report 主模块中拆出。
- `harness-sample-gap-evidence` change-triggered 路由和 tool-contract registry 现在显式覆盖新的 pending review card helper。

## 修复问题

- `scripts/harness_pending_sample_report.py` 不再同时承担 review card helper 职责，降低 repo-wide code-shape warning 风险。
- `report_from_accounting` 的 capture-focus 字段组装已下沉到 `harness_pending_capture_focus.report_fields`，避免 pending report 主模块继续膨胀并移除行数预算 warning。

## 行为变化

- `check_harness_pending_samples.py` 的 stdout / JSON / `--review-cards` 输出语义保持不变。
- 改动 review card helper 时，会继续触发 sample-gap follow-up 和 harness code-shape follow-up。

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_harness_pending_samples.py`
- `python3 tests/test_change_triggered_followups.py`
- `python3 tests/test_harness_sample_followup_coverage.py`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus --capture-focus-limit 0`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `.codex/.venv/bin/python -m ruff check .codex/hooks scripts tests`
- `git diff --check`
- `python3 scripts/check_ai_governance.py`
- `.codex/.venv/bin/python -m unittest discover tests`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Tool Contracts](../tool-contracts/contracts.json)
- [Harness Maintenance Verification Commands](../../../.agents/skills/harness-maintenance/references/verification-commands.md)
