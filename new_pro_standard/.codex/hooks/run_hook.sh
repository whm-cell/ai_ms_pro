#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SCRIPT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd -P)"
ROOT="$SCRIPT_ROOT"
if GIT_ROOT="$(git -C "$SCRIPT_ROOT" rev-parse --show-toplevel 2>/dev/null)" && [[ "$GIT_ROOT" == "$SCRIPT_ROOT" ]]; then
  ROOT="$GIT_ROOT"
fi

if [[ $# -lt 1 ]]; then
  echo "usage: run_hook.sh <hook-script> [args...]" >&2
  exit 2
fi

SCRIPT_NAME="$1"
shift

exec "$ROOT/.codex/hooks/run_with_repo_python.sh" ".codex/hooks/$SCRIPT_NAME" "$@"
