# Upgrade Decision Candidate Review

- Date: 2026-05-24
- Scope: harness sample collection control plane
- Status: landed

## 新增功能

- 新增 `scripts/check_harness_upgrade_decision_candidate.py <candidate-jsonl>`，用于在人工替换 ready-gap upgrade decision 行前做 no-write candidate review。
- `review-upgrade-decision` lane 的 `upgrade_decision_review_command` 现在指向 candidate gate，next lane commands 仍保留 full `check_harness_upgrade_decisions.py` audit。

## 修复问题

- Upgrade-decision draft template 现在会复用已有 decision id，避免把 ready gap 决策草稿追加成 duplicate `gap_id` 行。

## 行为变化

- Planner / intake bundle / pending sample lane output 会先展示 `check_harness_upgrade_decision_candidate.py <candidate-jsonl>`，替换后再跑 `check_harness_upgrade_decisions.py`。
- Candidate gate 会校验当前 `review-upgrade-decision` lane、readiness snapshot 计数和现有 decision id。

## 破坏性变更

- 无。该工具只读仓库并输出 review report，不写 ledger、不写 ADR、不升级 blocking。

## 验证范围

- `python3 tests/test_harness_upgrade_decision_candidate.py`
- `python3 tests/test_harness_upgrade_decisions.py`
- `python3 tests/test_plan_harness_sample_collection.py`
- `python3 tests/test_harness_sample_intake_bundle.py`
- `python3 tests/test_harness_pending_samples.py`
- `python3 tests/test_harness_sample_followup_coverage.py`
- `python3 tests/test_change_triggered_followups.py`
- `python3 tests/test_tool_contracts.py`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/check-registry.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/tool-contracts/README.md`
- `.agents/skills/harness-maintenance/references/verification-commands.md`
