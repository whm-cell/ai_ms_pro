#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import summarize_tool_output


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / ".codex" / "runtime" / "tool-outputs"
DEFAULT_CHUNK_SIZE = 8192
SLUG_RE = re.compile(r"[^A-Za-z0-9_.-]+")


@dataclass(frozen=True)
class CaptureResult:
    command: list[str]
    exit_code: int
    started_at: str
    ended_at: str
    duration_ms: int
    artifact_path: str
    metadata_path: str
    bytes: int
    summary: summarize_tool_output.ToolOutputSummary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture raw command output to an artifact and print a bounded summary.")
    parser.add_argument("--slug", required=True, help="Short artifact name component.")
    parser.add_argument(
        "--max-output-chars",
        type=int,
        default=summarize_tool_output.DEFAULT_MAX_OUTPUT_CHARS,
        help="Maximum characters to emit in the returned summary.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=argparse.SUPPRESS,
    )
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command and arguments after --.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    command = normalize_command(args.command)
    if not command:
        print("ERROR: command required after --", file=sys.stderr)
        return 2
    try:
        result = capture_command(
            command,
            slug=args.slug,
            output_dir=Path(args.output_dir),
        )
    except OSError as exc:
        print(f"ERROR: failed to execute command: {exc}", file=sys.stderr)
        return 1
    print(render_capture_report(result, max_output_chars=args.max_output_chars))
    return result.exit_code


def normalize_command(raw_command: list[str]) -> list[str]:
    if raw_command and raw_command[0] == "--":
        return raw_command[1:]
    return raw_command


def safe_slug(value: str) -> str:
    slug = SLUG_RE.sub("-", value.strip()).strip("-._")
    return slug[:60] or "command"


def timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def capture_command(
    command: list[str],
    *,
    slug: str,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> CaptureResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    base = f"{timestamp()}-{safe_slug(slug)}"
    artifact_path = unique_path(output_dir / f"{base}.log")
    metadata_path = artifact_path.with_suffix(".meta.json")
    started_at = iso_now()
    start = time.monotonic()
    exit_code = run_and_capture(command, artifact_path)
    ended_at = iso_now()
    duration_ms = round((time.monotonic() - start) * 1000)
    byte_count = artifact_path.stat().st_size
    metadata = {
        "command": command,
        "exit_code": exit_code,
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_ms": duration_ms,
        "artifact_path": summarize_tool_output.relative(artifact_path),
        "bytes": byte_count,
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = summarize_tool_output.build_summary(artifact_path)
    return CaptureResult(
        command=command,
        exit_code=exit_code,
        started_at=started_at,
        ended_at=ended_at,
        duration_ms=duration_ms,
        artifact_path=summarize_tool_output.relative(artifact_path),
        metadata_path=summarize_tool_output.relative(metadata_path),
        bytes=byte_count,
        summary=summary,
    )


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.with_suffix("")
    suffix = path.suffix
    for index in range(1, 1000):
        candidate = Path(f"{stem}-{index}{suffix}")
        if not candidate.exists():
            return candidate
    raise OSError(f"could not allocate unique artifact path under {path.parent}")


def run_and_capture(command: list[str], artifact_path: Path) -> int:
    with artifact_path.open("wb") as output:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        assert process.stdout is not None
        for chunk in iter(lambda: process.stdout.read(DEFAULT_CHUNK_SIZE), b""):
            output.write(chunk)
        return int(process.wait())


def render_capture_report(result: CaptureResult, *, max_output_chars: int) -> str:
    header = [
        "# Captured Tool Output",
        "",
        f"- artifact: `{result.artifact_path}`",
        f"- metadata: `{result.metadata_path}`",
        f"- exit code: {result.exit_code}",
        f"- bytes: {result.bytes}",
        "",
    ]
    summary = summarize_tool_output.render_markdown(result.summary, max_output_chars=max_output_chars)
    return "\n".join(header) + summary


def result_metadata(result: CaptureResult) -> dict[str, object]:
    payload = asdict(result)
    payload.pop("summary", None)
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
