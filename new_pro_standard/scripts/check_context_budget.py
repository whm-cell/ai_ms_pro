#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from context_budget_warnings import build_warnings, usage_percent
from harness_config import ContextBudgetConfig, HarnessConfigError, load_harness_config


ROOT = Path(__file__).resolve().parents[1]
AI_DOC_ROOT = ROOT / "docs" / "ai"
DEFAULT_SURFACE = (
    "AGENTS.md",
    "docs/ai/index.md",
    "docs/ai/working-context.md",
)


@dataclass(frozen=True)
class SurfaceItem:
    path: str
    lines: int
    estimated_tokens: int


@dataclass(frozen=True)
class SkillItem:
    path: str
    lines: int
    description_words: int


@dataclass(frozen=True)
class ContextBudgetReport:
    default_surface_tokens: int
    default_surface_budget: int
    default_surface_warning_percent: int
    default_surface_high_warning_percent: int
    default_surface: list[SurfaceItem]
    active_handoff_count: int
    active_handoff_budget: int
    adr_count: int
    adr_budget: int
    stage_status_line_budget: int
    skill_count: int
    mcp_server_count: int
    mcp_server_budget: int
    warnings: list[str]
    duplicate_instructions: list[str]
    skills: list[SkillItem]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit default context surface size and on-demand harness budget.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
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


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def estimate_tokens(text: str) -> int:
    # Cheap model-agnostic estimate; good enough for budget trend detection.
    return max(1, round(len(text) / 4)) if text else 0


def extract_active_status(root: Path) -> Path | None:
    text = read_text(root / "docs" / "ai" / "working-context.md")
    match = re.search(r"^- Active Status Source:\s*(.+?)\s*$", text, re.MULTILINE)
    if match:
        candidate = root / match.group(1).strip()
        if candidate.exists():
            return candidate
    status_docs = iter_docs(root / "docs" / "ai" / "status")
    return max(status_docs, key=lambda path: path.stat().st_mtime) if status_docs else None


def default_surface_paths(root: Path) -> list[Path]:
    items = [root / path for path in DEFAULT_SURFACE]
    if status_path := extract_active_status(root):
        items.append(status_path)

    seen: set[Path] = set()
    unique: list[Path] = []
    for path in items:
        resolved = path.resolve()
        if resolved not in seen and path.exists():
            seen.add(resolved)
            unique.append(path)
    return unique


def scan_default_surface(root: Path) -> list[SurfaceItem]:
    items: list[SurfaceItem] = []
    for path in default_surface_paths(root):
        text = read_text(path)
        items.append(
            SurfaceItem(
                path=relative(path, root),
                lines=len(text.splitlines()) if text else 0,
                estimated_tokens=estimate_tokens(text),
            )
        )
    return items


def skill_paths(root: Path) -> list[Path]:
    roots = [root / ".codex" / "skills", root / ".agents" / "skills"]
    paths: list[Path] = []
    for skill_root in roots:
        if skill_root.exists():
            paths.extend(sorted(skill_root.glob("*/SKILL.md")))
    return paths


def extract_skill_description(text: str) -> str:
    match = re.match(r"(?s)^---\n(.*?)\n---", text)
    if not match:
        return ""
    frontmatter = match.group(1)
    description_match = re.search(r"(?m)^description:\s*(.+?)\s*$", frontmatter)
    return description_match.group(1).strip().strip("\"'") if description_match else ""


def scan_skills(root: Path) -> list[SkillItem]:
    items: list[SkillItem] = []
    for path in skill_paths(root):
        text = read_text(path)
        items.append(
            SkillItem(
                path=relative(path, root),
                lines=len(text.splitlines()) if text else 0,
                description_words=len(re.findall(r"[\w-]+", extract_skill_description(text))),
            )
        )
    return items


