from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = ROOT / "docs" / "ai" / "standards" / "agent-productization-readiness-model.json"
DEFAULT_ASSESSMENT = (
    ROOT / "docs" / "ai" / "standards" / "agent-productization-readiness-assessment.jsonl"
)
MODEL_SCHEMA_VERSION = "agent-productization-readiness/v1"
ASSESSMENT_SCHEMA_VERSION = "agent-productization-assessment/v1"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CAPABILITY_ID_RE = re.compile(r"^APR-\d{2}$")
TARGET_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
STATUSES = {"covered", "partial", "missing", "not-applicable", "deferred"}
REVIEW_STATUSES = {"partial", "missing", "deferred"}
LEVELS = {"advisory", "review-required", "blocking-candidate", "blocking"}
REQUIRED_BOUNDARY_FLAGS = (
    "review_required_only",
    "no_product_agent_platform_claim",
    "no_hosted_runtime_claim",
    "no_external_effect_claim",
    "no_blocking_upgrade_without_real_samples",
)
REQUIRED_ASSESSMENT_FLAGS = (
    "local_first",
    "no_product_agent_platform_claim",
    "no_hosted_runtime_claim",
)
MAX_TEXT = 700
MAX_LIST_ITEMS = 12


@dataclass(frozen=True)
class Capability:
    capability_id: str
    slug: str
    name: str
    mvp_required: bool
    mature_required: bool


@dataclass(frozen=True)
class ReviewFinding:
    target_id: str
    capability_id: str
    status: str
    gap: str
    next_action: str


@dataclass(frozen=True)
class ReadinessReport:
    model_path: str
    assessment_path: str
    capability_count: int
    assessment_count: int
    targets: list[str]
    mvp_capabilities: list[str]
    mature_capabilities: list[str]
    status_counts: dict[str, int]
    review_findings: list[ReviewFinding]
    errors: list[str]
    warnings: list[str]


def build_report(
    model_path: Path = DEFAULT_MODEL,
    assessment_path: Path = DEFAULT_ASSESSMENT,
) -> ReadinessReport:
    errors: list[str] = []
    warnings: list[str] = []
    capabilities = load_model(model_path, errors)
    assessments = load_assessments(assessment_path, errors)
    capability_ids = {item.capability_id for item in capabilities}
    targets = sorted({target_id for target_id, _capability_id, _record in assessments})
    status_counts = {status: 0 for status in sorted(STATUSES)}
    review_findings: list[ReviewFinding] = []
    seen_pairs: set[tuple[str, str]] = set()

    for target_id, capability_id, record in assessments:
        pair = (target_id, capability_id)
        if pair in seen_pairs:
            errors.append(f"duplicate assessment for {target_id}/{capability_id}")
        seen_pairs.add(pair)
        if capability_id not in capability_ids:
            errors.append(f"{target_id}/{capability_id}: unknown capability id")
        status = text(record.get("status"))
        if status in status_counts:
            status_counts[status] += 1
        if status in REVIEW_STATUSES:
            review_findings.append(
                ReviewFinding(
                    target_id=target_id,
                    capability_id=capability_id,
                    status=status,
                    gap=text(record.get("gap")),
                    next_action=text(record.get("next_action")),
                )
            )

    for target_id in targets:
        assessed = {capability_id for current, capability_id in seen_pairs if current == target_id}
        missing = sorted(capability_ids - assessed)
        if missing:
            errors.append(f"{target_id}: missing assessment rows for {', '.join(missing)}")
    if capabilities and not targets:
        warnings.append("no readiness assessment target records found")

    return ReadinessReport(
        model_path=relative(model_path),
        assessment_path=relative(assessment_path),
        capability_count=len(capabilities),
        assessment_count=len(assessments),
        targets=targets,
        mvp_capabilities=[item.capability_id for item in capabilities if item.mvp_required],
        mature_capabilities=[item.capability_id for item in capabilities if item.mature_required],
        status_counts={status: count for status, count in status_counts.items() if count},
        review_findings=review_findings,
        errors=errors,
        warnings=warnings,
    )


def load_model(path: Path, errors: list[str]) -> list[Capability]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"model file missing: {relative(path)}")
        return []
    except json.JSONDecodeError as exc:
        errors.append(f"model file is invalid JSON: {exc.msg}")
        return []
    if not isinstance(payload, dict):
        errors.append("model root must be an object")
        return []

    validate_choice(payload, "schema_version", {MODEL_SCHEMA_VERSION}, "model", errors)
    validate_bounded_required_text(payload, "id", "model", errors)
    validate_date(payload, "updated_at", "model", errors)
    validate_choice(payload, "status", {"review-required"}, "model", errors)
    validate_required_flags(
        payload.get("claim_boundary"),
        REQUIRED_BOUNDARY_FLAGS,
        "model: claim_boundary",
        errors,
    )
    raw_capabilities = payload.get("capabilities")
    if not isinstance(raw_capabilities, list) or not raw_capabilities:
        errors.append("model.capabilities must be a non-empty list")
        return []
    if len(raw_capabilities) > 20:
        errors.append("model.capabilities has too many items")

    capabilities: list[Capability] = []
    seen_ids: set[str] = set()
    for index, raw in enumerate(raw_capabilities):
        item_prefix = f"model.capabilities[{index}]"
        if not isinstance(raw, dict):
            errors.append(f"{item_prefix}: must be an object")
            continue
        capability = validate_capability(raw, item_prefix, errors)
        if not capability:
            continue
        if capability.capability_id in seen_ids:
            errors.append(f"{item_prefix}: duplicate capability id {capability.capability_id}")
        seen_ids.add(capability.capability_id)
        capabilities.append(capability)
    return capabilities


