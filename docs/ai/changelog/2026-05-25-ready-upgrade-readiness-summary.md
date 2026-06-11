# Ready Upgrade Readiness Summary

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- Governance workflow 现在为 `--readiness ready-for-upgrade-discussion` 追加 collection planner capture-card、burn-in readiness、template drift 和 intake summary 视图。
- Change-triggered follow-up 覆盖和 tool contracts 同步要求这些 ready-readiness 聚焦命令。

## 修复问题

- 修复 ready gap 只能通过 `--capture-gate upgrade-decision-review` 或 ledger-action 视图间接发现的问题；现在可以直接按 readiness state 复核。

## 行为变化

- CI step summary 会单独展示 ready-for-upgrade-discussion 的 no-write review 面，便于人工复核 keep / promote / defer decision drafts。
- 该变更只改善治理可见性；不写 ledger、不生成样本、不接受 evidence、不升级 blocking。

## 破坏性变更

- 无。

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_governance_workflow_sample_outputs tests.test_harness_sample_followup_coverage tests.test_change_triggered_followups tests.test_tool_contracts`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --readiness ready-for-upgrade-discussion --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --readiness ready-for-upgrade-discussion --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --readiness ready-for-upgrade-discussion`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --readiness ready-for-upgrade-discussion --summary`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Open Items](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
