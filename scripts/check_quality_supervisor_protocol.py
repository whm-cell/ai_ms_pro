#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    tomllib = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[1]
HARNESS_CONFIG = ROOT / ".codex" / "harness.toml"
STANDARD_PATH = ROOT / "docs" / "ai" / "standards" / "quality-supervisor-protocol.md"
CHECK_REGISTRY_PATH = ROOT / "docs" / "ai" / "check-registry.md"
INDEX_PATH = ROOT / "docs" / "ai" / "index.md"
AGENTS_PATH = ROOT / "AGENTS.md"
ALLOWED_SCOPES = {"material-task", "every-task"}


@dataclass(frozen=True)
class QualitySupervisorConfig:
    enabled: bool
    default_scope: str
    supervisor_role: str
    task_profiles: tuple[str, ...]
    skip_allowed_for: tuple[str, ...]


@dataclass(frozen=True)
class QualitySupervisorReport:
    enabled: bool
    status: str
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate bounded quality supervisor protocol wiring.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    text = read_text(path)
    if tomllib is None:
        return {}
    return tomllib.loads(text)


def string_tuple(raw_value: object, default: tuple[str, ...], label: str, errors: list[str]) -> tuple[str, ...]:
    if raw_value is None:
        return default
    if not isinstance(raw_value, list) or not all(isinstance(item, str) for item in raw_value):
        errors.append(f"quality_supervisor.{label} must be a list of strings")
        return default
    return tuple(item.strip() for item in raw_value if item.strip())


def string_value(raw_value: object, default: str, label: str, errors: list[str]) -> str:
    if raw_value is None:
        return default
    if not isinstance(raw_value, str) or not raw_value.strip():
        errors.append(f"quality_supervisor.{label} must be a non-empty string")
        return default
    return raw_value.strip()


def bool_value(raw_value: object, default: bool, label: str, errors: list[str]) -> bool:
    if raw_value is None:
        return default
    if not isinstance(raw_value, bool):
        errors.append(f"quality_supervisor.{label} must be a boolean")
        return default
    return raw_value


def load_config(errors: list[str]) -> QualitySupervisorConfig:
    data = load_toml(HARNESS_CONFIG)
    raw = data.get("quality_supervisor", {})
    if not isinstance(raw, dict):
        errors.append("[quality_supervisor] must be a TOML table")
        raw = {}

    config = QualitySupervisorConfig(
        enabled=bool_value(raw.get("enabled"), False, "enabled", errors),
        default_scope=string_value(raw.get("default_scope"), "material-task", "default_scope", errors),
        supervisor_role=string_value(raw.get("supervisor_role"), "quality-supervisor", "supervisor_role", errors),
        task_profiles=string_tuple(
            raw.get("task_profiles"),
            ("medium", "complex", "0-1 stage", "recovery/dispute"),
            "task_profiles",
            errors,
        ),
        skip_allowed_for=string_tuple(
            raw.get("skip_allowed_for"),
            ("direct-answer", "single-command", "explicit-user-opt-out", "tool-unavailable"),
            "skip_allowed_for",
            errors,
        ),
    )

    if config.default_scope not in ALLOWED_SCOPES:
        allowed = ", ".join(sorted(ALLOWED_SCOPES))
        errors.append(f"quality_supervisor.default_scope must be one of: {allowed}")
    if config.enabled and not config.task_profiles:
        errors.append("quality_supervisor.task_profiles must not be empty when enabled")
    if config.enabled and not config.skip_allowed_for:
        errors.append("quality_supervisor.skip_allowed_for must not be empty when enabled")
    return config


def require_tokens(path: Path, tokens: tuple[str, ...], errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"missing required quality supervisor document: {relative(path)}")
        return
    text = read_text(path).lower()
    for token in tokens:
        if token.lower() not in text:
            errors.append(f"{relative(path)} missing quality supervisor token: {token}")


def validate_enabled_documents(errors: list[str]) -> None:
    require_tokens(
        AGENTS_PATH,
        (
            "quality supervisor",
            "subagent",
            "main agent",
            "canonical",
        ),
        errors,
    )
    require_tokens(
        STANDARD_PATH,
        (
            "quality-supervisor-protocol/v1",
            "hooks cannot spawn subagents",
            "main agent owns canonical writes",
            "does not prove",
        ),
        errors,
    )
    require_tokens(
        CHECK_REGISTRY_PATH,
        (
            "check_quality_supervisor_protocol.py",
            "review-required",
        ),
        errors,
    )
    require_tokens(INDEX_PATH, ("quality supervisor",), errors)


def build_report() -> QualitySupervisorReport:
    errors: list[str] = []
    warnings: list[str] = []
    config = load_config(errors)

    if config.enabled:
        validate_enabled_documents(errors)
        status = "failed" if errors else "enabled"
    else:
        status = "disabled"
        warnings.append("quality supervisor protocol is configured but disabled; no subagent workflow is claimed")

    return QualitySupervisorReport(
        enabled=config.enabled,
        status=status,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


def main() -> int:
    args = parse_args()
    report = build_report()
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print("Quality supervisor protocol check")
        print(f"Status: {report.status}")
        for warning in report.warnings:
            print(f"WARN: {warning}")
        for error in report.errors:
            print(f"ERROR: {error}")
        if not report.errors:
            print("OK")
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
