#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOTS = (".agents/skills", ".codex/skills")
CODEX_DISCOVERABLE_ROOT = ".agents/skills"


@dataclass(frozen=True)
class SkillReport:
    name: str
    repo_path: str
    codex_discoverable: bool
    global_path: str | None
    install_status: str
    has_description: bool
    has_agent_metadata: bool
    implicit_invocation: str
    errors: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List repo-local skills and compare them with CODEX_HOME skills.",
    )
    parser.add_argument(
        "--root",
        default=str(ROOT),
        help="Repository root to scan. Defaults to the current harness repository.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".codex"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def skill_docs(roots: tuple[Path, ...]) -> list[Path]:
    docs: list[Path] = []
    for root in roots:
        if root.exists():
            docs.extend(sorted(root.glob("*/SKILL.md")))
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


def skill_name(path: Path) -> str:
    try:
        metadata = frontmatter(read_text(path))
    except OSError:
        return path.parent.name
    return metadata.get("name") or path.parent.name


def global_skill_index(global_root: Path) -> dict[str, Path]:
    return {skill_name(path): path for path in skill_docs((global_root,))}


def is_codex_discoverable(path: Path, root: Path) -> bool:
    return relative(path, root).startswith(f"{CODEX_DISCOVERABLE_ROOT}/")


def implicit_invocation(path: Path) -> str:
    metadata_path = path.parent / "agents" / "openai.yaml"
    if not metadata_path.exists():
        return "unknown"
    text = read_text(metadata_path)
    match = re.search(
        r"(?ms)^policy:\s*(?:\n\s+[^\n]+)*\n\s+allow_implicit_invocation:\s*(\S+)\s*$",
        text,
    )
    return match.group(1).strip().lower() if match else "unknown"


def build_report(path: Path, global_skills: dict[str, Path], root: Path) -> SkillReport:
    errors: list[str] = []
    text = read_text(path)
    metadata = frontmatter(text)
    name = metadata.get("name") or path.parent.name
    description = metadata.get("description", "").strip()
    if not metadata:
        errors.append("missing YAML frontmatter")
    if "name" not in metadata:
        errors.append("missing frontmatter name")
    if not description:
        errors.append("missing frontmatter description")
    codex_discoverable = is_codex_discoverable(path, root)
    metadata_path = path.parent / "agents" / "openai.yaml"
    implicit = implicit_invocation(path)
    if not codex_discoverable:
        errors.append("skill is not under .agents/skills, so Codex may not discover it natively")
    if not metadata_path.exists():
        errors.append("missing agents/openai.yaml")
    elif implicit == "unknown":
        errors.append("agents/openai.yaml missing policy.allow_implicit_invocation")

    global_path = global_skills.get(name)
    install_status = "globally installed" if global_path else "repo-local only"
    return SkillReport(
        name=name,
        repo_path=relative(path, root),
        codex_discoverable=codex_discoverable,
        global_path=global_path.as_posix() if global_path else None,
        install_status=install_status,
        has_description=bool(description),
        has_agent_metadata=metadata_path.exists(),
        implicit_invocation=implicit,
        errors=errors,
    )


def emit_text(reports: list[SkillReport], code_home: Path, root: Path) -> None:
    print("Repo-local skill discoverability:")
    print(f"- Repo root: {root}")
    print(f"- CODEX_HOME: {code_home}")
    print(f"- Global skills root: {code_home / 'skills'}")
    if not reports:
        print("- No repo-local skills found.")
        return

    for report in reports:
        print(
            f"- {report.name}: {report.install_status}; "
            f"repo={report.repo_path}; "
            f"codex_discoverable={str(report.codex_discoverable).lower()}; "
            f"global={report.global_path or '-'}; "
            f"agent_metadata={str(report.has_agent_metadata).lower()}; "
            f"implicit={report.implicit_invocation}"
        )
        for error in report.errors:
            print(f"  ERROR: {error}")


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    code_home = codex_home()
    global_skills = global_skill_index(code_home / "skills")
    repo_roots = tuple(root / rel_path for rel_path in SKILL_ROOTS)
    reports = [build_report(path, global_skills, root) for path in skill_docs(repo_roots)]
    errors = [error for report in reports for error in report.errors]

    if args.json:
        print(
            json.dumps(
                {
                    "codex_home": code_home.as_posix(),
                    "global_skills_root": (code_home / "skills").as_posix(),
                    "repo_root": root.as_posix(),
                    "reports": [asdict(report) for report in reports],
                    "ok": not errors,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        emit_text(reports, code_home, root)

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
