from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from harness_config import ContextBudgetConfig

DEFAULT_SKILL_CATALOG_TOKEN_BUDGET = 2000
DEFAULT_RAW_SOURCE_TOKEN_BUDGET = 30000
DEFAULT_STATIC_PACKET_TOKEN_BUDGET = 32000


@dataclass(frozen=True)
class BudgetUsage:
    name: str
    used_tokens: int
    budget: int


def usage_percent(used: int, budget: int) -> float:
    return (used / budget) * 100 if budget else 0.0


def configured_budget(root: Path, key: str, default: int) -> int:
    text = _read_text(root / ".codex" / "harness.toml")
    match = re.search(rf"(?m)^\s*{re.escape(key)}\s*=\s*([0-9]+)\s*$", text)
    value = int(match.group(1)) if match else default
    return value if value > 0 else default


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _estimate_tokens(text: str) -> int:
    return max(1, round(len(text) / 4)) if text else 0


def _file_token_total(paths: list[Path]) -> int:
    return sum(_estimate_tokens(_read_text(path)) for path in paths if path.exists())


def _raw_source_paths(root: Path) -> list[Path]:
    roots = (
        root / "docs" / "requirements" / "source",
        root / "docs" / "requirements" / "source-raw",
    )
    paths: list[Path] = []
    for source_root in roots:
        if not source_root.exists():
            continue
        paths.extend(
            path
            for path in sorted(source_root.rglob("*"))
            if path.is_file() and not path.name.startswith(("_", ".")) and path.name != "README.md"
        )
    return paths


def budget_usages(root: Path) -> list[BudgetUsage]:
    skill_catalog_tokens = _file_token_total([root / ".codex" / "skills.catalog.json"])
    raw_source_tokens = _file_token_total(_raw_source_paths(root))
    static_packet_tokens = skill_catalog_tokens + raw_source_tokens
    return [
        BudgetUsage(
            name="skill catalog",
            used_tokens=skill_catalog_tokens,
            budget=configured_budget(
                root,
                "skill_catalog_token_budget",
                DEFAULT_SKILL_CATALOG_TOKEN_BUDGET,
            ),
        ),
        BudgetUsage(
            name="raw source",
            used_tokens=raw_source_tokens,
            budget=configured_budget(root, "raw_source_token_budget", DEFAULT_RAW_SOURCE_TOKEN_BUDGET),
        ),
        BudgetUsage(
            name="static task packet",
            used_tokens=static_packet_tokens,
            budget=configured_budget(
                root,
                "static_packet_token_budget",
                DEFAULT_STATIC_PACKET_TOKEN_BUDGET,
            ),
        ),
    ]


def default_surface_warning(default_tokens: int, config: ContextBudgetConfig) -> str | None:
    budget = config.default_surface_token_budget
    pct = usage_percent(default_tokens, budget)
    if default_tokens > budget:
        return f"Default context surface exceeds budget ({default_tokens} > {budget}, {pct:.1f}%)."
    if pct >= config.default_surface_high_warning_percent:
        return (
            "Default context surface reached high warning threshold "
            f"({default_tokens} / {budget}, {pct:.1f}% >= "
            f"{config.default_surface_high_warning_percent}%)."
        )
    if pct >= config.default_surface_warning_percent:
        return (
            "Default context surface reached warning threshold "
            f"({default_tokens} / {budget}, {pct:.1f}% >= "
            f"{config.default_surface_warning_percent}%)."
        )
    return None


