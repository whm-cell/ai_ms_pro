from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Callable


CONTRACT_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]*$")
TRACE_ATTRIBUTE_RE = re.compile(r"^[A-Za-z0-9_.:-]+$")
TRACE_SCHEMA_VERSION = "agent-trace/v1"
TRACE_EXPECTATION_FIELDS = (
    "schema_version",
    "producer",
    "required_event",
    "required_kinds",
    "required_attributes",
    "required_redaction_states",
    "evidence_artifacts",
    "tool_contracts",
    "notes",
)
TRACE_KIND_VALUES = {
    "agent_run",
    "agent_step",
    "tool_call",
    "check",
    "guardrail",
    "handoff",
    "reducer",
    "event",
}
REDACTION_STATES = {"redacted", "unredacted", "not_applicable"}
FORBIDDEN_TRACE_ATTRIBUTE_KEYS = {
    "cwd",
    "prompt",
    "prompt_preview",
    "raw_prompt",
    "session_id",
    "transcript",
    "transcript_path",
}


HasText = Callable[[object], bool]
HasTextList = Callable[[object], bool]
Relative = Callable[[Path], str]


def load_contract_names(path: Path, errors: list[str], relative: Relative, has_text: HasText) -> set[str]:
    if not path.exists():
        errors.append(f"tool contract registry missing: {relative(path)}")
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"tool contract registry is invalid JSON: {exc.msg}")
        return set()
    contracts = data.get("contracts") if isinstance(data, dict) else None
    if not isinstance(contracts, list):
        errors.append("tool contract registry contracts must be a list")
        return set()
    return {item["name"] for item in contracts if isinstance(item, dict) and has_text(item.get("name"))}


def validate_trace_expectations(
    line_no: int,
    value: object,
    contract_names: set[str],
    errors: list[str],
    has_text: HasText,
    has_text_list: HasTextList,
) -> None:
    if not isinstance(value, dict):
        errors.append(f"line {line_no}: trace_expectations must be an object")
        return
    missing = [field for field in TRACE_EXPECTATION_FIELDS if field not in value]
    if missing:
        errors.append(f"line {line_no}: trace_expectations missing fields: {', '.join(missing)}")
        return
    if value["schema_version"] != TRACE_SCHEMA_VERSION:
        errors.append(f"line {line_no}: trace_expectations.schema_version must be {TRACE_SCHEMA_VERSION}")
    for field in ("producer", "required_event", "notes"):
        if not has_text(value[field]):
            errors.append(f"line {line_no}: trace_expectations.{field} must be non-empty text")
    validate_trace_kinds(line_no, value["required_kinds"], errors, has_text_list)
    validate_trace_attributes(line_no, value["required_attributes"], errors, has_text_list)
    validate_redaction_states(line_no, value["required_redaction_states"], errors, has_text_list)
    validate_evidence_artifacts(line_no, value["evidence_artifacts"], errors, has_text_list)
    validate_tool_contracts(line_no, value["tool_contracts"], contract_names, errors, has_text_list)


def validate_trace_kinds(line_no: int, value: object, errors: list[str], has_text_list: HasTextList) -> None:
    if not has_text_list(value):
        errors.append(f"line {line_no}: trace_expectations.required_kinds must be a non-empty text list")
        return
    unknown = sorted({str(item) for item in value if item not in TRACE_KIND_VALUES})
    if unknown:
        errors.append(f"line {line_no}: unsupported trace kinds: {', '.join(unknown)}")


def validate_trace_attributes(line_no: int, value: object, errors: list[str], has_text_list: HasTextList) -> None:
    if not has_text_list(value):
        errors.append(f"line {line_no}: trace_expectations.required_attributes must be a non-empty text list")
        return
    for attribute in value:
        text = str(attribute)
        if not TRACE_ATTRIBUTE_RE.match(text):
            errors.append(f"line {line_no}: invalid trace attribute name: {text}")
        if text in FORBIDDEN_TRACE_ATTRIBUTE_KEYS:
            errors.append(f"line {line_no}: trace attribute must not require raw local payload key: {text}")


def validate_redaction_states(line_no: int, value: object, errors: list[str], has_text_list: HasTextList) -> None:
    if not has_text_list(value):
        errors.append(f"line {line_no}: trace_expectations.required_redaction_states must be a non-empty text list")
        return
    unknown = sorted({str(item) for item in value if item not in REDACTION_STATES})
    if unknown:
        errors.append(f"line {line_no}: unsupported redaction states: {', '.join(unknown)}")


def validate_evidence_artifacts(line_no: int, value: object, errors: list[str], has_text_list: HasTextList) -> None:
    if not has_text_list(value):
        errors.append(f"line {line_no}: trace_expectations.evidence_artifacts must be a non-empty text list")
        return
    for artifact in value:
        path = Path(str(artifact))
        if path.is_absolute() or ".." in path.parts:
            errors.append(f"line {line_no}: evidence artifact must be repo-relative: {artifact}")


def validate_tool_contracts(
    line_no: int,
    value: object,
    contract_names: set[str],
    errors: list[str],
    has_text_list: HasTextList,
) -> None:
    if not has_text_list(value):
        errors.append(f"line {line_no}: trace_expectations.tool_contracts must be a non-empty text list")
        return
    for name in value:
        text = str(name)
        if not CONTRACT_NAME_RE.match(text):
            errors.append(f"line {line_no}: invalid tool contract name: {text}")
        elif text not in contract_names:
            errors.append(f"line {line_no}: unknown tool contract referenced by trace_expectations: {text}")
