# Upgrade Decision Next Evidence

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `scripts/check_harness_upgrade_decisions.py` now requires each ready-gap decision row to include `next_evidence_needed`.
- Text / JSON output exposes `next_evidence_needed_by_gap` so keep-advisory follow-up evidence is machine-readable.
- Upgrade-decision templates and `scripts/check_harness_upgrade_decision_candidate.py` now carry the same next-evidence list.
- Planner capture cards and intake summary / JSON now surface the same next-evidence list for `review-upgrade-decision` lanes.

## 修复问题

- Prevents the remaining evidence needed after a keep-advisory decision from being hidden inside free-form rationale.
- Keeps ready-gap replacement drafts aligned with the full decision audit schema.
- Prevents ready-gap intake summaries from showing only generic decision fields when the current keep-advisory row already names the follow-up evidence needed.

## 行为变化

- Existing ready-gap decisions remain keep-advisory.
- This only changes decision-review metadata and reporting; it does not add samples, accept evidence, write ADRs, or upgrade checks.

## 破坏性变更

- 无。

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_harness_upgrade_decisions tests.test_harness_upgrade_decision_candidate tests.test_plan_harness_sample_collection tests.test_harness_sample_intake_bundle tests.test_harness_sample_templates tests.test_tool_contracts`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_upgrade_decisions.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_upgrade_decisions.py --json`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --ledger-action review-upgrade-decision --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --ledger-action review-upgrade-decision --summary`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --ledger-action review-upgrade-decision --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --ledger-action review-upgrade-decision --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Open Items](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
