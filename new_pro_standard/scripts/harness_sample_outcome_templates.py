#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol


ROOT = Path(__file__).resolve().parents[1]


class OutcomeTemplateItem(Protocol):
    gap_id: str
    pending_slot_refs: tuple[str, ...]


def outcome_candidate_template(item: OutcomeTemplateItem) -> dict[str, object]:
    record = pending_record_for_item(item)
    if not record:
        return {
            "schema_version": "",
            "id": "",
            "gap_id": item.gap_id,
            "source_type": "",
            "outcome": "rejected",
        }
    candidate = dict(record)
    candidate["outcome"] = "rejected"
    return candidate


def pending_record_for_item(item: OutcomeTemplateItem) -> dict[str, object]:
    if len(item.pending_slot_refs) != 1:
        return {}
    ledger_ref = item.pending_slot_refs[0].split(" @ ", 1)[-1].strip()
    ledger_path, separator, line_text = ledger_ref.rpartition(":")
    if not separator or not line_text.isdigit():
        return {}
    path = ROOT / ledger_path
    if not path.exists():
        return {}
    line_no = int(line_text)
    lines = path.read_text(encoding="utf-8").splitlines()
    if line_no < 1 or line_no > len(lines):
        return {}
    try:
        record = json.loads(lines[line_no - 1])
    except json.JSONDecodeError:
        return {}
    return record if isinstance(record, dict) else {}
