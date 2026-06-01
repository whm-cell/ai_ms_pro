#!/usr/bin/env python3

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
WORKING_CONTEXT_PATH = ROOT / "docs" / "ai" / "working-context.md"
SNAPSHOT_DIR = ROOT / ".codex" / "runtime" / "execution-snapshots"
SCHEMA_VERSION = "runtime-execution-snapshot/v1"
ALLOWED_STATES = {
    "created",
    "running",
    "paused",
    "resumable",
    "completed",
    "failed",
    "cancelled",
}
STATE_KEYS = (
    "execution_state",
    "task_state",
    "run_state",
    "state",
)
SUMMARY_KEYS = (
    "task_summary",
    "goal",
    "summary",
)
REASON_KEYS = (
    "state_reason",
    "execution_state_reason",
    "reason",
)
AUTHORITY_KEYS = (
    "authority",
    "authority_level",
)
TOOL_CONTRACT_KEYS = (
    "tool_contracts",
    "toolContracts",
)


def write_snapshot(snapshot: dict[str, Any], snapshot_dir: Path | None = None) -> Path:
    snapshot_dir = snapshot_dir or SNAPSHOT_DIR
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    session_id = text_value(snapshot.get("session_id")) or "unknown-session"
    path = snapshot_dir / f"{session_id}.json"
    path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def build_execution_snapshot(
    *,
    payload: dict[str, Any],
    session_id: str,
    agent_label: str,
    branch_or_thread: str,
    session_type: str,
    requirement_ids: list[str],
    workstream_ids: list[str],
    traceability_source: str,
    changed_paths: list[str],
    prompt_preview: str,
    transcript_path: str,
) -> dict[str, Any]:
    state = infer_state(payload)
    state_reason = (
        text_value(first_value(payload, REASON_KEYS))
        or default_state_reason(state, session_type)
    )
    stage = read_current_stage()
    authority_level = infer_authority(payload, agent_label)
    tool_contracts = infer_tool_contracts(payload)
    now = datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")

    snapshot: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "session_id": session_id,
        "recorded_at": now,
        "stage": stage or "UNKNOWN",
        "branch_or_thread": branch_or_thread,
        "session_type": session_type,
        "state": state,
        "state_reason": state_reason,
        "agent": agent_label,
        "authority": {
            "level": authority_level,
            "canonical_promotion_required": True,
        },
        "task_summary": infer_task_summary(payload, prompt_preview),
        "requirement_ids": requirement_ids or ["未绑定"],
        "workstream_ids": workstream_ids or ["未绑定"],
        "traceability_source": traceability_source or "unbound",
        "tool_contracts": tool_contracts,
        "claim_boundary": "local-only",
        "changed_paths": changed_paths[:20],
        "changed_path_count": len(changed_paths),
        "artifacts": {
            "transcript_path": transcript_path,
            "working_context_path": relative_or_text(WORKING_CONTEXT_PATH),
        },
    }
    return snapshot


def load_snapshot(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} does not contain a JSON object")
    return value


def infer_state(payload: dict[str, Any]) -> str:
    explicit = text_value(first_value(payload, STATE_KEYS)).lower().replace("_", "-")
    if explicit in ALLOWED_STATES:
        return explicit
    task_complete = payload.get("task_complete")
    if task_complete is True:
        return "completed"
    return "resumable"


def default_state_reason(state: str, session_type: str) -> str:
    if state == "completed":
        return "Explicit completion signal was provided before snapshot write."
    if state == "failed":
        return "Explicit failure signal was provided before snapshot write."
    if state == "cancelled":
        return "Explicit cancel signal was provided before snapshot write."
    if session_type == "resume":
        return "Stop hook captured a resumed task as resumable for the next local continuation."
    return "Stop hook captured the current local task as resumable without promoting runtime artifacts to canonical truth."


def infer_authority(payload: dict[str, Any], agent_label: str) -> str:
    explicit = text_value(first_value(payload, AUTHORITY_KEYS))
    if explicit:
        return explicit
    return "subagent-draft" if agent_label == "subagent" else "main-agent"


def infer_tool_contracts(payload: dict[str, Any]) -> list[str]:
    value = first_value(payload, TOOL_CONTRACT_KEYS)
    if isinstance(value, list):
        contracts = [text_value(item) for item in value if isinstance(item, str)]
        filtered = [item for item in contracts if item]
        if filtered:
            return filtered
    return ["stop_runtime_observation", "stop_runtime_session"]


def infer_task_summary(payload: dict[str, Any], prompt_preview: str) -> str:
    explicit = text_value(first_value(payload, SUMMARY_KEYS))
    if explicit:
        return explicit
    if prompt_preview:
        return prompt_preview
    return "Local runtime execution snapshot captured without a task summary."


def read_current_stage() -> str:
    if not WORKING_CONTEXT_PATH.exists():
        return ""
    for line in WORKING_CONTEXT_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith("- Current Stage:"):
            return line.split(":", 1)[1].strip()
        if line.startswith("当前阶段："):
            return line.split("：", 1)[1].strip()
    return ""


def first_value(data: Any, keys: tuple[str, ...]) -> Any:
    if isinstance(data, dict):
        for key in keys:
            if key in data:
                return data[key]
    return None


def text_value(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


def relative_or_text(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)
