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


def validate_document_roots() -> bool:
    if not AI_DIR.exists():
        print("ERROR: docs/ai directory does not exist.", file=sys.stderr)
        return False

    if not INDEX_PATH.exists():
        print("ERROR: docs/ai/index.md does not exist.", file=sys.stderr)
        return False

    if not REQ_DIR.exists():
        print("ERROR: docs/requirements directory does not exist.", file=sys.stderr)
        return False

    if not REQ_INDEX_PATH.exists():
        print("ERROR: docs/requirements/index.md does not exist.", file=sys.stderr)
        return False

    return True


def load_required_docs() -> tuple[list[Path], list[Path]] | None:
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
        return None

    return required_ai_docs, required_req_docs


def validate_required_docs(
    errors: list[str],
    index_text: str,
    req_index_text: str,
    required_ai_docs: list[Path],
    required_req_docs: list[Path],
) -> None:
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


def validate_index_targets(errors: list[str], targets: list[Path], req_targets: list[Path]) -> None:
    for target in targets:
        if str(target).startswith(str(ROOT)) and not target.exists():
            errors.append(f"Index links to missing path: {target}")

    for target in req_targets:
        if str(target).startswith(str(ROOT)) and not target.exists():
            errors.append(f"Requirements index links to missing path: {target}")


def validate_ai_collection(
    index_text: str,
    errors: list[str],
    docs: list[Path],
    empty_marker: str,
    stale_empty_error: str,
    label: str,
    anchor_tokens: tuple[str, ...],
) -> None:
    if not docs:
        return

    if empty_marker in index_text:
        errors.append(stale_empty_error)

    for path in docs:
        if not is_doc_or_anchor_referenced(index_text, path, anchor_tokens=anchor_tokens):
            errors.append(f"{label} not referenced in index: {path.relative_to(ROOT)}")


def validate_ai_collections(index_text: str, errors: list[str], warnings: list[str]) -> None:
    checks = [
        (
            iter_docs(AI_DIR / "handoffs" / "active"),
            "暂无活跃 `handoff`",
            "Index still says there are no active handoffs, but active handoff files exist.",
            "Active handoff",
            ("docs/ai/handoffs/active", "./handoffs/active", "docs/ai/working-context.md", "./working-context.md"),
            "No active handoffs found. Consider updating index wording if this is intentional.",
        ),
        (
            iter_docs(AI_DIR / "status"),
            "暂无阶段 `status`",
            "Index still says there is no status document, but status files exist.",
            "Status document",
            ("docs/ai/status", "./status"),
            "No stage status files found. Consider updating index wording if this is intentional.",
        ),
        (
            iter_docs(AI_DIR / "changelog"),
            "暂无阶段 `changelog`",
            "Index still says there is no changelog, but changelog files exist.",
            "Changelog document",
            ("docs/ai/changelog", "./changelog"),
            "No stage changelog files found. Consider updating index wording if this is intentional.",
        ),
        (
            iter_docs(AI_DIR / "adr"),
            "暂无正式 `adr`",
            "Index still says there is no ADR, but ADR files exist.",
            "ADR document",
            ("docs/ai/adr", "./adr"),
            "No ADR files found. Consider updating index wording if this is intentional.",
        ),
    ]

    for docs, marker, stale_error, label, anchor_tokens, missing_warning in checks:
        validate_ai_collection(index_text, errors, docs, marker, stale_error, label, anchor_tokens)
        if not docs and marker not in index_text:
            warnings.append(missing_warning)


def validate_requirement_collections(errors: list[str], req_index_text: str) -> None:
    checks = [
        (iter_docs(REQ_DIR / "source"), "Source requirement document"),
        (iter_docs(REQ_DIR / "normalized"), "Normalized requirement document"),
        (iter_docs(REQ_DIR / "workstreams"), "Workstream document"),
    ]

    for docs, label in checks:
        for path in docs:
            add_missing_doc_error(errors, req_index_text, path, label)


def print_result(errors: list[str], warnings: list[str]) -> int:
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


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    if not validate_document_roots():
        return 1

    index_text = load_text(INDEX_PATH)
    req_index_text = load_text(REQ_INDEX_PATH)
    required_docs = load_required_docs()
    if required_docs is None:
        return 1

    required_ai_docs, required_req_docs = required_docs
    validate_required_docs(errors, index_text, req_index_text, required_ai_docs, required_req_docs)
    validate_index_targets(errors, link_targets(index_text), link_targets(req_index_text))
    validate_ai_collections(index_text, errors, warnings)
    validate_requirement_collections(errors, req_index_text)
    return print_result(errors, warnings)


if __name__ == "__main__":
    raise SystemExit(main())
