# Control Matrix Real Sample

日期：2026-05-25

## 新增功能

- 在 `docs/ai/standards/harness-sample-gap-evidence.jsonl` 记录 1 个 `GAP-SEC-CONTROL-MATRIX-BURNIN` accepted real sample，映射到 `AC-01`。
- 文档同步说明该样本只证明一次 bounded control-matrix mapping 和 upgrade restraint，不证明 prompt-injection 防护完成。

## 修复问题

- 无。

## 行为变化

- `GAP-SEC-CONTROL-MATRIX-BURNIN` 从 `needs-first-real-sample` 前进到 `needs-more-real-samples`。
- burn-in readiness 汇总从 `needs_first_real_sample=15` 变为 `14`，`needs_more_real_samples=4`。
- pending sample accounting 的 accepted evidence class `real` 从 10 增加到 11。

## 破坏性变更

- 无。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_append.py /tmp/harness-control-matrix-pending.jsonl`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_outcome.py /tmp/harness-control-matrix-accepted.jsonl`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_gap_evidence.py --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus --capture-focus-limit 0`
- `python3 tests/test_harness_sample_gap_evidence.py`
- `python3 tests/test_harness_sample_gaps.py`
- `python3 tests/test_harness_burn_in_readiness.py`
- `python3 tests/test_plan_harness_sample_collection.py`
- `python3 tests/test_harness_pending_samples.py`
- `python3 tests/test_harness_sample_intake_bundle.py`
- `python3 tests/test_harness_sample_templates.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `.codex/.venv/bin/python -m ruff check .codex/hooks scripts tests`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `git diff --check`
- `python3 scripts/check_ai_governance.py`
- `.codex/.venv/bin/python -m unittest discover tests`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Sample Gap Evidence](../standards/harness-sample-gap-evidence.md)
- [Agentic Control Matrix](../security/agentic-control-matrix.md)
- [Check Registry](../check-registry.md)
