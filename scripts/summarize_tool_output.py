#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import deque
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATTERN = r"ERROR|Error|FAILED|FAILURES|Traceback|Exception|AssertionError|panic|fatal|Caused by"
DEFAULT_MAX_LINE_CHARS = 800
DEFAULT_MAX_OUTPUT_CHARS = 12000
DEFAULT_MAX_WINDOWS = 3


@dataclass(frozen=True)
class LineEntry:
    line: int
    text: str
    truncated: bool = False
    original_chars: int = 0


@dataclass(frozen=True)
class LineBlock:
    start: int
    end: int
    lines: list[LineEntry]
    requested_line: int | None = None


@dataclass(frozen=True)
class ToolOutputSummary:
    path: str
    bytes: int
    line_count: int
    estimated_tokens: int
    pattern: str
    match_count: int
    matches_truncated: bool
    matches: list[LineEntry]
    tail: LineBlock
    windows: list[LineBlock]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize a large tool-output artifact.")
    parser.add_argument("--input", required=True, help="Path to the raw tool-output artifact.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--max-matches", type=int, default=80, help="Maximum error matches to show.")
    parser.add_argument("--tail-lines", type=int, default=80, help="Number of tail lines to show.")
    parser.add_argument("--around", action="append", type=int, default=[], help="Line to show context around.")
    parser.add_argument("--context", type=int, default=40, help="Lines before and after each --around line.")
    parser.add_argument("--max-output-chars", type=int, default=DEFAULT_MAX_OUTPUT_CHARS, help="Maximum emitted chars.")
    parser.add_argument("--max-windows", type=int, default=DEFAULT_MAX_WINDOWS, help="Maximum --around windows to emit.")
    parser.add_argument(
        "--max-line-chars",
        type=int,
        default=DEFAULT_MAX_LINE_CHARS,
        help="Maximum characters to show from any single output line.",
    )
    return parser.parse_args()


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def estimate_tokens_from_bytes(byte_count: int) -> int:
    return max(1, round(byte_count / 4)) if byte_count else 0


def bounded_int(value: int, *, label: str) -> int:
    if value < 0:
        raise ValueError(f"{label} must be zero or greater")
    return value


def artifact_lines(path: Path):
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line_no, raw_line in enumerate(handle, 1):
            yield line_no, raw_line.rstrip("\r\n")


def make_line_entry(line_no: int, text: str, max_line_chars: int) -> LineEntry:
    original_chars = len(text)
    if original_chars > max_line_chars:
        return LineEntry(
            line=line_no,
            text=text[:max_line_chars],
            truncated=True,
            original_chars=original_chars,
        )
    return LineEntry(line=line_no, text=text, original_chars=original_chars)


def build_summary(
    path: Path,
    *,
    max_matches: int = 80,
    tail_lines: int = 80,
    around: list[int] | None = None,
    context: int = 40,
    max_line_chars: int = DEFAULT_MAX_LINE_CHARS,
) -> ToolOutputSummary:
    max_matches = bounded_int(max_matches, label="max_matches")
    tail_lines = bounded_int(tail_lines, label="tail_lines")
    context = bounded_int(context, label="context")
    max_line_chars = bounded_int(max_line_chars, label="max_line_chars")
    byte_count = path.stat().st_size
    matcher = re.compile(DEFAULT_PATTERN)
    line_count, match_count, matches, tail = scan_summary_lines(
        path,
        matcher,
        max_matches=max_matches,
        tail_lines=tail_lines,
        max_line_chars=max_line_chars,
    )
    return ToolOutputSummary(
        path=relative(path),
        bytes=byte_count,
        line_count=line_count,
        estimated_tokens=estimate_tokens_from_bytes(byte_count),
        pattern=DEFAULT_PATTERN,
        match_count=match_count,
        matches_truncated=match_count > max_matches,
        matches=matches,
        tail=tail,
        windows=scan_windows(path, around or [], context, line_count, max_line_chars),
    )


