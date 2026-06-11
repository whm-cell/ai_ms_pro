# Remote Interop Summary Views

日期：2026-05-25

## 新增功能

- Governance workflow 现在把 `requires-approved-remote-interop` 的 planner capture-card、template drift、intake summary 和 pending capture-focus 视图写入 step summary。
- Existing sample follow-up coverage 与 change-triggered sample-gap follow-up bundle 已覆盖同一组 remote interop 聚焦命令；本次把 CI summary surface 补齐到同等可见度。

## 修复问题

- 避免 `GAP-TRACE-REMOTE-INTEROP` 只出现在 readiness remote-interop 或全量 queue 中。
- 让 ADR-017 remote interop capture lane 与 placeholder replacement、security workflow event、bounded real incident、workflow task event、readiness filter、template drift 和 intake bundle 的 reporting surface 保持一致。

## 行为变化

- 新增视图只读，只显示需要 ADR-017 允许的真实 remote interop probe 的 trace-interop lane。
- 当前聚焦 `GAP-TRACE-REMOTE-INTEROP`，仍为 `needs-first-real-sample` 且 accepted real remote interop samples 为 0。
- 真实 remote interop probe 补全后仍必须先跑 `check_harness_sample_append.py <candidate-jsonl>`，再单独做 outcome review。

## 破坏性变更

- 无。

## 验证范围

- `tests/test_governance_workflow_sample_outputs.py`
- `tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --capture-gate requires-approved-remote-interop --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --capture-gate requires-approved-remote-interop`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --capture-gate requires-approved-remote-interop --summary`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus --capture-focus-gate requires-approved-remote-interop --capture-focus-limit 0`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
