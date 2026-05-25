# 2026-05-24 Intake Capture Checklist

## 新增功能

- `scripts/build_harness_sample_intake_bundle.py` 的 entry 现在携带 `evidence_needed` capture checklist。
- `scripts/build_harness_sample_intake_bundle.py --summary` 现在输出 `Capture Checklist` 表，列出每个 gap 后续真实采样所需的 bounded evidence 字段和边界。
- `scripts/check_harness_sample_followup_coverage.py` 现在要求 change-triggered command bundle 覆盖 intake `--json` 输出。

## 修复问题

- 避免 intake summary 只展示 gap、target 和 review command，而让采样者必须回到 capture card 或模板正文里推断最小证据字段。

## 行为变化

- `--json` 输出中的每个 entry 新增 `evidence_needed` 字段。
- 普通 text bundle 在每个 entry 下显示 `evidence needed`，但仍保留 JSONL template body。
- `--summary` 仍不展示 JSONL template body，不写 ledger、不接受样本、不改变 burn-in 计数。

## 破坏性变更

- 无。

## 验证范围

- `python3 tests/test_harness_sample_intake_bundle.py`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --summary`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --json`

## 关联文档

- `docs/ai/check-registry.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
- `.agents/skills/harness-maintenance/references/verification-commands.md`
