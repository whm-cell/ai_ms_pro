#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import capture_tool_output
import summarize_tool_output


ROOT = Path(__file__).resolve().parents[1]
HOOKS_DIR = ROOT / ".codex" / "hooks"
if str(HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(HOOKS_DIR))

from preflight_risk_catalog import PreflightFinding, shell_command_findings, tool_name_findings  # noqa: E402


DEFAULT_OUTPUT_DIR = ROOT / ".codex" / "runtime" / "tool-outputs"
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_MAX_SUMMARY_CHARS = 4000
DEFAULT_CHUNK_SIZE = 8192
TIMEOUT_EXIT_CODE = 124
REFUSED_EXIT_CODE = 3
BLOCKING_FINDING_CODES = {
    "destructive-command",
    "external-tool-send",
    "externally-visible-command",
    "sensitive-output",
}
ALLOWED_ENV_KEYS = (
    "HOME",
    "LANG",
    "LC_ALL",
    "LC_CTYPE",
    "PATH",
    "TERM",
    "TMPDIR",
    "__CF_USER_TEXT_ENCODING",
)


@dataclass(frozen=True)
class PolicyRunResult:
    command: list[str]
    exit_code: int
    timed_out: bool
    started_at: str
    ended_at: str
    duration_ms: int
    cwd: str
    artifact_path: str
    stdout_artifact_path: str
    stderr_artifact_path: str
    metadata_path: str
    bytes: int
    stdout_bytes: int
    stderr_bytes: int
    human_confirmation_ref: str
    blocking_findings: list[str]
    warning_findings: list[str]
    stdout_summary: summarize_tool_output.ToolOutputSummary
    stderr_summary: summarize_tool_output.ToolOutputSummary


class PolicyRefusal(Exception):
    def __init__(self, command: list[str], findings: list[PreflightFinding]) -> None:
        self.command = command
        self.findings = findings
        super().__init__("local execution policy refused command")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run an argv-only command through an opt-in local execution policy wrapper."
    )
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--max-summary-chars", type=int, default=DEFAULT_MAX_SUMMARY_CHARS)
    parser.add_argument("--slug", default="local-execution-policy")
    parser.add_argument("--human-confirmation-ref", default="")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help=argparse.SUPPRESS)
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command and arguments after --.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    command = command_after_separator(args.command)
    if not command:
        print("ERROR: argv command required after --", file=sys.stderr)
        return 2
    if args.timeout_seconds <= 0:
        print("ERROR: --timeout-seconds must be greater than zero", file=sys.stderr)
        return 2
    if args.max_summary_chars <= 0:
        print("ERROR: --max-summary-chars must be greater than zero", file=sys.stderr)
        return 2
    try:
        result = run_policy_command(
            command,
            timeout_seconds=args.timeout_seconds,
            slug=args.slug,
            output_dir=Path(args.output_dir),
            human_confirmation_ref=args.human_confirmation_ref,
        )
    except PolicyRefusal as exc:
        print(render_refusal(exc))
        return REFUSED_EXIT_CODE
    except OSError as exc:
        print(f"ERROR: failed to execute command through local policy wrapper: {exc}", file=sys.stderr)
        return 1

    print(render_run_report(result, max_summary_chars=args.max_summary_chars))
    return result.exit_code


def command_after_separator(raw_command: list[str]) -> list[str]:
    if not raw_command or raw_command[0] != "--":
        return []
    return raw_command[1:]


def run_policy_command(
    command: list[str],
    *,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    slug: str = "local-execution-policy",
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    human_confirmation_ref: str = "",
) -> PolicyRunResult:
    findings = collect_policy_findings(command)
    blocking_findings = blocking_policy_findings(findings)
    if blocking_findings and not human_confirmation_ref.strip():
        raise PolicyRefusal(command, blocking_findings)

    output_dir.mkdir(parents=True, exist_ok=True)
    base = f"{capture_tool_output.timestamp()}-{capture_tool_output.safe_slug(slug)}"
    artifact_path = capture_tool_output.unique_path(output_dir / f"{base}.log")
    stdout_path = artifact_path.with_suffix(".stdout.log")
    stderr_path = artifact_path.with_suffix(".stderr.log")
    metadata_path = artifact_path.with_suffix(".meta.json")
    started_at = iso_now()
    start = time.monotonic()
    exit_code, timed_out = run_and_capture(
        command,
        artifact_path=artifact_path,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        timeout_seconds=timeout_seconds,
    )
    ended_at = iso_now()
    duration_ms = round((time.monotonic() - start) * 1000)
    stdout_summary = summarize_tool_output.build_summary(stdout_path)
    stderr_summary = summarize_tool_output.build_summary(stderr_path)
    result = PolicyRunResult(
        command=command,
        exit_code=exit_code,
        timed_out=timed_out,
        started_at=started_at,
        ended_at=ended_at,
        duration_ms=duration_ms,
        cwd=summarize_tool_output.relative(ROOT),
        artifact_path=summarize_tool_output.relative(artifact_path),
        stdout_artifact_path=summarize_tool_output.relative(stdout_path),
        stderr_artifact_path=summarize_tool_output.relative(stderr_path),
        metadata_path=summarize_tool_output.relative(metadata_path),
        bytes=artifact_path.stat().st_size,
        stdout_bytes=stdout_path.stat().st_size,
        stderr_bytes=stderr_path.stat().st_size,
        human_confirmation_ref=human_confirmation_ref.strip(),
        blocking_findings=[finding.code for finding in blocking_findings],
        warning_findings=[finding.code for finding in findings if finding.code not in BLOCKING_FINDING_CODES],
        stdout_summary=stdout_summary,
        stderr_summary=stderr_summary,
    )
    write_metadata(result, metadata_path)
    return result


