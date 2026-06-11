# Sandbox Honesty Real Sample

日期：2026-05-25

## 新增功能

- 在 `docs/ai/security/agentic-red-team-samples.jsonl` 记录 1 个 `sandbox-claim-honesty` accepted real incident，覆盖 goal continuation 中必须用当前 worktree / 命令证据区分 verified state 与 inferred context 的真实边界。
- `check_agentic_red_team_samples.py` 新增 `accepted_real_by_risk` 输出，让 red-team real incident 计数按 risk family 归因。

## 修复问题

- `collect_harness_sample_gaps.py` 的 red-team current evidence 不再把全局 real incident 数误显示到每个 red-team gap；现在按 risk family 输出真实事件计数。

## 行为变化

- `GAP-AGENTIC-SANDBOX-HONESTY` 从 `needs-first-real-sample` 前进到 `needs-more-real-samples`。
- burn-in readiness 汇总从 `needs_first_real_sample=17` 变为 `16`，`needs_more_real_samples=2`。

## 破坏性变更

- 无。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_append.py /tmp/agentic-sandbox-honesty-pending.jsonl`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_outcome.py /tmp/agentic-sandbox-honesty-accepted.jsonl`
- `.codex/hooks/run_with_repo_python.sh scripts/check_agentic_red_team_samples.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus --capture-focus-limit 0`
- `python3 tests/test_agentic_red_team_samples.py`
- `python3 tests/test_harness_sample_gaps.py`
- `python3 tests/test_harness_burn_in_readiness.py`
- `python3 tests/test_plan_harness_sample_collection.py`
- `python3 tests/test_harness_pending_samples.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `.codex/.venv/bin/python -m ruff check .codex/hooks scripts tests`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `git diff --check`
- `python3 scripts/check_ai_governance.py`
- `.codex/.venv/bin/python -m unittest discover tests`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Agentic Red-Team Samples](../security/agentic-red-team-samples.md)
- [Check Registry](../check-registry.md)
