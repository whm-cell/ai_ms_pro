# 2026-04-24 Harness Portability Hardening

更新时间：2026-04-24
阶段或版本：STAGE-00
状态：已确认

## 新增功能

- Added Windows PowerShell Codex hook entrypoints: `.codex/hooks/run_hook.ps1` and `.codex/hooks/run_with_repo_python.ps1`.
- Added `.codex/code_shape.toml` and `scripts/check_code_shape.py` for lightweight staged code-shape checks.
- Added `ADR-008-cross-platform-hooks-and-code-shape.md`.

## 修复问题

- Fixed the Windows harness path where hooks could depend too directly on host `python`.
- Fixed bootstrap handling for repo-local venvs that exist but are not runnable.

## 行为变化

- `.codex/hooks.json` now routes `SessionStart` and `Stop` through the PowerShell hook entrypoint in this Windows workspace.
- `.codex/hooks/run_with_repo_python.sh` now verifies Python candidates before use and supports Windows-style repo venv layouts.
- `scripts/bootstrap_harness.py` now resolves Python across Windows/POSIX layouts and rebuilds an unusable repo-local venv in place.
- `.githooks/pre-commit` now runs the code-shape check after AI governance.

## 破坏性变更

- 无

## 验证范围

- `python -m py_compile scripts/bootstrap_harness.py scripts/check_code_shape.py`
- `python scripts/check_code_shape.py --all`
- `python scripts/check_ai_governance.py`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .codex/hooks/run_hook.ps1 stop_ai_docs_check.py`

## 关联文档

- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [ADR-008 Cross-Platform Hooks And Code Shape Budget](../adr/ADR-008-cross-platform-hooks-and-code-shape.md)
