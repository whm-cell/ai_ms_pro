#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from requirements_source_boundary import check_external_content_boundary_metadata
from requirements_technical_assumptions import check_technical_assumption_lines


ROOT = Path(__file__).resolve().parents[1]
REQ_ROOT = ROOT / "docs" / "requirements"
SOURCE_DIR = REQ_ROOT / "source"
NORMALIZED_DIR = REQ_ROOT / "normalized"
WORKSTREAM_DIR = REQ_ROOT / "workstreams"
INDEX_PATH = REQ_ROOT / "index.md"
MATRIX_PATH = REQ_ROOT / "traceability-matrix.md"

REQDOC_RE = re.compile(r"REQDOC-\d+")
REQ_RE = re.compile(r"REQ-\d+")
WS_RE = re.compile(r"WS-\d+")
STAGE_RE = re.compile(r"STAGE-\d+", re.IGNORECASE)
SOURCE_EVIDENCE_TYPE_PREFIXES = ("文档类型：", "文档类型:", "Document type:", "Document Type:")
LINKED_REQDOC_PREFIXES = ("关联文档：", "关联文档:", "关联 REQDOC：", "关联 REQDOC:", "Linked REQDOC:", "Linked Source:")
SOURCE_EVIDENCE_RE = re.compile(r"(source-evidence|raw-prd-evidence|原始证据|原始附件)", re.IGNORECASE)


@dataclass(frozen=True)
class RequirementShapeReport:
    source_docs: dict[str, str]
    normalized_requirements: dict[str, str]
    workstreams: dict[str, str]
    matrix_rows: int
    errors: list[str]
    warnings: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check REQDOC -> REQ -> WS -> traceability-matrix coverage.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures.")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def iter_docs(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return [
        path
        for path in sorted(directory.glob("*.md"))
        if not path.name.startswith("_") and path.name != "README.md"
    ]


def is_source_evidence_attachment(path: Path) -> bool:
    text = read_text(path)
    doc_type = prefixed_value(text, SOURCE_EVIDENCE_TYPE_PREFIXES)
    linked_source = prefixed_value(text, LINKED_REQDOC_PREFIXES)
    return bool(doc_type and SOURCE_EVIDENCE_RE.search(doc_type) and first_id(linked_source or "", REQDOC_RE))


def split_source_paths(paths: list[Path]) -> tuple[list[Path], list[Path]]:
    source_docs: list[Path] = []
    evidence_attachments: list[Path] = []
    for path in paths:
        if is_source_evidence_attachment(path):
            evidence_attachments.append(path)
        else:
            source_docs.append(path)
    return source_docs, evidence_attachments


def first_id(text: str, pattern: re.Pattern[str]) -> str | None:
    match = pattern.search(text)
    return match.group(0).upper() if match else None


def all_ids(text: str, pattern: re.Pattern[str]) -> list[str]:
    seen: set[str] = set()
    values: list[str] = []
    for match in pattern.finditer(text):
        value = match.group(0).upper()
        if value not in seen:
            seen.add(value)
            values.append(value)
    return values


def prefixed_value(text: str, prefixes: tuple[str, ...]) -> str | None:
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        for prefix in prefixes:
            if stripped.startswith(prefix):
                return stripped[len(prefix):].strip()
    return None


def doc_id(path: Path, prefixes: tuple[str, ...], pattern: re.Pattern[str]) -> str | None:
    text = read_text(path)
    explicit = prefixed_value(text, prefixes)
    return first_id(explicit or "", pattern) or first_id(path.name, pattern) or first_id(text, pattern)


def parse_doc_ids(
    paths: list[Path],
    prefixes: tuple[str, ...],
    pattern: re.Pattern[str],
    label: str,
    errors: list[str],
) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in paths:
        identifier = doc_id(path, prefixes, pattern)
        if not identifier:
            errors.append(f"{label} missing id: {relative(path)}")
            continue
        if identifier in result:
            errors.append(
                f"duplicate {label} id {identifier}: {relative(result[identifier])}, {relative(path)}"
            )
            continue
        result[identifier] = path
    return result