def scan_summary_lines(
    path: Path,
    matcher: re.Pattern[str],
    *,
    max_matches: int,
    tail_lines: int,
    max_line_chars: int,
) -> tuple[int, int, list[LineEntry], LineBlock]:
    line_count = 0
    match_count = 0
    matches: list[LineEntry] = []
    tail_entries: deque[LineEntry] | None = deque(maxlen=tail_lines) if tail_lines else None
    for line_no, line in artifact_lines(path):
        line_count = line_no
        entry: LineEntry | None = None
        if matcher.search(line):
            match_count += 1
            if len(matches) < max_matches:
                entry = make_line_entry(line_no, line, max_line_chars)
                matches.append(entry)
        if tail_entries is not None:
            tail_entries.append(entry or make_line_entry(line_no, line, max_line_chars))
    tail = list(tail_entries or [])
    tail_block = LineBlock(
        start=tail[0].line if tail else 0,
        end=tail[-1].line if tail else 0,
        lines=tail,
    )
    return line_count, match_count, matches, tail_block


def window_bounds(requested_line: int, context: int, line_count: int) -> tuple[int, int]:
    if line_count == 0:
        return 0, 0
    clamped = max(1, min(requested_line, line_count))
    start = max(1, min(clamped - context, line_count))
    end = max(start, min(clamped + context, line_count))
    return start, end


def scan_windows(
    path: Path,
    around: list[int],
    context: int,
    line_count: int,
    max_line_chars: int,
) -> list[LineBlock]:
    windows = [
        (requested_line, *window_bounds(requested_line, context, line_count), [])
        for requested_line in around
    ]
    if not windows or line_count == 0:
        return [
            LineBlock(start=start, end=end, lines=entries, requested_line=requested_line)
            for requested_line, start, end, entries in windows
        ]
    for line_no, line in artifact_lines(path):
        for _, start, end, entries in windows:
            if start <= line_no <= end:
                entries.append(make_line_entry(line_no, line, max_line_chars))
    return [
        LineBlock(start=start, end=end, lines=entries, requested_line=requested_line)
        for requested_line, start, end, entries in windows
    ]


def render_lines(entries: list[LineEntry]) -> list[str]:
    lines = []
    for entry in entries:
        suffix = f" [truncated; original chars={entry.original_chars}]" if entry.truncated else ""
        lines.append(f"L{entry.line}: {entry.text}{suffix}")
    return lines


def selected_windows(summary: ToolOutputSummary, max_windows: int) -> tuple[list[LineBlock], int]:
    max_windows = bounded_int(max_windows, label="max_windows")
    if max_windows == 0:
        return [], len(summary.windows)
    windows = summary.windows[:max_windows]
    return windows, max(0, len(summary.windows) - len(windows))


def render_markdown(
    summary: ToolOutputSummary,
    *,
    max_output_chars: int = DEFAULT_MAX_OUTPUT_CHARS,
    max_windows: int = DEFAULT_MAX_WINDOWS,
) -> str:
    max_output_chars = bounded_int(max_output_chars, label="max_output_chars")
    windows, windows_omitted = selected_windows(summary, max_windows)
    truncated = "yes" if summary.matches_truncated else "no"
    lines = [
        "# Tool Output Summary",
        "",
        f"- artifact: `{summary.path}`",
        f"- bytes: {summary.bytes}",
        f"- lines: {summary.line_count}",
        f"- estimated tokens: {summary.estimated_tokens}",
        f"- match pattern: `{summary.pattern}`",
        f"- matches: {len(summary.matches)} / {summary.match_count} (truncated: {truncated})",
        f"- windows: {len(windows)} / {len(summary.windows)} (omitted: {windows_omitted})",
        f"- max output chars: {max_output_chars}",
        "",
        "## Error Matches",
    ]
    if summary.matches:
        lines.extend(f"- {item}" for item in render_lines(summary.matches))
    else:
        lines.append("- none")
    lines.extend(["", "## Tail", "```text"])
    lines.extend(render_lines(summary.tail.lines) or ["<empty>"])
    lines.append("```")
    if windows_omitted:
        lines.append(f"{windows_omitted} requested window(s) omitted by --max-windows.")
    for window in windows:
        lines.extend(["", f"## Window Around Line {window.requested_line}", f"- actual range: {window.start}-{window.end}", "```text"])
        lines.extend(render_lines(window.lines) or ["<empty>"])
        lines.append("```")
    return limit_text_output("\n".join(lines), max_output_chars)


