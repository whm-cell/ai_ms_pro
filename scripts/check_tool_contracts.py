#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "docs" / "ai" / "tool-contracts" / "contracts.json"
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]*$")
TIMEOUT_MIN = 1
TIMEOUT_MAX = 3600

REQUIRED_FIELDS = (
    "name",
    "purpose",
    "path",
    "command",
    "inputs",
    "outputs",
    "side_effects",
    "permissions",
    "timeout_seconds",
    "destructive",
    "externally_visible",
    "automation_mode",
    "verification_commands",
)

SIDE_EFFECTS = {
    "none",
    "read_repo",
    "read_runtime",
    "write_runtime",
    "write_governance",
    "write_worktree",
    "network_read",
    "network_write",
    "launch_local_server",
    "browser_automation",
    "git_read",
    "git_write",
    "github_read",
    "github_write",
}

AUTOMATION_MODES = {
    "hook",
    "ci",
    "dry_run",
    "assistive",
    "manual",
    "human_confirmed",
}

EXTERNALLY_VISIBLE_ALLOWED = {"manual", "human_confirmed"}


@dataclass(frozen=True)
class ValidationResult:
    errors: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate standard tool contracts.")
    parser.add_argument(
        "--registry",
        default=str(DEFAULT_REGISTRY),
        help="Path to contracts.json. Defaults to docs/ai/tool-contracts/contracts.json.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable result.")
    return parser.parse_args()


def load_registry(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"registry not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"registry is not valid JSON: {exc}") from exc


def validate_registry(data: Any, *, root: Path = ROOT) -> ValidationResult:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ValidationResult(["registry root must be an object"])
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    contracts = data.get("contracts")
    if not isinstance(contracts, list) or not contracts:
        errors.append("contracts must be a non-empty list")
        return ValidationResult(errors)

    seen: dict[str, int] = {}
    for index, contract in enumerate(contracts):
        if not isinstance(contract, dict):
            errors.append(f"contract[{index}] must be an object")
            continue
        validate_contract(contract, index=index, root=root, seen=seen, errors=errors)
    return ValidationResult(errors)


def validate_contract(
    contract: dict[str, Any],
    *,
    index: int,
    root: Path,
    seen: dict[str, int],
    errors: list[str],
) -> None:
    label = contract_label(contract, index)
    for field in REQUIRED_FIELDS:
        if field not in contract:
            errors.append(f"{label}: missing required field {field}")

    name = string_field(contract, "name", label, errors)
    if name:
        validate_name(name, index, seen, errors)
    string_field(contract, "purpose", label, errors)
    validate_path(contract.get("path"), label, root, errors)
    validate_command(contract.get("command"), label, root, errors)
    validate_string_list(contract.get("inputs"), "inputs", label, errors, non_empty=True)
    validate_string_list(contract.get("outputs"), "outputs", label, errors, non_empty=True)
    validate_side_effects(contract.get("side_effects"), label, errors)
    validate_string_list(contract.get("permissions"), "permissions", label, errors, non_empty=True)
    validate_timeout(contract.get("timeout_seconds"), label, errors)
    validate_bool(contract.get("destructive"), "destructive", label, errors)
    validate_bool(contract.get("externally_visible"), "externally_visible", label, errors)
    validate_automation(contract.get("automation_mode"), label, errors)
    validate_verification_commands(contract.get("verification_commands"), label, root, errors)
    validate_gating(contract, label, errors)


def contract_label(contract: dict[str, Any], index: int) -> str:
    name = contract.get("name")
    if isinstance(name, str) and name:
        return name
    return f"contract[{index}]"


def string_field(contract: dict[str, Any], field: str, label: str, errors: list[str]) -> str:
    value = contract.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}: {field} must be a non-empty string")
        return ""
    return value


def validate_name(name: str, index: int, seen: dict[str, int], errors: list[str]) -> None:
    if not NAME_RE.match(name):
        errors.append(f"{name}: name must match {NAME_RE.pattern}")
    if name in seen:
        errors.append(f"{name}: duplicate name also used by contract[{seen[name]}]")
    seen[name] = index


