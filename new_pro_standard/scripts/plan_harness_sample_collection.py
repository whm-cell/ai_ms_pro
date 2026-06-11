#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import sys

import collect_harness_sample_gaps
from harness_sample_collection_config import (
    CAPTURE_GATES,
    PRIORITIES,
    REVIEW_COMMAND,
    SAMPLE_LEDGER,
    SOURCE_TYPES,
    TEMPLATE_DOC,
)


@dataclass(frozen=True)
class CollectionItem:
    gap_id: str
    area: str
    priority: str
    status: str
    target_artifact: str
    source_type_needed: str
    capture_gate: str
    review_command: str
    trigger: str
    evidence_needed: list[str]
    boundary: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plan starter-safe harness sample collection targets.")
    parser.add_argument("--area", action="append", default=[], help="Filter by gap area. Repeatable.")
    parser.add_argument("--gap-id", action="append", default=[], help="Filter by exact gap id. Repeatable.")
    parser.add_argument("--include-future", action="store_true", help="Include future-work gaps.")
    parser.add_argument("--sample-template", action="store_true", help="Emit pending JSONL templates for selected gaps.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def build_queue(
    areas: set[str] | None = None,
    gap_ids: set[str] | None = None,
    include_future: bool = False,
) -> list[CollectionItem]:
    gaps = collect_harness_sample_gaps.select_gaps(areas or set(), include_future=include_future)
    items = [build_item(gap) for gap in gaps if not gap_ids or gap.id in gap_ids]
    return sorted(items, key=lambda item: (item.priority, item.area, item.gap_id))


def build_item(gap: collect_harness_sample_gaps.SampleGap) -> CollectionItem:
    return CollectionItem(
        gap_id=gap.id,
        area=gap.area,
        priority=PRIORITIES[gap.id],
        status=gap.status,
        target_artifact=SAMPLE_LEDGER,
        source_type_needed=SOURCE_TYPES[gap.id],
        capture_gate=CAPTURE_GATES[gap.id],
        review_command=REVIEW_COMMAND,
        trigger=gap.trigger,
        evidence_needed=gap.evidence_needed,
        boundary=boundary_for(gap),
    )


def boundary_for(gap: collect_harness_sample_gaps.SampleGap) -> str:
    if gap.status == "future-work":
        return "Do not collect until the new project has an ADR or contract for auth, endpoint, redaction, and cost."
    return (
        "Use bounded project evidence only. Do not use synthetic fixtures, placeholders, raw transcripts, "
        "runtime JSONL, secrets, prompts, or old-project ledger rows as accepted real evidence."
    )


def emit_markdown(items: list[CollectionItem]) -> None:
    print("# Harness Sample Collection Plan")
    print()
    if not items:
        print("No sample gaps matched the selected filters.")
        return
    print("| Gap | Priority | Area | Status | Source type | Capture gate | Review command |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for item in items:
        print(
            f"| {item.gap_id} | {item.priority} | {item.area} | {item.status} | "
            f"{item.source_type_needed} | {item.capture_gate} | `{item.review_command}` |"
        )


def emit_json(items: list[CollectionItem]) -> None:
    print(json.dumps([asdict(item) for item in items], ensure_ascii=False, indent=2))


def emit_templates(items: list[CollectionItem]) -> None:
    for item in items:
        payload = {
            "schema_version": "harness-sample-gap-evidence/v1",
            "id": "GAP-SAMPLE-YYYY-MM-DD-replace-me",
            "gap_id": item.gap_id,
            "sampled_at": "YYYY-MM-DD",
            "source_type": item.source_type_needed,
            "outcome": "pending",
            "local_only": item.source_type_needed != "real-interop-run",
            "no_external_claim": True,
            "false_positive": False,
            "network_exported": False,
            "endpoint_scope": "none",
            "remote_status": "none",
            "sample_summary": "Replace with a bounded real-event summary.",
            "decision": "Pending review; do not count as accepted evidence.",
            "boundary_note": item.boundary,
            "action_taken": ["replace with operator action"],
            "evidence_refs": [TEMPLATE_DOC],
            "checker_refs": ["scripts/check_harness_sample_gap_evidence.py"],
        }
        print(json.dumps(payload, ensure_ascii=False))


def main() -> int:
    args = parse_args()
    items = build_queue(set(args.area), set(args.gap_id), include_future=args.include_future)
    if args.sample_template:
        emit_templates(items)
    elif args.json:
        emit_json(items)
    else:
        emit_markdown(items)
    return 0


if __name__ == "__main__":
    sys.exit(main())
