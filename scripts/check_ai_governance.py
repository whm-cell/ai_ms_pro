#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKS = [
    ("structure", ROOT / "scripts" / "check_ai_docs.py"),
    ("quality", ROOT / "scripts" / "check_ai_doc_quality.py"),
]


def main() -> int:
    failures = []

    for label, script in CHECKS:
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            failures.append((label, result.stdout.strip(), result.stderr.strip()))

    if failures:
        print("AI governance checks: FAILED")
        for label, stdout, stderr in failures:
            print(f"[{label}]")
            if stdout:
                print(stdout)
            if stderr:
                print(stderr)
        return 1

    print("AI governance checks: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
