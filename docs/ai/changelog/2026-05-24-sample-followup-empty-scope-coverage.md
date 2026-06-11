# 2026-05-24 Sample Follow-up Empty Scope Coverage

## 新增功能

- `scripts/check_harness_sample_followup_coverage.py` 现在要求 sample-gap follow-up 命令包覆盖 planner、intake bundle 和 pending audit 的 empty-scope regression 命令。

## 修复问题

- 避免后续改 sample collection renderer、intake renderer 或 pending audit 时，只触发主检查命令而漏跑空过滤范围回归。

## 行为变化

- `scripts/change_triggered_harness_sample_rules.py` 的 `harness-sample-gap-evidence` follow-up 命令包新增：
  - `plan_harness_sample_collection.py --gap-id GAP-DOES-NOT-EXIST --capture-card`
  - `build_harness_sample_intake_bundle.py --gap-id GAP-DOES-NOT-EXIST --summary`
  - `check_harness_pending_samples.py --gap-id GAP-DOES-NOT-EXIST`
  - `check_harness_pending_samples.py --review-state review-ready --review-cards`

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_harness_sample_followup_coverage.py`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_change_triggered_followups.py --files scripts/harness_sample_intake_render.py --markdown`

## 关联文档

- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
- `.agents/skills/harness-maintenance/references/verification-commands.md`
