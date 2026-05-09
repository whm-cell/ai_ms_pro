from __future__ import annotations
import re
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REQ_DOC_ROOT = ROOT / "docs" / "requirements"
SOURCE_DOC_DIR = REQ_DOC_ROOT / "source"
NORMALIZED_REQ_DIR = REQ_DOC_ROOT / "normalized"
WORKSTREAM_DIR = REQ_DOC_ROOT / "workstreams"
TRACEABILITY_MATRIX_PATH = REQ_DOC_ROOT / "traceability-matrix.md"
REQDOC_ID_PATTERN = re.compile(r"REQDOC-\d+")
REQ_ID_PATTERN = re.compile(r"REQ-\d+")
WS_ID_PATTERN = re.compile(r"WS-\d+")
STAGE_TOKEN_PATTERN = re.compile(r"stage-\d+", re.IGNORECASE)
def iter_docs(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return [
        path
        for path in sorted(directory.glob("*.md"))
        if not path.name.startswith("_") and path.name != "README.md"
    ]
def normalize_stage_token(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        return ""
    match = STAGE_TOKEN_PATTERN.search(stripped)
    return match.group(0).upper() if match else stripped.upper()
def first_pattern_match(text: str | None, pattern: re.Pattern[str]) -> str | None:
    if not text:
        return None
    match = pattern.search(text)
    return None if match is None else match.group(0)
def read_prefixed_value(path: Path, prefixes: tuple[str, ...]) -> str | None:
    if not path.exists():
        return None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        for prefix in prefixes:
            if stripped.startswith(prefix):
                return stripped[len(prefix):].strip()
    return None
def extract_ids_from_section(path: Path, heading: str, pattern: re.Pattern[str]) -> list[str]:
    if not path.exists():
        return []
    in_section = False
    matches: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            if line.strip() == heading:
                in_section = True
                continue
            if in_section:
                break
        if in_section:
            matches.extend(pattern.findall(line))
    return list(dict.fromkeys(matches))
def parse_matrix_row(raw_line: str) -> dict[str, str] | None:
    stripped = raw_line.strip()
    if not stripped.startswith("|"):
        return None
    cells = [cell.strip() for cell in stripped.split("|")[1:-1]]
    if len(cells) < 6 or cells[0] == "原始文档":
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
        "stage_token": normalize_stage_token(cells[3]) or "",
    }
def load_matrix_rows() -> list[dict[str, str]]:
    if not TRACEABILITY_MATRIX_PATH.exists():
        return []
    rows: list[dict[str, str]] = []
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
    return rows
def load_source_doc_paths() -> dict[str, Path]:
    return {
        source_id: path
        for path in iter_docs(SOURCE_DOC_DIR)
        if (source_id := first_pattern_match(path.name, REQDOC_ID_PATTERN))
    }
def load_bound_doc_catalog(
    directory: Path,
    *,
    id_prefixes: tuple[str, ...],
    id_pattern: re.Pattern[str],
    section_heading: str,
    section_pattern: re.Pattern[str],
) -> tuple[dict[str, Path], dict[str, list[str]]]:
    paths: dict[str, Path] = {}
    section_ids: dict[str, list[str]] = {}
    for path in iter_docs(directory):
        doc_id = first_pattern_match(read_prefixed_value(path, id_prefixes), id_pattern)
        if not doc_id:
            doc_id = first_pattern_match(path.name, id_pattern)
        if not doc_id:
            continue
        paths[doc_id] = path
        section_ids[doc_id] = extract_ids_from_section(path, section_heading, section_pattern)
    return paths, section_ids
def matrix_indexes(
    rows: list[dict[str, str]],
) -> tuple[set[str], set[str], set[str], dict[str, set[str]], dict[str, set[str]]]:
    req_to_ws: dict[str, set[str]] = defaultdict(set)
    ws_to_req: dict[str, set[str]] = defaultdict(set)
    source_ids: set[str] = set()
    requirement_ids: set[str] = set()
    workstream_ids: set[str] = set()
    for row in rows:
        source_id = row["source_id"]
        requirement_id = row["requirement_id"]
        workstream_id = row["workstream_id"]
        source_ids.add(source_id)
        requirement_ids.add(requirement_id)
        workstream_ids.add(workstream_id)
        req_to_ws[requirement_id].add(workstream_id)
        ws_to_req[workstream_id].add(requirement_id)
    return source_ids, requirement_ids, workstream_ids, dict(req_to_ws), dict(ws_to_req)
@lru_cache(maxsize=1)
def load_traceability_catalog() -> dict[str, object]:
    rows = load_matrix_rows()
    source_ids, requirement_ids, workstream_ids, req_to_ws, ws_to_req = matrix_indexes(rows)
    normalized_paths, normalized_workstreams = load_bound_doc_catalog(
        NORMALIZED_REQ_DIR,
        id_prefixes=("需求编号：",),
        id_pattern=REQ_ID_PATTERN,
        section_heading="## 关联工作流",
        section_pattern=WS_ID_PATTERN,
    )
    workstream_paths, workstream_requirements = load_bound_doc_catalog(
        WORKSTREAM_DIR,
        id_prefixes=("工作流编号：",),
        id_pattern=WS_ID_PATTERN,
        section_heading="## 覆盖需求",
        section_pattern=REQ_ID_PATTERN,
    )
    return {
        "rows": rows,
        "source_ids": source_ids,
        "requirement_ids": requirement_ids,
        "workstream_ids": workstream_ids,
        "req_to_ws": req_to_ws,
        "ws_to_req": ws_to_req,
        "source_doc_paths": load_source_doc_paths(),
        "normalized_doc_paths": normalized_paths,
        "normalized_doc_workstreams": normalized_workstreams,
        "workstream_doc_paths": workstream_paths,
        "workstream_doc_requirements": workstream_requirements,
    }
def extract_known_ids(pattern: re.Pattern[str]) -> set[str]:
    catalog = load_traceability_catalog()
    if pattern.pattern == REQDOC_ID_PATTERN.pattern:
        return set(catalog["source_ids"])
    if pattern.pattern == REQ_ID_PATTERN.pattern:
        return set(catalog["requirement_ids"])
    if pattern.pattern == WS_ID_PATTERN.pattern:
        return set(catalog["workstream_ids"])
    return set()
def validate_requirement_workstream_pairings(
    *,
    requirement_ids: list[str],
    workstream_ids: list[str],
    owner_label: str,
    errors: list[str],
) -> None:
    if not requirement_ids or not workstream_ids:
        return
    catalog = load_traceability_catalog()
    req_to_ws: dict[str, set[str]] = catalog["req_to_ws"]  # type: ignore[assignment]
    ws_to_req: dict[str, set[str]] = catalog["ws_to_req"]  # type: ignore[assignment]
    unmatched_requirements = [
        req_id for req_id in requirement_ids if not req_to_ws.get(req_id, set()).intersection(workstream_ids)
    ]
    if unmatched_requirements:
        errors.append(
            f"{owner_label} declares Requirement IDs [{', '.join(unmatched_requirements)}] that do "
            f"not map to any of its declared Workstream IDs [{', '.join(workstream_ids)}] in "
            "docs/requirements/traceability-matrix.md."
        )
    unmatched_workstreams = [
        ws_id for ws_id in workstream_ids if not ws_to_req.get(ws_id, set()).intersection(requirement_ids)
    ]
    if unmatched_workstreams:
        errors.append(
            f"{owner_label} declares Workstream IDs [{', '.join(unmatched_workstreams)}] that do "
            f"not map to any of its declared Requirement IDs [{', '.join(requirement_ids)}] in "
            "docs/requirements/traceability-matrix.md."
        )
def stage_alignment_mismatches(
    *,
    rows: list[dict[str, str]],
    requirement_ids: list[str],
    workstream_ids: list[str],
    current_stage: str,
) -> list[str]:
    normalized_stage = normalize_stage_token(current_stage)
    if not normalized_stage or not requirement_ids or not workstream_ids:
        return []
    requirement_set = set(requirement_ids)
    workstream_set = set(workstream_ids)
    mismatches: list[str] = []
    for row in rows:
        requirement_id = row.get("requirement_id", "")
        workstream_id = row.get("workstream_id", "")
        if requirement_id not in requirement_set or workstream_id not in workstream_set:
            continue
        matrix_stage = row.get("stage_token", "")
        if matrix_stage != normalized_stage:
            mismatches.append(f"{requirement_id}/{workstream_id}={matrix_stage or '未绑定'}")
    return mismatches
def validate_stage_traceability_alignment(
    *,
    requirement_ids: list[str],
    workstream_ids: list[str],
    current_stage: str | None,
    owner_label: str,
    errors: list[str],
) -> None:
    if not current_stage:
        return
    normalized_stage = normalize_stage_token(current_stage)
    if not normalized_stage:
        errors.append(f"{owner_label} current stage is empty.")
        return
    catalog = load_traceability_catalog()
    rows: list[dict[str, str]] = catalog["rows"]  # type: ignore[assignment]
    mismatches = stage_alignment_mismatches(
        rows=rows,
        requirement_ids=requirement_ids,
        workstream_ids=workstream_ids,
        current_stage=normalized_stage,
    )
    if mismatches:
        errors.append(
            f"{owner_label} declares stage {normalized_stage}, but these REQ/WS bindings have "
            f"different stages in docs/requirements/traceability-matrix.md: {', '.join(mismatches)}"
        )
def validate_matrix_doc_references(catalog: dict[str, object], errors: list[str]) -> None:
    checks = (
        ("source_ids", "source_doc_paths", "source ids", "source document"),
        ("requirement_ids", "normalized_doc_paths", "requirement ids", "normalized requirement document"),
        ("workstream_ids", "workstream_doc_paths", "workstream ids", "workstream document"),
    )
    for matrix_key, doc_key, id_label, doc_label in checks:
        matrix_ids: set[str] = catalog[matrix_key]  # type: ignore[assignment]
        doc_paths: dict[str, Path] = catalog[doc_key]  # type: ignore[assignment]
        missing_docs = sorted(matrix_ids - set(doc_paths))
        if missing_docs:
            errors.append(
                f"docs/requirements/traceability-matrix.md references {id_label} with no matching "
                f"{doc_label}: {', '.join(missing_docs)}"
            )
def validate_doc_bindings(
    *,
    doc_paths: dict[str, Path],
    declared_links: dict[str, list[str]],
    matrix_ids: set[str],
    matrix_links: dict[str, set[str]],
    doc_id_label: str,
    linked_label: str,
    missing_linked_label: str,
    section_name: str,
    errors: list[str],
) -> None:
    for doc_id, path in sorted(doc_paths.items()):
        declared = declared_links.get(doc_id, [])
        matrix_bound = sorted(matrix_links.get(doc_id, set()))
        if doc_id not in matrix_ids:
            errors.append(
                f"{path.relative_to(ROOT)} declares {doc_id}, but the {doc_id_label} id is "
                "missing from docs/requirements/traceability-matrix.md."
            )
            continue
        if not declared:
            errors.append(
                f"{path.relative_to(ROOT)} is missing {missing_linked_label} under '{section_name}' "
                f"for matrix-backed {doc_id_label} {doc_id}."
            )
            continue
        add_link_mismatch_errors(path, doc_id, declared, matrix_bound, matrix_links, linked_label, errors)
def add_link_mismatch_errors(
    path: Path,
    doc_id: str,
    declared: list[str],
    matrix_bound: list[str],
    matrix_links: dict[str, set[str]],
    linked_label: str,
    errors: list[str],
) -> None:
    invalid = [linked_id for linked_id in declared if linked_id not in matrix_links.get(doc_id, set())]
    if invalid:
        errors.append(
            f"{path.relative_to(ROOT)} declares {linked_label} not mapped from {doc_id} "
            f"in docs/requirements/traceability-matrix.md: {', '.join(invalid)}"
        )
    missing = [linked_id for linked_id in matrix_bound if linked_id not in declared]
    if missing:
        errors.append(
            f"{path.relative_to(ROOT)} omits matrix-bound {linked_label} for {doc_id}: "
            f"{', '.join(missing)}"
        )
def validate_requirements_traceability_alignment(errors: list[str]) -> None:
    catalog = load_traceability_catalog()
    validate_matrix_doc_references(catalog, errors)
    validate_doc_bindings(
        doc_paths=catalog["normalized_doc_paths"],  # type: ignore[arg-type]
        declared_links=catalog["normalized_doc_workstreams"],  # type: ignore[arg-type]
        matrix_ids=catalog["requirement_ids"],  # type: ignore[arg-type]
        matrix_links=catalog["req_to_ws"],  # type: ignore[arg-type]
        doc_id_label="requirement",
        linked_label="workstreams",
        missing_linked_label="bound workstreams",
        section_name="## 关联工作流",
        errors=errors,
    )
    validate_doc_bindings(
        doc_paths=catalog["workstream_doc_paths"],  # type: ignore[arg-type]
        declared_links=catalog["workstream_doc_requirements"],  # type: ignore[arg-type]
        matrix_ids=catalog["workstream_ids"],  # type: ignore[arg-type]
        matrix_links=catalog["ws_to_req"],  # type: ignore[arg-type]
        doc_id_label="workstream",
        linked_label="requirements",
        missing_linked_label="covered requirements",
        section_name="## 覆盖需求",
        errors=errors,
    )
