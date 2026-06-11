# 2026-05-25 Readiness Metric Deltas

## 新增功能

- `scripts/check_harness_burn_in_readiness.py` 现在在 text / JSON 输出 `accepted_real_readiness_metric_deltas`。
- 该字段列出账本级 accepted real 粗计与具体 readiness source metric 的差异，例如 Stage Checkpoint 的 accepted real ledger row 不等于 accepted cross-task resume sample，Local Trace raw report 不等于 distinct task-class 覆盖。

## 修复问题

- 降低把 `accepted_real_by_gap` 粗计误读成 readiness 已满足或可升级证据的风险。

## 行为变化

- 只读报告增加一个顶层 summary 字段。
- readiness 判定、采集队列、样本账本和 upgrade decision 账本均不变。

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_harness_burn_in_readiness.py`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --json`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
