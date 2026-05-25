# No-Sample Template Skip

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `scripts/check_harness_sample_templates.py` 现在在 text / JSON 输出中报告 `skipped_no_sample_collection_count` 和 `skipped_no_sample_collection_gap_ids`。
- Governance workflow 追加 `--readiness local-sample-only` 的 template drift 视图，用来固定 local-only no-collection 路径。
- Governance workflow 追加 `plan_harness_sample_collection.py --include-accepted --readiness local-sample-only --capture-card` 和 `check_harness_burn_in_readiness.py --include-future --include-accepted --readiness local-sample-only` 视图，让 local-only `no-sample-collection` 边界在 planner/readiness summary 中可见。
- `scripts/harness_sample_template_records.py` 从模板入口中拆出具体 record 构造函数，避免 `scripts/harness_sample_templates.py` 超过 code-shape 行数预算。
- Change-triggered sample-gap follow-up required commands 现在包含 local-sample-only 的 planner capture-card、template drift 和 readiness JSON 命令。

## 修复问题

- 修复 local-only `no-sample-collection` gap 被 template drift check 当成普通 pending placeholder 草稿的问题。
- 当前 `GAP-TRACE-OTLP-PILOT-BURNIN` 会保持 inclusive 可见性，但不会生成可追加到样本账本的草稿。

## 行为变化

- `--readiness local-sample-only` 的 template drift 报告现在显示 `templates checked: 0`，并列出被跳过的 gap id。
- local-sample-only planner capture-card / readiness 输出只暴露 `no-sample-collection` 路由；intake bundle 和 pending capture-focus 仍然不把 local-only accepted gap 当成下一条可采集样本 lane。
- 该变更只改只读治理面；不写 ledger、不生成样本、不接受 evidence、不升级 blocking。

## 破坏性变更

- 无。

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_harness_sample_templates tests.test_tool_contracts`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --readiness local-sample-only`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --readiness local-sample-only --json`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --include-accepted --readiness local-sample-only --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --readiness local-sample-only --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`
- `.codex/.venv/bin/python -m unittest tests.test_harness_sample_followup_coverage tests.test_change_triggered_followups`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Open Items](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