def normalized_instruction(line: str) -> str | None:
    stripped = line.strip()
    if not re.match(r"^(-|\*|\d+\.)\s+", stripped):
        return None
    normalized = re.sub(r"\[[^\]]+\]\([^)]+\)", "LINK", stripped)
    normalized = re.sub(r"`[^`]+`", "CODE", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip().lower()
    return normalized if len(normalized) >= 50 else None


def duplicate_instructions(root: Path, limit: int = 8) -> list[str]:
    paths = default_surface_paths(root)
    paths.extend(skill_paths(root))
    occurrences: dict[str, set[str]] = {}
    originals: dict[str, str] = {}
    for path in paths:
        for line in read_text(path).splitlines():
            if normalized := normalized_instruction(line):
                occurrences.setdefault(normalized, set()).add(relative(path, root))
                originals.setdefault(normalized, line.strip())
    duplicates = [
        f"{originals[text]} ({', '.join(sorted(paths))})"
        for text, paths in occurrences.items()
        if len(paths) > 1
    ]
    duplicates.sort()
    return duplicates[:limit]


def mcp_server_count(root: Path) -> int:
    total = 0
    for rel_path in (".mcp.json", ".codex/mcp.json", "mcp.json"):
        path = root / rel_path
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        servers = data.get("mcpServers")
        if isinstance(servers, dict):
            total += len(servers)
    return total


def build_report(root: Path = ROOT) -> ContextBudgetReport:
    harness_config = load_harness_config(root)
    context_budget = harness_config.context_budget
    context_surface = harness_config.context_surface
    default_items = scan_default_surface(root)
    skills = scan_skills(root)
    duplicates = duplicate_instructions(root)
    active_handoff_count = len(iter_docs(root / "docs" / "ai" / "handoffs" / "active"))
    adr_count = len(iter_docs(root / "docs" / "ai" / "adr"))
    mcp_count = mcp_server_count(root)
    warnings = build_warnings(
        report_items=default_items,
        skills=skills,
        duplicates=duplicates,
        config=context_budget,
        active_handoff_count=active_handoff_count,
        active_handoff_budget=context_surface.active_handoff_budget,
        adr_count=adr_count,
        mcp_count=mcp_count,
    )
    return ContextBudgetReport(
        default_surface_tokens=sum(item.estimated_tokens for item in default_items),
        default_surface_budget=context_budget.default_surface_token_budget,
        default_surface_warning_percent=context_budget.default_surface_warning_percent,
        default_surface_high_warning_percent=context_budget.default_surface_high_warning_percent,
        default_surface=default_items,
        active_handoff_count=active_handoff_count,
        active_handoff_budget=context_surface.active_handoff_budget,
        adr_count=adr_count,
        adr_budget=context_budget.adr_count_budget,
        stage_status_line_budget=context_budget.stage_status_line_budget,
        skill_count=len(skills),
        mcp_server_count=mcp_count,
        mcp_server_budget=context_budget.mcp_server_budget,
        warnings=warnings,
        duplicate_instructions=duplicates,
        skills=skills,
    )


def render_report(report: ContextBudgetReport) -> str:
    lines = [
        "Context budget audit:",
        "- default surface: "
        f"{report.default_surface_tokens} estimated tokens / budget "
        f"{report.default_surface_budget} "
        f"({usage_percent(report.default_surface_tokens, report.default_surface_budget):.1f}%)",
        "- default warning thresholds: "
        f"{report.default_surface_warning_percent}% / "
        f"{report.default_surface_high_warning_percent}%",
        f"- active handoffs: {report.active_handoff_count} / budget {report.active_handoff_budget}",
        f"- ADR count: {report.adr_count} / budget {report.adr_budget}",
        f"- stage status line budget: {report.stage_status_line_budget}",
        f"- skills: {report.skill_count}",
        f"- MCP servers: {report.mcp_server_count} / budget {report.mcp_server_budget}",
        "",
        "Default surface:",
    ]
    for item in report.default_surface:
        lines.append(f"- {item.path}: {item.lines} lines, ~{item.estimated_tokens} tokens")

    if report.warnings:
        lines.extend(["", "Warnings:"])
        lines.extend(f"- {warning}" for warning in report.warnings)
    else:
        lines.extend(["", "Warnings: none"])

    if report.duplicate_instructions:
        lines.extend(["", "Duplicate instruction samples:"])
        lines.extend(f"- {item}" for item in report.duplicate_instructions)
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    try:
        report = build_report()
    except HarnessConfigError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print(render_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
