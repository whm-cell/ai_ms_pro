from __future__ import annotations

from typing import Any

from harness_config import ContextBudgetConfig


def usage_percent(used: int, budget: int) -> float:
    return (used / budget) * 100 if budget else 0.0


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
    return warnings
