# 2026-04-25 Harness Starter Sync And Surface Trim

更新时间：2026-04-25
阶段或版本：STAGE-00
状态：已确认

## 新增功能

- Synchronized `new_pro_standard` with the current harness mechanism layer, including PowerShell hook entrypoints, code-shape checks, runnable Python probing, repo-local venv self-heal, and active handoff/status traceability metadata validation.

## 修复问题

- Fixed starter drift where `new_pro_standard` claimed portability hardening coverage but still shipped older bootstrap, governance, and Git hook behavior.
- Fixed duplicated current-state expansion across the default governance surface by moving exact active handoff bindings back to `working-context` sync metadata.

## 行为变化

- `new_pro_standard/.githooks/pre-commit` now runs `scripts/check_code_shape.py --staged` after AI governance, matching the root harness.
- `new_pro_standard/README.md` and `new_pro_standard/AGENTS.md` now document the current portability, traceability, reducer, and code-shape rules instead of the earlier slimmed subset.
- `scripts/bootstrap_harness.py` now refreshes `.codex/hooks.json` for the current host shell during setup, so new projects do not need to hand-edit hook entrypoints in the normal bootstrap path.
- [AI 文档入口索引](../index.md) now treats active handoff membership as a `working-context` metadata concern instead of repeating a second full current-state list.

## 破坏性变更

- 无

## 验证范围

- `python scripts/check_ai_governance.py`
- `python scripts/check_code_shape.py --all`
- `python -m py_compile scripts/bootstrap_harness.py new_pro_standard/scripts/bootstrap_harness.py`
- `python new_pro_standard/scripts/check_ai_governance.py`
- `python new_pro_standard/scripts/check_code_shape.py --all`

## 关联文档

- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [ADR-008 Cross-Platform Hooks And Code Shape Budget](../adr/ADR-008-cross-platform-hooks-and-code-shape.md)
