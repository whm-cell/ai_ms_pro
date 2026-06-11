# Needs-More Sample Summary

日期：2026-05-25

## 新增功能

- Governance workflow 现在把 `needs-more-real-samples` 聚焦视图写入 step summary。
- 新增聚焦输出包括 readiness audit、sample collection capture-card、intake summary 和 pending capture focus。
- Follow-up coverage 将 `check_harness_burn_in_readiness.py --readiness needs-more-real-samples --json` 纳入 required command bundle。

## 修复问题

- 避免已有 first sample 但仍未达到 upgrade target 的 lane 只出现在全量表格或 bucket count 中。
- 当前可直接在 CI summary 中看到 `GAP-TRACE-LOCAL-SUMMARY-BURNIN` 仍需 distinct task-class report。

## 行为变化

- CI summary 增加只读 sections，不写 ledger、不生成样本、不接受 pending row。
- 默认 CLI 行为不变；新增 workflow 调用只是显式使用现有 `--readiness` / `--capture-focus-readiness` 过滤器。

## 破坏性变更

- 无。

## 验证范围

- `tests/test_governance_workflow_sample_outputs.py`
- `tests/test_harness_sample_followup_coverage.py`
- `tests/test_change_triggered_followups.py`
- `tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --readiness needs-more-real-samples`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --readiness needs-more-real-samples --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --readiness needs-more-real-samples --summary`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus --capture-focus-readiness needs-more-real-samples --capture-focus-limit 0`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
