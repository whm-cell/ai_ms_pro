from __future__ import annotations

from pathlib import Path


def validate_existing_repo_relative_refs(
    refs: list[str],
    root: Path,
    field: str,
    prefix: str,
    errors: list[str],
    *,
    allow_selectors: bool = False,
) -> None:
    for ref in refs:
        if "://" in ref or ref.startswith("/"):
            errors.append(f"{prefix}: {field} items must be repo-relative paths: {ref}")
            continue
        ref_path = selector_base_path(ref) if allow_selectors else ref
        if not ref_path:
            errors.append(f"{prefix}: {field} item must include a repo-relative path: {ref}")
            continue
        candidate = (root / ref_path).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            errors.append(f"{prefix}: {field} item escapes repository scope: {ref}")
            continue
        if not candidate.exists():
            errors.append(f"{prefix}: {field} item does not exist: {ref}")


def selector_base_path(ref: str) -> str:
    ref_path = ref.split("#", 1)[0].split("::", 1)[0]
    before_line, separator, line = ref_path.rpartition(":")
    return before_line if separator and line.isdigit() else ref_path
