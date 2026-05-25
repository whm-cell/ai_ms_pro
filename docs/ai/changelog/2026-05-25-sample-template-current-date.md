# Sample Template Current Date

日期：2026-05-25

## 新增功能

- `check_harness_sample_templates.py` 和 `build_harness_sample_intake_bundle.py` 的默认 `sampled_at` 现在使用运行当天日期。
- 保留 `--sampled-at YYYY-MM-DD`，用于需要固定草稿日期的人工复核、CI 对照或单测。

## 修复问题

- 修复默认模板审计和 intake bundle 输出仍固定为 `2026-05-24`，导致 2026-05-25 之后的 sample draft 继续生成旧日期 id 的问题。

## 行为变化

- 未显式传 `--sampled-at` 时，CLI 输出会随当前本地日期生成 sample id / `sampled_at`。
- 显式传 `--sampled-at` 的测试和人工复核路径保持可复现。

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_harness_sample_templates.py`
- `python3 tests/test_harness_sample_intake_bundle.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --summary`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `.codex/.venv/bin/python -m ruff check .codex/hooks scripts tests`
- `git diff --check`

## 关联文档

- [Harness Sample Gap Evidence](../standards/harness-sample-gap-evidence.md)
- [Check Registry](../check-registry.md)