def validate_capability(record: dict[str, Any], prefix: str, errors: list[str]) -> Capability | None:
    capability_id = validate_bounded_required_text(record, "id", prefix, errors)
    if capability_id and not CAPABILITY_ID_RE.match(capability_id):
        errors.append(f"{prefix}: id must match APR-NN")
    slug = validate_bounded_required_text(record, "slug", prefix, errors)
    name = validate_bounded_required_text(record, "name", prefix, errors)
    mvp_required = validate_bool(record, "mvp_required", prefix, errors)
    mature_required = validate_bool(record, "mature_required", prefix, errors)
    validate_bounded_required_text(record, "why", prefix, errors)
    validate_text_list(record, "acceptance_signals", prefix, errors)
    validate_path_list(record, "recommended_surfaces", prefix, errors)
    validate_text_list(record, "source_basis", prefix, errors)
    validate_choice(record, "level", LEVELS, prefix, errors)
    if not capability_id or not slug or not name:
        return None
    return Capability(capability_id, slug, name, mvp_required, mature_required)


def load_assessments(path: Path, errors: list[str]) -> list[tuple[str, str, dict[str, Any]]]:
    if not path.exists():
        errors.append(f"assessment file missing: {relative(path)}")
        return []
    rows: list[tuple[str, str, dict[str, Any]]] = []
    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw_line.strip():
            errors.append(f"assessment line {line_no}: blank line is not allowed")
            continue
        try:
            record = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            errors.append(f"assessment line {line_no}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(record, dict):
            errors.append(f"assessment line {line_no}: record must be an object")
            continue
        target_id, capability_id = validate_assessment_record(line_no, record, errors)
        if target_id and capability_id:
            rows.append((target_id, capability_id, record))
    return rows


def validate_assessment_record(line_no: int, record: dict[str, Any], errors: list[str]) -> tuple[str, str]:
    prefix = f"assessment line {line_no}"
    validate_choice(record, "schema_version", {ASSESSMENT_SCHEMA_VERSION}, prefix, errors)
    target_id = validate_bounded_required_text(record, "target_id", prefix, errors)
    if target_id and not TARGET_ID_RE.match(target_id):
        errors.append(f"{prefix}: target_id must be lowercase kebab-case")
    validate_bounded_required_text(record, "target_type", prefix, errors)
    validate_date(record, "assessed_at", prefix, errors)
    capability_id = validate_bounded_required_text(record, "capability_id", prefix, errors)
    if capability_id and not CAPABILITY_ID_RE.match(capability_id):
        errors.append(f"{prefix}: capability_id must match APR-NN")
    status = validate_choice(record, "status", STATUSES, prefix, errors)
    validate_path_list(record, "evidence_refs", prefix, errors)
    validate_bounded_required_text(record, "current_evidence", prefix, errors)
    gap = validate_bounded_required_text(record, "gap", prefix, errors)
    next_action = validate_bounded_required_text(record, "next_action", prefix, errors)
    validate_required_flags(
        record.get("claim_boundary"),
        REQUIRED_ASSESSMENT_FLAGS,
        f"{prefix}: claim_boundary",
        errors,
    )
    if status in REVIEW_STATUSES and (not gap or not next_action):
        errors.append(f"{prefix}: review statuses require gap and next_action")
    return target_id, capability_id


def validate_required_flags(value: Any, flags: tuple[str, ...], prefix: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix} must be an object")
        return
    for flag in flags:
        if value.get(flag) is not True:
            errors.append(f"{prefix}.{flag} must be true")


def validate_date(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    value = validate_bounded_required_text(record, field, prefix, errors)
    if value and not DATE_RE.match(value):
        errors.append(f"{prefix}: {field} must use YYYY-MM-DD")


def validate_choice(
    record: dict[str, Any],
    field: str,
    choices: set[str],
    prefix: str,
    errors: list[str],
) -> str:
    value = validate_bounded_required_text(record, field, prefix, errors)
    if value and value not in choices:
        errors.append(f"{prefix}: {field} must be one of {sorted(choices)}")
    return value


def validate_bool(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> bool:
    value = record.get(field)
    if not isinstance(value, bool):
        errors.append(f"{prefix}: {field} must be a boolean")
        return False
    return value


def validate_bounded_required_text(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> str:
    value = text(record.get(field))
    if not value:
        errors.append(f"{prefix}: {field} must be non-empty text")
    elif len(value) > MAX_TEXT:
        errors.append(f"{prefix}: {field} exceeds {MAX_TEXT} characters")
    return value


def validate_text_list(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> list[str]:
    value = record.get(field)
    if not isinstance(value, list) or not value:
        errors.append(f"{prefix}: {field} must be a non-empty list")
        return []
    if len(value) > MAX_LIST_ITEMS:
        errors.append(f"{prefix}: {field} has too many items")
    items: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{prefix}: {field}[{index}] must be non-empty text")
            continue
        if len(item) > MAX_TEXT:
            errors.append(f"{prefix}: {field}[{index}] exceeds {MAX_TEXT} characters")
        items.append(item.strip())
    return items


def validate_path_list(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    for item in validate_text_list(record, field, prefix, errors):
        if item.startswith(("http://", "https://")):
            errors.append(f"{prefix}: {field} must use repo-relative refs, not URLs: {item}")
            continue
        path = Path(item)
        if path.is_absolute():
            errors.append(f"{prefix}: {field} must be repo-relative: {item}")
            continue
        if item.startswith(".codex/runtime/"):
            errors.append(f"{prefix}: {field} must not reference raw runtime artifacts: {item}")
            continue
        if not (ROOT / path).exists():
            errors.append(f"{prefix}: {field} path does not exist: {item}")


def text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()
