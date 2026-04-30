#!/usr/bin/env python3

from __future__ import annotations

import re
from collections import defaultdict
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKING_CONTEXT_PATH = ROOT / "docs" / "ai" / "working-context.md"
TRACEABILITY_MATRIX_PATH = ROOT / "docs" / "requirements" / "traceability-matrix.md"
SOURCE_DOC_DIR = ROOT / "docs" / "requirements" / "source"
NORMALIZED_REQ_DIR = ROOT / "docs" / "requirements" / "normalized"
WORKSTREAM_DIR = ROOT / "docs" / "requirements" / "workstreams"

REQDOC_ID_PATTERN = re.compile(r"REQDOC-\d+")
REQ_ID_PATTERN = re.compile(r"REQ-\d+")
WS_ID_PATTERN = re.compile(r"WS-\d+")
BACKTICK_RE = re.compile(r"`([^`]+)`")


def resolve_runtime_traceability(
    payload_requirement_ids: list[str],
    payload_workstream_ids: list[str],
    env_requirement_ids: list[str],
    env_workstream_ids: list[str],
    changed_paths: list[str],
) -> tuple[list[str], list[str], str]:
    requirement_ids = ordered_unique([*payload_requirement_ids, *env_requirement_ids])
    workstream_ids = ordered_unique([*payload_workstream_ids, *env_workstream_ids])
    sources: list[str] = []

    if payload_requirement_ids or payload_workstream_ids:
        sources.append("payload")
    if env_requirement_ids or env_workstream_ids:
        sources.append("env")

    should_expand_requirements = not requirement_ids
    should_expand_workstreams = not workstream_ids
    requirement_ids, workstream_ids, expanded = expand_traceability_ids(
        requirement_ids,
        workstream_ids,
        expand_requirements=should_expand_requirements,
        expand_workstreams=should_expand_workstreams,
    )
    if requirement_ids or workstream_ids:
        if expanded:
            sources.append("matrix-expansion")
        return requirement_ids, workstream_ids, ",".join(ordered_unique(sources))

    return infer_runtime_traceability(changed_paths)


def infer_runtime_traceability(changed_paths: list[str]) -> tuple[list[str], list[str], str]:
    normalized_paths = [normalize_changed_path(path) for path in changed_paths if normalize_changed_path(path)]
    if not normalized_paths:
        return [], [], "unbound"

    catalog = load_traceability_catalog()
    requirement_ids: set[str] = set()
    workstream_ids: set[str] = set()
    reasons: list[str] = []

    for path_text in normalized_paths:
        path_requirement_ids = set(REQ_ID_PATTERN.findall(path_text))
        path_workstream_ids = set(WS_ID_PATTERN.findall(path_text))
        path_source_ids = set(REQDOC_ID_PATTERN.findall(path_text))

        if path_requirement_ids:
            requirement_ids.update(path_requirement_ids)
            reasons.append("changed-path:req")
        if path_workstream_ids:
            workstream_ids.update(path_workstream_ids)
            reasons.append("changed-path:ws")
        if path_source_ids:
            for source_id in path_source_ids:
                requirement_ids.update(catalog["source_to_req"].get(source_id, set()))
                workstream_ids.update(catalog["source_to_ws"].get(source_id, set()))
            reasons.append("changed-path:reqdoc")

        workstream_from_module = infer_workstream_from_module_path(path_text, catalog["module_to_workstreams"])
        if workstream_from_module:
            workstream_ids.add(workstream_from_module)
            reasons.append("module-path")

    should_expand_requirements = not requirement_ids
    should_expand_workstreams = not workstream_ids
    requirement_list, workstream_list, _ = expand_traceability_ids(
        sorted(requirement_ids),
        sorted(workstream_ids),
        expand_requirements=should_expand_requirements,
        expand_workstreams=should_expand_workstreams,
    )

    if requirement_list or workstream_list:
        source = ",".join(ordered_unique(reasons)) or "auto-discovery"
        return requirement_list, workstream_list, source

    fallback_requirement_ids, fallback_workstream_ids = infer_unambiguous_working_context_ids()
    if fallback_requirement_ids or fallback_workstream_ids:
        return fallback_requirement_ids, fallback_workstream_ids, "working-context-fallback"

    return [], [], "unbound"


