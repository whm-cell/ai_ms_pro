# Active Area Priority Focus Coverage

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `scripts/check_harness_collection_config.py` now requires every active real-sample roadmap area and priority to have a matching pending capture-focus command in `HARNESS_SAMPLE_GAP_COMMANDS`.
- `scripts/check_harness_sample_followup_coverage.py` now requires the same active area / priority focus commands in its closed required command set.
- `tests/test_harness_collection_config.py` and `tests/test_harness_sample_followup_coverage.py` cover missing area / priority command drift.

## 修复问题

- Prevents a roadmap area or priority from being visible in pending focus parser choices but missing from the follow-up command package.
- Prevents future sample-gap handoffs from falling back to a full queue when an exact `--capture-focus-area` or `--capture-focus-priority` command should exist.

## 行为变化

- 只强化 read-only collection config 和 follow-up coverage audit.
- 不运行采集命令.
- 不生成模板.
- 不写 ledger.
- 不生成或接受样本.
- 不改变 readiness / upgrade decision.

## 破坏性变更

- 无.

## 验证范围

- `python3 tests/test_harness_collection_config.py`
- `python3 tests/test_harness_sample_followup_coverage.py`
- `.codex/.venv/bin/ruff check scripts/harness_collection_command_coverage.py scripts/check_harness_collection_config.py scripts/change_triggered_harness_sample_rules.py scripts/check_harness_sample_followup_coverage.py tests/test_harness_collection_config.py tests/test_harness_sample_followup_coverage.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_collection_config.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Remaining Work](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
