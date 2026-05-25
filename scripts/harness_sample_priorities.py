from __future__ import annotations

from typing import Any

from harness_sample_collection_config import PRIORITIES


def priority_for_gap(gap: Any) -> str:
    if gap.id in PRIORITIES:
        return PRIORITIES[gap.id]
    if gap.status == "future-work":
        return "P3"
    if gap.area in {"agentic-red-team", "workflow-skills"}:
        return "P2"
    return "P1"
