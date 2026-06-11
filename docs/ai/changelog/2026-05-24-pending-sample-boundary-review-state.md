# Pending Sample Boundary Review State

- Date: 2026-05-24
- Scope: harness sample intake control plane
- Status: landed

## 新增功能

- `scripts/harness_sample_slots.py` 的 pending review-state 现在会把 sample boundary drift 纳入 placeholder blocker。
- `scripts/check_harness_sample_append.py <candidate-jsonl>` 通过共享 review-state 拒绝边界含糊的新 pending row。
- `scripts/check_harness_placeholder_replacement.py <candidate-jsonl>` 对未来适用相同 pending boundary blockers。
- `scripts/check_harness_sample_outcome.py <candidate-jsonl>` 现在会在 outcome review 阶段拒绝边界字段漂移。

## 修复问题

- 防止 pending 候选在进入 ledger 前把 `no_external_claim`、`local_only` 或 `no_network` 填错但仍被视为 review-ready。
- 防止 shared gap evidence、red-team pending sample 和 local trace pending sample 带着含糊边界进入 outcome review。
- 防止 rejected outcome candidate 绕过 accepted-sample checker 时改掉 `no_external_claim`、`local_only` 或 `no_network` 边界。

## 行为变化

- Shared gap evidence pending row 必须保持 `no_external_claim=true`，且 real/local source type 要匹配 `local_only`。
- Red-team pending row 必须保持 `local_only=true` 和 `no_external_claim=true`。
- Local Trace Summary pending row 必须保持 `no_network=true` 和 `local_only=true`。
- Outcome candidate 必须保持相同边界语义，否则 no-write review gate 会拒绝。

## 破坏性变更

- 无。该变更只影响 no-write review gate 和 pending slot 分类；不会写 ledger、接受样本或生成真实证据。

## 验证范围

- `python3 tests/test_harness_sample_append.py`
- `python3 tests/test_harness_pending_samples.py`
- `python3 tests/test_harness_placeholder_replacement.py`
- `python3 tests/test_harness_sample_outcome.py`
- `python3 tests/test_tool_contracts.py`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
- `.agents/skills/harness-maintenance/references/verification-commands.md`
