#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_UPGRADE_DECISIONS = ROOT / "docs" / "ai" / "standards" / "harness-upgrade-decisions.jsonl"


@dataclass(frozen=True)
class UpgradeDecisionSnapshot:
    decision_id: str
    decision: str
    decision_ref: str
    next_evidence_needed: tuple[str, ...]


def load_upgrade_decisions(
    path: Path = DEFAULT_UPGRADE_DECISIONS,
) -> tuple[dict[str, UpgradeDecisionSnapshot], list[str]]:
    if not path.exists():
        return {}, [f"upgrade decision file missing: {relative(path)}"]
    decisions: dict[str, UpgradeDecisionSnapshot] = {}
    warnings: list[str] = []
    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw_line.strip():
            warnings.append(f"{relative(path)}:{line_no}: blank upgrade decision line")
            continue
        try:
            record = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            warnings.append(f"{relative(path)}:{line_no}: invalid upgrade decision JSON: {exc.msg}")
            continue
        if not isinstance(record, dict):
            warnings.append(f"{relative(path)}:{line_no}: upgrade decision must be an object")
            continue
        gap_id = text(record.get("gap_id"))
        decision_id = text(record.get("id"))
        decision = text(record.get("decision"))
        if gap_id and decision:
            decisions[gap_id] = UpgradeDecisionSnapshot(
                decision_id=decision_id,
                decision=decision,
                decision_ref=f"{relative(path)}:{line_no}",
                next_evidence_needed=tuple(safe_text_list(record.get("next_evidence_needed"))),
            )
    return decisions, warnings


def safe_text_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def text(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()
