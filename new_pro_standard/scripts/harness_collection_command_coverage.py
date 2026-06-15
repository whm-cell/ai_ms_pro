#!/usr/bin/env python3

from __future__ import annotations

import harness_pending_capture_focus as capture_focus
from harness_collection_command_templates import (
    CAPTURE_GATE_SUMMARY_LABELS,
    FOCUSED_CAPTURE_GATE_COMMAND_TEMPLATES,
    FOCUSED_REAL_AREA_COMMAND_TEMPLATES,
    FOCUSED_REAL_LEDGER_ACTION_COMMAND_TEMPLATES,
    FOCUSED_REAL_PRIORITY_COMMAND_TEMPLATES,
    FOCUSED_REAL_READINESS_COMMAND_TEMPLATES,
    LEDGER_ACTION_SUMMARY_LABELS,
    READINESS_SUMMARY_LABELS,
    REAL_SAMPLE_LEDGER_ACTIONS,
    WORKFLOW_AREA_PRIORITY_SECTION_TEMPLATES,
    WORKFLOW_CAPTURE_GATE_COMMAND_TEMPLATES,
    WORKFLOW_CAPTURE_GATE_SECTION_TEMPLATES,
    WORKFLOW_LEDGER_ACTION_SECTION_TEMPLATES,
    WORKFLOW_READINESS_SECTION_TEMPLATES,
    WORKFLOW_REAL_AREA_COMMAND_TEMPLATES,
    WORKFLOW_REAL_LEDGER_ACTION_COMMAND_TEMPLATES,
    WORKFLOW_REAL_PRIORITY_COMMAND_TEMPLATES,
    WORKFLOW_REAL_READINESS_COMMAND_TEMPLATES,
)


def focused_capture_gate_commands(capture_gate: str) -> tuple[str, ...]:
    return tuple(
        template.format(capture_gate=capture_gate)
        for template in FOCUSED_CAPTURE_GATE_COMMAND_TEMPLATES
    )


def focused_real_sample_ledger_action_commands(ledger_action: str) -> tuple[str, ...]:
    return tuple(
        template.format(ledger_action=ledger_action)
        for template in FOCUSED_REAL_LEDGER_ACTION_COMMAND_TEMPLATES
    )


def focused_real_sample_readiness_commands(readiness: str) -> tuple[str, ...]:
    return tuple(
        template.format(readiness=readiness)
        for template in FOCUSED_REAL_READINESS_COMMAND_TEMPLATES
    )


def focused_real_sample_area_commands(area: str) -> tuple[str, ...]:
    return tuple(
        template.format(area=area)
        for template in FOCUSED_REAL_AREA_COMMAND_TEMPLATES
    )


def focused_real_sample_priority_commands(priority: str) -> tuple[str, ...]:
    return tuple(
        template.format(priority=priority)
        for template in FOCUSED_REAL_PRIORITY_COMMAND_TEMPLATES
    )


def workflow_capture_gate_summary_commands(capture_gate: str) -> tuple[str, ...]:
    return tuple(
        template.format(capture_gate=capture_gate)
        for template in WORKFLOW_CAPTURE_GATE_COMMAND_TEMPLATES
    )


def workflow_real_sample_ledger_action_summary_commands(ledger_action: str) -> tuple[str, ...]:
    return tuple(
        template.format(ledger_action=ledger_action)
        for template in WORKFLOW_REAL_LEDGER_ACTION_COMMAND_TEMPLATES
    )


def workflow_real_sample_readiness_summary_commands(readiness: str) -> tuple[str, ...]:
    return tuple(
        template.format(readiness=readiness)
        for template in WORKFLOW_REAL_READINESS_COMMAND_TEMPLATES
    )


def workflow_real_sample_area_summary_commands(area: str) -> tuple[str, ...]:
    return tuple(
        template.format(area=area)
        for template in WORKFLOW_REAL_AREA_COMMAND_TEMPLATES
    )


def workflow_real_sample_priority_summary_commands(priority: str) -> tuple[str, ...]:
    return tuple(
        template.format(priority=priority)
        for template in WORKFLOW_REAL_PRIORITY_COMMAND_TEMPLATES
    )


