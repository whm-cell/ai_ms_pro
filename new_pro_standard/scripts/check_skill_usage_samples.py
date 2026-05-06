#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOTS = (ROOT / ".agents" / "skills", ROOT / ".codex" / "skills")
SAMPLE_REGISTRY = ROOT / "docs" / "ai" / "skill-usage-samples.md"
OBSERVED_SKILLS = ("team-pr-conflict-control",)
REQUIRED_EVAL_FIELDS = (
    "baseline_without_skill",
    "run_with_skill",
    "delta",
    "acceptance",
    "verification",
)


@dataclass(frozen=True)
class CandidateSkillReport:
    name: str
    tracking_scope: str
    path: str
    accepted_real_task_samples: int
    accepted_complete_eval_samples: int
    rejected_real_task_samples: int
    pending_real_task_samples: int
    evidence_status: str


@dataclass(frozen=True)
class UsageSampleReport:
    registry_path: str
    min_samples: int
    candidate_skills: list[CandidateSkillReport]
    required_eval_fields: list[str]
    warnings: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check real-task evidence for candidate repo-local skills.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--strict", action="store_true", help="Treat missing samples as failure.")
    parser.add_argument("--min-samples", type=int, default=2, help="Accepted samples needed per skill.")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def skill_docs() -> list[Path]:
    docs: list[Path] = []
    seen_names: set[str] = set()
    for root in SKILL_ROOTS:
        if root.exists():
            for path in sorted(root.glob("*/SKILL.md")):
                if path.parent.name in seen_names:
                    continue
                seen_names.add(path.parent.name)
                docs.append(path)
    return docs


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    metadata: dict[str, str] = {}
    for raw_line in parts[1].splitlines():
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        metadata[key.strip()] = value.strip().strip("'\"")
    return metadata


def current_status(text: str) -> str:
    match = re.search(r"(?ms)^## Current Status\s+(.+?)(?:\n## |\Z)", text)
    if not match:
        return ""
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def candidate_skills() -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in skill_docs():
        text = read_text(path)
        metadata = frontmatter(text)
        name = metadata.get("name") or path.parent.name
        if current_status(text).lower() == "candidate":
            result[name] = path
    return result


def observed_skills() -> dict[str, Path]:
    result: dict[str, Path] = {}
    for name in OBSERVED_SKILLS:
        for root in SKILL_ROOTS:
            path = root / name / "SKILL.md"
            if path.exists():
                result[name] = path
                break
    return result


def sample_blocks(registry_text: str) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    for line in registry_text.splitlines():
        if line.startswith("### "):
            if current:
                blocks.append("\n".join(current))
            current = [line]
            continue
        if current:
            current.append(line)
    if current:
        blocks.append("\n".join(current))
    return blocks


def metadata_value(block: str, key: str) -> str:
    pattern = re.compile(rf"(?mi)^-\s*{re.escape(key)}\s*[:：]\s*(.+?)\s*$")
    match = pattern.search(block)
    return match.group(1).strip() if match else ""


def sample_title(block: str) -> str:
    lines = block.splitlines()
    if not lines:
        return "unknown sample"
    return lines[0].removeprefix("### ").strip()


