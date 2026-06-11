from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime_token_budget_types import (
    CONFIG_KEYS,
    RuntimeTokenBudgetConfig,
    RuntimeTokenBudgetReport,
    ToolOutputFinding,
    TranscriptReport,
)

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class TranscriptScanState:
    line_count: int = 0
    task_complete_count: int = 0
    token_snapshot_count: int = 0
    first_timestamp: datetime | None = None
    last_timestamp: datetime | None = None
    max_last_input: int = 0
    max_last_cached: int = 0
    max_fresh_input: int = 0
    max_tool_output: int = 0
    tool_calls: dict[str, tuple[str, str]] = field(default_factory=dict)
    large_outputs: list[ToolOutputFinding] = field(default_factory=list)

    def observe_timestamp(self, value: object) -> None:
        timestamp = parse_timestamp(value)
        if timestamp is None:
            return
        self.first_timestamp = min(self.first_timestamp, timestamp) if self.first_timestamp else timestamp
        self.last_timestamp = max(self.last_timestamp, timestamp) if self.last_timestamp else timestamp

    def elapsed_minutes(self) -> int:
        if not self.first_timestamp or not self.last_timestamp:
            return 0
        return round((self.last_timestamp - self.first_timestamp).total_seconds() / 60)


def relative(path: Path, root: Path = ROOT) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def read_config(root: Path = ROOT) -> RuntimeTokenBudgetConfig:
    path = root / ".codex" / "harness.toml"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    section = extract_section(text, "runtime_token_budget")
    values = {key: positive_int(section, key, default) for key, default in CONFIG_KEYS.items()}
    return RuntimeTokenBudgetConfig(**values)


def extract_section(raw_text: str, section_name: str) -> str:
    match = re.search(rf"(?ms)^\[{re.escape(section_name)}\]\s*(.*?)(?=^\[|\Z)", raw_text)
    return match.group(1) if match else ""


def positive_int(section_text: str, key: str, default: int) -> int:
    match = re.search(rf"(?m)^\s*{re.escape(key)}\s*=\s*([0-9]+)\s*$", section_text)
    if not match:
        return default
    value = int(match.group(1))
    if value < 1:
        raise ValueError(f"runtime_token_budget.{key} must be positive")
    return value


def parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def estimated_tokens(text: str) -> int:
    match = re.search(r"Original token count:\s*([0-9]+)", text)
    if match:
        return int(match.group(1))
    return max(1, round(len(text) / 4)) if text else 0


def compact_preview(value: object, limit: int = 140) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
    return re.sub(r"\s+", " ", text).strip()[:limit]


def token_usage(payload: dict[str, Any]) -> tuple[int, int]:
    info = payload.get("info")
    if not isinstance(info, dict):
        return 0, 0
    last = info.get("last_token_usage")
    if not isinstance(last, dict):
        return 0, 0
    return int(last.get("input_tokens") or 0), int(last.get("cached_input_tokens") or 0)


def call_key(payload: dict[str, Any]) -> str:
    return str(payload.get("call_id") or payload.get("id") or "")


def handle_event_msg(state: TranscriptScanState, payload: dict[str, Any]) -> None:
    event_type = payload.get("type")
    if event_type == "task_complete":
        state.task_complete_count += 1
    elif event_type == "token_count" and payload.get("info"):
        state.token_snapshot_count += 1
        last_input, last_cached = token_usage(payload)
        state.max_last_input = max(state.max_last_input, last_input)
        state.max_last_cached = max(state.max_last_cached, last_cached)
        state.max_fresh_input = max(state.max_fresh_input, max(last_input - last_cached, 0))


def handle_response_item(
    state: TranscriptScanState,
    payload: dict[str, Any],
    line_no: int,
    config: RuntimeTokenBudgetConfig,
) -> None:
    item_type = payload.get("type")
    if item_type in {"function_call", "custom_tool_call"}:
        state.tool_calls[call_key(payload)] = (
            str(payload.get("name") or item_type),
            compact_preview(payload.get("arguments") or payload.get("input") or ""),
        )
    elif item_type in {"function_call_output", "custom_tool_call_output"}:
        record_tool_output(state, payload, line_no, config, str(item_type))


def record_tool_output(
    state: TranscriptScanState,
    payload: dict[str, Any],
    line_no: int,
    config: RuntimeTokenBudgetConfig,
    fallback_name: str,
) -> None:
    output = payload.get("output")
    if not isinstance(output, str):
        return
    output_tokens = estimated_tokens(output)
    state.max_tool_output = max(state.max_tool_output, output_tokens)
    if output_tokens <= config.tool_output_token_budget:
        return
    tool_name, arguments = state.tool_calls.get(call_key(payload), (fallback_name, ""))
    state.large_outputs.append(
        ToolOutputFinding(
            line=line_no,
            estimated_tokens=output_tokens,
            tool_name=tool_name,
            arguments_preview=arguments,
        )
    )


def audit_transcript(path: Path, config: RuntimeTokenBudgetConfig) -> TranscriptReport:
    state = TranscriptScanState()
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line_no, raw_line in enumerate(handle, 1):
            state.line_count = line_no
            try:
                record = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            state.observe_timestamp(record.get("timestamp"))
            payload = record.get("payload")
            if not isinstance(payload, dict):
                continue
            if record.get("type") == "event_msg":
                handle_event_msg(state, payload)
            elif record.get("type") == "response_item":
                handle_response_item(state, payload, line_no, config)
    return build_transcript_report(path, state, config)


