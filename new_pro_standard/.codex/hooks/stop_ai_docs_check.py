#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECK_SCRIPT = ROOT / "scripts" / "check_ai_governance.py"


def main() -> int:
    try:
        json.load(sys.stdin)
    except json.JSONDecodeError:
        pass

    result = subprocess.run(
        [sys.executable, str(CHECK_SCRIPT)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        return 0

    details = (result.stdout or result.stderr).strip()
    system_message = "AI governance check failed. Update docs/ai, docs/requirements, or index files, then retry."
    if details:
        compact = " ".join(details.splitlines())
        system_message = f"{system_message} {compact}"

    print(
        json.dumps(
            {
                "continue": False,
                "stopReason": "AI docs governance check failed",
                "systemMessage": system_message,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
