#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from runtime_sanitizer import compact_text, compact_transcript_path


ROOT = Path(__file__).resolve().parents[2]
TRANSCRIPT_KEYS = ("transcript_path", "transcriptPath")
MAX_ADDITIONAL_CONTEXT_CHARS = 1200
MAX_WARNINGS = 4
MAX_COMMAND_CHARS = 220
REPEATED_COMMAND_THRESHOLD = 3
REPEATED_FAILURE_THRESHOLD = 2
VALIDATION_LOOP_THRESHOLD = 6
PROMPT_CHURN_THRESHOLD = 4
LOOP_FINDING_CODES = ("repeated-command", "repeated-failure", "validation-loop", "prompt-churn")
RECOMMENDATION_BY_FINDING = {"repeated-command": "inspect-repeated-command", "repeated-failure": "checkpoint", "validation-loop": "shrink-validation", "prompt-churn": "narrow-task"}


@dataclass(frozen=True)
class ToolCall:
    signature: str
    is_validation: bool


@dataclass(frozen=True)
class LoopFinding:
    code: str
    message: str


@dataclass
class LoopScanState:
    calls_by_id: dict[str, ToolCall] = field(default_factory=dict)
    command_counts: Counter[str] = field(default_factory=Counter)
    command_first_line: dict[str, int] = field(default_factory=dict)
    validation_counts: Counter[str] = field(default_factory=Counter)
    failure_counts: Counter[str] = field(default_factory=Counter)
    failure_first_line: dict[str, int] = field(default_factory=dict)
    prompt_clusters: Counter[str] = field(default_factory=Counter)


def main() -> int:
    payload = load_payload()
    try:
        additional_context = build_additional_context(payload)
    except Exception:
        # Loop/scope monitoring is advisory and must never block Stop.
        return 0

    if not additional_context:
        return 0

    print(render_hook_output(additional_context))
    return 0


def load_payload() -> dict[str, Any]:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def build_additional_context(payload: dict[str, Any], root: Path = ROOT) -> str:
    transcript_path = resolve_transcript_path(payload, root)
    if transcript_path is None or not transcript_path.is_file():
        return ""

    state = scan_transcript(transcript_path)
    findings = collect_findings(state)
    if not findings:
        return ""

    selected = findings[:MAX_WARNINGS]
    lines = [
        "Loop/scope advisory: current transcript shows repeated work patterns.",
        f"Transcript: `{display_transcript_path(transcript_path)}`",
        *[f"- {finding.message}" for finding in selected],
    ]
    omitted_count = len(findings) - len(selected)
    if omitted_count > 0:
        lines.append(f"... {omitted_count} more loop/scope warning(s) omitted.")
    lines.append(f"Finding codes: `{','.join(finding.code for finding in selected)}`")
    recommendations = dict.fromkeys(RECOMMENDATION_BY_FINDING.get(finding.code, "checkpoint") for finding in selected)
    lines.append(f"Recommended sample actions: `{','.join(recommendations)}`")
    lines.append("Sample capture: keep bounded fields only; do not copy raw transcripts, secrets, or full tool output.")
    lines.append("Next turn: checkpoint, narrow the task, or inspect the repeated command before rerunning it.")
    return limit_additional_context("\n".join(lines))


def resolve_transcript_path(payload: dict[str, Any], root: Path) -> Path | None:
    raw_value = first_string(payload, TRANSCRIPT_KEYS)
    if not raw_value:
        return None
    path = Path(raw_value).expanduser()
    if not path.is_absolute():
        path = root / path
    return path


def scan_transcript(path: Path) -> LoopScanState:
    state = LoopScanState()
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line_no, raw_line in enumerate(handle, 1):
            try:
                record = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            payload = record.get("payload")
            if not isinstance(payload, dict):
                continue
            if record.get("type") == "response_item":
                observe_response_item(state, payload, line_no)
            elif record.get("type") == "event_msg":
                observe_event_msg(state, payload)
    return state


def observe_response_item(state: LoopScanState, payload: dict[str, Any], line_no: int) -> None:
    item_type = str(payload.get("type") or "")
    if item_type in {"function_call", "custom_tool_call"}:
        call = build_tool_call(payload, line_no)
        key = call_key(payload)
        if key:
            state.calls_by_id[key] = call
        if call.signature:
            state.command_counts[call.signature] += 1
            state.command_first_line.setdefault(call.signature, line_no)
            if call.is_validation:
                state.validation_counts[call.signature] += 1
        return

    if item_type not in {"function_call_output", "custom_tool_call_output"}:
        return
    output = payload.get("output")
    if not isinstance(output, str) or not is_failure_output(output):
        return
    call = state.calls_by_id.get(call_key(payload))
    signature = call.signature if call else "unknown tool output"
    state.failure_counts[signature] += 1
    state.failure_first_line.setdefault(signature, line_no)


def observe_event_msg(state: LoopScanState, payload: dict[str, Any]) -> None:
    text = first_string(payload, ("user_prompt", "prompt", "message", "text", "content", "input"))
    if not text:
        return
    cluster = prompt_cluster(text)
    if cluster:
        state.prompt_clusters[cluster] += 1


