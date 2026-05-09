#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from runtime_handoff_renderer import render_handoff_draft

ROOT = Path(__file__).resolve().parents[1]

OBSERVATION_DIR = ROOT / ".codex" / "runtime" / "observations"
DEFAULT_LIMIT = 20


def main() -> int:
    args = parse_args()
    observation_file = resolve_observation_file(args.input)
    entries = load_observations(observation_file)
    selected = select_entries(entries, args.limit)
    markdown = render_handoff_draft(
        observation_file=observation_file,
        entries=entries,
        selected=selected,
        stage=args.stage,
        task=args.task,
        title=args.title,
        requirement_ids=args.requirement_ids,
        workstream_ids=args.workstream_ids,
    )

    if args.output:
        output_path = Path(args.output).expanduser()
        if not output_path.is_absolute():
            output_path = (ROOT / output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    else:
        print(markdown, end="")

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reduce runtime observations into a handoff-first markdown draft."
    )
    parser.add_argument(
        "--input",
        help="Path to a JSONL observation file. Defaults to the latest file in .codex/runtime/observations/.",
    )
    parser.add_argument(
        "--output",
        help="Optional markdown output path. If omitted, the reducer prints to stdout.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=f"How many most recent observations to consider after promotion filtering. Default: {DEFAULT_LIMIT}.",
    )
    parser.add_argument(
        "--stage",
        default="stage-00",
        help="Stage label to include in the draft metadata. Default: stage-00.",
    )
    parser.add_argument(
        "--task",
        default="runtime-observation-reducer-draft",
        help="Task label to include in the draft metadata.",
    )
    parser.add_argument(
        "--title",
        default="Runtime Observation Reducer Draft",
        help="Markdown title for the generated draft.",
    )
    parser.add_argument(
        "--requirement-id",
        action="append",
        default=[],
        dest="requirement_ids",
        help="Requirement ID to attach to the generated draft. Repeat for multiple IDs.",
    )
    parser.add_argument(
        "--workstream-id",
        action="append",
        default=[],
        dest="workstream_ids",
        help="Workstream ID to attach to the generated draft. Repeat for multiple IDs.",
    )
    return parser.parse_args()


def resolve_observation_file(value: str | None) -> Path:
    if value:
        path = Path(value).expanduser()
        if not path.is_absolute():
            path = (ROOT / path).resolve()
        if not path.exists():
            raise SystemExit(f"Observation file not found: {path}")
        return path

    candidates = observation_candidates()
    if not candidates:
        raise SystemExit(
            "No observation files found under .codex/runtime/observations/. "
            "Capture runtime observations first or pass --input."
        )
    return candidates[-1]


def observation_candidates() -> list[Path]:
    if not OBSERVATION_DIR.exists():
        return []
    files: list[Path] = []
    for path in sorted(OBSERVATION_DIR.glob("*.jsonl")):
        if path.name.startswith("_"):
            continue
        files.append(path)
    return files


def load_observations(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            records.append(payload)
    return records


def select_entries(entries: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    promotable = [entry for entry in entries if entry.get("needs_governance_promotion") is True]
    source = promotable if promotable else entries
    if limit <= 0:
        return source
    return source[-limit:]


if __name__ == "__main__":
    raise SystemExit(main())
