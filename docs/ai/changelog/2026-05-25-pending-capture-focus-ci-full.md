# 2026-05-25 Pending Capture Focus Full CI Summary

更新时间：2026-05-25
阶段或版本：stage-01
状态：已确认

## 新增功能

- Governance workflow 的 pending sample audit step 现在除了默认 `--capture-focus` 视图，还会追加 `--capture-focus --capture-focus-limit 0` 的 full-expansion 视图。
- `tests/test_governance_workflow_sample_outputs.py` 覆盖新增的 full-expansion 输出文件和 step-summary section。
- `check-registry`、tool contracts、roadmap、open items 和 `$harness-maintenance` verification reference 同步说明 CI 会显示默认截断视图和全量 matching lane 视图。

## 修复问题

- 避免默认 focus 只显示前 5 个 actionable capture lanes 时，CI summary 里只能靠 bucket count 推断后面还有 P2/P3 / area lanes。
- 避免维护者需要手动重跑 `--capture-focus-limit 0` 才能在 CI 复核中看到全部真实采集入口。

## 行为变化

- CI step summary 会同时包含默认 focus 和 full-expansion focus。
- full-expansion 视图仍然是 read-only；它只让真实样本采集入口更可见，不写 ledger、不接受 pending row、不改变 readiness。

## 破坏性变更

- 无。默认 `--capture-focus` CLI 行为不变；新增 CI 输出不生成或接受任何样本。

## 验证范围

- `python3 tests/test_governance_workflow_sample_outputs.py`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus --capture-focus-limit 0`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