def block_metadata(block: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    pattern = re.compile(r"(?m)^-\s*([^:：]+?)\s*[:：]\s*(.*?)\s*$")
    for match in pattern.finditer(block):
        key = match.group(1).strip().lower().replace(" ", "_").replace("-", "_")
        metadata[key] = match.group(2).strip()
    return metadata


def missing_eval_fields(block: str) -> list[str]:
    metadata = block_metadata(block)
    return [field for field in REQUIRED_EVAL_FIELDS if not metadata.get(field)]


def accepted_sample_counts(
    skill_names: set[str],
) -> tuple[dict[str, int], dict[str, int], dict[str, int], dict[str, int], list[str]]:
    counts = {name: 0 for name in skill_names}
    complete_counts = {name: 0 for name in skill_names}
    rejected_counts = {name: 0 for name in skill_names}
    pending_counts = {name: 0 for name in skill_names}
    warnings: list[str] = []
    if not SAMPLE_REGISTRY.exists():
        return counts, complete_counts, rejected_counts, pending_counts, warnings
    for block in sample_blocks(read_text(SAMPLE_REGISTRY)):
        outcome = metadata_value(block, "Outcome").strip().lower()
        evidence_type = metadata_value(block, "Evidence Type").strip().lower()
        skills = metadata_value(block, "Skills")
        if evidence_type not in {"real-task", "真实任务"}:
            continue
        missing_fields = missing_eval_fields(block)
        for name in skill_names:
            if name not in skills:
                continue
            if outcome in {"accepted", "已采纳"}:
                counts[name] += 1
                if missing_fields:
                    warnings.append(
                        f"Accepted sample {sample_title(block)} for {name} is missing "
                        f"eval fields: {', '.join(missing_fields)}."
                    )
                else:
                    complete_counts[name] += 1
            elif outcome in {"rejected", "已拒绝"}:
                rejected_counts[name] += 1
            elif outcome in {"pending", "待定"}:
                pending_counts[name] += 1
    return counts, complete_counts, rejected_counts, pending_counts, warnings


def build_report(min_samples: int) -> UsageSampleReport:
    candidates = candidate_skills()
    observed = {name: path for name, path in observed_skills().items() if name not in candidates}
    tracked = {**candidates, **observed}
    counts, complete_counts, rejected_counts, pending_counts, sample_warnings = accepted_sample_counts(set(tracked))
    warnings: list[str] = []
    if not SAMPLE_REGISTRY.exists():
        warnings.append(f"sample registry missing: {relative(SAMPLE_REGISTRY)}")
    warnings.extend(sample_warnings)

    reports: list[CandidateSkillReport] = []
    for name, path in sorted(tracked.items()):
        scope = "candidate" if name in candidates else "observed"
        count = counts.get(name, 0)
        complete_count = complete_counts.get(name, 0)
        rejected_count = rejected_counts.get(name, 0)
        pending_count = pending_counts.get(name, 0)
        status = "enough evidence" if complete_count >= min_samples else "needs samples"
        if complete_count < min_samples:
            warnings.append(
                f"{scope.title()} skill {name} has {complete_count}/{min_samples} "
                "accepted real-task eval samples with required contrast fields."
            )
        reports.append(
            CandidateSkillReport(
                name=name,
                tracking_scope=scope,
                path=relative(path),
                accepted_real_task_samples=count,
                accepted_complete_eval_samples=complete_count,
                rejected_real_task_samples=rejected_count,
                pending_real_task_samples=pending_count,
                evidence_status=status,
            )
        )

    return UsageSampleReport(
        registry_path=relative(SAMPLE_REGISTRY),
        min_samples=min_samples,
        candidate_skills=reports,
        required_eval_fields=list(REQUIRED_EVAL_FIELDS),
        warnings=warnings,
    )


def emit_text(report: UsageSampleReport) -> None:
    print("Candidate skill usage sample check:")
    print(f"- registry: {report.registry_path}")
    print(f"- min accepted real-task eval samples: {report.min_samples}")
    print(f"- required eval fields: {', '.join(report.required_eval_fields)}")
    for item in report.candidate_skills:
        print(
            f"- {item.name} ({item.tracking_scope}): "
            f"{item.accepted_complete_eval_samples}/{report.min_samples} complete eval samples; "
            f"accepted={item.accepted_real_task_samples}; rejected={item.rejected_real_task_samples}; "
            f"pending={item.pending_real_task_samples}; {item.evidence_status}; path={item.path}"
        )
    for warning in report.warnings:
        print(f"WARN: {warning}")


def main() -> int:
    args = parse_args()
    report = build_report(args.min_samples)
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        emit_text(report)
    return 1 if args.strict and report.warnings else 0


if __name__ == "__main__":
    sys.exit(main())
