#!/usr/bin/env python3

from __future__ import annotations

from datetime import datetime
from typing import Any

from runtime_sanitizer import compact_text, compact_transcript_path
from runtime_execution_snapshot import build_execution_snapshot, write_snapshot
from runtime_traceability import resolve_runtime_traceability
from session_snapshot_render import render_session_snapshot
from session_runtime_utils import (
    ENV_REQUIREMENT_ID_KEYS,
    ENV_SESSION_ID_KEYS,
    ENV_WORKSTREAM_ID_KEYS,
    MAX_FIELD_LENGTH,
    REQUIREMENT_ID_KEYS,
    SESSION_DIR,
    SESSION_ID_KEYS,
    TEXT_KEYS,
    TRANSCRIPT_KEYS,
    WORKING_CONTEXT_PATH,
    WORKSTREAM_ID_KEYS,
    collect_env_identifiers,
    collect_identifier_values,
    first_env_value,
    first_value,
    git_branch as _git_branch,
    git_status_paths,
    infer_agent_label,
    infer_promotion_reason,
    infer_session_type,
    load_payload,
    should_promote,
    slugify,
)


def main() -> int:
    payload = load_payload()
    try:
        write_session_snapshot(payload)
    except Exception:
        # Runtime session persistence is best-effort and must never block Stop.
        return 0
    return 0


def git_branch() -> str:
    return _git_branch()


def find_or_create_session_file(session_id: str, agent_label: str, branch_or_thread: str):
    existing = sorted(SESSION_DIR.glob(f"*_{session_id}.md"))
    if existing:
        return existing[-1]

    stamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    safe_branch = slugify(branch_or_thread)
    safe_agent = slugify(agent_label)
    safe_session = slugify(session_id)
    return SESSION_DIR / f"{stamp}_{safe_agent}_{safe_branch}_{safe_session}.md"


def infer_branch_or_thread(payload: dict[str, Any], session_id: str) -> str:
    branch = git_branch()
    if branch:
        return branch
    thread = first_value(payload, ("thread_id", "threadId"))
    if isinstance(thread, str) and thread.strip():
        return thread.strip()
    return session_id


def write_session_snapshot(payload: dict[str, Any]) -> None:
    SESSION_DIR.mkdir(parents=True, exist_ok=True)

    session_id = first_value(payload, SESSION_ID_KEYS) or first_env_value(ENV_SESSION_ID_KEYS) or "unknown-session"
    agent_label = infer_agent_label(payload)
    branch_or_thread = infer_branch_or_thread(payload, session_id)
    session_file = find_or_create_session_file(session_id, agent_label, branch_or_thread)

    session_type = infer_session_type(payload, session_file)
    prompt_preview = compact_text(first_value(payload, TEXT_KEYS), MAX_FIELD_LENGTH)
    transcript_path = compact_transcript_path(first_value(payload, TRANSCRIPT_KEYS), MAX_FIELD_LENGTH)
    changed_paths = git_status_paths()
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
    now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")

    promote = should_promote(changed_paths)
    promote_reason = infer_promotion_reason(promote, changed_paths)
    content = render_session_snapshot(
        {
            "now": now,
            "agent_label": agent_label,
            "session_type": session_type,
            "branch_or_thread": branch_or_thread,
            "session_id": session_id,
            "requirement_ids": requirement_ids,
            "workstream_ids": workstream_ids,
            "traceability_source": traceability_source,
            "prompt_preview": prompt_preview,
            "transcript_path": transcript_path,
            "changed_paths": changed_paths,
            "promote": promote,
            "promote_reason": promote_reason,
            "working_context_path": compact_text(str(WORKING_CONTEXT_PATH), MAX_FIELD_LENGTH),
        }
    )

    session_file.write_text(content, encoding="utf-8")
    execution_snapshot = build_execution_snapshot(
        payload=payload,
        session_id=session_id,
        agent_label=agent_label,
        branch_or_thread=branch_or_thread,
        session_type=session_type,
        requirement_ids=requirement_ids,
        workstream_ids=workstream_ids,
        traceability_source=traceability_source,
        changed_paths=changed_paths,
        prompt_preview=prompt_preview,
        transcript_path=transcript_path,
    )
    write_snapshot(execution_snapshot)


if __name__ == "__main__":
    raise SystemExit(main())
