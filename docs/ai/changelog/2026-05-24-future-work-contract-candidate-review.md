# Future Work Contract Candidate Review

更新时间：2026-05-24
阶段或版本：stage-01
状态：已确认

## 新增功能

- 新增 `scripts/check_harness_future_work_contract_candidate.py <candidate-jsonl>`，用于 future-work contract row 的 no-write candidate review。
- `define-contract-precondition` lane 的 `contract_precondition_review_command` 现在指向 candidate gate；整本 ledger 仍由 `check_harness_future_work_contracts.py` 复核。
- future-work contract template 现在优先复用现有 contract id，提示替换当前 contract row，而不是追加 duplicate gap row。

## 修复问题

- `check_harness_future_work_contracts.py` 现在拒绝同一个 future-work gap 出现多条 contract row。
- 防止 `FWC-DRAFT-*` 草稿被误追加到 `harness-future-work-contracts.jsonl` 后覆盖同 gap 的当前状态。

## 行为变化

- candidate review 不写 ledger、不批准 future-work sampling、不采集样本、不证明远端互通。
- candidate 通过后仍需人工替换对应 row，并重新运行 `check_harness_future_work_contracts.py`。

## 破坏性变更

- 无。现有 ledger 行仍有效；新增校验只拒绝 duplicate future-work gap contract row。

## 验证范围

- `python3 tests/test_harness_future_work_contract_candidate.py`
- `python3 tests/test_harness_future_work_contracts.py`
- `python3 tests/test_plan_harness_sample_collection.py`
- `python3 tests/test_harness_sample_intake_bundle.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
