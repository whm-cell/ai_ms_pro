#!/usr/bin/env python3

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:
    tomllib = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REQUIRED_AI_DOCS = (
    "AGENTS.md",
    "docs/ai/plan.md",
    "docs/ai/working-context.md",
)
DEFAULT_REQUIRED_REQ_DOCS = (
    "docs/requirements/traceability-matrix.md",
)
DEFAULT_ACTIVE_HANDOFF_BUDGET = 5
DEFAULT_ARCHIVE_CANDIDATE_MIN_SCORE = 3
DEFAULT_WARN_AT_BUDGET = True
DEFAULT_DEFAULT_SURFACE_TOKEN_BUDGET = 6500
DEFAULT_ALWAYS_ON_DOC_LINE_BUDGET = 300
DEFAULT_SKILL_DESCRIPTION_WORD_BUDGET = 30
DEFAULT_SKILL_BODY_LINE_BUDGET = 400
DEFAULT_ADR_COUNT_BUDGET = 15
DEFAULT_MCP_SERVER_BUDGET = 10


class HarnessConfigError(ValueError):
    pass


@dataclass(frozen=True)
class ChecksConfig:
    required_ai_docs: tuple[str, ...]
    required_requirements_docs: tuple[str, ...]


@dataclass(frozen=True)
class ContextSurfaceConfig:
    active_handoff_budget: int
    archive_candidate_min_score: int
    warn_at_budget: bool


@dataclass(frozen=True)
class ContextBudgetConfig:
    default_surface_token_budget: int
    always_on_doc_line_budget: int
    skill_description_word_budget: int
    skill_body_line_budget: int
    adr_count_budget: int
    mcp_server_budget: int


@dataclass(frozen=True)
class HarnessConfig:
    checks: ChecksConfig
    context_surface: ContextSurfaceConfig
    context_budget: ContextBudgetConfig


def load_harness_config(root: Path = ROOT) -> HarnessConfig:
    config_path = root / ".codex" / "harness.toml"
    data: dict[str, Any] = {}
    if config_path.exists():
        raw_text = config_path.read_text(encoding="utf-8")
        try:
            data = load_toml_config(raw_text)
        except ValueError as exc:
            rel_path = _display_path(config_path, root)
            raise HarnessConfigError(f"invalid TOML in {rel_path}: {exc}") from exc

    checks = _load_checks(data.get("checks", {}))
    context_surface = _load_context_surface(data.get("context_surface", {}))
    context_budget = _load_context_budget(data.get("context_budget", {}))
    return HarnessConfig(
        checks=checks,
        context_surface=context_surface,
        context_budget=context_budget,
    )


def load_toml_config(raw_text: str) -> dict[str, Any]:
    if tomllib is not None:
        try:
            return tomllib.loads(raw_text)
        except tomllib.TOMLDecodeError as exc:
            raise ValueError(str(exc)) from exc
    return load_minimal_toml_config(raw_text)


def load_minimal_toml_config(raw_text: str) -> dict[str, Any]:
    return {
        "checks": _parse_checks_section(_extract_section(raw_text, "checks")),
        "context_surface": _parse_context_surface_section(
            _extract_section(raw_text, "context_surface")
        ),
        "context_budget": _parse_context_budget_section(
            _extract_section(raw_text, "context_budget")
        ),
    }


def resolve_repo_paths(root: Path, entries: tuple[str, ...], *, config_label: str) -> list[Path]:
    resolved: list[Path] = []
    root = root.resolve()
    for entry in entries:
        path = (root / entry).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise HarnessConfigError(f"{config_label} path escapes repository root: {entry}") from exc
        resolved.append(path)
    return resolved


def _load_checks(raw_value: object) -> ChecksConfig:
    if raw_value is None:
        raw_value = {}
    if not isinstance(raw_value, dict):
        raise HarnessConfigError("[checks] must be a table")

    required_ai_docs = _string_tuple(
        raw_value.get("required_ai_docs"),
        default=DEFAULT_REQUIRED_AI_DOCS,
        label="checks.required_ai_docs",
    )
    required_requirements_docs = _string_tuple(
        raw_value.get("required_requirements_docs"),
        default=DEFAULT_REQUIRED_REQ_DOCS,
        label="checks.required_requirements_docs",
    )
    return ChecksConfig(
        required_ai_docs=required_ai_docs,
        required_requirements_docs=required_requirements_docs,
    )


def _load_context_surface(raw_value: object) -> ContextSurfaceConfig:
    if raw_value is None:
        raw_value = {}
    if not isinstance(raw_value, dict):
        raise HarnessConfigError("[context_surface] must be a table")

    return ContextSurfaceConfig(
        active_handoff_budget=_positive_int(
            raw_value.get("active_handoff_budget"),
            default=DEFAULT_ACTIVE_HANDOFF_BUDGET,
            label="context_surface.active_handoff_budget",
        ),
        archive_candidate_min_score=_positive_int(
            raw_value.get("archive_candidate_min_score"),
            default=DEFAULT_ARCHIVE_CANDIDATE_MIN_SCORE,
            label="context_surface.archive_candidate_min_score",
        ),
        warn_at_budget=_bool_value(
            raw_value.get("warn_at_budget"),
            default=DEFAULT_WARN_AT_BUDGET,
            label="context_surface.warn_at_budget",
        ),
    )


