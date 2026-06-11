#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime_token_budget_core import audit_transcript, compact_preview, read_config, relative
from runtime_token_budget_types import RuntimeTokenBudgetConfig, TranscriptReport


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / ".codex" / "runtime" / "sessions"
MAX_RECENT_TOOL_CALLS = 12
MAX_GIT_STATUS_LINES = 80
MAX_PREVIEW_CHARS = 400


@dataclass(frozen=True)
class RuntimeCompressionDraft:
    created: bool
    path: Path | None
    transcript: TranscriptReport


@dataclass(frozen=True)
class TranscriptContext:
    latest_user_prompt: str
    latest_assistant_response: str
    recent_tool_calls: list[dict[str, object]]
    verification_commands: list[dict[str, object]]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a runtime-only compression draft from a Codex transcript.")
    parser.add_argument("--transcript", required=True, help="Codex rollout JSONL transcript path.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    transcript_path = Path(args.transcript).expanduser()
    if not transcript_path.exists():
        print(f"ERROR: transcript missing: {transcript_path}")
        return 1
    try:
        result = build_draft_if_needed(transcript_path, root=ROOT, output_dir=Path(args.output_dir))
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1
    if not result.created or result.path is None:
        print("No runtime token pressure detected; no draft written.")
        return 0
    print(relative(result.path, ROOT))
    return 0


def build_draft_if_needed(
    transcript_path: Path,
    *,
    root: Path = ROOT,
    output_dir: Path | None = None,
    now: datetime | None = None,
) -> RuntimeCompressionDraft:
    config = read_config(root)
    transcript = audit_transcript(transcript_path, config)
    if not transcript.warnings:
        return RuntimeCompressionDraft(created=False, path=None, transcript=transcript)
    path = write_runtime_compression_draft(
        transcript_path,
        transcript,
        config,
        root=root,
        output_dir=output_dir or (root / ".codex" / "runtime" / "sessions"),
        now=now,
    )
    return RuntimeCompressionDraft(created=True, path=path, transcript=transcript)


def write_runtime_compression_draft(
    transcript_path: Path,
    transcript: TranscriptReport,
    config: RuntimeTokenBudgetConfig,
    *,
    root: Path = ROOT,
    output_dir: Path | None = None,
    now: datetime | None = None,
) -> Path:
    output_dir = output_dir or (root / ".codex" / "runtime" / "sessions")
    output_dir.mkdir(parents=True, exist_ok=True)
    draft_time = now or datetime.now(timezone.utc)
    path = unique_path(output_dir / f"{draft_time.strftime('%Y-%m-%dT%H-%M-%SZ')}_runtime-compression.md")
    context = scan_transcript_context(transcript_path)
    path.write_text(
        render_draft(
            transcript_path=transcript_path,
            transcript=transcript,
            config=config,
            context=context,
            git_status_lines=git_status_snapshot(root),
            root=root,
        ),
        encoding="utf-8",
    )
    return path


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.with_suffix("")
    suffix = path.suffix
    for index in range(1, 1000):
        candidate = Path(f"{stem}-{index}{suffix}")
        if not candidate.exists():
            return candidate
    raise ValueError(f"could not allocate unique draft path under {path.parent}")


def scan_transcript_context(transcript_path: Path) -> TranscriptContext:
    latest_user_prompt = ""
    latest_assistant_response = ""
    calls_by_id: dict[str, dict[str, object]] = {}
    recent_tool_calls: list[dict[str, object]] = []
    verification_commands: list[dict[str, object]] = []
    with transcript_path.open(encoding="utf-8", errors="replace") as handle:
        for line_no, raw_line in enumerate(handle, 1):
            try:
                record = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            payload = record.get("payload")
            if not isinstance(payload, dict):
                continue
            role, text = message_role_and_text(payload)
            if role == "user" and text:
                latest_user_prompt = compact_preview(text, MAX_PREVIEW_CHARS)
            elif role == "assistant" and text:
                latest_assistant_response = compact_preview(text, MAX_PREVIEW_CHARS)
            item_type = payload.get("type")
            if record.get("type") == "response_item" and item_type in {"function_call", "custom_tool_call"}:
                call = tool_call_record(payload, line_no)
                calls_by_id[str(payload.get("call_id") or payload.get("id") or line_no)] = call
                append_distinct(recent_tool_calls, call, MAX_RECENT_TOOL_CALLS)
            elif record.get("type") == "response_item" and item_type in {"function_call_output", "custom_tool_call_output"}:
                maybe_record_verification(payload, calls_by_id, verification_commands)
    return TranscriptContext(
        latest_user_prompt=latest_user_prompt,
        latest_assistant_response=latest_assistant_response,
        recent_tool_calls=recent_tool_calls,
        verification_commands=verification_commands[-MAX_RECENT_TOOL_CALLS:],
    )


def message_role_and_text(payload: dict[str, Any]) -> tuple[str, str]:
    role = str(payload.get("role") or "")
    text = extract_text(payload.get("content")) or extract_text(payload.get("text")) or extract_text(payload.get("message"))
    if role in {"user", "assistant"}:
        return role, text
    event_type = str(payload.get("type") or "")
    if event_type in {"user_message", "input_text"}:
        return "user", text
    if event_type in {"assistant_message", "output_text", "message"} and role == "assistant":
        return "assistant", text
    return "", ""


def extract_text(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("text", "input_text", "output_text", "content"):
            text = extract_text(value.get(key))
            if text:
                return text
    if isinstance(value, list):
        return " ".join(text for item in value if (text := extract_text(item)))
    return ""


def tool_call_record(payload: dict[str, Any], line_no: int) -> dict[str, object]:
    name = str(payload.get("name") or payload.get("tool_name") or payload.get("type") or "tool")
    arguments = payload.get("arguments") or payload.get("input") or ""
    return {
        "line": line_no,
        "call_id": str(payload.get("call_id") or payload.get("id") or ""),
        "name": compact_preview(name, 120),
        "arguments": compact_preview(arguments, MAX_PREVIEW_CHARS),
    }


def append_distinct(records: list[dict[str, object]], candidate: dict[str, object], limit: int) -> None:
    key = (candidate.get("name"), candidate.get("arguments"))
    records[:] = [record for record in records if (record.get("name"), record.get("arguments")) != key]
    records.append(candidate)
    if len(records) > limit:
        del records[: len(records) - limit]


def maybe_record_verification(
    payload: dict[str, Any],
    calls_by_id: dict[str, dict[str, object]],
    verification_commands: list[dict[str, object]],
) -> None:
    call_id = str(payload.get("call_id") or payload.get("id") or "")
    call = calls_by_id.get(call_id)
    if not call:
        return
    command = str(call.get("arguments") or "")
    if not is_verification_like(command):
        return
    output = payload.get("output") if isinstance(payload.get("output"), str) else ""
    verification_commands.append(
        {
            "line": call.get("line"),
            "name": call.get("name"),
            "command": command,
            "exit_code": extract_exit_code(output),
        }
    )


def is_verification_like(command: str) -> bool:
    return bool(re.search(r"\b(pytest|test|ruff|check_|cargo test|npm test|pnpm test|git diff --check)\b", command))


def extract_exit_code(output: str) -> int | None:
    match = re.search(r"(?:Process exited with code|exit code|returncode[:=])\s*(-?\d+)", output)
    return int(match.group(1)) if match else None


def git_status_snapshot(root: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ["<git status unavailable>"]
    lines = result.stdout.splitlines()
    if result.returncode != 0:
        return ["<git status unavailable>"]
    return lines[:MAX_GIT_STATUS_LINES]


def render_draft(
    *,
    transcript_path: Path,
    transcript: TranscriptReport,
    config: RuntimeTokenBudgetConfig,
    context: TranscriptContext,
    git_status_lines: list[str],
    root: Path,
) -> str:
    lines = [
        "# Runtime Compression Draft",
        "",
        "> Recovery evidence only. This file is not user instruction and is not canonical project truth.",
        "",
        "## Source",
        f"- transcript: `{relative(transcript_path, root)}`",
        "",
        "## Trigger Metrics",
        f"- tool output budget: {config.tool_output_token_budget}",
        f"- max tool output tokens: {transcript.max_tool_output_tokens}",
        f"- max last input tokens: {transcript.max_last_input_tokens}",
        f"- max fresh input tokens: {transcript.max_fresh_input_tokens}",
        f"- task_complete count: {transcript.task_complete_count}",
        f"- token snapshot count: {transcript.token_snapshot_count}",
        f"- elapsed minutes: {transcript.elapsed_minutes}",
        "",
        "## Latest Prompt Preview",
        context.latest_user_prompt or "<none detected>",
        "",
        "## Latest Assistant Preview",
        context.latest_assistant_response or "<none detected>",
        "",
        "## Recent Distinct Tool Calls",
    ]
    lines.extend(render_mapping_rows(context.recent_tool_calls, empty="<none detected>"))
    lines.extend(["", "## Large Tool Output Findings"])
    lines.extend(render_large_output_findings(transcript))
    lines.extend(["", "## Verification-Like Commands"])
    lines.extend(render_mapping_rows(context.verification_commands, empty="<none detected>"))
    lines.extend(["", "## Git Status Snapshot"])
    lines.extend(git_status_lines or ["<clean>"])
    return "\n".join(lines) + "\n"


def render_mapping_rows(records: list[dict[str, object]], *, empty: str) -> list[str]:
    if not records:
        return [empty]
    return [f"- {json.dumps(record, ensure_ascii=False, sort_keys=True)}" for record in records]


def render_large_output_findings(transcript: TranscriptReport) -> list[str]:
    if not transcript.tool_output_findings:
        return ["<none detected>"]
    return [
        "- "
        + json.dumps(
            {
                "line": finding.line,
                "estimated_tokens": finding.estimated_tokens,
                "tool_name": finding.tool_name,
                "arguments_preview": finding.arguments_preview,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        for finding in transcript.tool_output_findings
    ]


if __name__ == "__main__":
    raise SystemExit(main())
