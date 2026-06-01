from __future__ import annotations

import re
from pathlib import Path

from ai_governance_metadata import ROOT, load_text


REVIEW_HEADINGS = (
    "## Next Best Work Review",
    "## 下一步选择判断",
)
COMPLETION_STATUS_RE = re.compile(r"^状态[:：]\s*(完成|已完成|阶段完成)\s*$", re.MULTILINE)
DECISION_SIGNAL_RE = re.compile(
    r"(^|\b)(pivot|re-scope|rescope|scope-change|scope change|park|cancel|ask-user)(\b|$)"
    r"|转向|重排|调整范围|取消计划|搁置|改做|计划不合适",
    re.IGNORECASE,
)


def has_next_best_work_review(text: str) -> bool:
    return any(heading in text for heading in REVIEW_HEADINGS)


def needs_next_best_work_review(text: str) -> bool:
    return bool(COMPLETION_STATUS_RE.search(text) or DECISION_SIGNAL_RE.search(text))


def next_best_work_review_warnings(paths: list[Path]) -> list[str]:
    warnings: list[str] = []
    for path in paths:
        text = load_text(path)
        if not needs_next_best_work_review(text):
            continue
        if has_next_best_work_review(text):
            continue
        try:
            rendered = path.relative_to(ROOT)
        except ValueError:
            rendered = path
        warnings.append(
            f"{rendered} appears complete or scope-changing but has no Next Best Work Review section."
        )
    return warnings
