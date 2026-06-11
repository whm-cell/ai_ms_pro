# Sandbox Honesty Upgrade Decision

日期：2026-05-25

## 新增功能

- `docs/ai/security/agentic-red-team-samples.jsonl` 新增第 2 个 `sandbox-claim-honesty` accepted real incident，覆盖 goal continuation 中 stale CLI / prior context 不得替代当前命令证据的边界。
- `docs/ai/standards/harness-upgrade-decisions.jsonl` 新增 `GAP-AGENTIC-SANDBOX-HONESTY` 的 keep-advisory 决策；该 gap 已达到 2/2 real-incident 门槛，但不升级 blocking。

## 修复问题

- `scripts/check_harness_sample_templates.py` 的 upgrade decision 模板复核改为单条 candidate gate，避免多个 ready gap 同时存在时单条模板因缺另一条 ready decision 被误判失败。
- `scripts/harness_sample_templates.py` 的 red-team upgrade decision 草稿现在指向 red-team sample ledger / roadmap 证据，而不是 task-profile audit refs。

## 行为变化

- `GAP-AGENTIC-SANDBOX-HONESTY` 从 `needs-more-real-samples` 前进到 `ready-for-upgrade-discussion`，并进入 `review-upgrade-decision` lane。
- 当时 ready gaps 为 `GAP-WORKFLOW-TASK-PROFILE-AUDIT` 与 `GAP-AGENTIC-SANDBOX-HONESTY`，二者均记录 keep-advisory；后续 source-boundary ready 决策见同日独立 changelog。

## 破坏性变更

- 无。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_agentic_red_team_samples.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_upgrade_decisions.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --ledger-action review-upgrade-decision --summary`
- `python3 tests/test_agentic_red_team_samples.py`
- `python3 tests/test_harness_upgrade_decisions.py`
- `python3 tests/test_harness_upgrade_decision_candidate.py`
- `python3 tests/test_harness_burn_in_readiness.py`
- `python3 tests/test_harness_sample_templates.py`
- `python3 tests/test_harness_sample_intake_bundle.py`
- `python3 tests/test_plan_harness_sample_collection.py`
- `python3 tests/test_harness_pending_samples.py`
- `python3 tests/test_harness_sample_gaps.py`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Remaining Work](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Agentic Red-Team Samples](../security/agentic-red-team-samples.md)
