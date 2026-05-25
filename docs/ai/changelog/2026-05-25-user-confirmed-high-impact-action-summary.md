# User Confirmed High Impact Action Summary

日期：2026-05-25

## 新增功能

- governance workflow 现在额外输出 `requires-user-confirmed-high-impact-action` 的 collection planner capture-card、sample template drift、intake summary 和 pending capture-focus 四个只读视图。
- 该 lane 当前只聚焦 P1 `GAP-GUARDRAIL-CONFIRMATION`，readiness 仍是 `needs-first-real-sample`，升级指标是 accepted real generic gap samples 0/2。
- 四个视图都会显示真实采集门槛：只有真实高影响动作且已有显式用户确认时才可进入候选复核。

## 修复问题

- 避免 `GAP-GUARDRAIL-CONFIRMATION` 只藏在 needs-first-real-sample 聚合视图里，导致采集者忽略 explicit user confirmation 这个前置条件。
- 避免把模板、普通 warning、未确认命令或未记录 rollback note 的动作误读为 accepted evidence。

## 行为变化

- follow-up coverage 和 change-triggered followups 现在要求同步运行这条 capture gate 的 planner、template、intake 和 pending focus 命令。
- tool contracts、check registry、roadmap 和 open-items 现在明确记录 user-confirmed high-impact action lane。
- 该变更只读展示采集队列，不写入 `docs/ai/standards/harness-sample-gap-evidence.jsonl`，也不授权任何高影响动作。

## 破坏性变更

- 无。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --capture-gate requires-user-confirmed-high-impact-action --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --capture-gate requires-user-confirmed-high-impact-action`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --capture-gate requires-user-confirmed-high-impact-action --summary`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus --capture-focus-gate requires-user-confirmed-high-impact-action --capture-focus-limit 0`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
