from __future__ import annotations

from typing import Any


MAX_TEXT = 700
MAX_LIST_ITEMS = 12
POLICIES = {"evidence-backed-default-permit"}
EVIDENCE_GRADES = {"first-party-source-backed"}
REQUIRED_BLOCKED_SCOPE_MARKERS = (
    "hosted trace/eval claim",
    "verified remote claim without operator review",
    "native sandbox claim",
    "mcp/a2a runtime claim",
    "real ci agent workflow",
    "external effect without explicit confirmation",
)


def validate(
    record: dict[str, Any],
    status: str,
    prefix: str,
    errors: list[str],
) -> tuple[int, set[str]]:
    if status != "active":
        return 0, set()
    value = record.get("default_permission")
    if not isinstance(value, dict):
        errors.append(f"{prefix}: active records must include default_permission")
        return 0, set()
    validate_choice(value, "policy", POLICIES, prefix, errors)
    validate_choice(value, "evidence_grade", EVIDENCE_GRADES, prefix, errors)
    if value.get("positive_for_current_harness") is not True:
        errors.append(f"{prefix}: default_permission.positive_for_current_harness must be true")
    permitted = validate_text_list(value, "permitted_scope", prefix, errors)
    blocked = validate_text_list(value, "blocked_scope", prefix, errors)
    validate_text_list(value, "evidence_threshold", prefix, errors)
    validate_text_list(value, "verification_commands", prefix, errors)
    validate_blocked_scope(blocked, prefix, errors)
    return 1, set(permitted)


def validate_blocked_scope(blocked: list[str], prefix: str, errors: list[str]) -> None:
    blocked_text = "\n".join(item.lower() for item in blocked)
    for marker in REQUIRED_BLOCKED_SCOPE_MARKERS:
        if marker not in blocked_text:
            errors.append(f"{prefix}: default_permission.blocked_scope must mention {marker}")


def validate_choice(
    record: dict[str, Any],
    field: str,
    choices: set[str],
    prefix: str,
    errors: list[str],
) -> str:
    value = text(record.get(field))
    if not value:
        errors.append(f"{prefix}: {field} must be non-empty text")
        return ""
    if value not in choices:
        errors.append(f"{prefix}: {field} must be one of {sorted(choices)}")
    return value


def validate_text_list(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> list[str]:
    value = record.get(field)
    if not isinstance(value, list) or not value:
        errors.append(f"{prefix}: {field} must be a non-empty list")
        return []
    if len(value) > MAX_LIST_ITEMS:
        errors.append(f"{prefix}: {field} has too many items")
    items: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{prefix}: {field}[{index}] must be non-empty text")
            continue
        if len(item) > MAX_TEXT:
            errors.append(f"{prefix}: {field}[{index}] exceeds {MAX_TEXT} characters")
        items.append(item.strip())
    return items


def text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""
