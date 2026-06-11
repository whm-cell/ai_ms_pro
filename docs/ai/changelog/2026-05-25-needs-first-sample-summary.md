# Needs-First Sample Summary

日期：2026-05-25

## 新增功能

- Governance workflow 现在把 `needs-first-real-sample` 的 collection capture-card、intake summary 和 pending capture focus 写入 step summary。
- Follow-up coverage 将 planner、intake 和 pending capture focus 的 `needs-first-real-sample` 命令纳入 required command bundle。

## 修复问题

- 避免首个真实样本缺口只出现在 readiness 表格、全量队列或 capture-focus bucket count 中。
- 当前 CI summary 可直接看到 14 条首样本 blocker 的 target artifact、review command、capture gate 和 bounded evidence checklist。

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
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --readiness needs-first-real-sample`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --readiness needs-first-real-sample --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --readiness needs-first-real-sample --summary`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus --capture-focus-readiness needs-first-real-sample --capture-focus-limit 0`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
