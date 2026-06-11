# Intake Draft Review State

日期：2026-05-25

## 新增功能

- `scripts/build_harness_sample_intake_bundle.py` 现在在每个 entry 上输出 draft `template_review_state` 和 `template_review_blockers`。
- intake bundle summary 现在输出 `draft review state counts` 和 `Draft Template Review` 表。

## 修复问题

- 防止 `check_harness_sample_templates.py` 的 schema validation 通过被误读为 pending 草稿已经 review-ready。
- Stage Checkpoint cross-task resume 草稿会在 intake summary 中显示必须替换模板 checkpoint id。

## 行为变化

- `--json` 输出新增 `template_review_state_counts`、entry-level `template_review_state` 和 `template_review_blockers`。
- `--summary` 输出新增草稿 review-state 可见性；模板仍不写 ledger、不接受样本、不计入 burn-in。

## 破坏性变更

- 无。新增字段是只读诊断字段。

## 验证范围

- `python3 tests/test_harness_sample_intake_bundle.py`

## 关联文档

- `docs/ai/standards/harness-sample-gap-evidence.md`
- `docs/ai/check-registry.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/agentic-harness-gap-roadmap.md`
