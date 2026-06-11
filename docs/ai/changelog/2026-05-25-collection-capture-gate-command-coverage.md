# Collection Capture-Gate Command Coverage

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `check_harness_collection_config.py` now validates active capture gates, ledger actions, and readiness states emitted by the inclusive readiness report against CLI choice constants.
- Real-sample capture gates now require focused planner, template, intake, readiness, and pending-focus commands in `HARNESS_SAMPLE_GAP_COMMANDS`.
- The collection config report now prints active capture gate counts and real-sample capture gate counts.

## 修复问题

- Prevents adding a new real-sample capture gate without adding the corresponding focused command package.
- Prevents readiness routing from emitting capture gates, ledger actions, or readiness states that cannot be selected through the CLI.

## 行为变化

- 只强化 collection routing drift audit。
- 不写 ledger。
- 不生成或接受样本。
- 不改变 readiness / upgrade decision。

## 破坏性变更

- 无。

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_harness_collection_config tests.test_tool_contracts`
- `.codex/.venv/bin/ruff check scripts/check_harness_collection_config.py tests/test_harness_collection_config.py tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_collection_config.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Open Items](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
