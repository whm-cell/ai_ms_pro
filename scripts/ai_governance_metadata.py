from __future__ import annotations

import re
from pathlib import Path

from harness_config import ContextSurfaceConfig


ROOT = Path(__file__).resolve().parents[1]
AI_DOC_ROOT = ROOT / "docs" / "ai"
REQ_DOC_ROOT = ROOT / "docs" / "requirements"
WORKING_CONTEXT_PATH = AI_DOC_ROOT / "working-context.md"
ACTIVE_HANDOFF_DIR = AI_DOC_ROOT / "handoffs" / "active"
STATUS_DIR = AI_DOC_ROOT / "status"
SYNC_METADATA_SECTION = "## 同步元数据"
SYNC_METADATA_REQUIRED_KEYS = (
    "Current Stage",
    "Active Status Source",
    "Active Handoff Sources",
    "Requirement IDs",
    "Workstream IDs",
    "Last Synced From",
    "Last Synced At",
)
SYNC_ALLOWED_SOURCE_TOKENS = {"bootstrap", "handoff", "status", "manual"}
UNBOUND_VALUE = "未绑定"
PLACEHOLDER_DATE = "YYYY-MM-DD"
REQ_ID_PATTERN = re.compile(r"REQ-\d+")
WS_ID_PATTERN = re.compile(r"WS-\d+")
STAGE_TOKEN_PATTERN = re.compile(r"stage-\d+", re.IGNORECASE)


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_markdown_section(path: Path, heading: str) -> list[str]:
    if not path.exists():
        return []

    in_section = False
    collected: list[str] = []
    for line in load_text(path).splitlines():
        if line.startswith("## "):
            if line.strip() == heading:
                in_section = True
                continue
            if in_section:
                break
        if in_section:
            collected.append(line.rstrip())
    return collected


def split_metadata_field(text: str) -> tuple[str | None, str | None]:
    for separator in (":", "："):
        if separator in text:
            key, value = text.split(separator, 1)
            return key.strip(), value.strip()
    return None, None


def parse_working_context_sync_metadata() -> dict[str, str | list[str]]:
    metadata: dict[str, str | list[str]] = {}
    current_key: str | None = None

    for raw_line in extract_markdown_section(WORKING_CONTEXT_PATH, SYNC_METADATA_SECTION):
        if raw_line.startswith("- "):
            key, value = split_metadata_field(raw_line[2:].strip())
            if not key:
                current_key = None
                continue
            if value:
                metadata[key] = value
                current_key = None
                continue
            metadata[key] = []
            current_key = key
            continue
        if raw_line.startswith("  - ") or raw_line.startswith("    - "):
            nested_value = raw_line.strip()[2:].strip()
            existing_value = metadata.get(current_key or "")
            if isinstance(existing_value, list) and nested_value:
                existing_value.append(nested_value)
    return metadata


def scalar_metadata_value(
    metadata: dict[str, str | list[str]],
    key: str,
    errors: list[str],
) -> str | None:
    value = metadata.get(key)
    if value is None:
        return None
    if isinstance(value, list):
        if not value:
            errors.append(f"working-context sync metadata field '{key}' is empty.")
        else:
            errors.append(f"working-context sync metadata field '{key}' must be a single value.")
        return None

    stripped = value.strip()
    if not stripped:
        errors.append(f"working-context sync metadata field '{key}' is empty.")
        return None
    return stripped


def normalize_stage_token(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        return ""
    match = STAGE_TOKEN_PATTERN.search(stripped)
    return match.group(0).upper() if match else stripped.upper()


def read_prefixed_value(path: Path, prefixes: tuple[str, ...]) -> str | None:
    if not path.exists():
        return None
    for raw_line in load_text(path).splitlines():
        stripped = raw_line.strip()
        for prefix in prefixes:
            if stripped.startswith(prefix):
                return stripped[len(prefix):].strip()
    return None


def resolve_repo_relative_path(path_text: str) -> Path | None:
    stripped = path_text.strip()
    if not stripped or stripped.startswith("/"):
        return None
    if stripped.startswith("./"):
        stripped = stripped[2:]
    return (ROOT / stripped).resolve()


def parse_csv_values(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"[，,]", text) if part.strip()]


def context_surface_budget_warnings(
    *,
    count: int,
    label: str,
    config: ContextSurfaceConfig,
) -> list[str]:
    budget = config.active_handoff_budget
    over_budget = count > budget
    at_budget = config.warn_at_budget and count >= budget
    if not over_budget and not at_budget:
        return []

    relation = ">=" if count == budget else ">"
    return [
        (
            f"{label} has reached the configured default surface budget "
            f"({count} {relation} {budget}). Run scripts/check_archive_candidates.py "
            "and archive or compress handoffs already absorbed by stage status/ADR."
        )
    ]


def ordered_unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def metadata_identifier_tokens(
    metadata: dict[str, str | list[str]],
    key: str,
    pattern: re.Pattern[str],
) -> tuple[list[str], bool]:
    value = metadata.get(key)
    if value is None:
        return [], False

    raw_values = value if isinstance(value, list) else [value]
    tokens: list[str] = []
    for raw_value in raw_values:
        stripped = raw_value.strip()
        if not stripped:
            continue
        if stripped == UNBOUND_VALUE:
            return [], True
        tokens.extend(token for token in parse_csv_values(stripped) if pattern.fullmatch(token))
    return ordered_unique(tokens), False


def validate_identifier_field(
    metadata: dict[str, str | list[str]],
    *,
    key: str,
    pattern: re.Pattern[str],
    known_ids: set[str],
    bootstrap_like: bool,
    errors: list[str],
    warnings: list[str],
    owner_label: str,
    warn_on_unbound: bool,
) -> None:
    value = metadata.get(key)
    if value is None:
        return

    raw_values = value if isinstance(value, list) else [value]
    tokens: list[str] = []
    for raw_value in raw_values:
        stripped = raw_value.strip()
        if not stripped:
            continue
        if stripped == UNBOUND_VALUE:
            if warn_on_unbound and known_ids and not bootstrap_like:
                warnings.append(
                    f"{owner_label} leaves '{key}' unbound even though "
                    "traceability ids already exist."
                )
            return
        tokens.extend(parse_csv_values(stripped))

    if not tokens:
        errors.append(f"{owner_label} field '{key}' is empty.")
        return

    invalid_tokens = [token for token in tokens if not pattern.fullmatch(token)]
    if invalid_tokens:
        rendered = ", ".join(sorted(set(invalid_tokens)))
        errors.append(f"{owner_label} field '{key}' contains malformed ids: {rendered}")
        return

    unknown_ids = [token for token in tokens if token not in known_ids]
    if unknown_ids:
        rendered = ", ".join(sorted(set(unknown_ids)))
        errors.append(
            f"{owner_label} field '{key}' contains ids missing from "
            f"docs/requirements/traceability-matrix.md: {rendered}"
        )


def is_under_root(path: Path, roots: tuple[Path, ...]) -> bool:
    for root in roots:
        try:
            path.relative_to(root)
            return True
        except ValueError:
            continue
    return False


def latest_doc(paths: list[Path]) -> Path | None:
    if not paths:
        return None
    return max(paths, key=lambda path: path.stat().st_mtime)
