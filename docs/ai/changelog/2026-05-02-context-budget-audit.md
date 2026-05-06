# 2026-05-02 Context Budget Audit

更新时间：2026-05-02
阶段或版本：stage-00
状态：已确认

## 新增功能

- Added `scripts/check_context_budget.py` as a warning-only default context audit.
- Added `[context_budget]` thresholds to `.codex/harness.toml`.
- Synced the script and config into `new_pro_standard`.
- Added ADR-014 for the manual budget audit strategy.
- Added `--使用细节/上下文预算OPEN-10使用细节.md` as the recall note for when and how to rerun OPEN-10 style triage.

## 修复问题

- Added a concrete way to detect when default harness context becomes heavy.
- Separated context budget auditing from archive candidate detection.
- Completed the first OPEN-10 triage by compressing `AGENTS.md`, the current stage status, and `$repo-governed-coding` metadata.

## 行为变化

- Context budget audit is manual and warning-only.
- Starter/new-project budget keeps the 6500 token target, while this mature Stage-00 root repo now uses an 8500 local default-surface budget.
- Context budget is not wired into Stop hook and does not automatically compact or archive.

## 破坏性变更

- 无

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `python3 -m unittest discover -s tests -p 'test_context_budget.py'`
- `python3 -m unittest discover -s tests -p 'test_harness_config.py'`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --staged`

## 关联文档

- [AI 文档入口索引](../index.md)
- [ADR-014 Context Budget Audit](../adr/ADR-014-context-budget-audit.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [上下文预算 OPEN-10 使用细节](/Volumes/usd/codes/go_projects/ai_ms_pro/--使用细节/上下文预算OPEN-10使用细节.md)
