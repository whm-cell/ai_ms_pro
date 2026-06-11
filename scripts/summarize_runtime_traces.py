#!/usr/bin/env python3

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUNTIME_DIR = ROOT / ".codex" / "runtime" / "observations"
TRACE_DIR_NAME = "agent-traces"


@dataclass(frozen=True)
class CountEntry:
    value: str
    count: int


@dataclass(frozen=True)
class RecentObservation:
    timestamp: str
    event: str
    agent: str
    changed_path_count: int
    docs_changed: bool
    runtime_only_changes: bool
    needs_governance_promotion: bool
    requirement_ids: list[str]
    workstream_ids: list[str]
    traceability_source: str


@dataclass(frozen=True)
class RuntimeTraceSummary:
    runtime_dir: str
    observation_files: list[str]
    trace_files: list[str]
    observation_count: int
    trace_record_count: int
    invalid_jsonl_lines: int
    session_count: int
    trace_count: int
    agent_roles: list[CountEntry]
    observation_events: list[CountEntry]
    trace_events: list[CountEntry]
    trace_statuses: list[CountEntry]
    redaction_states: list[CountEntry]
    promotion_needed_count: int
    docs_changed_count: int
    runtime_only_count: int
    missing_traceability_count: int
    requirement_ids: list[CountEntry]
    workstream_ids: list[CountEntry]
    changed_paths: list[CountEntry]
    recent_observations: list[RecentObservation]
    warnings: list[str]


@dataclass
class SummaryState:
    observation_files: list[str] = field(default_factory=list)
    trace_files: list[str] = field(default_factory=list)
    observation_count: int = 0
    trace_record_count: int = 0
    invalid_jsonl_lines: int = 0
    promotion_needed_count: int = 0
    docs_changed_count: int = 0
    runtime_only_count: int = 0
    missing_traceability_count: int = 0
    sessions: set[str] = field(default_factory=set)
    traces: set[str] = field(default_factory=set)
    agent_roles: Counter[str] = field(default_factory=Counter)
    observation_events: Counter[str] = field(default_factory=Counter)
    trace_events: Counter[str] = field(default_factory=Counter)
    trace_statuses: Counter[str] = field(default_factory=Counter)
    redaction_states: Counter[str] = field(default_factory=Counter)
    requirement_ids: Counter[str] = field(default_factory=Counter)
    workstream_ids: Counter[str] = field(default_factory=Counter)
    changed_paths: Counter[str] = field(default_factory=Counter)
    recent: list[RecentObservation] = field(default_factory=list)

    def add_observation(self, record: dict[str, Any]) -> None:
        self.observation_count += 1
        self.sessions.add(text_value(record.get("session_id")) or "unknown-session")
        self.agent_roles.update([text_value(record.get("agent")) or "unknown"])
        self.observation_events.update([text_value(record.get("event")) or "unknown"])
        self.add_common_metadata(record)
        self.recent.append(recent_observation(record))

    def add_trace(self, record: dict[str, Any]) -> None:
        self.trace_record_count += 1
        self.traces.add(text_value(record.get("trace_id")) or "unknown-trace")
        self.trace_events.update([text_value(record.get("event")) or "unknown"])
        self.trace_statuses.update([dict_text(record.get("status"), "code", "unset")])
        self.redaction_states.update([dict_text(record.get("redaction"), "state", "unset")])
        if self.observation_count == 0:
            agent = record.get("agent") if isinstance(record.get("agent"), dict) else {}
            self.agent_roles.update([text_value(agent.get("role")) or text_value(agent.get("name")) or "unknown"])
            self.add_common_metadata(trace_common(record))

    def add_common_metadata(self, record: dict[str, Any]) -> None:
        if bool(record.get("needs_governance_promotion")):
            self.promotion_needed_count += 1
        if bool(record.get("docs_changed")):
            self.docs_changed_count += 1
        if bool(record.get("runtime_only_changes")):
            self.runtime_only_count += 1
        requirement_ids = list_values(record.get("requirement_ids"))
        workstream_ids = list_values(record.get("workstream_ids"))
        if not requirement_ids and not workstream_ids:
            self.missing_traceability_count += 1
        self.requirement_ids.update(requirement_ids)
        self.workstream_ids.update(workstream_ids)
        self.changed_paths.update(list_values(record.get("changed_paths")))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize local runtime observations and agent traces.")
    parser.add_argument("--runtime-dir", default=str(DEFAULT_RUNTIME_DIR), help="Runtime observation directory.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--max-files", type=int, default=14, help="Maximum recent observation and trace files per type.")
    parser.add_argument("--top", type=int, default=10, help="Maximum entries per distribution.")
    parser.add_argument("--max-recent", type=int, default=5, help="Maximum recent observations to show.")
    return parser.parse_args()


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def newest(paths: list[Path], max_files: int) -> list[Path]:
    ordered = sorted(paths, key=lambda path: path.name, reverse=True)
    return ordered if max_files == 0 else ordered[:max_files]


