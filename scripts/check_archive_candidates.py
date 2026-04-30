#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AI_DOC_ROOT = ROOT / "docs" / "ai"
ACTIVE_HANDOFF_DIR = AI_DOC_ROOT / "handoffs" / "active"
STATUS_DIR = AI_DOC_ROOT / "status"
ADR_DIR = AI_DOC_ROOT / "adr"
CHANGELOG_DIR = AI_DOC_ROOT / "changelog"
WORKING_CONTEXT_PATH = AI_DOC_ROOT / "working-context.md"
DEFAULT_ACTIVE_HANDOFF_BUDGET = 5
COMPLETED_VALUES = {"已完成", "完成", "done", "completed"}


@dataclass(frozen=True)
class ArchiveCandidate:
    path: str
    status: str
    score: int
    reasons: list[str]
    cautions: list[str]


@dataclass(frozen=True)
class ArchiveReport:
    active_handoff_count: int
    budget: int
    candidates: list[ArchiveCandidate]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List active handoffs that look ready for manual archive review.",
    )
    parser.add_argument(
        "--budget",
        type=int,
        default=DEFAULT_ACTIVE_HANDOFF_BUDGET,
        help=f"Active handoff budget. Default: {DEFAULT_ACTIVE_HANDOFF_BUDGET}.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON.",
    )
    return parser.parse_args()


def iter_docs(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return [
        path
        for path in sorted(directory.glob("*.md"))
        if not path.name.startswith("_") and path.name != "README.md"
    ]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def extract_field(text: str, field_name: str) -> str:
    pattern = re.compile(rf"^\s*{re.escape(field_name)}\s*[:：]\s*(.+?)\s*$", re.MULTILINE)
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def extract_title(text: str) -> str:
    match = re.search(r"^#\s+(.+?)\s*$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def section_body(text: str, heading: str) -> str:
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*$\n(.*?)(?=^##\s+|\Z)",
        flags=re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def has_non_empty_bullets(section_text: str) -> bool:
    for line in section_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") and stripped not in {"- 无", "- 无。", "- N/A"}:
            return True
    return False


def load_bound_active_handoffs(root: Path) -> set[str]:
    text = read_text(root / "docs" / "ai" / "working-context.md")
    results: set[str] = set()
    in_list = False
    for line in text.splitlines():
        if line.strip().startswith("- Active Handoff Sources:"):
            in_list = True
            continue
        if not in_list:
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            results.add(stripped[2:].strip())
            continue
        if stripped and not line.startswith("  "):
            break
    return results


def compression_corpus(root: Path) -> str:
    paths = [*iter_docs(root / "docs" / "ai" / "status")]
    paths.extend(iter_docs(root / "docs" / "ai" / "adr"))
    paths.extend(iter_docs(root / "docs" / "ai" / "changelog"))
    return "\n".join(read_text(path) for path in paths).lower()


def latest_status_mtime(root: Path) -> float | None:
    status_docs = iter_docs(root / "docs" / "ai" / "status")
    if not status_docs:
        return None
    return max(path.stat().st_mtime for path in status_docs)


def mention_terms(path: Path, text: str) -> list[str]:
    title = extract_title(text)
    task = extract_field(text, "任务")
    terms = [
        path.name,
        path.stem,
        path.stem.replace("-", " "),
        title,
        task,
        task.replace("-", " ") if task else "",
    ]
    return [term.lower() for term in terms if len(term.strip()) >= 4]


def is_completed(status: str) -> bool:
    return status.strip().lower() in COMPLETED_VALUES


def relative_to_root(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def score_handoff(
    path: Path,
    *,
    root: Path,
    active_count: int,
    budget: int,
    bound_handoffs: set[str],
    corpus: str,
    status_mtime: float | None,
) -> ArchiveCandidate | None:
    text = read_text(path)
    status = extract_field(text, "状态") or "未知"
    reasons: list[str] = []
    cautions: list[str] = []
    score = 0
    repo_relative = relative_to_root(path, root)
    completed = is_completed(status)
    bound = repo_relative in bound_handoffs

    if completed:
        score += 3
        reasons.append("handoff 状态为已完成")
    if not bound:
        score += 2
        reasons.append("working-context 未把它列为默认接力入口")
    if any(term in corpus for term in mention_terms(path, text)):
        score += 2
        reasons.append("status / ADR / changelog 中已出现该任务线索")
    if status_mtime is not None and path.stat().st_mtime < status_mtime:
        score += 1
        reasons.append("更新时间早于最新 stage status，可能已被阶段摘要吸收")
    if active_count >= budget and completed:
        score += 1
        reasons.append(f"active handoff 数量已达到预算 {budget}")

    pending = section_body(text, "当前未完成项")
    if has_non_empty_bullets(pending):
        cautions.append("仍写有未完成项，归档前需确认这些内容已进入 status/backlog")

    next_step = section_body(text, "下一位 Agent 的第一步动作")
    if has_non_empty_bullets(next_step):
        cautions.append("仍写有下一步动作，归档前需确认它不再是默认恢复入口")

    eligible_for_review = completed or not bound or active_count > budget
    if not eligible_for_review or score < 3:
        return None

    return ArchiveCandidate(
        path=repo_relative,
        status=status,
        score=score,
        reasons=reasons,
        cautions=cautions,
    )


def build_report(root: Path = ROOT, budget: int = DEFAULT_ACTIVE_HANDOFF_BUDGET) -> ArchiveReport:
    active_handoffs = iter_docs(root / "docs" / "ai" / "handoffs" / "active")
    bound_handoffs = load_bound_active_handoffs(root)
    corpus = compression_corpus(root)
    status_mtime = latest_status_mtime(root)

    candidates = [
        candidate
        for path in active_handoffs
        if (
            candidate := score_handoff(
                path,
                root=root,
                active_count=len(active_handoffs),
                budget=budget,
                bound_handoffs=bound_handoffs,
                corpus=corpus,
                status_mtime=status_mtime,
            )
        )
        is not None
    ]
    candidates.sort(key=lambda item: (-item.score, item.path))
    return ArchiveReport(
        active_handoff_count=len(active_handoffs),
        budget=budget,
        candidates=candidates,
    )


def render_text(report: ArchiveReport) -> str:
    lines = [
        "Archive candidate monitor: OK",
        f"Active handoffs: {report.active_handoff_count} (budget {report.budget})",
    ]
    if not report.candidates:
        lines.append("No archive candidates found by heuristic scan.")
        return "\n".join(lines)

    lines.append("Archive review candidates:")
    for candidate in report.candidates:
        lines.append(f"- {candidate.path}")
        lines.append(f"  status: {candidate.status}; score: {candidate.score}")
        for reason in candidate.reasons:
            lines.append(f"  reason: {reason}")
        for caution in candidate.cautions:
            lines.append(f"  caution: {caution}")
    lines.append("Manual review required: this script never moves files or edits index/status docs.")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    report = build_report(budget=args.budget)
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print(render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