def parse_matrix_rows() -> list[dict[str, str]]:
    if not MATRIX_PATH.exists():
        return []
    rows: list[dict[str, str]] = []
    for raw_line in read_text(MATRIX_PATH).splitlines():
        stripped = raw_line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.split("|")[1:-1]]
        if len(cells) < 6 or cells[0] in {"原始文档", "---"}:
            continue
        source_id = first_id(cells[0], REQDOC_RE)
        req_id = first_id(cells[1], REQ_RE)
        ws_id = first_id(cells[2], WS_RE)
        stage_id = first_id(cells[3], STAGE_RE)
        if source_id and req_id and ws_id:
            rows.append(
                {
                    "source_id": source_id,
                    "req_id": req_id,
                    "ws_id": ws_id,
                    "stage_id": stage_id or "",
                }
            )
    return rows


def check_index_mentions(
    ids: dict[str, Path],
    *,
    index_text: str,
    label: str,
    warnings: list[str],
) -> None:
    for identifier, path in ids.items():
        if identifier not in index_text and path.name not in index_text:
            warnings.append(f"{label} not referenced in requirements index: {identifier}")


def check_matrix_coverage(
    *,
    source_docs: dict[str, Path],
    req_docs: dict[str, Path],
    ws_docs: dict[str, Path],
    rows: list[dict[str, str]],
    errors: list[str],
    warnings: list[str],
) -> None:
    row_sources = {row["source_id"] for row in rows}
    row_reqs = {row["req_id"] for row in rows}
    row_ws = {row["ws_id"] for row in rows}
    for source_id in source_docs:
        if source_id not in row_sources:
            warnings.append(f"REQDOC has no traceability row: {source_id}")
    for req_id in req_docs:
        if req_id not in row_reqs:
            errors.append(f"REQ has no traceability row: {req_id}")
    for ws_id in ws_docs:
        if ws_id not in row_ws:
            warnings.append(f"WS has no traceability row: {ws_id}")

    for row in rows:
        if row["source_id"] not in source_docs:
            errors.append(f"traceability references missing REQDOC: {row['source_id']}")
        if row["req_id"] not in req_docs:
            errors.append(f"traceability references missing REQ: {row['req_id']}")
        if row["ws_id"] not in ws_docs:
            errors.append(f"traceability references missing WS: {row['ws_id']}")
        if not row["stage_id"]:
            warnings.append(
                f"traceability row missing stage: {row['source_id']} -> {row['req_id']} -> {row['ws_id']}"
            )


def check_req_source_metadata(
    req_docs: dict[str, Path],
    source_docs: dict[str, Path],
    errors: list[str],
) -> None:
    for req_id, path in req_docs.items():
        source_text = prefixed_value(read_text(path), ("来源文档：", "来源文档:"))
        source_id = first_id(source_text or "", REQDOC_RE)
        if not source_id:
            errors.append(f"REQ missing 来源文档: {req_id} ({relative(path)})")
        elif source_id not in source_docs:
            errors.append(f"REQ references unknown source: {req_id} -> {source_id}")


def check_workstream_links(
    ws_docs: dict[str, Path],
    req_docs: dict[str, Path],
    rows: list[dict[str, str]],
    warnings: list[str],
) -> None:
    matrix_pairs = {(row["req_id"], row["ws_id"]) for row in rows}
    for ws_id, path in ws_docs.items():
        req_ids = all_ids(read_text(path), REQ_RE)
        if not req_ids:
            warnings.append(f"WS does not list covered REQ ids: {ws_id}")
        for req_id in req_ids:
            if req_id not in req_docs:
                warnings.append(f"WS references missing REQ: {ws_id} -> {req_id}")
            elif (req_id, ws_id) not in matrix_pairs:
                warnings.append(f"WS coverage not present in traceability matrix: {ws_id} -> {req_id}")