def build_warnings(
    *,
    report_items: list[Any],
    skills: list[Any],
    duplicates: list[str],
    config: ContextBudgetConfig,
    active_handoff_count: int,
    active_handoff_budget: int,
    adr_count: int,
    mcp_count: int,
    budget_usages: list[Any] | None = None,
) -> list[str]:
    warnings: list[str] = []
    default_tokens = sum(item.estimated_tokens for item in report_items)
    if warning := default_surface_warning(default_tokens, config):
        warnings.append(warning)

    for item in report_items:
        if item.lines > config.always_on_doc_line_budget:
            warnings.append(
                f"Always-on document {item.path} is long "
                f"({item.lines} lines > {config.always_on_doc_line_budget})."
            )
        if item.path.startswith("docs/ai/status/") and item.lines >= config.stage_status_line_budget:
            warnings.append(
                f"Stage status {item.path} reached compression line budget "
                f"({item.lines} lines >= {config.stage_status_line_budget})."
            )

    if active_handoff_count >= active_handoff_budget:
        warnings.append(
            "Active handoffs reached the configured surface budget "
            f"({active_handoff_count} >= {active_handoff_budget})."
        )
    if adr_count >= config.adr_count_budget:
        warnings.append(f"ADR count reached budget ({adr_count} >= {config.adr_count_budget}).")
    if mcp_count > config.mcp_server_budget:
        warnings.append(
            f"MCP server count exceeds budget ({mcp_count} > {config.mcp_server_budget})."
        )

    for skill in skills:
        if skill.description_words > config.skill_description_word_budget:
            warnings.append(
                f"Skill description is long in {skill.path} "
                f"({skill.description_words} words > {config.skill_description_word_budget})."
            )
        if skill.lines > config.skill_body_line_budget:
            warnings.append(
                f"Skill body is long in {skill.path} "
                f"({skill.lines} lines > {config.skill_body_line_budget})."
            )

    if duplicates:
        warnings.append(
            "Duplicate instruction lines found across always-on docs or skills; "
            "consider moving repeated detail to an on-demand template or ADR."
        )
    warnings.extend(multi_budget_warnings(budget_usages or [], config))
    return warnings


def multi_budget_warnings(budget_usages: list[Any], config: ContextBudgetConfig) -> list[str]:
    warnings: list[str] = []
    for usage in budget_usages:
        pct = usage_percent(usage.used_tokens, usage.budget)
        label = usage.name.title()
        if usage.used_tokens > usage.budget:
            warnings.append(
                f"{label} exceeds budget "
                f"({usage.used_tokens} > {usage.budget}, {pct:.1f}%)."
            )
        elif pct >= config.default_surface_high_warning_percent:
            warnings.append(
                f"{label} reached high warning threshold "
                f"({usage.used_tokens} / {usage.budget}, {pct:.1f}% >= "
                f"{config.default_surface_high_warning_percent}%)."
            )
        elif pct >= config.default_surface_warning_percent:
            warnings.append(
                f"{label} reached warning threshold "
                f"({usage.used_tokens} / {usage.budget}, {pct:.1f}% >= "
                f"{config.default_surface_warning_percent}%)."
            )
    return warnings


def blocking_findings(report: Any) -> list[str]:
    failures: list[str] = []
    default_pct = usage_percent(report.default_surface_tokens, report.default_surface_budget)
    if report.default_surface_tokens > report.default_surface_budget:
        failures.append(
            "Default context surface exceeds hard budget "
            f"({report.default_surface_tokens} > {report.default_surface_budget}, "
            f"{default_pct:.1f}%). Compress active docs before continuing."
        )
    elif default_pct >= report.default_surface_high_warning_percent:
        failures.append(
            "Default context surface reached the compression trigger "
            f"({report.default_surface_tokens} / {report.default_surface_budget}, "
            f"{default_pct:.1f}% >= {report.default_surface_high_warning_percent}%)."
        )

    for item in report.default_surface:
        if item.path.startswith("docs/ai/status/"):
            if item.lines >= report.stage_status_line_budget:
                failures.append(
                    f"Stage status {item.path} reached compression line budget "
                    f"({item.lines} lines >= {report.stage_status_line_budget})."
                )
        elif item.lines > report.always_on_doc_line_budget:
            failures.append(
                f"Always-on document {item.path} exceeds line budget "
                f"({item.lines} lines > {report.always_on_doc_line_budget})."
            )
    for usage in getattr(report, "budget_usages", []):
        pct = usage_percent(usage.used_tokens, usage.budget)
        label = usage.name.title()
        if usage.used_tokens > usage.budget:
            failures.append(
                f"{label} exceeds hard budget "
                f"({usage.used_tokens} > {usage.budget}, {pct:.1f}%)."
            )
        elif pct >= report.default_surface_high_warning_percent:
            failures.append(
                f"{label} reached the compression trigger "
                f"({usage.used_tokens} / {usage.budget}, {pct:.1f}% >= "
                f"{report.default_surface_high_warning_percent}%)."
            )
    return failures


def strict_gate_failures(report: Any) -> list[str]:
    return blocking_findings(report)
