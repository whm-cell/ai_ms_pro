# ADR-008 Cross-Platform Hooks And Code Shape Budget

更新时间：2026-04-30
编号：ADR-008
标题：Cross-platform hooks and code shape budget
状态：已采纳

## 背景

`ghtt_crawler` exercised this harness in a more realistic Windows and business-code setting. That exposed three reusable gaps in the current project:

- Codex hooks were still biased toward POSIX shell entrypoints.
- Python discovery trusted interpreter paths too easily.
- Real implementation work needed a small guard against growing monolithic harness and app scripts.

## 决策

This repository adopts the portable subset of those findings:

1. Codex hooks now use `.codex/hooks/run_hook.ps1` on Windows.
2. PowerShell and POSIX runners resolve Python through repo-local `.codex/.venv` first, then environment and system fallbacks.
3. Python candidates must pass a runnable `import sys` probe before use.
4. `scripts/bootstrap_harness.py` supports Windows and POSIX venv layouts and rebuilds a broken `.codex/.venv` in place.
5. Code shape checks live in `scripts/check_code_shape.py` with thresholds in `.codex/code_shape.toml`.

2026-04-30 amendment:

6. POSIX/macOS fallback discovery must not stop at the first `python3` on PATH, because Codex or non-interactive shells may expose `/usr/bin/python3` before the user's pyenv/managed Python.
7. Windows Python discovery must account for `.exe` / `PATHEXT` command names, not only extensionless POSIX-style executable names.
8. Windows PowerShell fallback discovery follows the same version-scored rule across `python3`, `python`, `py -3`, and common per-user Python installs.
9. Repo-local `.codex/.venv` remains first priority. If it is unavailable, runners and bootstrap enumerate PATH candidates and prefer Python 3.11+ before falling back to the launcher Python.
10. `CODEX_HARNESS_PYTHON` remains an explicit override between active env prefixes and PATH fallback.

## 备选方案

- Keep the existing POSIX-first hook entrypoints only.
- Fold code-shape checks into `scripts/check_ai_governance.py`.
- Copy `ghtt_crawler` business-specific asset governance directly into this repository.

## 决策理由

- Windows hook continuity is now a real portability requirement for the harness.
- Verifying that Python is runnable avoids false-positive interpreter selection.
- Keeping code-shape checks separate prevents governance checks from becoming a mixed-purpose script.
- Only the reusable harness mechanics are being adopted; `ghtt_crawler` business rules stay out of this project.

## 影响

- Runtime hook continuity is stronger on Windows without removing POSIX support.
- Starter portability is closer to real cross-platform use.
- Code shape is checked separately from AI governance so documentation rules stay focused.
- Existing large files may warn, but new oversized files or definitions should be split before landing.
- macOS hook and bootstrap resolution no longer inherits `/usr/bin/python3` just because that interpreter launched the wrapper.
- Windows PowerShell runner fallback no longer blindly accepts the first runnable interpreter when a newer Python 3.11+ candidate is available.

## 关联文档

- [AI 文档入口索引](../index.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [2026-04-24 Harness Portability Hardening](../changelog/2026-04-24-harness-portability-hardening.md)
- [2026-04-30 Cross-platform Python Resolution Hardening](../changelog/2026-04-30-macos-python-resolution-hardening.md)

## Verification

- `python -m py_compile scripts/bootstrap_harness.py scripts/check_code_shape.py`
- `python scripts/check_code_shape.py --all`
- `python scripts/check_ai_governance.py`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .codex/hooks/run_hook.ps1 stop_ai_docs_check.py`
- `python3 -m unittest tests/test_python_resolution.py`