def check_source_evidence_attachments(
    attachment_paths: list[Path],
    source_docs: dict[str, Path],
    errors: list[str],
    warnings: list[str],
) -> None:
    for path in attachment_paths:
        text = read_text(path)
        linked_source = prefixed_value(text, LINKED_REQDOC_PREFIXES)
        source_id = first_id(linked_source or "", REQDOC_RE)
        if not source_id or source_id not in source_docs:
            errors.append(f"source evidence attachment references missing REQDOC: {relative(path)}")
            continue
        for label, prefixes in (
            ("source trust", ("来源可信度：", "来源可信度:", "Source trust:", "Source Trust:")),
            ("instruction handling", ("指令处理：", "指令处理:", "Instruction handling:", "Instruction Handling:")),
            ("sanitization status", ("清洗状态：", "清洗状态:", "Sanitization status:", "Sanitization Status:")),
        ):
            if not prefixed_value(text, prefixes):
                warnings.append(
                    f"source evidence attachment missing {label}; review required: {relative(path)} -> {source_id}"
                )


def build_report() -> RequirementShapeReport:
    errors: list[str] = []
    warnings: list[str] = []
    source_paths, source_evidence_attachments = split_source_paths(iter_docs(SOURCE_DIR))
    source_docs = parse_doc_ids(source_paths, ("文档编号：", "文档编号:"), REQDOC_RE, "REQDOC", errors)
    req_docs = parse_doc_ids(iter_docs(NORMALIZED_DIR), ("需求编号：", "需求编号:"), REQ_RE, "REQ", errors)
    ws_docs = parse_doc_ids(iter_docs(WORKSTREAM_DIR), ("工作流编号：", "工作流编号:"), WS_RE, "WS", errors)
    rows = parse_matrix_rows()

    if not MATRIX_PATH.exists():
        errors.append("missing docs/requirements/traceability-matrix.md")
    if not INDEX_PATH.exists():
        errors.append("missing docs/requirements/index.md")
    index_text = read_text(INDEX_PATH) if INDEX_PATH.exists() else ""
    check_index_mentions(source_docs, index_text=index_text, label="REQDOC", warnings=warnings)
    check_index_mentions(req_docs, index_text=index_text, label="REQ", warnings=warnings)
    check_index_mentions(ws_docs, index_text=index_text, label="WS", warnings=warnings)
    check_req_source_metadata(req_docs, source_docs, errors)
    check_external_content_boundary_metadata(source_docs, warnings, root=ROOT)
    check_source_evidence_attachments(source_evidence_attachments, source_docs, errors, warnings)
    check_matrix_coverage(
        source_docs=source_docs,
        req_docs=req_docs,
        ws_docs=ws_docs,
        rows=rows,
        errors=errors,
        warnings=warnings,
    )
    check_workstream_links(ws_docs, req_docs, rows, warnings)
    check_technical_assumption_lines(
        [*source_docs.values(), *source_evidence_attachments, *req_docs.values(), *ws_docs.values()],
        warnings,
        root=ROOT,
    )

    return RequirementShapeReport(
        source_docs={key: relative(path) for key, path in source_docs.items()},
        normalized_requirements={key: relative(path) for key, path in req_docs.items()},
        workstreams={key: relative(path) for key, path in ws_docs.items()},
        matrix_rows=len(rows),
        errors=errors,
        warnings=warnings,
    )


def emit_text(report: RequirementShapeReport) -> None:
    print("Requirements shape check:")
    print(f"- REQDOC docs: {len(report.source_docs)}")
    print(f"- REQ docs: {len(report.normalized_requirements)}")
    print(f"- WS docs: {len(report.workstreams)}")
    print(f"- traceability rows: {report.matrix_rows}")
    for error in report.errors:
        print(f"ERROR: {error}")
    for warning in report.warnings:
        print(f"WARN: {warning}")


def main() -> int:
    args = parse_args()
    report = build_report()
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        emit_text(report)
    return 1 if report.errors or (args.strict and report.warnings) else 0
if __name__ == "__main__":
    sys.exit(main())