def validate_path(value: Any, label: str, root: Path, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}: path must be a non-empty string")
        return
    if Path(value).is_absolute():
        errors.append(f"{label}: path must be repo-relative")
        return
    if not (root / value).exists():
        errors.append(f"{label}: path does not exist: {value}")


def validate_command(value: Any, label: str, root: Path, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}: command must be a non-empty string")
        return
    validate_command_paths(value, label, root, errors, field="command")


def validate_string_list(
    value: Any,
    field: str,
    label: str,
    errors: list[str],
    *,
    non_empty: bool,
) -> list[str]:
    if not isinstance(value, list) or (non_empty and not value):
        errors.append(f"{label}: {field} must be a non-empty list")
        return []
    items: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{label}: {field}[{index}] must be a non-empty string")
            continue
        items.append(item)
    return items


def validate_side_effects(value: Any, label: str, errors: list[str]) -> None:
    items = validate_string_list(value, "side_effects", label, errors, non_empty=True)
    unknown = sorted(set(items) - SIDE_EFFECTS)
    for item in unknown:
        errors.append(f"{label}: unknown side_effects value {item}")
    if "none" in items and len(items) > 1:
        errors.append(f"{label}: side_effects none cannot be combined with other values")


def validate_timeout(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        errors.append(f"{label}: timeout_seconds must be an integer")
        return
    if value < TIMEOUT_MIN or value > TIMEOUT_MAX:
        errors.append(f"{label}: timeout_seconds must be between {TIMEOUT_MIN} and {TIMEOUT_MAX}")


def validate_bool(value: Any, field: str, label: str, errors: list[str]) -> None:
    if not isinstance(value, bool):
        errors.append(f"{label}: {field} must be a boolean")


def validate_automation(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or value not in AUTOMATION_MODES:
        errors.append(f"{label}: automation_mode must be one of {sorted(AUTOMATION_MODES)}")


def validate_verification_commands(value: Any, label: str, root: Path, errors: list[str]) -> None:
    commands = validate_string_list(value, "verification_commands", label, errors, non_empty=True)
    for command in commands:
        validate_command_paths(command, label, root, errors, field="verification_commands")


def validate_command_paths(command: str, label: str, root: Path, errors: list[str], *, field: str) -> None:
    try:
        parts = shlex.split(command)
    except ValueError as exc:
        errors.append(f"{label}: {field} is not shell-parseable: {exc}")
        return
    for part in parts:
        if part.startswith(("scripts/", "tests/", ".codex/")):
            path = root / part
            if not path.exists():
                errors.append(f"{label}: {field} references missing path {part}")


def validate_gating(contract: dict[str, Any], label: str, errors: list[str]) -> None:
    automation = contract.get("automation_mode")
    permissions = contract.get("permissions")
    permission_set = set(permissions) if isinstance(permissions, list) else set()
    side_effects = set(contract.get("side_effects", [])) if isinstance(contract.get("side_effects"), list) else set()
    external_writes = {"network_write", "github_write"} & side_effects
    if external_writes and contract.get("externally_visible") is not True:
        errors.append(f"{label}: {sorted(external_writes)} side effects require externally_visible=true")
    if contract.get("destructive") is True:
        if automation != "human_confirmed":
            errors.append(f"{label}: destructive default command must use human_confirmed")
        if "human-confirmation-required" not in permission_set:
            errors.append(f"{label}: destructive default command requires human-confirmation-required permission")
    if contract.get("externally_visible") is True and automation not in EXTERNALLY_VISIBLE_ALLOWED:
        errors.append(f"{label}: externally visible default command cannot run in unattended automation")


def main() -> int:
    args = parse_args()
    try:
        data = load_registry(Path(args.registry))
        result = validate_registry(data)
    except ValueError as exc:
        result = ValidationResult([str(exc)])

    if args.json:
        print(json.dumps({"ok": not result.errors, "errors": result.errors}, indent=2))
    elif result.errors:
        print("Tool contract validation failed:")
        for error in result.errors:
            print(f"- {error}")
    else:
        print("Tool contract validation passed.")
    return 1 if result.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
