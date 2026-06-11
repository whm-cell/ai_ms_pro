#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / ".codex" / "hooks") not in sys.path:
    sys.path.insert(0, str(ROOT / ".codex" / "hooks"))

from runtime_execution_snapshot import ALLOWED_STATES, SCHEMA_VERSION, SNAPSHOT_DIR  # noqa: E402


ALLOWED_AUTHORITY = {"main-agent", "subagent-draft", "manual-review", "user-confirmed"}
ALLOWED_BOUNDARIES = {"local-only"}
ALLOWED_STATE_SOURCES = {"payload", "payload-task-complete", "default-stop-hook"}
CONTRACTS_PATH = ROOT / "docs" / "ai" / "tool-contracts" / "contracts.json"
DEFAULT_SAMPLE = ROOT / "docs" / "ai" / "standards" / "runtime-execution-snapshot.sample.json"
RAW_PATH_MARKERS = (".codex/runtime/", "/.codex/runtime/", ".codex\\runtime\\", "\\.codex\\runtime\\", "/Users/", "C:\\Users\\")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate local runtime execution snapshot artifacts.")
    parser.add_argument(
        "--snapshot-dir",
        default=str(SNAPSHOT_DIR),
        help=f"Snapshot directory. Default: {SNAPSHOT_DIR}",
    )
    parser.add_argument(
        "--sample",
        default=str(DEFAULT_SAMPLE),
        help=f"Fallback sample path when no runtime snapshot exists. Default: {DEFAULT_SAMPLE}",
    )
    return parser.parse_args()


