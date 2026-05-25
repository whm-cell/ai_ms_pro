# Template Readiness Summary

日期：2026-05-25

## 新增功能

- Governance workflow 现在把 sample template drift check 的默认报告、`needs-first-real-sample` 聚焦报告和 `needs-more-real-samples` 聚焦报告写入 step summary。
- Follow-up coverage 将 `check_harness_sample_templates.py --readiness needs-first-real-sample` 纳入 required command bundle。

## 修复问题

- 避免首样本 blocker 的 pending template drift 只能从默认总量中人工推断。
- 让 template drift、planner、intake、readiness 和 pending focus 的 readiness 聚焦面保持一致。

## 行为变化

- CI summary 增加只读 template drift sections，不写 ledger、不生成样本、不接受 pending row。
- 默认 CLI 行为不变；新增 workflow 调用只是显式使用现有 `--readiness` 过滤器。

## 破坏性变更

- 无。

## 验证范围

- `tests/test_governance_workflow_sample_outputs.py`
- `tests/test_harness_sample_followup_coverage.py`
- `tests/test_change_triggered_followups.py`
- `tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --readiness needs-first-real-sample`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --readiness needs-more-real-samples`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
