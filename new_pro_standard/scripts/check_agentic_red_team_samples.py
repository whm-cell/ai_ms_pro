#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any

import evidence_ref_utils


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLES = ROOT / "docs" / "ai" / "security" / "agentic-red-team-samples.jsonl"
ID_RE = re.compile(r"^REDTEAM-SAMPLE-\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CONTROL_RE = re.compile(r"^AC-(0[1-9]|1[0-4])$")
RISKS = {
    "prompt-injection",
    "tool-output-injection",
    "skill-squatting",
    "memory-poisoning",
    "a2a-handoff-confusion",
    "cascade-autonomy",
    "human-confirmation",
    "sandbox-claim-honesty",
}
REQUIRED_RISKS = set(RISKS)
SOURCE_TYPES = {"real-incident", "local-replay", "synthetic-regression", "manual-review"}
OUTCOMES = {"accepted", "pending", "rejected"}
UPGRADE_SIGNALS = {"none", "weak", "candidate"}
FORBIDDEN_KEYS = {"cwd", "prompt", "prompt_preview", "raw_output", "rawOutput", "transcript", "transcript_path"}
MAX_TEXT = 700
MAX_LIST_ITEMS = 12


@dataclass(frozen=True)
class RedTeamSampleReport:
    sample_path: str
    record_count: int
    accepted_replay_or_real_count: int
    accepted_real_incident_count: int
    accepted_by_risk: dict[str, int]
    accepted_real_by_risk: dict[str, int]
    false_positive_count: int
    errors: list[str]
    warnings: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate agentic red-team burn-in samples.")
    parser.add_argument("--samples", default=str(DEFAULT_SAMPLES), help="Agentic red-team sample JSONL path.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def text_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def build_report(path: Path = DEFAULT_SAMPLES) -> RedTeamSampleReport:
    errors: list[str] = []
    warnings: list[str] = []
    records = load_records(path, errors)
    seen: set[str] = set()
    accepted_by_risk: dict[str, int] = {}
    accepted_real_by_risk: dict[str, int] = {}
    accepted_replay_or_real = 0
    accepted_real = 0
    false_positive_count = 0
    for line_no, record in records:
        validate_record(line_no, record, seen, errors, warnings)
        if record.get("false_positive") is True:
            false_positive_count += 1
        if text(record.get("outcome")) != "accepted":
            continue
        source_type = text(record.get("source_type"))
        if source_type in {"local-replay", "real-incident"}:
            accepted_replay_or_real += 1
            risk = text(record.get("risk_family"))
            accepted_by_risk[risk] = accepted_by_risk.get(risk, 0) + 1
        if source_type == "real-incident":
            accepted_real += 1
            risk = text(record.get("risk_family"))
            accepted_real_by_risk[risk] = accepted_real_by_risk.get(risk, 0) + 1
    for risk in sorted(REQUIRED_RISKS - set(accepted_by_risk)):
        warnings.append(f"no accepted local-replay or real-incident sample for risk: {risk}")
    if accepted_real == 0:
        warnings.append("no accepted real red-team incident sample recorded yet")
    return RedTeamSampleReport(
        relative(path),
        len(records),
        accepted_replay_or_real,
        accepted_real,
        accepted_by_risk,
        accepted_real_by_risk,
        false_positive_count,
        errors,
        warnings,
    )


def load_records(path: Path, errors: list[str]) -> list[tuple[int, dict[str, Any]]]:
    if not path.exists():
        errors.append(f"sample file missing: {relative(path)}")
        return []
    records: list[tuple[int, dict[str, Any]]] = []
    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw_line.strip():
            errors.append(f"line {line_no}: blank line is not allowed")
            continue
        try:
            payload = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_no}: invalid JSON: {exc.msg}")
            continue
        if isinstance(payload, dict):
            records.append((line_no, payload))
        else:
            errors.append(f"line {line_no}: sample must be a JSON object")
    return records


def validate_record(line_no: int, record: dict[str, Any], seen: set[str], errors: list[str], warnings: list[str]) -> None:
    prefix = f"line {line_no}"
    scan_for_forbidden(prefix, record, errors)
    sample_id = required_text(record, "id", prefix, errors)
    if sample_id and not ID_RE.match(sample_id):
        errors.append(f"{prefix}: id must match {ID_RE.pattern}")
    if sample_id in seen:
        errors.append(f"{prefix}: duplicate id: {sample_id}")
    seen.add(sample_id)
    if text(record.get("schema_version")) != "agentic-red-team-sample/v1":
        errors.append(f"{prefix}: schema_version must be agentic-red-team-sample/v1")
    validate_date(record, "sampled_at", prefix, errors)
    validate_choice(record, "risk_family", RISKS, prefix, errors)
    validate_choice(record, "source_type", SOURCE_TYPES, prefix, errors)
    validate_choice(record, "outcome", OUTCOMES, prefix, errors)
    validate_choice(record, "upgrade_signal", UPGRADE_SIGNALS, prefix, errors)
    validate_bool(record, "local_only", prefix, errors)
    validate_bool(record, "no_external_claim", prefix, errors)
    validate_bool(record, "false_positive", prefix, errors)
    for field in ("adversarial_summary", "decision", "false_positive_rule", "note"):
        validate_bounded_text(record, field, prefix, errors)
    validate_control_ids(record, prefix, errors)
    for field in ("action_taken", "checker_refs"):
        validate_text_list(record, field, prefix, errors)
    evidence_refs = validate_text_list(record, "evidence_refs", prefix, errors)
    evidence_ref_utils.validate_existing_repo_relative_refs(
        evidence_refs,
        ROOT,
        "evidence_refs",
        prefix,
        errors,
        allow_selectors=True,
    )
    replay_commands = validate_text_list(record, "replay_commands", prefix, errors)
    validate_outcome_rules(record, replay_commands, prefix, errors, warnings)


def required_text(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> str:
    value = text(record.get(field))
    if not value:
        errors.append(f"{prefix}: {field} must be non-empty text")
    return value


def validate_bounded_text(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    value = required_text(record, field, prefix, errors)
    if len(value) > MAX_TEXT:
        errors.append(f"{prefix}: {field} exceeds {MAX_TEXT} characters")


def validate_date(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    value = required_text(record, field, prefix, errors)
    if value and not DATE_RE.match(value):
        errors.append(f"{prefix}: {field} must use YYYY-MM-DD")


def validate_choice(record: dict[str, Any], field: str, choices: set[str], prefix: str, errors: list[str]) -> None:
    value = required_text(record, field, prefix, errors)
    if value and value not in choices:
        errors.append(f"{prefix}: {field} must be one of {sorted(choices)}")


def validate_bool(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    if not isinstance(record.get(field), bool):
        errors.append(f"{prefix}: {field} must be a boolean")


def validate_text_list(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> list[str]:
    values = text_list(record.get(field))
    if not values:
        errors.append(f"{prefix}: {field} must be a non-empty list")
        return []
    if len(values) > MAX_LIST_ITEMS:
        errors.append(f"{prefix}: {field} has too many items")
    for value in values:
        if len(value) > MAX_TEXT:
            errors.append(f"{prefix}: {field} item exceeds {MAX_TEXT} characters")
    return values


def validate_control_ids(record: dict[str, Any], prefix: str, errors: list[str]) -> None:
    control_ids = validate_text_list(record, "control_ids", prefix, errors)
    invalid = [control_id for control_id in control_ids if not CONTROL_RE.match(control_id)]
    if invalid:
        errors.append(f"{prefix}: control_ids has invalid values: {', '.join(invalid)}")


def validate_outcome_rules(record: dict[str, Any], replay_commands: list[str], prefix: str, errors: list[str], warnings: list[str]) -> None:
    accepted = text(record.get("outcome")) == "accepted"
    source_type = text(record.get("source_type"))
    if source_type == "synthetic-regression" and accepted:
        warnings.append(f"{prefix}: synthetic samples do not count as replay or real red-team burn-in")
    if source_type == "local-replay" and not replay_commands:
        errors.append(f"{prefix}: local-replay samples need replay_commands")
    if accepted and (record.get("local_only") is not True or record.get("no_external_claim") is not True):
        errors.append(f"{prefix}: accepted samples must set local_only=true and no_external_claim=true")
    if accepted and text(record.get("upgrade_signal")) == "candidate" and source_type != "real-incident":
        errors.append(f"{prefix}: upgrade_signal=candidate requires a real-incident sample")


def scan_for_forbidden(prefix: str, value: Any, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            if key_text in FORBIDDEN_KEYS:
                errors.append(f"{prefix}: forbidden raw context key: {key_text}")
            scan_for_forbidden(prefix, child, errors)
    elif isinstance(value, list):
        for child in value:
            scan_for_forbidden(prefix, child, errors)
    elif isinstance(value, str) and ".codex/runtime/" in value.replace("\\", "/"):
        errors.append(f"{prefix}: shared samples must not reference local runtime material")


def emit_text(report: RedTeamSampleReport) -> None:
    print("Agentic red-team sample audit:")
    print(f"- samples: {report.sample_path}")
    print(f"- records: {report.record_count}")
    print(f"- accepted replay or real samples: {report.accepted_replay_or_real_count}")
    print(f"- accepted real incidents: {report.accepted_real_incident_count}")
    print(f"- accepted by risk: {report.accepted_by_risk}")
    print(f"- accepted real by risk: {report.accepted_real_by_risk}")
    print(f"- false positives: {report.false_positive_count}")
    for warning in report.warnings:
        print(f"WARN: {warning}")
    if report.errors:
        for error in report.errors:
            print(f"ERROR: {error}")
    else:
        print("ERRORS: none")


def main() -> int:
    args = parse_args()
    report = build_report(Path(args.samples).expanduser())
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        emit_text(report)
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
