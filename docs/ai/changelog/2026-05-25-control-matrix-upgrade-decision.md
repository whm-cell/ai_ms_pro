# Control Matrix Upgrade Decision

日期：2026-05-25

## 新增功能

- 在 `docs/ai/standards/harness-sample-gap-evidence.jsonl` 追加第二个 `GAP-SEC-CONTROL-MATRIX-BURNIN` accepted real sample，映射到 `AC-01`，并保留 bounded evidence / no raw runtime 边界。
- 在 `docs/ai/standards/harness-upgrade-decisions.jsonl` 追加 `HUD-2026-05-25-control-matrix-keep-advisory`，让 control-matrix burn-in 达到 2/2 后进入 keep-advisory 决策状态。

## 修复问题

- `check_harness_upgrade_decisions.py` 不再把 `GAP-SEC-CONTROL-MATRIX-BURNIN` 报成 ready gap 缺少升级决策。
- pending / planner / intake 的计数同步到 control-matrix 从 sample append lane 转入 `review-upgrade-decision` lane 后的状态。

## 行为变化

- `GAP-SEC-CONTROL-MATRIX-BURNIN` 从 `needs-more-real-samples` 前进到 `ready-for-upgrade-discussion`，当前决策为 `keep-advisory`。
- actionable sample gaps 从 16 降到 15；append-new-pending-slot gaps 从 14 降到 13；review-upgrade-decision gaps 从 3 增到 4。

## 破坏性变更

- 无。该变更只追加 bounded ledger row、升级决策和同步文档 / 测试断言，不改变 blocking policy。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_append.py docs/ai/standards/control-matrix-source-priority-candidate.jsonl`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_outcome.py docs/ai/standards/control-matrix-source-priority-candidate.jsonl`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_upgrade_decision_candidate.py docs/ai/standards/control-matrix-upgrade-decision-candidate.jsonl`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_gap_evidence.py --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_upgrade_decisions.py --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --json`
