from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SESSION_DIR = ROOT / ".codex" / "runtime" / "sessions"
WORKING_CONTEXT_PATH = ROOT / "docs" / "ai" / "working-context.md"
MAX_FIELD_LENGTH = 300
SESSION_ID_KEYS = ("session_id", "sessionId")
TEXT_KEYS = ("user_prompt", "prompt", "message", "text", "content", "input")
TRANSCRIPT_KEYS = ("transcript_path", "transcriptPath")
REQUIREMENT_ID_KEYS = ("requirement_ids", "requirementIds", "requirement_id", "requirementId")
WORKSTREAM_ID_KEYS = ("workstream_ids", "workstreamIds", "workstream_id", "workstreamId")
RESUME_KEYS = ("resumed", "is_resume", "resume")
SUBAGENT_KEYS = ("subagent", "is_subagent", "agent_type", "agentType")
ENV_SESSION_ID_KEYS = ("CODEX_SESSION_ID", "SESSION_ID")
ENV_REQUIREMENT_ID_KEYS = ("CODEX_REQUIREMENT_IDS", "REQUIREMENT_IDS")
ENV_WORKSTREAM_ID_KEYS = ("CODEX_WORKSTREAM_IDS", "WORKSTREAM_IDS")
ENV_AGENT_KEYS = ("CODEX_AGENT_TYPE", "AGENT_TYPE")


def load_payload() -> dict[str, Any]:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def find_or_create_session_file(session_id: str, agent_label: str, branch_or_thread: str) -> Path:
    existing = sorted(SESSION_DIR.glob(f"*_{session_id}.md"))
    if existing:
        return existing[-1]

    stamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    safe_branch = slugify(branch_or_thread)
    safe_agent = slugify(agent_label)
    safe_session = slugify(session_id)
    return SESSION_DIR / f"{stamp}_{safe_agent}_{safe_branch}_{safe_session}.md"


def infer_session_type(payload: dict[str, Any], session_file: Path) -> str:
    resumed = first_value(payload, RESUME_KEYS)
    if isinstance(resumed, bool) and resumed:
        return "resume"
    if session_file.exists():
        return "pause-before-exit"
    return "new"


def infer_agent_label(payload: dict[str, Any]) -> str:
    env_label = first_env_value(ENV_AGENT_KEYS)
    if env_label:
        return "subagent" if "sub" in env_label.lower() else "main"

    value = first_value(payload, SUBAGENT_KEYS)
    if isinstance(value, bool):
        return "subagent" if value else "main"
    if isinstance(value, str):
        lowered = value.lower()
        if "sub" in lowered or "worker" in lowered:
            return "subagent"
    return "main"


def infer_branch_or_thread(payload: dict[str, Any], session_id: str) -> str:
    branch = git_branch()
    if branch:
        return branch
    thread = first_value(payload, ("thread_id", "threadId"))
    if isinstance(thread, str) and thread.strip():
        return thread.strip()
    return session_id


def git_branch() -> str:
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    return result.stdout.strip()


def git_status_paths() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return []

    paths: list[str] = []
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        path_text = line[3:]
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1]
        paths.append(path_text)
    return paths


def should_promote(changed_paths: list[str]) -> bool:
    if not changed_paths:
        return False
    for path_text in changed_paths:
        if path_text.startswith(".codex/runtime/"):
            continue
        if path_text.startswith("mysjzhishidian/"):
            continue
        return True
    return False


def infer_promotion_reason(promote: bool, changed_paths: list[str]) -> str:
    if not promote:
        return "当前仅检测到本地 runtime 或参考草稿层改动，暂不强制提升"
    return "检测到除 runtime/参考草稿之外的仓库级改动；主 Agent 应判断是否需要发布 canonical handoff"


def first_env_value(keys: tuple[str, ...]) -> str:
    for key in keys:
        value = os.environ.get(key)
        if value:
            return value
    return ""


def first_value(data: Any, keys: tuple[str, ...]) -> Any:
    if isinstance(data, dict):
        for key in keys:
            value = data.get(key)
            if is_meaningful(value):
                return value
        for value in data.values():
            found = first_value(value, keys)
            if is_meaningful(found):
                return found
    elif isinstance(data, list):
        for item in data:
            found = first_value(item, keys)
            if is_meaningful(found):
                return found
    return None


def collect_identifier_values(data: Any, keys: tuple[str, ...]) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()

    def add(candidate: str) -> None:
        normalized = candidate.strip()
        if not normalized or normalized in seen:
            return
        seen.add(normalized)
        values.append(normalized)

    def extract_from_value(value: Any) -> None:
        if isinstance(value, str):
            for piece in value.split(","):
                add(piece)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    add(item)
        elif isinstance(value, dict):
            visit(value)

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in keys:
                    extract_from_value(value)
                else:
                    visit(value)
        elif isinstance(node, list):
            for item in node:
                visit(item)

    visit(data)
    return values


def collect_env_identifiers(keys: tuple[str, ...]) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for key in keys:
        raw = os.environ.get(key, "")
        if not raw:
            continue
        for piece in raw.split(","):
            normalized = piece.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            values.append(normalized)
    return values


def is_meaningful(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def slugify(value: str) -> str:
    lowered = value.lower().strip()
    slug = re.sub(r"[^a-z0-9._-]+", "-", lowered)
    return slug.strip("-") or "unknown"
