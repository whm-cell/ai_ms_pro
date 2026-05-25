# Outcome Review Stable Field Gate

- Date: 2026-05-24
- Scope: harness sample outcome review control plane
- Status: landed

## 新增功能

- `scripts/check_harness_sample_outcome.py <candidate-jsonl>` 现在会读取目标 pending ledger 原始行，并把 outcome candidate 与原始行做稳定字段对比。
- Outcome review 只允许 schema 明确列出的 outcome / review 字段变化，例如 `outcome`、`decision`、`action_taken`、`evidence_refs` 和对应 checker 需要的 review 元数据。

## 修复问题

- 防止人工 outcome review 阶段把 `sample_summary`、`sampled_at`、`boundary_note`、source evidence 或其他采样事实字段一起改写。
- 防止 rejected outcome candidate 借由较宽的 target checker 规则绕过原始 pending 证据一致性校验。

## 行为变化

- 候选记录若改动稳定 evidence 字段，会报告 `outcome candidate changed stable evidence field <field>` 并拒绝 outcome 变更。
- 边界字段漂移仍由 boundary gate 单独报告；稳定字段 gate 会作为第二层 no-write 复核。

## 破坏性变更

- 无。该变更只收紧 no-write outcome review gate；不会写 ledger、接受样本或生成真实证据。

## 验证范围

- `python3 tests/test_harness_sample_outcome.py`
- `python3 tests/test_tool_contracts.py`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
- `.agents/skills/harness-maintenance/references/verification-commands.md`