def workflow_capture_gate_summary_sections(capture_gate: str) -> tuple[str, ...]:
    return workflow_summary_sections(
        capture_gate,
        CAPTURE_GATE_SUMMARY_LABELS,
        WORKFLOW_CAPTURE_GATE_SECTION_TEMPLATES,
    )


def workflow_real_sample_ledger_action_summary_sections(ledger_action: str) -> tuple[str, ...]:
    return workflow_summary_sections(
        ledger_action,
        LEDGER_ACTION_SUMMARY_LABELS,
        WORKFLOW_LEDGER_ACTION_SECTION_TEMPLATES,
    )


def workflow_real_sample_readiness_summary_sections(readiness: str) -> tuple[str, ...]:
    return workflow_summary_sections(
        readiness,
        READINESS_SUMMARY_LABELS,
        WORKFLOW_READINESS_SECTION_TEMPLATES,
    )


def workflow_real_sample_area_summary_sections(area: str) -> tuple[str, ...]:
    return workflow_summary_sections_from_label(
        label=f"area {area}",
        slug=f"area-{area}",
        templates=WORKFLOW_AREA_PRIORITY_SECTION_TEMPLATES,
    )


def workflow_real_sample_priority_summary_sections(priority: str) -> tuple[str, ...]:
    return workflow_summary_sections_from_label(
        label=f"priority {priority}",
        slug=f"priority-{priority.lower()}",
        templates=WORKFLOW_AREA_PRIORITY_SECTION_TEMPLATES,
    )


def workflow_summary_sections(
    value: str,
    labels: dict[str, tuple[str, str]],
    templates: tuple[tuple[str, str], ...],
) -> tuple[str, ...]:
    label, slug = labels[value]
    return workflow_summary_sections_from_label(label=label, slug=slug, templates=templates)


def workflow_summary_sections_from_label(
    label: str,
    slug: str,
    templates: tuple[tuple[str, str], ...],
) -> tuple[str, ...]:
    sections: list[str] = []
    for title_template, cat_template in templates:
        sections.append(title_template.format(label=label, slug=slug))
        sections.append(cat_template.format(label=label, slug=slug))
    return tuple(sections)


def pending_capture_focus_choice_errors(report: object) -> tuple[str, ...]:
    checks = (
        ("CAPTURE_FOCUS_AREAS", "area", real_sample_area_values(report), capture_focus.CAPTURE_FOCUS_AREAS),
        (
            "CAPTURE_FOCUS_PRIORITIES",
            "priority",
            real_sample_priority_values(report),
            capture_focus.CAPTURE_FOCUS_PRIORITIES,
        ),
        (
            "CAPTURE_FOCUS_LEDGER_ACTIONS",
            "ledger action",
            real_sample_ledger_action_values(report),
            capture_focus.CAPTURE_FOCUS_LEDGER_ACTIONS,
        ),
        (
            "CAPTURE_FOCUS_CAPTURE_GATES",
            "capture gate",
            real_sample_capture_gate_values(report),
            capture_focus.CAPTURE_FOCUS_CAPTURE_GATES,
        ),
        (
            "CAPTURE_FOCUS_READINESS_STATES",
            "readiness",
            real_sample_readiness_values(report),
            capture_focus.CAPTURE_FOCUS_READINESS_STATES,
        ),
    )
    errors: list[str] = []
    for constant_name, value_label, active_values, choices in checks:
        for value in sorted(set(active_values) - set(choices)):
            errors.append(f"{constant_name}: active real-sample {value_label} missing from choices: {value}")
    return tuple(errors)


def real_sample_capture_gate_values(report: object) -> tuple[str, ...]:
    return real_sample_item_values(report, "capture_gate")


def real_sample_area_values(report: object) -> tuple[str, ...]:
    return real_sample_item_values(report, "area")


def real_sample_priority_values(report: object) -> tuple[str, ...]:
    return real_sample_item_values(report, "priority")


def real_sample_ledger_action_values(report: object) -> tuple[str, ...]:
    return real_sample_item_values(report, "ledger_action")


def real_sample_readiness_values(report: object) -> tuple[str, ...]:
    return real_sample_item_values(report, "readiness")


def real_sample_item_values(report: object, attribute: str) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                getattr(item, attribute)
                for item in report.items
                if item.ledger_action in REAL_SAMPLE_LEDGER_ACTIONS
            }
        )
    )
