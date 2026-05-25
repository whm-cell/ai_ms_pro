# 2026-05-24 Ready Gap Upgrade Decision Lane

更新时间：2026-05-24
阶段或版本：stage-00 / agentic harness hardening
状态：已确认

## 新增功能

- `plan_harness_sample_collection.py` now routes `ready-for-upgrade-discussion` gaps to `review-upgrade-decision` and targets `docs/ai/standards/harness-upgrade-decisions.jsonl`.
- `build_harness_sample_intake_bundle.py --ledger-action review-upgrade-decision --summary` now emits the focused upgrade decision draft and review command.
- `check_harness_pending_samples.py` next-lane guidance now includes the `review-upgrade-decision` lane before future-work contract lanes.

## 修复问题

- 修复 ready gap 在默认 planner 队列里仍表现为 `append-new-pending-slot` 的路由歧义；Task Profile Audit 已有 upgrade decision，不应继续被当作缺 pending 样本处理。

## 行为变化

- Ready gaps now review keep/promote/defer decisions before collecting more samples.
- Upgrade-decision drafts are validated through `check_harness_upgrade_decisions.py`; they are not sample evidence and do not change accepted burn-in counts.
- Existing sample counts are unchanged.

## 破坏性变更

- 无。该变更只调整 read-only queue / intake / pending lane routing，不写 ledger、不升级 blocking、不接受样本。

## 验证范围

- `python3 tests/test_plan_harness_sample_collection.py`
- `python3 tests/test_harness_pending_samples.py`
- `python3 tests/test_harness_sample_intake_bundle.py`
- `python3 tests/test_harness_sample_templates.py`
- `python3 tests/test_harness_upgrade_decisions.py`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --ledger-action review-upgrade-decision --summary`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --include-future --include-accepted`
