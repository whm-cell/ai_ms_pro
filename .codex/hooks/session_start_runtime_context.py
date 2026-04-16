#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SESSION_DIR = ROOT / ".codex" / "runtime" / "sessions"
MAX_SECTION_CHARS = 240


def main() -> int:
    payload = load_payload()
    try:
        additional_context = build_additional_context(payload)
    except Exception:
        return 0

    if not additional_context:
        return 0

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": additional_context,
                }
            }
        )
    )
    return 0


def load_payload() -> dict[str, Any]:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def build_additional_context(payload: dict[str, Any]) -> str:
    source = string_value(payload.get("source")) or "startup"
    session_id = string_value(payload.get("session_id"))
    session_file = pick_session_file(source, session_id)
    if session_file is None or not session_file.exists():
        return ""

    sections = parse_sections(session_file)
    traceability = compact(sections.get("需求与工作流标识", ""))
    current_goal = compact(sections.get("当前目标", ""))
    open_loops = compact(sections.get("当前 Open Loops", ""))
    resume_tips = compact(sections.get("下次 Resume 提示", ""))
    promotion = compact(sections.get("是否需要提升为 Handoff", ""))

    lines = [
        f"本地 runtime session 恢复材料：`{session_file.relative_to(ROOT)}`",
        f"启动来源：`{source}`",
    ]
    if traceability:
        lines.append(f"Requirement/Workstream 绑定：{traceability}")
    if current_goal:
        lines.append(f"最近目标：{current_goal}")
    if open_loops:
        lines.append(f"最近 Open Loops：{open_loops}")
    if resume_tips:
        lines.append(f"Resume 提示：{resume_tips}")
    if promotion:
        lines.append(f"Handoff 提升判断：{promotion}")
    lines.append("如需发布 repo 共享真相，仍以 `docs/ai/working-context.md`、active `handoff`、`ADR` 为准。")
    return "\n".join(lines)


def pick_session_file(source: str, session_id: str) -> Path | None:
    session_files = session_candidates()
    if not session_files:
        return None

    if source == "resume" and session_id:
        matching = [path for path in session_files if path.name.endswith(f"_{slug_fragment(session_id)}.md")]
        if matching:
            return matching[-1]

    return session_files[-1]


def session_candidates() -> list[Path]:
    if not SESSION_DIR.exists():
        return []
    files = []
    for path in sorted(SESSION_DIR.glob("*.md")):
        if path.name == "README.md" or path.name.startswith("_"):
            continue
        files.append(path)
    return files


def parse_sections(path: Path) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current = ""
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if line.startswith("## "):
            current = line[3:].strip()
            sections.setdefault(current, [])
            continue
        if current:
            sections[current].append(line)

    return {
        name: "\n".join(strip_empty_edges(lines)).strip()
        for name, lines in sections.items()
    }


def strip_empty_edges(lines: list[str]) -> list[str]:
    start = 0
    end = len(lines)
    while start < end and not lines[start].strip():
        start += 1
    while end > start and not lines[end - 1].strip():
        end -= 1
    return lines[start:end]


def compact(text: str) -> str:
    if not text:
        return ""
    merged = " ".join(part.strip() for part in text.splitlines() if part.strip())
    return merged[:MAX_SECTION_CHARS].strip()


def string_value(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


def slug_fragment(value: str) -> str:
    return value.lower().strip()


if __name__ == "__main__":
    raise SystemExit(main())
