# Python Runtime And Hook Maintenance

Use this reference when editing `scripts/bootstrap_harness.py`, `.codex/hooks/*`, `.githooks/*`, hook sync, or `run_with_repo_python` entrypoints.

## Rules

- Harness Python should prefer the repo-local virtual environment `.codex/.venv`.
- Git hooks and Codex hooks should resolve Python through `.codex/hooks/` runners instead of hardcoding a system Python path.
- Runners must verify that a Python candidate is runnable before using it.
- If `.codex/.venv` exists but is not runnable, bootstrap may rebuild it in place without touching `.codex/runtime/*`.
- POSIX/macOS and Windows hook fallback discovery should prefer `.codex/.venv`, active envs, `CODEX_HARNESS_PYTHON`, then the best runnable Python 3.11+ candidate before falling back to the launcher Python.
- Bootstrap may inherit parent-directory `.env` Python selector keys or pyenv's selected Python when creating `.codex/.venv`.
- Parent-directory `.env` inheritance is limited to allowlisted Python selector keys: `CODEX_HARNESS_PYTHON`, `PYTHON`, `PYTHON3`, `PYTHON_BIN`, `PYTHON_EXECUTABLE`, `CODEX_HARNESS_PYTHON_VERSION`, `PYTHON_VERSION`, and `PYENV_VERSION`. Bootstrap must not print or import arbitrary `.env` values.
- Do not commit `.codex/.venv`.

## Checks

Run the smallest relevant set:

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py
.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --staged
python3 scripts/bootstrap_harness.py --help
```

When hook config changes, also run the hook sync check if available.