def normalize_changed_path(path_text: str) -> str:
    stripped = path_text.strip()
    if not stripped:
        return ""

    path = Path(stripped)
    if path.is_absolute():
        try:
            stripped = str(path.resolve().relative_to(ROOT)).replace("\\", "/")
        except ValueError:
            stripped = path.as_posix()
    return stripped.lstrip("./")


def infer_workstream_from_module_path(
    changed_path: str,
    module_to_workstreams: dict[str, set[str]],
) -> str | None:
    matching_workstreams: set[str] = set()
    for module_path, workstream_ids in module_to_workstreams.items():
        normalized_module = module_path.rstrip("/")
        if not normalized_module:
            continue
        if changed_path == normalized_module or changed_path.startswith(f"{normalized_module}/"):
            if len(workstream_ids) == 1:
                matching_workstreams.update(workstream_ids)
    if len(matching_workstreams) == 1:
        return next(iter(matching_workstreams))
    return None


def expand_traceability_ids(
    requirement_ids: list[str],
    workstream_ids: list[str],
    *,
    expand_requirements: bool,
    expand_workstreams: bool,
) -> tuple[list[str], list[str], bool]:
    catalog = load_traceability_catalog()
    req_set = set(requirement_ids)
    ws_set = set(workstream_ids)
    before_req = set(req_set)
    before_ws = set(ws_set)

    if expand_requirements and ws_set:
        for workstream_id in list(ws_set):
            req_set.update(catalog["ws_to_req"].get(workstream_id, set()))
    if expand_workstreams and req_set:
        for requirement_id in list(req_set):
            ws_set.update(catalog["req_to_ws"].get(requirement_id, set()))

    expanded = req_set != before_req or ws_set != before_ws
    return sorted(req_set), sorted(ws_set), expanded


def ordered_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def parse_csv_values(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"[，,]", text) if part.strip()]


def extract_markdown_section(path: Path, heading: str) -> list[str]:
    if not path.exists():
        return []

    lines = path.read_text(encoding="utf-8").splitlines()
    in_section = False
    collected: list[str] = []
    for line in lines:
        if line.startswith("## "):
            if line.strip() == heading:
                in_section = True
                continue
            if in_section:
                break
        if in_section:
            collected.append(line.rstrip())
    return collected


def extract_backtick_paths(lines: list[str]) -> list[str]:
    paths: list[str] = []
    for line in lines:
        for match in BACKTICK_RE.findall(line):
            candidate = normalize_doc_path_token(match)
            if candidate:
                paths.append(candidate)
    return ordered_unique(paths)


def normalize_doc_path_token(token: str) -> str:
    stripped = token.strip()
    if not stripped:
        return ""
    if "/" not in stripped and "\\" not in stripped:
        return ""
    stripped = stripped.replace("\\", "/").rstrip("/")
    if stripped.startswith("/"):
        path = Path(stripped)
        try:
            stripped = str(path.resolve().relative_to(ROOT)).replace("\\", "/")
        except ValueError:
            return ""
    if stripped.startswith("./"):
        stripped = stripped[2:]
    candidate = ROOT / stripped
    if candidate.exists():
        return stripped
    candidate_dir = ROOT / f"{stripped}/"
    if candidate_dir.exists():
        return stripped
    return ""


def read_prefixed_value(path: Path, prefixes: tuple[str, ...]) -> str | None:
    if not path.exists():
        return None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        for prefix in prefixes:
            if stripped.startswith(prefix):
                return stripped[len(prefix):].strip()
    return None


def first_pattern_match(text: str | None, pattern: re.Pattern[str]) -> str | None:
    if not text:
        return None
    match = pattern.search(text)
    if match is None:
        return None
    return match.group(0)


