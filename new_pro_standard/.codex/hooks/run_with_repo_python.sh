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

PYTHON_ARGS=()

python_can_run() {
  local bin="$1"
  shift || true
  "$bin" "$@" -c "import sys" >/dev/null 2>&1
}

resolve_python_from_prefix() {
  local prefix="$1"
  local candidates=(
    "$prefix/Scripts/python.exe"
    "$prefix/Scripts/python"
    "$prefix/bin/python"
    "$prefix/bin/python3"
    "$prefix/python.exe"
    "$prefix/python"
  )
  local candidate
  for candidate in "${candidates[@]}"; do
    if [[ -f "$candidate" ]]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  return 1
}

if PYTHON_BIN="$(resolve_python_from_prefix "$ROOT/.codex/.venv")" && python_can_run "$PYTHON_BIN"; then
  :
elif [[ -n "${VIRTUAL_ENV:-}" ]] && PYTHON_BIN="$(resolve_python_from_prefix "${VIRTUAL_ENV}")" && python_can_run "$PYTHON_BIN"; then
  :
elif [[ -n "${CONDA_PREFIX:-}" ]] && PYTHON_BIN="$(resolve_python_from_prefix "${CONDA_PREFIX}")" && python_can_run "$PYTHON_BIN"; then
  :
elif [[ -n "${CODEX_HARNESS_PYTHON:-}" ]] && python_can_run "${CODEX_HARNESS_PYTHON}"; then
  PYTHON_BIN="${CODEX_HARNESS_PYTHON}"
elif command -v python3 >/dev/null 2>&1 && python_can_run "$(command -v python3)"; then
  PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1 && python_can_run "$(command -v python)"; then
  PYTHON_BIN="$(command -v python)"
elif command -v py >/dev/null 2>&1 && python_can_run "$(command -v py)" -3; then
  PYTHON_BIN="$(command -v py)"
  PYTHON_ARGS=(-3)
else
  echo "ERROR: could not determine a runnable Python executable for harness scripts" >&2
  exit 1
fi

exec "$PYTHON_BIN" "${PYTHON_ARGS[@]}" "$TARGET" "$@"
