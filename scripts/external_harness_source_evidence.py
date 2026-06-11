from __future__ import annotations

from typing import Any


MAX_TEXT = 700
MAX_LIST_ITEMS = 12
SOURCE_TYPES = {"official-doc", "github-release", "pypi-release", "official-spec"}


def validate(
    record: dict[str, Any],
    prefix: str,
    errors: list[str],
) -> tuple[int, set[str]]:
    value = record.get("source_evidence")
    if not isinstance(value, list) or not value:
        errors.append(f"{prefix}: source_evidence must be a non-empty list")
        return 0, set()
    if len(value) > MAX_LIST_ITEMS:
        errors.append(f"{prefix}: source_evidence has too many items")
    valid_count = 0
    local_upgrade_scopes: set[str] = set()
    for index, item in enumerate(value):
        item_prefix = f"{prefix}: source_evidence[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        validate_choice(item, "source_type", SOURCE_TYPES, item_prefix, errors)
        source_date = validate_bounded_required_text(item, "source_date", item_prefix, errors)
        if source_date and len(source_date) < len("YYYY-MM-DD"):
            errors.append(f"{item_prefix}: source_date must include at least YYYY-MM-DD")
        url = validate_bounded_required_text(item, "url", item_prefix, errors)
        if url and not url.startswith("https://"):
            errors.append(f"{item_prefix}: url must start with https://")
        if item.get("positive_signal") is not True:
            errors.append(f"{item_prefix}: positive_signal must be true")
        validate_bounded_required_text(item, "finding", item_prefix, errors)
        scope = validate_bounded_required_text(item, "local_upgrade_scope", item_prefix, errors)
        if scope:
            local_upgrade_scopes.add(scope)
        valid_count += 1
    return valid_count, local_upgrade_scopes


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


def validate_bounded_required_text(
    record: dict[str, Any],
    field: str,
    prefix: str,
    errors: list[str],
) -> str:
    value = text(record.get(field))
    if not value:
        errors.append(f"{prefix}: {field} must be non-empty text")
        return ""
    if len(value) > MAX_TEXT:
        errors.append(f"{prefix}: {field} exceeds {MAX_TEXT} characters")
    return value


def text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""