def jsonl_files(directory: Path, pattern: str, max_files: int) -> list[Path]:
    if not directory.exists():
        return []
    return newest([path for path in directory.glob(pattern) if path.is_file()], max_files)


def iter_jsonl(path: Path):
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                yield line_no, None
                continue
            yield line_no, record if isinstance(record, dict) else None


def build_summary(
    runtime_dir: Path = DEFAULT_RUNTIME_DIR,
    *,
    max_files: int = 14,
    top: int = 10,
    max_recent: int = 5,
) -> RuntimeTraceSummary:
    if max_files < 0 or top < 0 or max_recent < 0:
        raise ValueError("max_files, top, and max_recent must be zero or greater")
    state = SummaryState()
    read_records(state, jsonl_files(runtime_dir, "*.jsonl", max_files), trace=False)
    read_records(state, jsonl_files(runtime_dir / TRACE_DIR_NAME, "*.agent-trace.jsonl", max_files), trace=True)
    recent = sorted(state.recent, key=lambda item: item.timestamp, reverse=True)[:max_recent]
    return RuntimeTraceSummary(
        runtime_dir=relative(runtime_dir),
        observation_files=state.observation_files,
        trace_files=state.trace_files,
        observation_count=state.observation_count,
        trace_record_count=state.trace_record_count,
        invalid_jsonl_lines=state.invalid_jsonl_lines,
        session_count=len(state.sessions),
        trace_count=len(state.traces),
        agent_roles=top_counts(state.agent_roles, top),
        observation_events=top_counts(state.observation_events, top),
        trace_events=top_counts(state.trace_events, top),
        trace_statuses=top_counts(state.trace_statuses, top),
        redaction_states=top_counts(state.redaction_states, top),
        promotion_needed_count=state.promotion_needed_count,
        docs_changed_count=state.docs_changed_count,
        runtime_only_count=state.runtime_only_count,
        missing_traceability_count=state.missing_traceability_count,
        requirement_ids=top_counts(state.requirement_ids, top),
        workstream_ids=top_counts(state.workstream_ids, top),
        changed_paths=top_counts(state.changed_paths, top),
        recent_observations=recent,
        warnings=warnings_for(state),
    )


def read_records(state: SummaryState, files: list[Path], *, trace: bool) -> None:
    for path in files:
        (state.trace_files if trace else state.observation_files).append(relative(path))
        for _, record in iter_jsonl(path):
            if record is None:
                state.invalid_jsonl_lines += 1
                continue
            state.add_trace(record) if trace else state.add_observation(record)


def trace_common(record: dict[str, Any]) -> dict[str, Any]:
    attributes = record.get("attributes") if isinstance(record.get("attributes"), dict) else {}
    return {
        "needs_governance_promotion": attributes.get("needs_governance_promotion"),
        "docs_changed": attributes.get("docs_changed"),
        "runtime_only_changes": attributes.get("runtime_only_changes"),
        "requirement_ids": record.get("requirement_ids"),
        "workstream_ids": record.get("workstream_ids"),
        "changed_paths": attributes.get("changed_paths"),
    }


