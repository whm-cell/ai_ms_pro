#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

from agent_productization_readiness import DEFAULT_ASSESSMENT, DEFAULT_MODEL, ReadinessReport, build_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit agent productization readiness records.")
    parser.add_argument("--model", default=str(DEFAULT_MODEL), help="Readiness model JSON path.")
    parser.add_argument("--assessment", default=str(DEFAULT_ASSESSMENT), help="Assessment JSONL path.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when review findings are present. Keep off until real samples justify it.",
    )
    return parser.parse_args()


def emit_text(report: ReadinessReport) -> None:
    print("Agent productization readiness audit:")
    print(f"- model: {report.model_path}")
    print(f"- assessment: {report.assessment_path}")
    print(f"- capabilities: {report.capability_count}")
    print(f"- assessment records: {report.assessment_count}")
    print(f"- targets: {', '.join(report.targets) if report.targets else 'none'}")
    print(f"- MVP capabilities: {', '.join(report.mvp_capabilities) if report.mvp_capabilities else 'none'}")
    mature = ", ".join(report.mature_capabilities) if report.mature_capabilities else "none"
    print(f"- mature capabilities: {mature}")
    if report.status_counts:
        print("- status counts:")
        for status, count in sorted(report.status_counts.items()):
            print(f"  - {status}: {count}")
    for finding in report.review_findings:
        print(
            "REVIEW: "
            f"{finding.target_id}/{finding.capability_id} is {finding.status}; "
            f"gap={finding.gap}; next={finding.next_action}"
        )
    for warning in report.warnings:
        print(f"WARN: {warning}")
    if report.errors:
        for error in report.errors:
            print(f"ERROR: {error}")
    else:
        print("ERRORS: none")


def main() -> int:
    args = parse_args()
    report = build_report(Path(args.model).expanduser(), Path(args.assessment).expanduser())
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        emit_text(report)
    if report.errors:
        return 1
    if args.strict and report.review_findings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
