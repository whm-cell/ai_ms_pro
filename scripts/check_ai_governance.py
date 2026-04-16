#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AI_DOC_ROOT = ROOT / "docs" / "ai"
REQ_DOC_ROOT = ROOT / "docs" / "requirements"
CHECKS = [
    ("structure", ROOT / "scripts" / "check_ai_docs.py"),
    ("quality", ROOT / "scripts" / "check_ai_doc_quality.py"),
]
DOC_ROOTS = (AI_DOC_ROOT, REQ_DOC_ROOT)


def main() -> int:
    failures = []
    warnings = []

    changed_paths = load_changed_paths()
    if changed_paths:
        docs_changed = any(is_under_root(path, DOC_ROOTS) for path in changed_paths)
        non_docs_changed = any(not is_under_root(path, DOC_ROOTS) for path in changed_paths)
        if non_docs_changed and not docs_changed:
            warnings.append(
                "Implementation changes detected outside docs/ai and docs/requirements, "
                "but no docs updates were found."
            )

    for label, script in CHECKS:
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            failures.append((label, result.stdout.strip(), result.stderr.strip()))

    if failures:
        print("AI governance checks: FAILED")
        for label, stdout, stderr in failures:
            print(f"[{label}]")
            if stdout:
                print(stdout)
            if stderr:
                print(stderr)
        return 1

    print("AI governance checks: OK")
    for message in warnings:
        print(f"WARN: {message}")
    return 0


def load_changed_paths() -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain=v1"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return []

    entries = [entry for entry in result.stdout.splitlines() if entry.strip()]
    paths: list[Path] = []
    for entry in entries:
        if len(entry) < 4:
            continue
        path_text = entry[3:]
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1]
        paths.append((ROOT / path_text).resolve())
    return paths


def is_under_root(path: Path, roots: tuple[Path, ...]) -> bool:
    for root in roots:
        try:
            path.relative_to(root)
            return True
        except ValueError:
            continue
    return False


if __name__ == "__main__":
    raise SystemExit(main())
