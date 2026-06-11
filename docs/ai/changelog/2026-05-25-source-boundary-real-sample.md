# Source Boundary Real Sample

日期：2026-05-25

## 新增功能

- 在 `docs/ai/standards/harness-sample-gap-evidence.jsonl` 记录 1 个 `GAP-GUARDRAIL-SOURCE-BOUNDARY` accepted real sample，覆盖 goal continuation 中对 goal context、prior summary、memory lookup 和 repo docs 的 source normalization 边界。

## 修复问题

- 无。

## 行为变化

- `GAP-GUARDRAIL-SOURCE-BOUNDARY` 从 `needs-first-real-sample` 前进到 `needs-more-real-samples`。
- burn-in readiness 汇总从 `needs_first_real_sample=16` 变为 `15`，`needs_more_real_samples=3`。

## 破坏性变更

- 无。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_append.py /tmp/harness-source-boundary-pending.jsonl`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_outcome.py /tmp/harness-source-boundary-accepted.jsonl`
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
- `python3 tests/test_harness_sample_append.py`
- `python3 tests/test_harness_sample_outcome.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --summary`
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
- [Check Registry](../check-registry.md)
