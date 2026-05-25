# Readiness Next Collection Commands

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `scripts/check_harness_burn_in_readiness.py` 的每个 readiness item 现在输出 `target_artifact`、`target_checker_command`、`ledger_action`、`planner_command`、`intake_command` 和 `lane_review_command`。
- Markdown 输出新增 `Next Collection Commands` 表，把每个 gap 的下一步 target / checker / planner / intake / lane review route 直接展示在 readiness audit 中。
- JSON 输出同步携带相同字段，供 CI summary、人工 handoff 或后续 drift check 复用。

## 修复问题

- 修复 readiness audit 只能看到 readiness state / capture gate，但不能直接知道下一步该走 append、placeholder replacement、upgrade decision 还是 no-sample route 的交接缺口。
- 避免 ready gap、local-only gap 和 placeholder gap 需要人工再打开 planner / intake / pending focus 才能判断下一步 no-write review command。

## 行为变化

- `needs-first-real-sample` / `needs-more-real-samples` 行会直接显示 focused planner / intake command 和 append / replacement review command。
- `ready-for-upgrade-discussion` 行会直接路由到 `docs/ai/standards/harness-upgrade-decisions.jsonl` 与 `check_harness_upgrade_decision_candidate.py <candidate-jsonl>`。
- local-only / no-sample rows 会显示 `not-applicable` 命令，明确不进入 append lane。
- 这些字段只用于只读采集交接，不写 ledger、不生成样本、不接受 evidence。

## 破坏性变更

- 无。CLI flags 和既有 readiness state 判定保持不变。

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_harness_burn_in_readiness tests.test_tool_contracts`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `.codex/.venv/bin/ruff check .codex/hooks scripts tests`
- `git diff --check`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/.venv/bin/python -m unittest discover tests`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Tool Contracts](../tool-contracts/README.md)
- [Check Registry](../check-registry.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Open Items](../harness-open-items.md)
