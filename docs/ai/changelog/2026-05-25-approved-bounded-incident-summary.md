# Approved Bounded Incident Summary

日期：2026-05-25

## 新增功能

- governance workflow 现在额外输出 `requires-approved-bounded-incident` 的 collection planner capture-card、sample template drift、intake summary 和 pending capture-focus 四个只读视图。
- 该 lane 当前只聚焦 P2 `GAP-AGENTIC-CASCADE-STOP`，readiness 仍是 `needs-first-real-sample`，升级指标是 accepted real red-team incidents for risk 0/2。
- 四个视图都会显示 ADR-016 采样门槛：只有 bounded local cascade-control incident 才能进入候选复核。

## 修复问题

- 避免 `GAP-AGENTIC-CASCADE-STOP` 只通过 generic red-team 或 gap-id 视图可见，导致 ADR-016 approved bounded incident 前置条件不够显眼。
- 避免把 local-replay 样本、模板、future-work contract approval 或未去除 raw prompt / transcript / secret / external payload 的材料误读为 accepted real incident evidence。

## 行为变化

- follow-up coverage 和 change-triggered followups 现在要求同步运行这条 capture gate 的 planner、template、intake 和 pending focus 命令。
- tool contracts、check registry、roadmap 和 open-items 现在明确记录 approved bounded incident lane。
- 该变更只读展示采集队列，不写入 `docs/ai/security/agentic-red-team-samples.jsonl`，也不接受 incident evidence。

## 破坏性变更

- 无。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --capture-gate requires-approved-bounded-incident --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --capture-gate requires-approved-bounded-incident`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --capture-gate requires-approved-bounded-incident --summary`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus --capture-focus-gate requires-approved-bounded-incident --capture-focus-limit 0`

## 关联文档

- `docs/ai/adr/ADR-016-agentic-cascade-stop-boundary.md`
- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
