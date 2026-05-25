# Append Replacement Focused Routing

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `check_harness_sample_append.py` 的 text / JSON report 现在输出当前 gap 的 focused `planner_command` 与 `intake_command`。
- `check_harness_placeholder_replacement.py` 的 text / JSON report 现在输出当前 gap 的 focused `planner_command` 与 `intake_command`。
- 两个字段由 `harness_sample_review_context.py` 通过当前 collection queue 统一生成，避免复核者手写 `--gap-id` 路由。

## 修复问题

- 避免 append / replacement review 失败或需要回看采集上下文时，复核者必须重新打开 planner 或 intake bundle 才能找到同一个 gap 的命令。
- 降低 stale lane 或手写命令造成的复核偏差。

## 行为变化

- JSON report 新增 `planner_command` 与 `intake_command` 字段。
- 不改 CLI 参数。
- 不写 ledger。
- 不接受或拒绝任何样本。
- 不改变 readiness、capture gate、review state 或 upgrade decision。

## 破坏性变更

- 无；既有 JSON 字段不移除、不重命名。

## 验证范围

- `.codex/.venv/bin/python -m unittest tests/test_harness_sample_append.py tests/test_harness_placeholder_replacement.py`
- `.codex/.venv/bin/ruff check scripts/check_harness_sample_append.py scripts/check_harness_placeholder_replacement.py scripts/harness_sample_review_context.py tests/test_harness_sample_append.py tests/test_harness_placeholder_replacement.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Open Items](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
