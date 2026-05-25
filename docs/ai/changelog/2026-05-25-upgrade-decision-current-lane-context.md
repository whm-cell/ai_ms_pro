# Upgrade Decision Current Lane Context

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- Added `scripts/harness_upgrade_decision_context.py` so single-row upgrade decision candidate review re-resolves the current `review-upgrade-decision` queue item before allowing a bounded decision replacement.
- `scripts/check_harness_upgrade_decision_candidate.py` now reports current `ledger_action`, readiness, source metric, current / target, capture gate, evidence checklist, trigger, and boundary from the queue instead of trusting the candidate JSON to describe the lane.

## 修复问题

- Avoids reviewing stale keep/promote/defer drafts after a gap has left the current ready-gap decision lane.
- Keeps candidate review output aligned with append / replacement / outcome gates, where reviewers see current queue context rather than candidate self-description.

## 行为变化

- Existing ready-gap decisions remain keep-advisory.
- This only changes no-write candidate review metadata and reporting; it does not add samples, accept evidence, write ADRs, or upgrade checks.

## 破坏性变更

- 无。

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_harness_upgrade_decision_candidate tests.test_tool_contracts`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --ledger-action review-upgrade-decision`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Open Items](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
