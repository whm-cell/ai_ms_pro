#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"

if [[ $# -lt 1 ]]; then
  echo "usage: run_with_repo_python.sh <script-path> [args...]" >&2
  exit 2
fi

TARGET="$1"
shift

if [[ "$TARGET" != /* ]]; then
  TARGET="$ROOT/$TARGET"
fi

if [[ ! -f "$TARGET" ]]; then
  echo "ERROR: target script not found: $TARGET" >&2
  exit 1
fi

if [[ -x "$ROOT/.codex/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT/.codex/.venv/bin/python"
elif [[ -n "${VIRTUAL_ENV:-}" && -x "${VIRTUAL_ENV}/bin/python" ]]; then
  PYTHON_BIN="${VIRTUAL_ENV}/bin/python"
elif [[ -n "${CONDA_PREFIX:-}" && -x "${CONDA_PREFIX}/bin/python" ]]; then
  PYTHON_BIN="${CONDA_PREFIX}/bin/python"
elif [[ -n "${CODEX_HARNESS_PYTHON:-}" ]]; then
  PYTHON_BIN="${CODEX_HARNESS_PYTHON}"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  PYTHON_BIN="/usr/bin/python3"
fi

exec "$PYTHON_BIN" "$TARGET" "$@"
