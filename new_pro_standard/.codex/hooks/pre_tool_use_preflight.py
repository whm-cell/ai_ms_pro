#!/usr/bin/env python3

from __future__ import annotations

import json
import shlex
import sys
from pathlib import Path
from typing import Any

from preflight_risk_catalog import (
    PreflightFinding,
    bounded_command_suggestions,
    shell_command_findings,
    tool_name_findings,
)
from runtime_sanitizer import compact_text


ROOT = Path(__file__).resolve().parents[2]
MAX_ADDITIONAL_CONTEXT_CHARS = 1200
MAX_WARNINGS = 4
MAX_COMMAND_CHARS = 260

TOOL_NAME_KEYS = ("tool_name", "toolName", "name")
TOOL_INPUT_KEYS = ("tool_input", "toolInput", "input", "parameters", "arguments")
COMMAND_KEYS = ("cmd", "command", "shell_command", "shellCommand", "script")
PREFLIGHT_FINDING_CODES = (
    "destructive-command",
    "external-tool-send",
    "externally-visible-command",
    "long-running-output",
    "sensitive-output",
    "unbounded-large-output",
)


def main() -> int:
    payload = load_payload()
    try:
        additional_context = build_additional_context(payload)
    except Exception:
        # Preflight is advisory only and must never block a tool call.
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


def build_additional_context(payload: dict[str, Any]) -> str:
    tool_name = first_string(payload, TOOL_NAME_KEYS)
    tool_input = extract_tool_input(payload)
    command = extract_command(payload, tool_input)
    findings = collect_findings(tool_name, tool_input, command)
    if not findings:
        return ""

    selected = findings[:MAX_WARNINGS]
    lines = [
        "Pre-tool advisory: this action matches a harness preflight risk pattern.",
        f"Tool: `{compact_text(tool_name, max_length=120) or 'unknown-tool'}`",
    ]
    if command:
        lines.append(f"Command: `{compact_text(command, max_length=MAX_COMMAND_CHARS)}`")
    lines.extend(f"- {finding.message}" for finding in selected)
    suggestions = bounded_command_suggestions(command)
    if suggestions:
        lines.append("Bounded alternatives:")
        lines.extend(f"- `{suggestion}`" for suggestion in suggestions)
    omitted_count = len(findings) - len(selected)
    if omitted_count > 0:
        lines.append(f"... {omitted_count} more preflight warning(s) omitted.")
    lines.append(f"Finding codes: `{finding_codes(selected)}`")
    lines.append("Sample capture: keep bounded fields only, then run `check_harness_placeholder_replacement.py <candidate-jsonl>`.")
    lines.append("This hook is warning-only. Do not proceed by relying on the warning as approval.")
    return limit_additional_context("\n".join(lines))


def finding_codes(findings: list[PreflightFinding]) -> str:
    return ",".join(finding.code for finding in findings)


def extract_tool_input(payload: dict[str, Any]) -> dict[str, Any]:
    for key in TOOL_INPUT_KEYS:
        value = payload.get(key)
        parsed = parse_mapping(value)
        if parsed:
            return parsed
    return {}


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


def extract_command(payload: dict[str, Any], tool_input: dict[str, Any]) -> str:
    direct = first_string(tool_input, COMMAND_KEYS)
    if direct:
        return direct
    direct = first_string(payload, COMMAND_KEYS)
    if direct:
        return direct
    text = first_string(tool_input, ("text",))
    return text if looks_like_shell_command(text) else ""


def collect_findings(
    tool_name: str,
    tool_input: dict[str, Any],
    command: str,
) -> list[PreflightFinding]:
    findings: list[PreflightFinding] = []
    normalized_tool = tool_name.lower()
    normalized_command = normalize_command(command)

    if command:
        findings.extend(shell_command_findings(normalized_command, tool_input))
    findings.extend(tool_name_findings(normalized_tool))
    return findings


def first_string(data: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def normalize_command(command: str) -> str:
    if not command:
        return ""
    return " ".join(command.strip().split())


def looks_like_shell_command(value: str) -> bool:
    if not value:
        return False
    try:
        parts = shlex.split(value)
    except ValueError:
        parts = value.split()
    if not parts:
        return False
    commands = {
        "ack",
        "ag",
        "aws",
        "bun",
        "cargo",
        "cat",
        "curl",
        "docker",
        "env",
        "fd",
        "find",
        "gcloud",
        "gh",
        "git",
        "go",
        "gradle",
        "grep",
        "journalctl",
        "kubectl",
        "ls",
        "make",
        "mvn",
        "npm",
        "pip",
        "pip3",
        "pnpm",
        "printenv",
        "ps",
        "python",
        "python3",
        "pytest",
        "rg",
        "rm",
        "sed",
        "tail",
        "tree",
        "twine",
        "vercel",
        "yarn",
    }
    return parts[0] in commands


def limit_additional_context(text: str, max_chars: int = MAX_ADDITIONAL_CONTEXT_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    marker = "\n[Pre-tool advisory truncated; inspect the hook warning patterns if needed.]"
    prefix_length = max(0, max_chars - len(marker))
    return f"{text[:prefix_length].rstrip()}{marker}"[:max_chars]


def render_hook_output(additional_context: str) -> str:
    return json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": additional_context,
            }
        },
        ensure_ascii=False,
    )


if __name__ == "__main__":
    raise SystemExit(main())
