# Cross-Task Resume Summary Views

日期：2026-05-25

## 新增功能

- Governance workflow 现在把 `requires-cross-task-resume` 的 planner capture-card、template drift、intake summary 和 pending capture-focus 视图写入 step summary。
- Sample follow-up coverage 与 change-triggered sample-gap follow-up bundle 现在要求同一组 cross-task resume 聚焦命令。

## 修复问题

- 避免 `GAP-RUNTIME-STAGE-CHECKPOINT-RESUME` 只藏在 full queue 或 needs-first-real-sample 聚合视图中。
- 让 Stage Checkpoint cross-task resume lane 与 remote interop、placeholder replacement、security workflow event、bounded real incident 和 workflow task event 的 reporting surface 保持一致。

## 行为变化

- 新增视图只读，只显示需要真实跨任务 resume 的 Stage Checkpoint lane。
- 当前聚焦 `GAP-RUNTIME-STAGE-CHECKPOINT-RESUME`，该 gap 仍为 `needs-first-real-sample`，accepted cross-task resume samples 为 0/2。
- Stage Checkpoint 已有 accepted real ledger row 不等于 cross-task readiness；真实样本必须来自 harness-hardening 任务类之外的 resume。
- 真实 cross-task resume 补全后仍必须先跑 `check_harness_sample_append.py <candidate-jsonl>`，再单独做 outcome review。

## 破坏性变更

- 无。

## 验证范围

- `tests/test_governance_workflow_sample_outputs.py`
- `tests/test_harness_sample_followup_coverage.py`
- `tests/test_change_triggered_followups.py`
- `tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --capture-gate requires-cross-task-resume --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --capture-gate requires-cross-task-resume`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --capture-gate requires-cross-task-resume --summary`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus --capture-focus-gate requires-cross-task-resume --capture-focus-limit 0`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
