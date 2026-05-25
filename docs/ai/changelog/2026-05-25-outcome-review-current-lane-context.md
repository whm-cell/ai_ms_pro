# Outcome Review Current Lane Context

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `check_harness_sample_outcome.py` 的 no-write report 现在输出当前 `review-existing-pending-slot` lane 的 `ledger_action`、readiness、source metric、current / target、`capture_gate`、`capture_gate_detail`、`evidence_needed`、trigger 和 boundary。
- Outcome review gate 现在确认 candidate gap 当前仍属于 `review-existing-pending-slot` lane。

## 修复问题

- 避免 replacement / append 通过后，后续 outcome review 只能看到 pending row 与 checker 结果，却看不到当前 queue 是否仍把该 gap 路由到 outcome-review。
- 避免过期 pending row 在 readiness、pending-slot 状态或 lane 已变化后继续被误改成 accepted / rejected。

## 行为变化

- 不写 ledger。
- 不接受样本。
- 不改变 readiness 或 upgrade decision。
- 不把 candidate 或 report 计为 accepted evidence。

## 破坏性变更

- 无。

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_harness_sample_outcome tests.test_tool_contracts`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --pending-state with-review-ready-pending`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Open Items](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