def recent_observation(record: dict[str, Any]) -> RecentObservation:
    return RecentObservation(
        timestamp=text_value(record.get("timestamp")),
        event=text_value(record.get("event")) or "unknown",
        agent=text_value(record.get("agent")) or "unknown",
        changed_path_count=int_value(record.get("changed_path_count")),
        docs_changed=bool(record.get("docs_changed")),
        runtime_only_changes=bool(record.get("runtime_only_changes")),
        needs_governance_promotion=bool(record.get("needs_governance_promotion")),
        requirement_ids=list_values(record.get("requirement_ids"))[:8],
        workstream_ids=list_values(record.get("workstream_ids"))[:8],
        traceability_source=text_value(record.get("traceability_source")) or "unknown",
    )


def warnings_for(state: SummaryState) -> list[str]:
    warnings: list[str] = []
    if state.promotion_needed_count:
        warnings.append(f"{state.promotion_needed_count} records need governance promotion review.")
    if state.missing_traceability_count:
        warnings.append(f"{state.missing_traceability_count} records have no REQ/WS traceability IDs.")
    if state.invalid_jsonl_lines:
        warnings.append(f"{state.invalid_jsonl_lines} JSONL lines could not be parsed.")
    error_statuses = sum(count for status, count in state.trace_statuses.items() if status.lower() not in {"ok", "unset"})
    if error_statuses:
        warnings.append(f"{error_statuses} trace records report non-ok status.")
    return warnings


def top_counts(counter: Counter[str], limit: int) -> list[CountEntry]:
    return [CountEntry(value=value, count=count) for value, count in counter.most_common(limit)]


def text_value(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def int_value(value: Any) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def list_values(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def dict_text(value: Any, key: str, default: str) -> str:
    if isinstance(value, dict):
        return text_value(value.get(key)) or default
    return default


def render_count_entries(entries: list[CountEntry]) -> list[str]:
    return [f"- `{item.value}`: {item.count}" for item in entries] or ["- none"]


def render_markdown(summary: RuntimeTraceSummary) -> str:
    lines = [
        "# Runtime Trace Summary",
        "",
        f"- runtime dir: `{summary.runtime_dir}`",
        f"- observation files: {len(summary.observation_files)}",
        f"- trace files: {len(summary.trace_files)}",
        f"- observations: {summary.observation_count}",
        f"- trace records: {summary.trace_record_count}",
        f"- unique sessions: {summary.session_count}",
        f"- unique traces: {summary.trace_count}",
        f"- invalid JSONL lines: {summary.invalid_jsonl_lines}",
        f"- needs governance promotion: {summary.promotion_needed_count}",
        "",
        "## Warnings",
    ]
    lines.extend(f"- {item}" for item in summary.warnings or ["none"])
    lines.extend(section("Agent Roles", summary.agent_roles))
    lines.extend(section("Observation Events", summary.observation_events))
    lines.extend(section("Trace Events", summary.trace_events))
    lines.extend(section("Trace Statuses", summary.trace_statuses))
    lines.extend(section("REQ Coverage", summary.requirement_ids))
    lines.extend(section("WS Coverage", summary.workstream_ids))
    lines.extend(section("Top Changed Paths", summary.changed_paths))
    lines.extend(["", "## Recent Observations"])
    if not summary.recent_observations:
        lines.append("- none")
    for item in summary.recent_observations:
        lines.append(
            "- "
            f"{item.timestamp or 'unknown-time'} | {item.event} | agent={item.agent} | "
            f"changed_paths={item.changed_path_count} | docs_changed={item.docs_changed} | "
            f"runtime_only={item.runtime_only_changes} | promotion={item.needs_governance_promotion} | "
            f"REQ={','.join(item.requirement_ids) or 'none'} | WS={','.join(item.workstream_ids) or 'none'}"
        )
    return "\n".join(lines)


def section(title: str, entries: list[CountEntry]) -> list[str]:
    return ["", f"## {title}", *render_count_entries(entries)]


def main() -> int:
    args = parse_args()
    try:
        summary = build_summary(
            Path(args.runtime_dir).expanduser(),
            max_files=args.max_files,
            top=args.top,
            max_recent=args.max_recent,
        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(asdict(summary), ensure_ascii=False, indent=2))
    else:
        print(render_markdown(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
