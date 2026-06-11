# Source Boundary Upgrade Decision

日期：2026-05-25

## 新增功能

- Accepted `GAP-SAMPLE-2026-05-25-source-boundary-priority` as the second bounded real sample for `GAP-GUARDRAIL-SOURCE-BOUNDARY`.
- Recorded `HUD-2026-05-25-source-boundary-keep-advisory` in `docs/ai/standards/harness-upgrade-decisions.jsonl`.

## 修复问题

- Moved source-boundary from `append-new-pending-slot` into `review-upgrade-decision`, leaving default capture focus at 16 actionable sample gaps.

## 行为变化

- The 2/2 threshold is enough for upgrade discussion, not for blocking.
- Both accepted source-boundary samples are continuation/source-priority cases from harness hardening, so the current decision remains `keep-advisory` until broader PRD, issue, web, Slack, or pasted-source diversity is observed.

## 破坏性变更

- None.

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_gap_evidence.py --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_upgrade_decisions.py --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --json`
- `python3 -m unittest tests.test_plan_harness_sample_collection tests.test_harness_sample_intake_bundle tests.test_harness_pending_samples tests.test_harness_burn_in_readiness tests.test_harness_upgrade_decisions tests.test_harness_sample_gap_evidence`
