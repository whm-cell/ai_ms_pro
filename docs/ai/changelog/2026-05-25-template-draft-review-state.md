# Template Draft Review State

日期：2026-05-25

## 新增功能

- `scripts/check_harness_sample_templates.py` 现在输出 draft review-state counts。
- JSON validation entry 新增 `template_review_state` 和 `template_review_blockers`。

## 修复问题

- 防止模板审计通过被误读为 pending 草稿已经 review-ready 或可计入 evidence。

## 行为变化

- text 输出会显示 `draft review state counts`。
- schema-valid 但仍含 placeholder 字段的模板会继续通过模板漂移检查，同时在 review-state 字段中显示 blocker。

## 破坏性变更

- 无。新增字段是只读诊断字段。

## 验证范围

- `python3 tests/test_harness_sample_templates.py`

## 关联文档

- `docs/ai/standards/harness-sample-gap-evidence.md`
- `docs/ai/check-registry.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/agentic-harness-gap-roadmap.md`