def parse_matrix_row(raw_line: str) -> dict[str, str] | None:
    stripped = raw_line.strip()
    if not stripped.startswith("|"):
        return None

    cells = [cell.strip() for cell in stripped.split("|")[1:-1]]
    if len(cells) < 6:
        return None
    if cells[0] == "原始文档":
        return None
    if all(re.fullmatch(r"-+", cell) for cell in cells):
        return None

    source_id = first_pattern_match(cells[0], REQDOC_ID_PATTERN)
    requirement_id = first_pattern_match(cells[1], REQ_ID_PATTERN)
    workstream_id = first_pattern_match(cells[2], WS_ID_PATTERN)
    if not source_id or not requirement_id or not workstream_id:
        return None

    return {
        "source_id": source_id,
        "requirement_id": requirement_id,
        "workstream_id": workstream_id,
    }


@lru_cache(maxsize=1)
def load_traceability_catalog() -> dict[str, object]:
    rows: list[dict[str, str]] = []
    if TRACEABILITY_MATRIX_PATH.exists():
        in_matrix = False
        for raw_line in TRACEABILITY_MATRIX_PATH.read_text(encoding="utf-8").splitlines():
            stripped = raw_line.strip()
            if stripped == "## 矩阵":
                in_matrix = True
                continue
            if in_matrix and stripped.startswith("## "):
                break
            if not in_matrix:
                continue
            row = parse_matrix_row(raw_line)
            if row is not None:
                rows.append(row)

    req_to_ws: dict[str, set[str]] = defaultdict(set)
    ws_to_req: dict[str, set[str]] = defaultdict(set)
    source_to_req: dict[str, set[str]] = defaultdict(set)
    source_to_ws: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        source_id = row["source_id"]
        requirement_id = row["requirement_id"]
        workstream_id = row["workstream_id"]
        req_to_ws[requirement_id].add(workstream_id)
        ws_to_req[workstream_id].add(requirement_id)
        source_to_req[source_id].add(requirement_id)
        source_to_ws[source_id].add(workstream_id)

    module_to_workstreams: dict[str, set[str]] = defaultdict(set)
    for path in iter_docs(WORKSTREAM_DIR):
        workstream_id = first_pattern_match(
            read_prefixed_value(path, ("工作流编号：",)),
            WS_ID_PATTERN,
        ) or first_pattern_match(path.name, WS_ID_PATTERN)
        if not workstream_id:
            continue
        for module_path in extract_backtick_paths(extract_markdown_section(path, "## 主要模块")):
            module_to_workstreams[module_path].add(workstream_id)

    return {
        "req_to_ws": dict(req_to_ws),
        "ws_to_req": dict(ws_to_req),
        "source_to_req": dict(source_to_req),
        "source_to_ws": dict(source_to_ws),
        "module_to_workstreams": dict(module_to_workstreams),
    }


def iter_docs(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    files: list[Path] = []
    for path in sorted(directory.glob("*.md")):
        if path.name.startswith("_"):
            continue
        if path.name == "README.md":
            continue
        files.append(path)
    return files


def infer_unambiguous_working_context_ids() -> tuple[list[str], list[str]]:
    if not WORKING_CONTEXT_PATH.exists():
        return [], []

    requirement_ids: list[str] = []
    workstream_ids: list[str] = []
    for raw_line in extract_markdown_section(WORKING_CONTEXT_PATH, "## 同步元数据"):
        stripped = raw_line.strip()
        if stripped.startswith("- Requirement IDs:") or stripped.startswith("- Requirement IDs："):
            requirement_ids = ordered_unique(REQ_ID_PATTERN.findall(stripped))
        if stripped.startswith("- Workstream IDs:") or stripped.startswith("- Workstream IDs："):
            workstream_ids = ordered_unique(WS_ID_PATTERN.findall(stripped))

    if len(workstream_ids) == 1:
        return requirement_ids, workstream_ids
    if len(requirement_ids) == 1 and not workstream_ids:
        return requirement_ids, []
    return [], []
