#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"

if [[ $# -lt 1 ]]; then
  echo "usage: run_hook.sh <hook-script> [args...]" >&2
  exit 2
fi

SCRIPT_NAME="$1"
shift

exec "$ROOT/.codex/hooks/run_with_repo_python.sh" ".codex/hooks/$SCRIPT_NAME" "$@"
