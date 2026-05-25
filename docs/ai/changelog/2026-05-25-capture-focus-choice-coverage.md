# Capture Focus Choice Coverage

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `scripts/check_harness_collection_config.py` now reports active real-sample area and priority counts.
- Active real-sample area / priority / ledger-action / capture-gate / readiness values now have to remain supported by `check_harness_pending_samples.py --capture-focus-*` choices.
- The shared value extraction and choice audit live in `scripts/harness_collection_command_coverage.py` so the collection config checker stays within code-shape budget.

## 修复问题

- Prevents future roadmap area or priority additions from being visible in the full queue but unavailable through capture-focus filters.
- Prevents pending capture-focus parser choices from drifting away from the active real-sample queue after a new real-sample lane is introduced.

## 行为变化

- 只强化 collection routing drift audit.
- 不生成模板.
- 不写 ledger.
- 不生成或接受样本.
- 不改变 readiness / upgrade decision.

## 破坏性变更

- 无.

## 验证范围

- `python3 tests/test_harness_collection_config.py`
- `.codex/.venv/bin/ruff check scripts/check_harness_collection_config.py scripts/harness_collection_command_coverage.py tests/test_harness_collection_config.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_collection_config.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Remaining Work](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