def collect_policy_findings(command: list[str]) -> list[PreflightFinding]:
    command_text = shlex.join(command)
    tool_name = Path(command[0]).name.lower() if command else ""
    findings = list(shell_command_findings(command_text, {"max_output_tokens": DEFAULT_MAX_SUMMARY_CHARS}))
    findings.extend(tool_name_findings(tool_name))
    return findings


def blocking_policy_findings(findings: list[PreflightFinding]) -> list[PreflightFinding]:
    return [finding for finding in findings if finding.code in BLOCKING_FINDING_CODES]


def run_and_capture(
    command: list[str],
    *,
    artifact_path: Path,
    stdout_path: Path,
    stderr_path: Path,
    timeout_seconds: int,
) -> tuple[int, bool]:
    lock = threading.Lock()
    with artifact_path.open("wb") as combined:
        with subprocess.Popen(
            command,
            cwd=ROOT,
            env=policy_env(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        ) as process:
            stdout_thread = copy_thread(process.stdout, stdout_path, combined, lock)
            stderr_thread = copy_thread(process.stderr, stderr_path, combined, lock)
            timed_out = False
            try:
                return_code = int(process.wait(timeout=timeout_seconds))
            except subprocess.TimeoutExpired:
                timed_out = True
                process.kill()
                process.wait()
                return_code = TIMEOUT_EXIT_CODE
            stdout_thread.join()
            stderr_thread.join()
    return return_code, timed_out


def copy_thread(
    source: object,
    stream_path: Path,
    combined_output: object,
    lock: threading.Lock,
) -> threading.Thread:
    thread = threading.Thread(
        target=copy_stream,
        args=(source, stream_path, combined_output, lock),
        daemon=True,
    )
    thread.start()
    return thread


def copy_stream(
    source: object,
    stream_path: Path,
    combined_output: object,
    lock: threading.Lock,
) -> None:
    if source is None:
        stream_path.write_bytes(b"")
        return
    with source, stream_path.open("wb") as stream_output:
        for chunk in iter(lambda: source.read(DEFAULT_CHUNK_SIZE), b""):
            stream_output.write(chunk)
            with lock:
                combined_output.write(chunk)


def policy_env(source: dict[str, str] | None = None) -> dict[str, str]:
    env_source = os.environ if source is None else source
    return {key: env_source[key] for key in ALLOWED_ENV_KEYS if key in env_source}


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def write_metadata(result: PolicyRunResult, metadata_path: Path) -> None:
    payload = asdict(result)
    payload.pop("stdout_summary", None)
    payload.pop("stderr_summary", None)
    payload["policy"] = {
        "name": "local-execution-policy-wrapper",
        "native_sandbox": False,
        "argv_only": True,
        "shell": False,
        "cwd_enforced": result.cwd,
        "allowed_env_keys": list(ALLOWED_ENV_KEYS),
    }
    metadata_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_refusal(refusal: PolicyRefusal) -> str:
    lines = [
        "# Local Execution Policy Wrapper Refused Command",
        "",
        f"- command: `{shlex.join(refusal.command)}`",
        f"- finding codes: `{','.join(finding.code for finding in refusal.findings)}`",
        "- execution: not run",
        "- override: pass `--human-confirmation-ref <ref>` when a human has confirmed the exact target and risk.",
        "",
        "## Findings",
    ]
    lines.extend(f"- {finding.code}: {finding.message}" for finding in refusal.findings)
    return "\n".join(lines)


def render_run_report(result: PolicyRunResult, *, max_summary_chars: int) -> str:
    timeout = "yes" if result.timed_out else "no"
    lines = [
        "# Local Execution Policy Wrapper Result",
        "",
        f"- command: `{shlex.join(result.command)}`",
        f"- cwd: `{result.cwd}`",
        "- native sandbox: `false`",
        "- execution policy: `argv_only=true shell=false reduced_env=true`",
        f"- exit code: {result.exit_code}",
        f"- timed out: {timeout}",
        f"- raw output artifact: `{result.artifact_path}`",
        f"- stdout artifact: `{result.stdout_artifact_path}`",
        f"- stderr artifact: `{result.stderr_artifact_path}`",
        f"- metadata: `{result.metadata_path}`",
        f"- blocking finding codes: `{','.join(result.blocking_findings) or 'none'}`",
        f"- warning finding codes: `{','.join(result.warning_findings) or 'none'}`",
        f"- human confirmation ref: `{result.human_confirmation_ref or 'not-provided'}`",
        "",
        "## Stdout Summary",
        summarize_tool_output.render_markdown(result.stdout_summary, max_output_chars=max_summary_chars),
        "",
        "## Stderr Summary",
        summarize_tool_output.render_markdown(result.stderr_summary, max_output_chars=max_summary_chars),
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
