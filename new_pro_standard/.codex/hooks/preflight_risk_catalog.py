from __future__ import annotations

import re
import shlex
from dataclasses import dataclass
from typing import Any

BOUNDED_OUTPUT_TOKENS = 4000


@dataclass(frozen=True)
class PreflightFinding:
    code: str
    message: str


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
    if is_sensitive_output_command(command):
        findings.append(
            PreflightFinding(
                "sensitive-output",
                "Command may print secrets, credentials, account identifiers, or environment values; inspect only redacted keys or bounded metadata.",
            )
        )
    if is_likely_large_output_command(command) and not has_bounded_output(tool_input, command):
        findings.append(
            PreflightFinding(
                "unbounded-large-output",
                "Likely large output without a local artifact or max_output_tokens<=4000; redirect raw output to .codex/runtime/tool-outputs/ and summarize it.",
            )
        )
    if is_long_running_output_command(command) and not has_bounded_output(tool_input, command):
        findings.append(
            PreflightFinding(
                "long-running-output",
                "Long-running test/build/install command may stream excessive logs; cap output or write raw logs to .codex/runtime/tool-outputs/.",
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
    return matches_any(command, destructive_patterns)


def is_externally_visible_command(command: str) -> bool:
    external_patterns = (
        r"\bgit\s+push\b",
        r"\bgh\s+pr\s+(merge|close|comment|review)\b",
        r"\bgh\s+release\s+(create|upload|delete)\b",
        r"\b(npm|pnpm|yarn)\s+publish\b",
        r"\btwine\s+upload\b",
        r"\bcurl\b.*\s-X\s*(POST|PUT|PATCH|DELETE)\b",
    )
    return matches_any(command, external_patterns)


def is_sensitive_output_command(command: str) -> bool:
    sensitive_patterns = (
        r"^(env|printenv)\b(?!\s+[A-Za-z_][A-Za-z0-9_]*$)",
        r"\b(gh\s+auth\s+token|gh\s+auth\s+status\b)",
        r"\bkubectl\s+get\s+secret\b",
        r"\b(cat|sed|less|more|tail|head)\b.*(\.env\b|id_rsa\b|\.pem\b|credential|secret|token|kubeconfig)",
        r"\b(aws|gcloud|vercel|heroku)\b.*\b(auth|credential|config|env|secret|token|whoami|sts)\b",
    )
    return matches_any(command, sensitive_patterns)


def is_likely_large_output_command(command: str) -> bool:
    large_output_patterns = (
        r"\bps\s+(-axo|aux|-ef)\b",
        r"\bgit\s+diff\b(?!.*\s(--check|--stat|--name-only|--name-status)\b)",
        r"\bgit\s+show\b(?!.*\s(--stat|--name-only|--name-status)\b)",
        r"\bcat\s+.*\.(log|jsonl|trace|out)\b",
        r"\brg\b(?!.*\s(--files|--max-count|-m)\b)",
        r"\b(e?grep|fgrep)\b.*\s(-r|-R|--recursive)\b(?!.*\s(-m|--max-count)\s+\d+)",
        r"\bfind\s+(\.|\S+)\b(?!.*\s-maxdepth\s+\d+)",
        r"\bls\s+-[A-Za-z]*R[A-Za-z]*\b",
        r"\btree\b(?!.*\s-L\s+\d+)",
        r"\bdocker\s+logs\b(?!.*\s(--tail|-n)\s*\d+)",
        r"\bkubectl\s+logs\b(?!.*\s--tail[=\s]\d+)",
        r"\bjournalctl\b(?!.*\s(-n|--lines)\s*\d+)",
        r"\btail\s+-f\b",
        r"\b(fd|ag|ack)\b(?!.*\s(-l|--files|-m|--max-count)\b)",
        r"\bgh\s+api\b.*\s--paginate\b",
    )
    return matches_any(command, large_output_patterns)


def is_long_running_output_command(command: str) -> bool:
    long_output_patterns = (
        r"\b(pytest|python\s+-m\s+pytest)\b.*\s(-vv|--capture=no|-s)\b",
        r"\bcargo\s+test\b.*(--\s+--nocapture|-vv)\b",
        r"\bgo\s+test\b.*\s-v\b",
        r"\b(mvn|gradle)\b",
        r"\bmake\b",
        r"\b(pip|pip3|python\s+-m\s+pip)\s+install\b.*\s-v\b",
        r"\b(npm|pnpm|yarn|bun)\s+(test|build|install|ci)\b",
        r"\bdocker\s+(build|compose\s+build|compose\s+up)\b",
    )
    return matches_any(command, long_output_patterns)


def has_bounded_output(tool_input: dict[str, Any], command: str) -> bool:
    max_output = max_output_tokens(tool_input)
    if max_output and max_output <= BOUNDED_OUTPUT_TOKENS:
        return True
    if ".codex/runtime/tool-outputs/" in command:
        return True
    if "scripts/capture_tool_output.py" in command:
        return True
    return has_inline_bound(command)


def has_inline_bound(command: str) -> bool:
    return matches_any(
        command,
        (
            r"\bhead\s+(-n\s*)?\d+\b",
            r"\bsed\s+-n\s+['\"]?1,\d+p['\"]?",
            r"\b(tail|journalctl)\b.*\s(-n|--lines)\s*\d+",
            r"\bdocker\s+logs\b.*\s(--tail|-n)\s*\d+",
            r"\bkubectl\s+logs\b.*\s--tail[=\s]\d+",
        ),
    )


def max_output_tokens(tool_input: dict[str, Any]) -> int:
    for key in ("max_output_tokens", "maxOutputTokens"):
        value = tool_input.get(key)
        if isinstance(value, int) and value > 0:
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    return 0


def bounded_command_suggestions(command: str) -> list[str]:
    parts = split_command(command)
    if not parts:
        return []
    head = parts[0]
    if head == "rg":
        return bounded_rg(parts[1:])
    if head in {"fd", "ag", "ack"}:
        return [capture_tool_command(parts, "search-output"), f"{head} -l <pattern> <path>"]
    if head in {"grep", "egrep", "fgrep"}:
        return [
            capture_tool_command(parts, "grep-output"),
            'grep -R -n -m 20 "pattern" path/',
            'grep -R -l "pattern" path/',
        ]
    if parts[:2] == ["git", "diff"]:
        return [capture_tool_command(parts, "git-diff"), "git diff --stat", "git diff --name-only"]
    if parts[:2] == ["git", "show"]:
        return [capture_tool_command(parts, "git-show"), "git show --stat", "git show --name-only"]
    if parts[:2] == ["gh", "api"]:
        return [capture_tool_command(parts, "gh-api")]
    if head in {"find", "tree", "ls"}:
        return [capture_tool_command(parts, "listing-output"), "find . -maxdepth 3 -print | head -200", "rg --files | head -200"]
    if parts[:2] == ["docker", "logs"]:
        return [capture_tool_command(parts, "docker-logs"), "docker logs --tail 200 <container>"]
    if parts[:2] == ["kubectl", "logs"]:
        return [capture_tool_command(parts, "kubectl-logs"), "kubectl logs --tail=200 <pod>"]
    if head == "journalctl":
        return [capture_tool_command(parts, "journalctl"), "journalctl -n 200 --no-pager"]
    if head == "tail":
        return [capture_tool_command(parts, "tail-output"), "tail -n 200 <target-file>"]
    if head == "cat":
        return ["sed -n '1,160p' <target-file>", "python3 scripts/summarize_tool_output.py --input .codex/runtime/tool-outputs/<artifact>.log"]
    if head == "ps":
        return [capture_tool_command(parts, "ps-output")]
    if head in {"env", "printenv"} or is_sensitive_output_command(command):
        return ["printenv PATH", "env | sed -E 's/(TOKEN|SECRET|KEY|PASSWORD)=.*/\\1=[REDACTED]/'"]
    if is_long_running_output_command(command):
        return [capture_tool_command(parts, "command-output")]
    return []


def bounded_rg(args: list[str]) -> list[str]:
    if not args:
        return []
    return [
        capture_tool_command(["rg", *args], "rg-output"),
        shell_join(["rg", "-n", "-m", "20", *args]),
        shell_join(["rg", "-l", *args]),
    ]


def capture_tool_command(parts: list[str], slug: str) -> str:
    if not parts:
        return "python3 scripts/capture_tool_output.py --slug command-output -- <command>"
    return shell_join(["python3", "scripts/capture_tool_output.py", "--slug", slug, "--", *parts])


def matches_any(command: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, command) for pattern in patterns)


def split_command(command: str) -> list[str]:
    if not command:
        return []
    try:
        return shlex.split(command)
    except ValueError:
        return command.split()


def shell_join(parts: list[str]) -> str:
    try:
        return shlex.join(parts)
    except AttributeError:
        return " ".join(shlex.quote(part) for part in parts)
