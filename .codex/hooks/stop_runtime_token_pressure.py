#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from runtime_sanitizer import compact_text, compact_transcript_path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from runtime_token_budget_core import audit_transcript, read_config  # noqa: E402
from runtime_token_budget_types import (  # noqa: E402
    RuntimeTokenBudgetConfig,
    RuntimeTokenBudgetReport,
    ToolOutputFinding,
    TranscriptReport,
)


TRANSCRIPT_KEYS = ("transcript_path", "transcriptPath")
MAX_WARNINGS = 3
MAX_ADDITIONAL_CONTEXT_CHARS = 1200
MAX_PATH_CHARS = 220
MAX_TOOL_NAME_CHARS = 80


def main() -> int:
    payload = load_payload()
    try:
        additional_context = build_additional_context(payload)
    except Exception:
        # Runtime token pressure warnings are advisory and must never block Stop.
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

    config = read_config(root)
    transcript = audit_transcript(transcript_path, config)
    report = RuntimeTokenBudgetReport(
        config=config,
        transcripts=[transcript],
        warnings=transcript.warnings,
    )
    messages = warning_messages(report)
    if not messages:
        return ""

    selected = messages[:MAX_WARNINGS]
    omitted_count = len(messages) - len(selected)
    lines = [
        "Runtime token pressure detected in the current Stop transcript.",
        f"Transcript: `{display_transcript_path(transcript_path)}`",
        *[f"- {message}" for message in selected],
    ]
    if omitted_count > 0:
        lines.append(f"... {omitted_count} more warning(s) omitted; run check_runtime_token_budget.py for the full audit.")
    lines.append(
        "Next turn: checkpoint or narrow the task; preserve large raw output under "
        ".codex/runtime/tool-outputs/ and use summarize_tool_output.py --around <line>."
    )
    return limit_additional_context("\n".join(lines))


def resolve_transcript_path(payload: dict[str, Any], root: Path) -> Path | None:
    raw_value = first_value(payload, TRANSCRIPT_KEYS)
    if not isinstance(raw_value, str) or not raw_value.strip():
        return None
    path = Path(raw_value.strip()).expanduser()
    if not path.is_absolute():
        path = root / path
    return path


def first_value(data: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        value = data.get(key)
        if value not in ("", None):
            return value
    return None


def warning_messages(report: RuntimeTokenBudgetReport) -> list[str]:
    messages: list[str] = []
    for transcript in report.transcripts:
        messages.extend(transcript_warning_messages(transcript, report.config))
    return messages


def transcript_warning_messages(
    transcript: TranscriptReport,
    config: RuntimeTokenBudgetConfig,
) -> list[str]:
    messages: list[str] = []
    finding = largest_tool_output(transcript.tool_output_findings)
    if finding is not None:
        messages.append(
            "Large tool output: "
            f"line {finding.line}, approx {finding.estimated_tokens} tokens > "
            f"budget {config.tool_output_token_budget} from `{safe_tool_name(finding.tool_name)}`."
        )
    if transcript.max_fresh_input_tokens > config.fresh_input_token_budget:
        messages.append(
            "Fresh input/cache miss spike: "
            f"{transcript.max_fresh_input_tokens} > {config.fresh_input_token_budget}."
        )
    if transcript.max_last_input_tokens > config.last_input_token_budget:
        messages.append(
            f"Last input spike: {transcript.max_last_input_tokens} > {config.last_input_token_budget}."
        )
    if transcript.task_complete_count > config.task_complete_budget:
        messages.append(
            f"task_complete count high: {transcript.task_complete_count} > {config.task_complete_budget}."
        )
    if transcript.elapsed_minutes > config.session_minutes_budget:
        messages.append(
            f"Session elapsed minutes high: {transcript.elapsed_minutes} > {config.session_minutes_budget}."
        )
    if transcript.token_snapshot_count > config.token_snapshot_budget:
        messages.append(
            f"Token snapshot count high: {transcript.token_snapshot_count} > {config.token_snapshot_budget}."
        )
    extra_tool_outputs = sorted(
        transcript.tool_output_findings,
        key=lambda item: item.estimated_tokens,
        reverse=True,
    )[1:]
    for item in extra_tool_outputs:
        messages.append(
            "Additional large tool output: "
            f"line {item.line}, approx {item.estimated_tokens} tokens from `{safe_tool_name(item.tool_name)}`."
        )
    return messages


def largest_tool_output(findings: list[ToolOutputFinding]) -> ToolOutputFinding | None:
    if not findings:
        return None
    return max(findings, key=lambda item: item.estimated_tokens)


def safe_tool_name(value: str) -> str:
    return compact_text(value, max_length=MAX_TOOL_NAME_CHARS) or "unknown-tool"


def display_transcript_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return compact_transcript_path(str(path), MAX_PATH_CHARS)


def limit_additional_context(text: str, max_chars: int = MAX_ADDITIONAL_CONTEXT_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    marker = "\n[Runtime token pressure warning truncated; run check_runtime_token_budget.py for full audit.]"
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
