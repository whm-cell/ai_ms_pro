from __future__ import annotations

from typing import Any


MODEL_USAGE = {"none", "local-model", "hosted-model", "mixed", "unknown"}
MAX_TEXT = 600


def text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def validate_run_metrics(value: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix}: run_metrics must be an object")
        return
    validate_choice(value, "model_usage", MODEL_USAGE, prefix, errors)
    validate_required_text(value, "model_name", prefix, errors)
    for field in ("estimated_input_tokens", "estimated_output_tokens", "latency_ms"):
        validate_non_negative_int(value, field, prefix, errors)
    validate_non_negative_number(value, "estimated_cost_usd", prefix, errors)
    validate_required_text(value, "measurement_boundary", prefix, errors)
    if value.get("model_usage") == "none":
        for field in ("estimated_input_tokens", "estimated_output_tokens", "latency_ms"):
            if value.get(field) != 0:
                errors.append(f"{prefix}: run_metrics.{field} must be 0 when model_usage=none")
        if value.get("estimated_cost_usd") != 0:
            errors.append(f"{prefix}: run_metrics.estimated_cost_usd must be 0 when model_usage=none")


def model_usage(value: Any) -> str:
    return text(value.get("model_usage")) if isinstance(value, dict) else "unknown"


def estimated_cost(value: Any) -> float:
    if not isinstance(value, dict):
        return 0.0
    cost = value.get("estimated_cost_usd")
    if isinstance(cost, int | float) and not isinstance(cost, bool):
        return float(cost)
    return 0.0


def validate_choice(value: dict[str, Any], field: str, choices: set[str], prefix: str, errors: list[str]) -> None:
    item = text(value.get(field))
    if not item:
        errors.append(f"{prefix}: run_metrics.{field} must be non-empty text")
    elif item not in choices:
        errors.append(f"{prefix}: run_metrics.{field} must be one of {sorted(choices)}")


def validate_required_text(value: dict[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    item = text(value.get(field))
    if not item:
        errors.append(f"{prefix}: run_metrics.{field} must be non-empty text")
    elif len(item) > MAX_TEXT:
        errors.append(f"{prefix}: run_metrics.{field} exceeds {MAX_TEXT} characters")


def validate_non_negative_int(value: dict[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    item = value.get(field)
    if not isinstance(item, int) or isinstance(item, bool) or item < 0:
        errors.append(f"{prefix}: run_metrics.{field} must be a non-negative integer")


def validate_non_negative_number(value: dict[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    item = value.get(field)
    if not isinstance(item, int | float) or isinstance(item, bool) or item < 0:
        errors.append(f"{prefix}: run_metrics.{field} must be a non-negative number")
