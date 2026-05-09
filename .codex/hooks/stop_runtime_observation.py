#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from runtime_sanitizer import compact_text, compact_transcript_path
from runtime_traceability import resolve_runtime_traceability


ROOT = Path(__file__).resolve().parents[2]
OBSERVATION_DIR = ROOT / ".codex" / "runtime" / "observations"
DOC_ROOTS = (
    ROOT / "docs" / "ai",
    ROOT / "docs" / "requirements",
)
MAX_FIELD_LENGTH = 300
MAX_CHANGED_PATHS = 20
SESSION_ID_KEYS = (
    "session_id",
    "sessionId",
)
TEXT_KEYS = (
    "user_prompt",
    "prompt",
    "message",
    "text",
    "content",
    "input",
)
TRANSCRIPT_KEYS = (
    "transcript_path",
    "transcriptPath",
)
REQUIREMENT_ID_KEYS = (
    "requirement_ids",
    "requirementIds",
    "requirement_id",
    "requirementId",
)
WORKSTREAM_ID_KEYS = (
    "workstream_ids",
    "workstreamIds",
    "workstream_id",
    "workstreamId",
)
RESUME_KEYS = (
    "resumed",
    "is_resume",
    "resume",
)
SUBAGENT_KEYS = (
    "subagent",
    "is_subagent",
    "agent_type",
    "agentType",
)
ENV_SESSION_ID_KEYS = (
    "CODEX_SESSION_ID",
    "SESSION_ID",
)
ENV_REQUIREMENT_ID_KEYS = (
    "CODEX_REQUIREMENT_IDS",
    "REQUIREMENT_IDS",
)
ENV_WORKSTREAM_ID_KEYS = (
    "CODEX_WORKSTREAM_IDS",
    "WORKSTREAM_IDS",
)
ENV_AGENT_KEYS = (
    "CODEX_AGENT_TYPE",
    "AGENT_TYPE",
)


def main() -> int:
    payload = load_payload()
    try:
        append_observation(payload)
    except Exception:
        # Runtime observations are raw materials and must not block Stop.
        return 0
    return 0


def load_payload() -> dict[str, Any]:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def append_observation(payload: dict[str, Any]) -> None:
    OBSERVATION_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now().astimezone()
    session_id = first_value(payload, SESSION_ID_KEYS) or first_env_value(ENV_SESSION_ID_KEYS) or "unknown-session"
    changed_paths = git_status_paths()
    promote = should_promote(changed_paths)
    payload_requirement_ids = collect_identifier_values(payload, REQUIREMENT_ID_KEYS)
    payload_workstream_ids = collect_identifier_values(payload, WORKSTREAM_ID_KEYS)
    env_requirement_ids = [] if payload_requirement_ids else collect_env_identifiers(ENV_REQUIREMENT_ID_KEYS)
    env_workstream_ids = [] if payload_workstream_ids else collect_env_identifiers(ENV_WORKSTREAM_ID_KEYS)
    requirement_ids, workstream_ids, traceability_source = resolve_runtime_traceability(
        payload_requirement_ids,
        payload_workstream_ids,
        env_requirement_ids,
        env_workstream_ids,
        changed_paths,
    )

    observation = {
        "timestamp": now.isoformat(),
        "event": "Stop",
        "source": "codex-stop-hook",
        "session_id": session_id,
        "agent": infer_agent_label(payload),
        "session_kind": "resume" if infer_resumed(payload) else "active",
        "branch_or_thread": infer_branch_or_thread(payload, session_id),
        "cwd": compact_text(string_value(payload.get("cwd")), MAX_FIELD_LENGTH) or str(ROOT),
        "transcript_path": compact_transcript_path(first_value(payload, TRANSCRIPT_KEYS), MAX_FIELD_LENGTH),
        "prompt_preview": compact_text(first_value(payload, TEXT_KEYS), MAX_FIELD_LENGTH),
        "changed_paths": changed_paths[:MAX_CHANGED_PATHS],
        "changed_path_count": len(changed_paths),
        "docs_changed": any(is_under_doc_root(path_text) for path_text in changed_paths),
        "runtime_only_changes": has_runtime_only_changes(changed_paths),
        "requirement_ids": requirement_ids,
        "workstream_ids": workstream_ids,
        "traceability_source": traceability_source,
        "needs_governance_promotion": promote,
        "promotion_reason": infer_promotion_reason(promote, changed_paths),
    }

    clean_observation = {
        key: value
        for key, value in observation.items()
        if value not in ("", [], None)
    }

    observation_file = OBSERVATION_DIR / f"{now.strftime('%Y-%m-%d')}.jsonl"
    with observation_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(clean_observation, ensure_ascii=False) + "\n")


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


def infer_resumed(payload: dict[str, Any]) -> bool:
    value = first_value(payload, RESUME_KEYS)
    return isinstance(value, bool) and value


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


def is_under_doc_root(path_text: str) -> bool:
    path = (ROOT / path_text).resolve()
    for root in DOC_ROOTS:
        try:
            path.relative_to(root)
            return True
        except ValueError:
            continue
    return False


def has_runtime_only_changes(changed_paths: list[str]) -> bool:
    if not changed_paths:
        return False
    for path_text in changed_paths:
        if path_text.startswith(".codex/runtime/"):
            continue
        if path_text.startswith("mysjzhishidian/"):
            continue
        return False
    return True


def should_promote(changed_paths: list[str]) -> bool:
    if not changed_paths:
        return False
    return not has_runtime_only_changes(changed_paths)


def infer_promotion_reason(promote: bool, changed_paths: list[str]) -> str:
    if not changed_paths:
        return "当前未检测到工作区变更，先保留为 runtime observation"
    if not promote:
        return "当前仅检测到本地 runtime 或参考草稿层改动，暂不强制提升"
    return (
        "检测到除 runtime/参考草稿之外的仓库级改动；后续 reducer 或主 Agent 应判断是否提升到 handoff/status/ADR"
    )


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


def string_value(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


if __name__ == "__main__":
    raise SystemExit(main())
