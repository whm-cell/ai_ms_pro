#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict
import json

from reuse_retirement_core import (
    ROOT,
    ReuseRetirementFinding,
    ReuseRetirementReport,
    build_report,
)


__all__ = [
    "ReuseRetirementFinding",
    "ReuseRetirementReport",
    "build_report",
    "exit_code",
    "render_report",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review code reuse and stale-path retirement candidates.")
    parser.add_argument("--base", default="origin/main", help="Base ref for changed-file discovery.")
    parser.add_argument("--files", nargs="*", help="Explicit changed files to review.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when findings or errors exist.")
    return parser.parse_args()


def render_report(report: ReuseRetirementReport) -> str:
    if not report.enabled and not report.errors:
        return "OK: reuse/retirement gate disabled"
    lines = [
        "Reuse / Retirement Gate",
        f"Changed code files: {len(report.changed_files)}",
        f"Scanned code files: {report.scanned_files}",
    ]
    lines.extend(f"ERROR: {error}" for error in report.errors)
    if report.findings:
        lines.append("REVIEW:")
        for item in report.findings:
            candidates = ", ".join(item.candidates) if item.candidates else "(none)"
            lines.append(f"- {item.path}:{item.line} [{item.code}] {item.message}; candidates: {candidates}")
    if not report.errors and not report.findings:
        lines.append("OK: no reuse/retirement findings")
    return "\n".join(lines)


def exit_code(report: ReuseRetirementReport, *, strict: bool) -> int:
    return 1 if strict and (report.errors or report.findings) else 0


def main() -> int:
    args = parse_args()
    explicit_files = tuple(args.files) if args.files is not None else None
    report = build_report(ROOT, base=args.base, files=explicit_files)
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print(render_report(report))
    return exit_code(report, strict=args.strict)


if __name__ == "__main__":
    raise SystemExit(main())
