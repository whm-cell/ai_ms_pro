# 2026-04-30 Cross-platform Python Resolution Hardening

更新时间：2026-04-30
阶段或版本：stage-00
状态：已确认

## 新增功能

- Added regression coverage for macOS/POSIX Python resolution.
- Added PATH candidate scoring so fallback discovery can prefer Python 3.11+ instead of blindly accepting the first `python3`.
- Added static parity coverage for the root and starter PowerShell runners so Windows fallback discovery keeps the same version-scored behavior.

## 修复问题

- Fixed `.codex/hooks/run_hook.py` so it no longer runs hook targets with the Python that happened to launch the wrapper when `.codex/.venv` is available.
- Fixed POSIX `run_with_repo_python.sh` fallback discovery so `/usr/bin/python3` does not mask a later pyenv or managed Python 3.11+.
- Fixed PowerShell `run_with_repo_python.ps1` fallback discovery so Windows hosts can compare `python3`, `python`, `py -3`, and common per-user Python installs before choosing an interpreter.
- Fixed Python-based PATH enumeration so Windows `python.exe` / `python3.exe` candidates are considered instead of only extensionless command names.
- Fixed `scripts/bootstrap_harness.py` and the starter copy so new `.codex/.venv` creation prefers active envs, `CODEX_HARNESS_PYTHON`, then the best PATH Python before falling back to launcher Python.

## 行为变化

- Repo-local `.codex/.venv` remains the first choice for hooks and Git checks.
- On macOS/POSIX without a runnable repo venv, the harness now enumerates PATH Python candidates and prefers Python 3.11+.
- On Windows without a runnable repo venv, the PowerShell runner now uses the same version-scored fallback model before executing harness scripts.
- `CODEX_HARNESS_PYTHON` can still force a specific interpreter explicitly.

## 破坏性变更

- 无

## 验证范围

- `python3 -m unittest tests/test_python_resolution.py`
- `.codex/.venv/bin/python -m unittest discover -s tests`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/.venv/bin/python -m py_compile .codex/hooks/run_hook.py scripts/bootstrap_harness.py new_pro_standard/scripts/bootstrap_harness.py`
- `.codex/.venv/bin/python scripts/check_code_shape.py --all`
- `.codex/hooks/run_hook.py stop_ai_docs_check.py`
- `python3 -c 'import sys; sys.path.insert(0,".codex/hooks"); import run_hook; print(run_hook.resolve_python_command())'`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- Static test coverage verifies PowerShell runner parity; this macOS checkout does not provide `pwsh` / `powershell` for direct `.ps1` execution.

## 关联文档

- [ADR-008 Cross-Platform Hooks And Code Shape Budget](../adr/ADR-008-cross-platform-hooks-and-code-shape.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [当前工作上下文](../working-context.md)