def load_contract_names() -> set[str]:
    try:
        data = json.loads(CONTRACTS_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()
    contracts = data.get("contracts")
    if not isinstance(contracts, list):
        return set()
    return {
        item["name"]
        for item in contracts
        if isinstance(item, dict) and isinstance(item.get("name"), str) and item["name"].strip()
    }


def validate_snapshot(snapshot: dict[str, Any], contract_names: set[str], path: Path) -> list[str]:
    errors: list[str] = []
    if snapshot.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{path}: schema_version must be {SCHEMA_VERSION}")
    for field in (
        "session_id",
        "recorded_at",
        "stage",
        "branch_or_thread",
        "session_type",
        "state",
        "state_reason",
        "agent",
        "task_summary",
        "traceability_source",
        "claim_boundary",
    ):
        if not isinstance(snapshot.get(field), str) or not str(snapshot[field]).strip():
            errors.append(f"{path}: {field} must be a non-empty string")
    state = snapshot.get("state")
    if isinstance(state, str) and state not in ALLOWED_STATES:
        errors.append(f"{path}: state must be one of {sorted(ALLOWED_STATES)}")
    authority = snapshot.get("authority")
    if not isinstance(authority, dict):
        errors.append(f"{path}: authority must be an object")
    else:
        level = authority.get("level")
        if not isinstance(level, str) or level not in ALLOWED_AUTHORITY:
            errors.append(f"{path}: authority.level must be one of {sorted(ALLOWED_AUTHORITY)}")
        if not isinstance(authority.get("canonical_promotion_required"), bool):
            errors.append(f"{path}: authority.canonical_promotion_required must be a boolean")
    boundary = snapshot.get("claim_boundary")
    if isinstance(boundary, str) and boundary not in ALLOWED_BOUNDARIES:
        errors.append(f"{path}: claim_boundary must be one of {sorted(ALLOWED_BOUNDARIES)}")
    validate_optional_execution_state(snapshot, path, errors)
    for field in ("requirement_ids", "workstream_ids", "tool_contracts", "changed_paths"):
        value = snapshot.get(field)
        if not isinstance(value, list):
            errors.append(f"{path}: {field} must be a list")
            continue
        for index, item in enumerate(value):
            if not isinstance(item, str) or not item.strip():
                errors.append(f"{path}: {field}[{index}] must be a non-empty string")
    if isinstance(snapshot.get("tool_contracts"), list):
        for contract in snapshot["tool_contracts"]:
            if contract not in contract_names:
                errors.append(f"{path}: unknown tool contract {contract}")
    artifacts = snapshot.get("artifacts")
    if not isinstance(artifacts, dict):
        errors.append(f"{path}: artifacts must be an object")
    else:
        working_context = artifacts.get("working_context_path")
        if not isinstance(working_context, str) or not working_context.endswith("docs/ai/working-context.md"):
            errors.append(f"{path}: artifacts.working_context_path must point to docs/ai/working-context.md")
        for key, value in artifacts.items():
            if isinstance(value, str) and contains_raw_runtime_path(value):
                errors.append(f"{path}: artifacts.{key} must not contain raw local transcript or runtime paths")
    return errors


def validate_optional_execution_state(snapshot: dict[str, Any], path: Path, errors: list[str]) -> None:
    if "state_source" in snapshot and snapshot["state_source"] not in ALLOWED_STATE_SOURCES:
        errors.append(f"{path}: state_source must be one of {sorted(ALLOWED_STATE_SOURCES)}")
    if "resume_ready" in snapshot and not isinstance(snapshot["resume_ready"], bool):
        errors.append(f"{path}: resume_ready must be a boolean")
    for field in ("resume_blockers", "last_validation_refs"):
        if field not in snapshot:
            continue
        validate_string_list(snapshot[field], f"{path}: {field}", errors)
    run_identity = snapshot.get("run_identity")
    if run_identity is not None:
        validate_string_object(
            run_identity,
            f"{path}: run_identity",
            ("session_id", "branch_or_thread", "session_type", "agent"),
            errors,
        )
    state_transition = snapshot.get("state_transition")
    if state_transition is not None:
        validate_string_object(
            state_transition,
            f"{path}: state_transition",
            ("state", "state_reason", "state_source", "recorded_at"),
            errors,
        )
    resume_context = snapshot.get("resume_context")
    if resume_context is not None:
        if not isinstance(resume_context, dict):
            errors.append(f"{path}: resume_context must be an object")
        else:
            if not isinstance(resume_context.get("resume_ready"), bool):
                errors.append(f"{path}: resume_context.resume_ready must be a boolean")
            validate_string_list(resume_context.get("resume_blockers"), f"{path}: resume_context.resume_blockers", errors)
            validate_string_list(
                resume_context.get("last_validation_refs"),
                f"{path}: resume_context.last_validation_refs",
                errors,
            )
            if not isinstance(resume_context.get("changed_path_count"), int):
                errors.append(f"{path}: resume_context.changed_path_count must be an integer")


def validate_string_object(value: Any, label: str, fields: tuple[str, ...], errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return
    for field in fields:
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append(f"{label}.{field} must be a non-empty string")


def validate_string_list(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{label}[{index}] must be a non-empty string")


def contains_raw_runtime_path(value: str) -> bool:
    if value.startswith("[REDACTED_PATH]"):
        return False
    return any(marker in value for marker in RAW_PATH_MARKERS)


def load_snapshot(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: snapshot must be a JSON object")
    return value


def main() -> int:
    args = parse_args()
    snapshot_dir = Path(args.snapshot_dir).expanduser()
    files = sorted(path for path in snapshot_dir.glob("*.json") if path.is_file()) if snapshot_dir.exists() else []
    if not files:
        sample_path = Path(args.sample).expanduser()
        if not sample_path.exists():
            print(
                f"runtime execution snapshot check failed: no runtime snapshots in {snapshot_dir} and sample not found: {sample_path}",
                file=sys.stderr,
            )
            return 1
        files = [sample_path]
    contract_names = load_contract_names()
    errors: list[str] = []
    for path in files:
        try:
            snapshot = load_snapshot(path)
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append(str(exc))
            continue
        errors.extend(validate_snapshot(snapshot, contract_names, path))
    if errors:
        print("runtime execution snapshot check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"runtime execution snapshot check passed ({len(files)} snapshot files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
