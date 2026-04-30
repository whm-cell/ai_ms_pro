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
PREFERRED_MIN_SCORE=$((3 * 1000000 + 11 * 1000))

python_can_run() {
  local bin="$1"
  shift || true
  "$bin" "$@" -c "import sys" >/dev/null 2>&1
}

python_version_score() {
  local bin="$1"
  shift || true
  "$bin" "$@" -c "import sys; v=sys.version_info; print(v[0] * 1000000 + v[1] * 1000 + v[2])" 2>/dev/null
}

choose_best_python_from_path() {
  local best_bin=""
  local best_score=-1
  local best_is_preferred=0
  local name directory candidate score is_preferred
  local old_ifs="$IFS"

  for name in python3 python; do
    IFS=:
    for directory in ${PATH:-}; do
      IFS="$old_ifs"
      [[ -n "$directory" ]] || continue
      candidate="$directory/$name"
      [[ -x "$candidate" && ! -d "$candidate" ]] || continue
      score="$(python_version_score "$candidate" || true)"
      [[ "$score" =~ ^[0-9]+$ ]] || continue
      is_preferred=0
      if [[ "$score" -ge "$PREFERRED_MIN_SCORE" ]]; then
        is_preferred=1
      fi
      if [[ "$is_preferred" -gt "$best_is_preferred" ]] || {
        [[ "$is_preferred" -eq "$best_is_preferred" ]] && [[ "$score" -gt "$best_score" ]]
      }; then
        best_bin="$candidate"
        best_score="$score"
        best_is_preferred="$is_preferred"
      fi
    done
    IFS="$old_ifs"
  done

  [[ -n "$best_bin" ]] || return 1
  printf '%s\n' "$best_bin"
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
elif PYTHON_BIN="$(choose_best_python_from_path)" && python_can_run "$PYTHON_BIN"; then
  :
elif command -v py >/dev/null 2>&1 && python_can_run "$(command -v py)" -3; then
  PYTHON_BIN="$(command -v py)"
  PYTHON_ARGS=(-3)
else
  echo "ERROR: could not determine a runnable Python executable for harness scripts" >&2
  exit 1
fi

if [[ ${#PYTHON_ARGS[@]} -gt 0 ]]; then
  exec "$PYTHON_BIN" "${PYTHON_ARGS[@]}" "$TARGET" "$@"
fi

exec "$PYTHON_BIN" "$TARGET" "$@"