def build_tool_call(payload: dict[str, Any], line_no: int) -> ToolCall:
    tool_name = str(payload.get("name") or payload.get("tool_name") or payload.get("type") or "unknown-tool")
    command = extract_command(payload)
    signature = command_signature(tool_name, command, payload)
    return ToolCall(
        signature=signature,
        is_validation=is_validation_command(command),
    )


def extract_command(payload: dict[str, Any]) -> str:
    mapping = parse_mapping(payload.get("arguments") or payload.get("input") or payload.get("parameters"))
    command = first_string(mapping, ("cmd", "command", "shell_command", "shellCommand", "script"))
    if command:
        return command
    text = first_string(mapping, ("text",))
    return text if looks_like_command(text) else ""


def parse_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not isinstance(value, str) or not value.strip():
        return {}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return {"text": value}
    return parsed if isinstance(parsed, dict) else {"text": value}


def command_signature(tool_name: str, command: str, payload: dict[str, Any]) -> str:
    if command:
        return normalize_command(command)
    preview = payload.get("arguments") or payload.get("input") or payload.get("parameters") or ""
    return f"{tool_name}:{compact_text(str(preview), max_length=MAX_COMMAND_CHARS)}"


def collect_findings(state: LoopScanState) -> list[LoopFinding]:
    findings: list[LoopFinding] = []
    findings.extend(repeated_command_findings(state))
    findings.extend(repeated_failure_findings(state))
    findings.extend(validation_loop_findings(state))
    findings.extend(prompt_churn_findings(state))
    return findings


def repeated_command_findings(state: LoopScanState) -> list[LoopFinding]:
    findings = []
    for signature, count in state.command_counts.most_common():
        if count < REPEATED_COMMAND_THRESHOLD:
            continue
        findings.append(
            LoopFinding(
                "repeated-command",
                f"Repeated tool command {count}x from line {state.command_first_line[signature]}: "
                f"`{compact_text(signature, max_length=MAX_COMMAND_CHARS)}`.",
            )
        )
    return findings


def repeated_failure_findings(state: LoopScanState) -> list[LoopFinding]:
    findings = []
    for signature, count in state.failure_counts.most_common():
        if count < REPEATED_FAILURE_THRESHOLD:
            continue
        findings.append(
            LoopFinding(
                "repeated-failure",
                f"Repeated failed output {count}x from line {state.failure_first_line[signature]}: "
                f"`{compact_text(signature, max_length=MAX_COMMAND_CHARS)}`.",
            )
        )
    return findings


def validation_loop_findings(state: LoopScanState) -> list[LoopFinding]:
    total = sum(state.validation_counts.values())
    if total < VALIDATION_LOOP_THRESHOLD:
        return []
    repeated = ", ".join(
        compact_text(signature, max_length=80)
        for signature, count in state.validation_counts.most_common(3)
        if count > 1
    )
    suffix = f" Most repeated: {repeated}." if repeated else ""
    return [
        LoopFinding(
            "validation-loop",
            f"Validation/test commands ran {total} times in this transcript.{suffix}",
        )
    ]


def prompt_churn_findings(state: LoopScanState) -> list[LoopFinding]:
    if sum(state.prompt_clusters.values()) < PROMPT_CHURN_THRESHOLD:
        return []
    clusters = [cluster for cluster, count in state.prompt_clusters.items() if count > 0]
    if len(clusters) < PROMPT_CHURN_THRESHOLD:
        return []
    return [
        LoopFinding(
            "prompt-churn",
            f"Multiple distinct user/task prompt clusters observed ({len(clusters)}); confirm current scope before expanding context.",
        )
    ]


def is_failure_output(output: str) -> bool:
    return bool(
        re.search(
            r"(?i)\b(error|failed|failures|traceback|exception|assertionerror|panic|fatal|exit code [1-9])\b",
            output,
        )
    )


def is_validation_command(command: str) -> bool:
    if not command:
        return False
    return bool(
        re.search(
            r"\b(pytest|unittest|ruff|mypy|tsc|eslint|vitest|jest|go test|cargo test|check_.*\.py)\b"
            r"|\bpython3?\s+tests/",
            command,
        )
    )


def looks_like_command(value: str) -> bool:
    if not value:
        return False
    return value.split()[0] in {"python", "python3", "pytest", "npm", "pnpm", "cargo", "go", "ruff"}


def prompt_cluster(text: str) -> str:
    compact = compact_text(text, max_length=120).lower()
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", compact).strip()[:80]


def normalize_command(command: str) -> str:
    return " ".join(command.strip().split())


def call_key(payload: dict[str, Any]) -> str:
    return str(payload.get("call_id") or payload.get("id") or "")


def first_string(data: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def display_transcript_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return compact_transcript_path(str(path), MAX_COMMAND_CHARS)


def limit_additional_context(text: str, max_chars: int = MAX_ADDITIONAL_CONTEXT_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    marker = "\n[Loop/scope advisory truncated; inspect the current transcript if needed.]"
    prefix_length = max(0, max_chars - len(marker))
    return f"{text[:prefix_length].rstrip()}{marker}"[:max_chars]


def render_hook_output(additional_context: str) -> str:
    return json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "Stop",
                "additionalContext": additional_context,
            }
        },
        ensure_ascii=False,
    )


if __name__ == "__main__":
    raise SystemExit(main())