def limit_text_output(text: str, max_output_chars: int) -> str:
    if max_output_chars == 0 or len(text) <= max_output_chars:
        return text
    marker = "\n[Tool output summary truncated by --max-output-chars; re-run with --around <line> for focused context.]"
    prefix_length = max(0, max_output_chars - len(marker))
    return f"{text[:prefix_length].rstrip()}{marker}"[:max_output_chars]


def summary_to_json_payload(summary: ToolOutputSummary, *, max_windows: int) -> dict[str, object]:
    payload = asdict(summary)
    windows, windows_omitted = selected_windows(summary, max_windows)
    payload["windows"] = [asdict(window) for window in windows]
    payload["windows_omitted"] = windows_omitted
    payload["output_truncated"] = False
    return payload


def render_json(
    summary: ToolOutputSummary,
    *,
    max_output_chars: int = DEFAULT_MAX_OUTPUT_CHARS,
    max_windows: int = DEFAULT_MAX_WINDOWS,
) -> str:
    max_output_chars = bounded_int(max_output_chars, label="max_output_chars")
    payload = summary_to_json_payload(summary, max_windows=max_windows)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    if max_output_chars == 0 or len(rendered) <= max_output_chars:
        return rendered
    return render_trimmed_json(summary, max_output_chars=max_output_chars, max_windows=max_windows)


def render_trimmed_json(summary: ToolOutputSummary, *, max_output_chars: int, max_windows: int) -> str:
    trimmed = summary_to_json_payload(summary, max_windows=max_windows)
    trimmed["output_truncated"] = True
    trimmed["matches_omitted"] = len(trimmed["matches"])  # type: ignore[arg-type]
    trimmed["tail_lines_omitted"] = len(trimmed["tail"]["lines"])  # type: ignore[index]
    trimmed["matches"] = []
    trimmed["tail"]["lines"] = []  # type: ignore[index]
    for window in trimmed["windows"]:  # type: ignore[union-attr]
        window["lines_omitted"] = len(window["lines"])
        window["lines"] = []
    rendered = json.dumps(trimmed, ensure_ascii=False, indent=2)
    if len(rendered) <= max_output_chars:
        return rendered
    minimal = {
        "path": summary.path,
        "bytes": summary.bytes,
        "line_count": summary.line_count,
        "estimated_tokens": summary.estimated_tokens,
        "pattern": summary.pattern,
        "match_count": summary.match_count,
        "matches_truncated": summary.matches_truncated,
        "windows_omitted": len(summary.windows),
        "output_truncated": True,
        "truncation_reason": "max_output_chars",
    }
    return json.dumps(minimal, ensure_ascii=False, indent=2)


def main() -> int:
    args = parse_args()
    path = Path(args.input).expanduser()
    if not path.exists():
        print(f"ERROR: input missing: {path}", file=sys.stderr)
        return 1
    try:
        summary = build_summary(
            path,
            max_matches=args.max_matches,
            tail_lines=args.tail_lines,
            around=args.around,
            context=args.context,
            max_line_chars=args.max_line_chars,
        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(render_json(summary, max_output_chars=args.max_output_chars, max_windows=args.max_windows))
    else:
        print(render_markdown(summary, max_output_chars=args.max_output_chars, max_windows=args.max_windows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
