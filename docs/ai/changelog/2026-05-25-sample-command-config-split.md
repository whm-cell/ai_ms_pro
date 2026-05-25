# Sample Command Config Split

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `scripts/harness_collection_command_templates.py` 持有 collection / workflow focused command template 常量。
- `scripts/harness_sample_followup_coverage_config.py` 持有 sample follow-up discovery patterns 和 required command constants。
- 两个新 helper 均纳入 `harness-sample-gap-evidence` change-triggered follow-up 覆盖。

## 修复问题

- 消除了 `scripts/harness_collection_command_coverage.py` 和 `scripts/check_harness_sample_followup_coverage.py` 因常量块膨胀接近或超过 code-shape line budget 的维护风险。

## 行为变化

- 无采样行为变化。原有 collection config、follow-up coverage、workflow summary coverage 仍使用同一命令集合和同一只读审计语义。

## 破坏性变更

- 无。

## 验证范围

- `wc -l scripts/check_harness_sample_followup_coverage.py scripts/harness_collection_command_coverage.py scripts/harness_collection_command_templates.py scripts/harness_sample_followup_coverage_config.py`
- `.codex/.venv/bin/ruff check scripts/harness_collection_command_coverage.py scripts/harness_collection_command_templates.py scripts/check_harness_sample_followup_coverage.py scripts/harness_sample_followup_coverage_config.py scripts/change_triggered_harness_sample_rules.py tests/test_harness_sample_followup_coverage.py tests/test_tool_contracts.py`
- `python3 tests/test_harness_sample_followup_coverage.py`
- `python3 tests/test_harness_collection_config.py`
- `python3 tests/test_governance_workflow_sample_outputs.py`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_collection_config.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `.codex/.venv/bin/python -m unittest discover -s tests`
- `.codex/.venv/bin/ruff check .codex/hooks scripts tests`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus --capture-focus-limit 0`
- `git diff --check`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Tool Contracts](../tool-contracts/README.md)
- [AI 文档入口索引](../index.md)