def _load_context_budget(raw_value: object) -> ContextBudgetConfig:
    if raw_value is None:
        raw_value = {}
    if not isinstance(raw_value, dict):
        raise HarnessConfigError("[context_budget] must be a table")

    return ContextBudgetConfig(
        default_surface_token_budget=_positive_int(
            raw_value.get("default_surface_token_budget"),
            default=DEFAULT_DEFAULT_SURFACE_TOKEN_BUDGET,
            label="context_budget.default_surface_token_budget",
        ),
        always_on_doc_line_budget=_positive_int(
            raw_value.get("always_on_doc_line_budget"),
            default=DEFAULT_ALWAYS_ON_DOC_LINE_BUDGET,
            label="context_budget.always_on_doc_line_budget",
        ),
        skill_description_word_budget=_positive_int(
            raw_value.get("skill_description_word_budget"),
            default=DEFAULT_SKILL_DESCRIPTION_WORD_BUDGET,
            label="context_budget.skill_description_word_budget",
        ),
        skill_body_line_budget=_positive_int(
            raw_value.get("skill_body_line_budget"),
            default=DEFAULT_SKILL_BODY_LINE_BUDGET,
            label="context_budget.skill_body_line_budget",
        ),
        adr_count_budget=_positive_int(
            raw_value.get("adr_count_budget"),
            default=DEFAULT_ADR_COUNT_BUDGET,
            label="context_budget.adr_count_budget",
        ),
        mcp_server_budget=_positive_int(
            raw_value.get("mcp_server_budget"),
            default=DEFAULT_MCP_SERVER_BUDGET,
            label="context_budget.mcp_server_budget",
        ),
    )


def _string_tuple(value: object, *, default: tuple[str, ...], label: str) -> tuple[str, ...]:
    if value is None:
        return default
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise HarnessConfigError(f"{label} must be a list of strings")
    return tuple(value)


def _positive_int(value: object, *, default: int, label: str) -> int:
    if value is None:
        return default
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise HarnessConfigError(f"{label} must be a positive integer")
    return value


def _bool_value(value: object, *, default: bool, label: str) -> bool:
    if value is None:
        return default
    if not isinstance(value, bool):
        raise HarnessConfigError(f"{label} must be a boolean")
    return value


def _extract_section(raw_text: str, section_name: str) -> str:
    match = re.search(rf"(?ms)^\[{re.escape(section_name)}\]\s*(.*?)(?=^\[|\Z)", raw_text)
    return match.group(1) if match else ""


def _parse_checks_section(section_text: str) -> dict[str, object]:
    checks: dict[str, object] = {}
    for key in ("required_ai_docs", "required_requirements_docs"):
        if value := _parse_string_array(section_text, key):
            checks[key] = value
    return checks


def _parse_context_surface_section(section_text: str) -> dict[str, object]:
    values: dict[str, object] = {}
    for key in ("active_handoff_budget", "archive_candidate_min_score"):
        if (value := _parse_int(section_text, key)) is not None:
            values[key] = value
    if (value := _parse_bool(section_text, "warn_at_budget")) is not None:
        values["warn_at_budget"] = value
    return values


def _parse_context_budget_section(section_text: str) -> dict[str, object]:
    values: dict[str, object] = {}
    for key in (
        "default_surface_token_budget",
        "always_on_doc_line_budget",
        "skill_description_word_budget",
        "skill_body_line_budget",
        "adr_count_budget",
        "mcp_server_budget",
    ):
        if (value := _parse_int(section_text, key)) is not None:
            values[key] = value
    return values


def _parse_string_array(section_text: str, key: str) -> list[str] | None:
    match = re.search(rf"(?ms)^\s*{re.escape(key)}\s*=\s*(\[[^\]]*\])", section_text)
    if not match:
        return None
    try:
        parsed = ast.literal_eval(match.group(1))
    except (SyntaxError, ValueError) as exc:
        raise ValueError(f"could not parse {key}") from exc
    if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
        raise ValueError(f"{key} must be a list of strings")
    return parsed


def _parse_int(section_text: str, key: str) -> int | None:
    match = re.search(rf"(?m)^\s*{re.escape(key)}\s*=\s*([0-9]+)\s*$", section_text)
    return int(match.group(1)) if match else None


def _parse_bool(section_text: str, key: str) -> bool | None:
    match = re.search(rf"(?m)^\s*{re.escape(key)}\s*=\s*(true|false)\s*$", section_text)
    if not match:
        return None
    return match.group(1) == "true"


def _display_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
