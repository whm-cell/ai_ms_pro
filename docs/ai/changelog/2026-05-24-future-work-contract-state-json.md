# Future Work Contract State JSON

更新时间：2026-05-24
阶段或版本：stage-01
状态：已确认

## 新增功能

- `scripts/check_harness_future_work_contracts.py --json` 现在输出 per-gap `contract_states`。
- 每个 state 暴露 `adr_refs`、`missing_adr_refs`、`required_decision_fields`、`sample_collection_boundary`、`next_action` 和 `review_command`。
- `scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --json` 现在复用这些 state，让 contract-blocked gap 的 current evidence / next action 不只显示 status。
- `scripts/check_harness_pending_samples.py --include-future --include-accepted --json` 现在输出 `contract_blocker_states`，让 pending audit / lane report 也能直接消费同一组 blocker 信息。
- `scripts/build_harness_sample_intake_bundle.py --ledger-action define-contract-precondition --json` 现在为每个 contract-precondition entry 输出 `contract_blocker_state`。
- `scripts/plan_harness_sample_collection.py --include-future --ledger-action define-contract-precondition --json` 现在为每个 future-work queue item 输出 `contract_blocker_state`，capture-card 也会显示 status、missing ADR refs、sample boundary 和 next action。

## 修复问题

- 修复 future-work contract 审计只输出总数，后续工具无法直接判断每个 gap 被哪个 ADR / contract 前置条件挡住的问题。

## 行为变化

- `GAP-TRACE-REMOTE-INTEROP` 和 `GAP-AGENTIC-CASCADE-STOP` 继续保持 `sample_collection_allowed=false`。
- `missing_adr_refs=true` 只说明 ADR / contract approval 仍缺失，不批准 sample collection。
- readiness 输出会把 `sample_collection_boundary` 写入 future-work current evidence，并把 next action 指向 ADR / contract approval，而不是泛化为继续采样。
- pending audit 输出会把 future-work blockers 和 actionable sample gaps 分开，并在 `contract_blocker_states` 中显示 review command；它仍不写 ledger、不批准 future-work sampling。
- intake bundle summary 会在 Contract Precondition Review 表里显示 status、missing ADR refs 和 sample boundary；它仍只生成前置合同草稿，不批准采样。
- planner 输出会让 future-work contract lane 可机器复核，但 `sample_collection_allowed=false` 仍然阻止真实样本采集。

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_harness_future_work_contracts.py`
- `python3 tests/test_harness_burn_in_readiness.py`
- `python3 tests/test_harness_pending_samples.py`
- `python3 tests/test_harness_sample_intake_bundle.py`
- `python3 tests/test_plan_harness_sample_collection.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_future_work_contracts.py --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --include-future --include-accepted --json`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --ledger-action define-contract-precondition --json`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --include-future --ledger-action define-contract-precondition --json`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
