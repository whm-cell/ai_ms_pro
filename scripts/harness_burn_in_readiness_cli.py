from __future__ import annotations

import argparse

from harness_burn_in_readiness_types import READINESS_STATES
from harness_sample_collection_config import CAPTURE_GATES, PRIORITY_LEVELS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit harness burn-in readiness without generating evidence.")
    parser.add_argument("--include-future", action="store_true", help="Include future-work gaps.")
    parser.add_argument("--include-accepted", action="store_true", help="Include accepted local-sample gaps.")
    parser.add_argument("--area", action="append", default=[], help="Filter by roadmap area. Repeatable.")
    parser.add_argument(
        "--priority",
        action="append",
        choices=PRIORITY_LEVELS,
        default=[],
        help="Filter by roadmap priority. Repeatable.",
    )
    parser.add_argument("--gap-id", action="append", default=[], help="Filter by exact gap id. Repeatable.")
    parser.add_argument(
        "--capture-gate",
        action="append",
        choices=CAPTURE_GATES,
        default=[],
        help="Filter by real-event capture gate. Repeatable.",
    )
    parser.add_argument(
        "--readiness",
        action="append",
        choices=READINESS_STATES,
        default=[],
        help="Filter by readiness state. Repeatable.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()
