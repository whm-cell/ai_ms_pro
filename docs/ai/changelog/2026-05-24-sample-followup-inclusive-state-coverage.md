# 2026-05-24 Sample Follow-up Inclusive State Coverage

## 新增功能

- `scripts/check_harness_sample_followup_coverage.py` 现在要求 sample-gap follow-up 命令包覆盖 future/local-inclusive 状态命令。

## 修复问题

- 避免后续 sample-gap 控制面变更只跑默认窄视图，而漏看 contract-blocked、local-only 和 ready-upgrade-decision lanes。

## 行为变化

- `scripts/change_triggered_harness_sample_rules.py` 的 `harness-sample-gap-evidence` follow-up 命令包新增：
  - `plan_harness_sample_collection.py --include-future --include-accepted --json`
  - `check_harness_pending_samples.py --include-future --include-accepted --json`
  - `check_harness_burn_in_readiness.py --include-future --include-accepted --json`

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_harness_sample_followup_coverage.py`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_change_triggered_followups.py --files scripts/check_harness_pending_samples.py --markdown`

## 关联文档

- `docs/ai/check-registry.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
- `.agents/skills/harness-maintenance/references/verification-commands.md`
