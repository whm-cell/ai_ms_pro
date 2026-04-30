#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from hook_config_lib import render_hooks_config


ROOT = Path(__file__).resolve().parents[1]
HOOKS_CONFIG_PATH = ROOT / ".codex" / "hooks.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a platform-specific .codex/hooks.json for the current machine.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero when .codex/hooks.json does not match the current system rendering.",
    )
    parser.add_argument(
        "--system",
        help="Override the detected system for validation or debugging, for example: Windows, Darwin, Linux.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rendered = render_hooks_config(root=ROOT, system=args.system)

    if args.check:
        current = HOOKS_CONFIG_PATH.read_text(encoding="utf-8") if HOOKS_CONFIG_PATH.exists() else ""
        if current == rendered:
            return 0
        print(
            f"{HOOKS_CONFIG_PATH} is out of date; run `python3 scripts/sync_hooks_config.py`.",
            file=sys.stderr,
        )
        return 1

    HOOKS_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    HOOKS_CONFIG_PATH.write_text(rendered, encoding="utf-8")
    print(f"Updated {HOOKS_CONFIG_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
