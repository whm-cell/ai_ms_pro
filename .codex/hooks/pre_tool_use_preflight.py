#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import shlex
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from runtime_sanitizer import compact_text


ROOT = Path(__file__).resolve().parents[2]
MAX_ADDITIONAL_CONTEXT_CHARS = 1200
MAX_WARNINGS = 4
MAX_COMMAND_CHARS = 260
BOUNDED_OUTPUT_TOKENS = 4000

TOOL_NAME_KEYS = ("tool_name", "toolName", "name")
TOOL_INPUT_KEYS = ("tool_input", "toolInput", "input", "parameters", "arguments")
COMMAND_KEYS = ("cmd", "command", "shell_command", "shellCommand", "script")
MAX_OUTPUT_KEYS = ("max_output_tokens", "maxOutputTokens")
PREFLIGHT_FINDING_CODES = (
    "destructive-command",
    "external-tool-send",
    "externally-visible-command",
    "unbounded-large-output",
)


@dataclass(frozen=True)
class PreflightFinding:
    code: str
    message: str


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


def shell_command_findings(command: str, tool_input: dict[str, Any]) -> list[PreflightFinding]:
    findings: list[PreflightFinding] = []
    if is_destructive_command(command):
        findings.append(
            PreflightFinding(
                "destructive-command",
                "Destructive or hard-to-recover command pattern; require explicit target-specific confirmation and recovery evidence.",
            )
        )
    if is_externally_visible_command(command):
        findings.append(
            PreflightFinding(
                "externally-visible-command",
                "Externally visible or remote-write command pattern; require explicit confirmation of target, audience, and verification evidence.",
            )
        )
    if is_likely_large_output_command(command) and not has_bounded_output(tool_input, command):
        findings.append(
            PreflightFinding(
                "unbounded-large-output",
                "Likely large output without a local artifact or max_output_tokens<=4000; redirect raw output to .codex/runtime/tool-outputs/ and summarize it.",
            )
        )
    return findings


def tool_name_findings(tool_name: str) -> list[PreflightFinding]:
    if not tool_name:
        return []
    if any(marker in tool_name for marker in ("send_message", "post_message", "send_email", "create_pr_comment")):
        return [
            PreflightFinding(
                "external-tool-send",
                "Externally visible send/comment tool; prepare a draft unless the user explicitly confirmed the target and body.",
            )
        ]
    return []


def is_destructive_command(command: str) -> bool:
    destructive_patterns = (
        r"\brm\s+.*(-r|-R|--recursive|-f|--force)",
        r"\bgit\s+reset\s+--hard\b",
        r"\bgit\s+checkout\s+--\b",
        r"\bgit\s+clean\s+-[A-Za-z]*[fdx]",
        r"\bfind\b.*\s-delete\b",
        r"\bchmod\s+-R\b",
        r"\bchown\s+-R\b",
        r"\bdocker\s+system\s+prune\b",
        r"\bkubectl\s+delete\b",
        r"\b(drop\s+database|drop\s+table|truncate\s+table)\b",
    )
    return any(re.search(pattern, command) for pattern in destructive_patterns)


def is_externally_visible_command(command: str) -> bool:
    external_patterns = (
        r"\bgit\s+push\b",
        r"\bgh\s+pr\s+(merge|close|comment|review)\b",
        r"\bgh\s+release\s+(create|upload|delete)\b",
        r"\b(npm|pnpm|yarn)\s+publish\b",
        r"\btwine\s+upload\b",
        r"\bcurl\b.*\s-X\s*(POST|PUT|PATCH|DELETE)\b",
    )
    return any(re.search(pattern, command) for pattern in external_patterns)


def is_likely_large_output_command(command: str) -> bool:
    large_output_patterns = (
        r"\bps\s+(-axo|aux|-ef)\b",
        r"\bgit\s+diff\b(?!.*\s(--check|--stat|--name-only|--name-status)\b)",
        r"\bgit\s+show\b(?!.*\s(--stat|--name-only|--name-status)\b)",
        r"\bcat\s+.*\.(log|jsonl|trace|out)\b",
        r"\brg\b(?!.*\s(--files|--max-count|-m)\b)",
    )
    return any(re.search(pattern, command) for pattern in large_output_patterns)


def has_bounded_output(tool_input: dict[str, Any], command: str) -> bool:
    max_output = max_output_tokens(tool_input)
    if max_output and max_output <= BOUNDED_OUTPUT_TOKENS:
        return True
    return ".codex/runtime/tool-outputs/" in command


def max_output_tokens(tool_input: dict[str, Any]) -> int:
    for key in MAX_OUTPUT_KEYS:
        value = tool_input.get(key)
        if isinstance(value, int) and value > 0:
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    return 0


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
    return parts[0] in {
        "cat",
        "curl",
        "docker",
        "find",
        "gh",
        "git",
        "kubectl",
        "npm",
        "pnpm",
        "ps",
        "rg",
        "rm",
        "sed",
        "twine",
        "yarn",
    }


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
