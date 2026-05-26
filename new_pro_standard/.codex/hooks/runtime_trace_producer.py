#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "agent-trace/v1"
TRACE_DIR_NAME = "agent-traces"
REQ_ID_RE = re.compile(r"^REQ-[0-9]{3}$")
WS_ID_RE = re.compile(r"^WS-[0-9]{2}$")
UTC = timezone.utc


def try_emit_stop_trace(observation: dict[str, Any], observation_dir: Path) -> Path | None:
    try:
        return emit_stop_trace(observation, observation_dir)
    except Exception:
        return None


def emit_stop_trace(observation: dict[str, Any], observation_dir: Path) -> Path:
    record = build_stop_trace_record(observation)
    trace_dir = observation_dir / TRACE_DIR_NAME
    trace_dir.mkdir(parents=True, exist_ok=True)
    trace_file = trace_dir / f"{record['start_time'][:10]}.agent-trace.jsonl"
    with trace_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return trace_file


def build_stop_trace_record(observation: dict[str, Any]) -> dict[str, Any]:
    timestamp = rfc3339_utc_z(observation.get("timestamp"))
    return {
        "schema_version": SCHEMA_VERSION,
        "trace_id": stable_trace_id(observation),
        "span_id": stable_span_id(observation, timestamp),
        "parent_span_id": None,
        "name": "codex stop runtime observation",
        "kind": "event",
        "event": "stop_runtime_observation",
        "start_time": timestamp,
        "end_time": timestamp,
        "status": {"code": "ok"},
        "agent": {
            "name": "codex-stop-hook",
            "role": text_value(observation.get("agent")) or "main",
        },
        "attributes": trace_attributes(observation),
        "requirement_ids": identifier_values(observation.get("requirement_ids"), REQ_ID_RE),
        "workstream_ids": identifier_values(observation.get("workstream_ids"), WS_ID_RE),
        "redaction": redaction_metadata(observation),
    }


def rfc3339_utc_z(value: Any) -> str:
    if isinstance(value, str) and value.strip():
        try:
            parsed = parse_datetime(value.strip())
            return parsed.astimezone(UTC).isoformat().replace("+00:00", "Z")
        except ValueError:
            pass
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_datetime(value: str) -> datetime:
    normalized = value.removesuffix("Z") + ("+00:00" if value.endswith("Z") else "")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed


def stable_trace_id(observation: dict[str, Any]) -> str:
    session_id = text_value(observation.get("session_id")) or "unknown-session"
    return f"trace-{stable_hash(session_id)}"


def stable_span_id(observation: dict[str, Any], timestamp: str) -> str:
    identity = {
        "changed_path_count": observation.get("changed_path_count"),
        "changed_paths": list_values(observation.get("changed_paths")),
        "event": observation.get("event"),
        "session_id": observation.get("session_id"),
        "timestamp": timestamp,
    }
    return f"span-stop-{stable_hash(identity)}"


def trace_attributes(observation: dict[str, Any]) -> dict[str, Any]:
    attributes: dict[str, Any] = {}
    for key in (
        "source",
        "session_kind",
        "branch_or_thread",
        "changed_path_count",
        "docs_changed",
        "runtime_only_changes",
        "traceability_source",
        "needs_governance_promotion",
        "promotion_reason",
    ):
        add_attribute(attributes, key, observation.get(key))
    changed_paths = list_values(observation.get("changed_paths"))
    if changed_paths:
        attributes["changed_paths"] = changed_paths
    return attributes


def add_attribute(attributes: dict[str, Any], key: str, value: Any) -> None:
    if isinstance(value, (str, int, float, bool)) or value is None:
        if value not in ("", None):
            attributes[key] = value


def redaction_metadata(observation: dict[str, Any]) -> dict[str, str]:
    if observation.get("prompt_preview") or observation.get("transcript_path"):
        return {
            "state": "redacted",
            "rule": "runtime sanitizer applied; raw prompt, transcript, session id, and cwd omitted",
        }
    return {
        "state": "not_applicable",
        "rule": "trace producer writes metadata fields only; raw session id and cwd omitted",
    }


def stable_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def text_value(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


def list_values(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def identifier_values(value: Any, pattern: re.Pattern[str]) -> list[str]:
    return [item for item in list_values(value) if pattern.match(item)]