def build_transcript_report(
    path: Path,
    state: TranscriptScanState,
    config: RuntimeTokenBudgetConfig,
) -> TranscriptReport:
    elapsed_minutes = state.elapsed_minutes()
    warnings = report_warnings(
        path=path,
        config=config,
        task_complete_count=state.task_complete_count,
        token_snapshot_count=state.token_snapshot_count,
        elapsed_minutes=elapsed_minutes,
        max_last_input=state.max_last_input,
        max_fresh_input=state.max_fresh_input,
        large_outputs=state.large_outputs,
    )
    return TranscriptReport(
        path=relative(path),
        line_count=state.line_count,
        task_complete_count=state.task_complete_count,
        token_snapshot_count=state.token_snapshot_count,
        elapsed_minutes=elapsed_minutes,
        max_last_input_tokens=state.max_last_input,
        max_last_cached_tokens=state.max_last_cached,
        max_fresh_input_tokens=state.max_fresh_input,
        max_tool_output_tokens=state.max_tool_output,
        tool_output_findings=state.large_outputs,
        warnings=warnings,
    )


def report_warnings(
    *,
    path: Path,
    config: RuntimeTokenBudgetConfig,
    task_complete_count: int,
    token_snapshot_count: int,
    elapsed_minutes: int,
    max_last_input: int,
    max_fresh_input: int,
    large_outputs: list[ToolOutputFinding],
) -> list[str]:
    prefix = relative(path)
    warnings = threshold_warnings(
        prefix=prefix,
        config=config,
        task_complete_count=task_complete_count,
        token_snapshot_count=token_snapshot_count,
        elapsed_minutes=elapsed_minutes,
        max_last_input=max_last_input,
        max_fresh_input=max_fresh_input,
    )
    warnings.extend(tool_output_warnings(prefix, config, large_outputs))
    return warnings


def threshold_warnings(
    *,
    prefix: str,
    config: RuntimeTokenBudgetConfig,
    task_complete_count: int,
    token_snapshot_count: int,
    elapsed_minutes: int,
    max_last_input: int,
    max_fresh_input: int,
) -> list[str]:
    checks = (
        ("last input tokens", max_last_input, config.last_input_token_budget),
        ("fresh input tokens", max_fresh_input, config.fresh_input_token_budget),
        ("task_complete count", task_complete_count, config.task_complete_budget),
        ("token snapshot count", token_snapshot_count, config.token_snapshot_budget),
        ("elapsed minutes", elapsed_minutes, config.session_minutes_budget),
    )
    return [
        f"{prefix}: {label} exceeded budget ({value} > {budget})."
        for label, value, budget in checks
        if value > budget
    ]


def tool_output_warnings(
    prefix: str,
    config: RuntimeTokenBudgetConfig,
    large_outputs: list[ToolOutputFinding],
) -> list[str]:
    return [
        f"{prefix}: line {finding.line} tool output exceeded budget "
        f"({finding.estimated_tokens} > {config.tool_output_token_budget}) "
        f"from {finding.tool_name}."
        for finding in large_outputs
    ]


def build_report(
    *,
    root: Path = ROOT,
    transcript_paths: list[Path] | None = None,
) -> RuntimeTokenBudgetReport:
    config = read_config(root)
    transcripts = [audit_transcript(path, config) for path in transcript_paths or []]
    warnings = [warning for report in transcripts for warning in report.warnings]
    return RuntimeTokenBudgetReport(config=config, transcripts=transcripts, warnings=warnings)


def render_report(report: RuntimeTokenBudgetReport) -> str:
    lines = [
        "Runtime token budget audit:",
        f"- transcripts: {len(report.transcripts)}",
        "- budgets: "
        f"tool_output<={report.config.tool_output_token_budget}, "
        f"last_input<={report.config.last_input_token_budget}, "
        f"fresh_input<={report.config.fresh_input_token_budget}, "
        f"task_complete<={report.config.task_complete_budget}, "
        f"token_snapshots<={report.config.token_snapshot_budget}, "
        f"elapsed_minutes<={report.config.session_minutes_budget}",
    ]
    if not report.transcripts:
        lines.append("- no transcript paths supplied; CI wiring check only")
    for transcript in report.transcripts:
        lines.extend(render_transcript_summary(transcript))
    if report.warnings:
        lines.extend(["", "Warnings:"])
        lines.extend(f"- {warning}" for warning in report.warnings)
    else:
        lines.extend(["", "Warnings: none"])
    return "\n".join(lines)


def render_transcript_summary(transcript: TranscriptReport) -> list[str]:
    return [
        "",
        f"Transcript: {transcript.path}",
        f"- lines: {transcript.line_count}",
        f"- task_complete: {transcript.task_complete_count}",
        f"- token snapshots: {transcript.token_snapshot_count}",
        f"- elapsed minutes: {transcript.elapsed_minutes}",
        f"- max last input tokens: {transcript.max_last_input_tokens}",
        f"- max cached input tokens: {transcript.max_last_cached_tokens}",
        f"- max fresh input tokens: {transcript.max_fresh_input_tokens}",
        f"- max tool output tokens: {transcript.max_tool_output_tokens}",
    ]
