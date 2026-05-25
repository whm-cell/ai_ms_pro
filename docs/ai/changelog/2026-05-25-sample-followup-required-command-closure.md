# Sample Follow-up Required Command Closure

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `check_harness_sample_followup_coverage.py` now requires `REQUIRED_COMMANDS` to exactly cover the routed `HARNESS_SAMPLE_GAP_COMMANDS` package.
- Required commands now include missing unit test commands for gap evidence, sample gaps, planner, templates, intake, placeholder replacement, readiness, pending, and future-work contracts.
- Required commands now include the unfiltered intake bundle and unfiltered readiness audit commands.

## 修复问题

- Fixed follow-up coverage audit passing when routed sample-gap commands were not represented in `REQUIRED_COMMANDS`.
- Prevents future route/helper changes from silently omitting core unit tests or baseline CLI outputs.

## 行为变化

- 只强化 follow-up coverage audit。
- 不写 ledger。
- 不生成或接受样本。
- 不改变 readiness / upgrade decision。

## 破坏性变更

- 无。

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_harness_sample_followup_coverage tests.test_tool_contracts`
- `.codex/.venv/bin/ruff check scripts/check_harness_sample_followup_coverage.py tests/test_harness_sample_followup_coverage.py tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Open Items](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
