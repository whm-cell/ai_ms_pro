# Outcome Candidate Template Routing

- Date: 2026-05-24
- Scope: harness sample intake and template review control plane
- Status: landed

## 新增功能

- `scripts/harness_sample_templates.py` 现在会在 `review-existing-pending-slot` lane 中通过 `scripts/harness_sample_outcome_templates.py` 读取原 pending ledger 行，并生成 outcome candidate，而不是继续生成 `outcome=pending` 的普通样本模板。
- `scripts/check_harness_sample_templates.py` 对该 lane 改走 `check_harness_sample_outcome.py` 复核，确保 outcome candidate 与 no-write outcome gate 一致。
- `scripts/harness_sample_intake_render.py` 在 text / summary 输出中标明 outcome candidate write mode，并在 outcome review summary 中显示 pending sample id。

## 修复问题

- 防止未来出现 review-ready pending row 时，intake bundle 同时显示 outcome review command 和 pending template，造成复核命令与草稿语义不一致。
- 防止 outcome review lane 被误当成 append-new-pending-slot 或 sample acceptance。

## 行为变化

- `review-existing-pending-slot` 的草稿默认从原 pending 行复制稳定 evidence 字段，并把 `outcome` 设为 `rejected` 作为人工复核候选；人工接受真实样本前仍需显式改成 `accepted` 并通过 `check_harness_sample_outcome.py <candidate-jsonl>`。
- 当前仓库没有 review-ready pending slot，因此默认 actionable draft bundle 数量不变。

## 破坏性变更

- 无。该变更只影响 review-ready pending lane 的 stdout-only 草稿和审计路径；不会写 ledger、接受样本或生成真实证据。

## 验证范围

- `python3 tests/test_harness_sample_templates.py`
- `python3 tests/test_harness_sample_intake_bundle.py`
- `python3 tests/test_plan_harness_sample_collection.py`
- `python3 tests/test_harness_sample_outcome.py`
- `python3 tests/test_tool_contracts.py`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/check-registry.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
- `.agents/skills/harness-maintenance/references/verification-commands.md`
- `scripts/harness_sample_outcome_templates.py`
