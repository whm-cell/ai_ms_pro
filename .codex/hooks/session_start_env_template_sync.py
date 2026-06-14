#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from check_env_template_sync import build_report  # noqa: E402


def main() -> int:
    try:
        report = build_report(root=ROOT)
    except Exception:
        return 0

    if not report.enabled or not report.missing_keys:
        return 0

    context = (
        "本机 env 与模板 key 集合同步检查发现缺失 key："
        + ", ".join(report.missing_keys)
        + "。该 hook 只比较 key，不读取、不输出、不覆盖任何 env 值。"
    )
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": context,
                }
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
