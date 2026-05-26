#!/usr/bin/env python3

from __future__ import annotations

import re
from pathlib import Path

from runtime_traceability_catalog import (
    REQDOC_ID_PATTERN,
    REQ_ID_PATTERN,
    ROOT,
    WS_ID_PATTERN,
    load_traceability_catalog,
    ordered_unique,
)


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


def parse_csv_values(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"[，,]", text) if part.strip()]
