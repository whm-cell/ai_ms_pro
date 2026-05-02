#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from pathlib import Path

from harness_config import HarnessConfigError, load_harness_config, resolve_repo_paths


ROOT = Path(__file__).resolve().parents[1]
AI_DIR = ROOT / "docs" / "ai"
INDEX_PATH = AI_DIR / "index.md"
REQ_DIR = ROOT / "docs" / "requirements"
REQ_INDEX_PATH = REQ_DIR / "index.md"

LINK_RE = re.compile(r"\[[^\]]+\]\((/[^)]+)\)")


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def iter_docs(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    files = []
    for path in sorted(directory.glob("*.md")):
        if path.name.startswith("_"):
            continue
        if path.name == "README.md":
            continue
        files.append(path)
    return files


def link_targets(index_text: str) -> list[Path]:
    return [Path(match.group(1)) for match in LINK_RE.finditer(index_text)]


def add_missing_doc_error(errors: list[str], index_text: str, path: Path, label: str) -> None:
    if path.name not in index_text:
        errors.append(f"{label} not referenced in index: {path.relative_to(ROOT)}")


def is_doc_or_anchor_referenced(index_text: str, path: Path, anchor_tokens: tuple[str, ...] = ()) -> bool:
    if path.name in index_text:
        return True
    repo_relative = path.relative_to(ROOT).as_posix()
    if repo_relative in index_text:
        return True
    return any(token in index_text for token in anchor_tokens)


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    if not AI_DIR.exists():
        print("ERROR: docs/ai directory does not exist.", file=sys.stderr)
        return 1

    if not INDEX_PATH.exists():
        print("ERROR: docs/ai/index.md does not exist.", file=sys.stderr)
        return 1

    if not REQ_DIR.exists():
        print("ERROR: docs/requirements directory does not exist.", file=sys.stderr)
        return 1

    if not REQ_INDEX_PATH.exists():
        print("ERROR: docs/requirements/index.md does not exist.", file=sys.stderr)
        return 1

    index_text = load_text(INDEX_PATH)
    req_index_text = load_text(REQ_INDEX_PATH)
    targets = link_targets(index_text)
    req_targets = link_targets(req_index_text)

    try:
        harness_config = load_harness_config(ROOT)
        required_ai_docs = resolve_repo_paths(
            ROOT,
            harness_config.checks.required_ai_docs,
            config_label="checks.required_ai_docs",
        )
        required_req_docs = resolve_repo_paths(
            ROOT,
            harness_config.checks.required_requirements_docs,
            config_label="checks.required_requirements_docs",
        )
    except HarnessConfigError as exc:
        print("AI docs governance check: FAILED")
        print(f"ERROR: {exc}")
        return 1

    for path in required_ai_docs:
        if not path.exists():
            errors.append(f"Required document is missing: {path.relative_to(ROOT)}")
            continue
        add_missing_doc_error(errors, index_text, path, "Required document")

    for path in required_req_docs:
        if not path.exists():
            errors.append(f"Required document is missing: {path.relative_to(ROOT)}")
            continue
        add_missing_doc_error(errors, req_index_text, path, "Required document")

    for target in targets:
        if str(target).startswith(str(ROOT)) and not target.exists():
            errors.append(f"Index links to missing path: {target}")

    for target in req_targets:
        if str(target).startswith(str(ROOT)) and not target.exists():
            errors.append(f"Requirements index links to missing path: {target}")

    active_handoffs = iter_docs(AI_DIR / "handoffs" / "active")
    status_docs = iter_docs(AI_DIR / "status")
    changelog_docs = iter_docs(AI_DIR / "changelog")
    adr_docs = iter_docs(AI_DIR / "adr")
    source_docs = iter_docs(REQ_DIR / "source")
    normalized_docs = iter_docs(REQ_DIR / "normalized")
    workstream_docs = iter_docs(REQ_DIR / "workstreams")

    if active_handoffs:
        if "暂无活跃 `handoff`" in index_text:
            errors.append("Index still says there are no active handoffs, but active handoff files exist.")
        for path in active_handoffs:
            if not is_doc_or_anchor_referenced(
                index_text,
                path,
                anchor_tokens=("docs/ai/handoffs/active", "./handoffs/active", "docs/ai/working-context.md", "./working-context.md"),
            ):
                errors.append(f"Active handoff not referenced in index: {path.relative_to(ROOT)}")

    if status_docs:
        if "暂无阶段 `status`" in index_text:
            errors.append("Index still says there is no status document, but status files exist.")
        for path in status_docs:
            if not is_doc_or_anchor_referenced(
                index_text,
                path,
                anchor_tokens=("docs/ai/status", "./status"),
            ):
                errors.append(f"Status document not referenced in index: {path.relative_to(ROOT)}")

    if changelog_docs:
        if "暂无阶段 `changelog`" in index_text:
            errors.append("Index still says there is no changelog, but changelog files exist.")
        for path in changelog_docs:
            if not is_doc_or_anchor_referenced(
                index_text,
                path,
                anchor_tokens=("docs/ai/changelog", "./changelog"),
            ):
                errors.append(f"Changelog document not referenced in index: {path.relative_to(ROOT)}")

    if adr_docs:
        if "暂无正式 `adr`" in index_text:
            errors.append("Index still says there is no ADR, but ADR files exist.")
        for path in adr_docs:
            if not is_doc_or_anchor_referenced(
                index_text,
                path,
                anchor_tokens=("docs/ai/adr", "./adr"),
            ):
                errors.append(f"ADR document not referenced in index: {path.relative_to(ROOT)}")

    if not active_handoffs and "暂无活跃 `handoff`" not in index_text:
        warnings.append("No active handoffs found. Consider updating index wording if this is intentional.")

    if not status_docs and "暂无阶段 `status`" not in index_text:
        warnings.append("No stage status files found. Consider updating index wording if this is intentional.")

    if not changelog_docs and "暂无阶段 `changelog`" not in index_text:
        warnings.append("No stage changelog files found. Consider updating index wording if this is intentional.")

    if not adr_docs and "暂无正式 `adr`" not in index_text:
        warnings.append("No ADR files found. Consider updating index wording if this is intentional.")

    if source_docs:
        for path in source_docs:
            add_missing_doc_error(errors, req_index_text, path, "Source requirement document")

    if normalized_docs:
        for path in normalized_docs:
            add_missing_doc_error(errors, req_index_text, path, "Normalized requirement document")

    if workstream_docs:
        for path in workstream_docs:
            add_missing_doc_error(errors, req_index_text, path, "Workstream document")

    if errors:
        print("AI docs governance check: FAILED")
        for message in errors:
            print(f"ERROR: {message}")
        for message in warnings:
            print(f"WARN: {message}")
        return 1

    print("AI docs governance check: OK")
    for message in warnings:
        print(f"WARN: {message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
