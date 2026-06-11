# Collection Ledger-action Command Coverage

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `scripts/check_harness_collection_config.py` now reports active real-sample ledger-action count.
- Active real-sample ledger actions now require lane-wide planner, template, intake, and pending-focus full-expansion commands in `HARNESS_SAMPLE_GAP_COMMANDS`.
- The check now catches append / placeholder-fill lane command drift before collection queue changes reach CI summary.
- Focused command templates live in `scripts/harness_collection_command_coverage.py` so `scripts/check_harness_collection_config.py` stays under the code-shape line budget.

## 修复问题

- Fixed a coverage asymmetry where active capture gates had focused command coverage but active real-sample ledger actions did not.
- Prevents future append or placeholder-fill lane changes from losing lane-wide focused views silently.

## 行为变化

- 只强化 collection routing drift audit.
- 不生成模板.
- 不写 ledger.
- 不生成或接受样本.
- 不改变 readiness / upgrade decision.

## 破坏性变更

- 无.

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_harness_collection_config tests.test_tool_contracts`
- `.codex/.venv/bin/ruff check scripts/check_harness_collection_config.py tests/test_harness_collection_config.py tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_collection_config.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Remaining Work](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
