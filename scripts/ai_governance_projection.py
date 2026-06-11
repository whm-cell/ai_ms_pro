from __future__ import annotations

from pathlib import Path

from ai_governance_metadata import (
    AI_DOC_ROOT,
    REQ_DOC_ROOT,
    ROOT,
    WORKING_CONTEXT_PATH,
    latest_doc,
    load_text,
)
from ai_governance_traceability import iter_docs


PLAN_PATH = AI_DOC_ROOT / "plan.md"
WORKSTREAM_DIR = REQ_DOC_ROOT / "workstreams"
TRACEABILITY_MATRIX_PATH = REQ_DOC_ROOT / "traceability-matrix.md"
PLAN_STATE_LABELS = (
    "项目状态：",
    "当前状态：",
    "验证状态：",
    "完成度：",
    "最新验证：",
    "验收证据：",
)
WORKSTREAM_STATE_LABELS = (
    "状态：",
    "当前状态：",
    "验证状态：",
    "完成度：",
    "最新验证：",
    "验收证据：",
)


def find_projection_state_labels(path: Path, labels: tuple[str, ...]) -> list[str]:
    if not path.exists():
        return []

    matches: list[str] = []
    for raw_line in load_text(path).splitlines():
        stripped = raw_line.strip()
        if stripped.startswith(("- ", "* ")):
            stripped = stripped[2:].strip()
        for label in labels:
            if stripped.startswith(label):
                matches.append(label)
                break
    return matches


def projection_freshness_errors(
    *,
    active_handoffs: list[Path],
    status_docs: list[Path],
) -> list[str]:
    errors: list[str] = []

    plan_state_labels = find_projection_state_labels(PLAN_PATH, PLAN_STATE_LABELS)
    plan_truth_sources = [
        path
        for path in [WORKING_CONTEXT_PATH, *active_handoffs, *status_docs]
        if path.exists()
    ]
    plan_truth_target = latest_doc(plan_truth_sources)
    if (
        plan_state_labels
        and PLAN_PATH.exists()
        and plan_truth_target is not None
        and plan_truth_target.stat().st_mtime > PLAN_PATH.stat().st_mtime
    ):
        labels = ", ".join(sorted(set(plan_state_labels)))
        errors.append(
            "docs/ai/plan.md still carries explicit current-state fields "
            f"({labels}) but is older than the latest primary truth document "
            f"{plan_truth_target.relative_to(ROOT)}. Remove those fields or sync them in the same change."
        )

    if TRACEABILITY_MATRIX_PATH.exists():
        traceability_mtime = TRACEABILITY_MATRIX_PATH.stat().st_mtime
        for workstream_path in iter_docs(WORKSTREAM_DIR):
            workstream_state_labels = find_projection_state_labels(
                workstream_path,
                WORKSTREAM_STATE_LABELS,
            )
            if not workstream_state_labels:
                continue
            if traceability_mtime <= workstream_path.stat().st_mtime:
                continue
            labels = ", ".join(sorted(set(workstream_state_labels)))
            errors.append(
                f"{workstream_path.relative_to(ROOT)} still carries explicit current-state fields "
                f"({labels}) but is older than docs/requirements/traceability-matrix.md. "
                "Remove those fields or sync them in the same change."
            )

    return errors
