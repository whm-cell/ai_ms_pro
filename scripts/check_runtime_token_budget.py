#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from runtime_token_budget_core import build_report, render_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Codex runtime transcript token pressure.")
    parser.add_argument(
        "--transcript",
        action="append",
        default=[],
        help="Path to a Codex rollout JSONL transcript. Can be repeated.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when any runtime token budget warning is found.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    transcript_paths = [Path(path).expanduser() for path in args.transcript]
    missing = [path.as_posix() for path in transcript_paths if not path.exists()]
    if missing:
        print(f"ERROR: transcript missing: {', '.join(missing)}", file=sys.stderr)
        return 1
    try:
        report = build_report(transcript_paths=transcript_paths)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print(render_report(report))
    return 1 if args.strict and report.warnings else 0


if __name__ == "__main__":
    raise SystemExit(main())
