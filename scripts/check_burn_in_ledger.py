#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re

import evidence_ref_utils


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "docs" / "ai" / "check-registry.md"
DEFAULT_LEDGER = ROOT / "docs" / "ai" / "check-burn-in-ledger.md"
SAMPLES_RE = re.compile(r"^(?P<accepted>[0-9]+)/(?P<target>2)$")
DECISIONS = {"keep-candidate", "ready-for-adr", "demote-to-advisory", "promote-to-blocking"}
UPGRADE_DECISIONS = {"ready-for-adr", "promote-to-blocking"}


@dataclass(frozen=True)
class BurnInLedgerRow:
    check: str
    accepted_samples: int
    sample_target: int
    remaining_samples: int
    evidence_refs: list[str]
    false_positives: str
    repair_path: str
    cost: str
    current_decision: str
    next_evidence: str
    upgrade_eligible: bool
    upgrade_review_needed: bool


@dataclass(frozen=True)
class LedgerResult:
    registry_path: str
    ledger_path: str
    blocking_candidate_count: int
    ledger_row_count: int
    decision_counts: dict[str, int]
    total_remaining_samples: int
    checks_needing_samples: list[str]
    upgrade_eligible_checks: list[str]
    upgrade_review_needed_checks: list[str]
    rows: list[BurnInLedgerRow]
    errors: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate check burn-in ledger coverage.")
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY), help="Path to check-registry.md.")
    parser.add_argument("--ledger", default=str(DEFAULT_LEDGER), help="Path to check-burn-in-ledger.md.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def markdown_tables(text: str) -> list[list[dict[str, str]]]:
    tables: list[list[dict[str, str]]] = []
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        if not table_header_at(lines, index):
            index += 1
            continue
        headers = split_row(lines[index])
        rows: list[dict[str, str]] = []
        index += 2
        while index < len(lines) and lines[index].strip().startswith("|"):
            values = split_row(lines[index])
            if len(values) == len(headers):
                rows.append(dict(zip(headers, values)))
            index += 1
        tables.append(rows)
    return tables


def table_header_at(lines: list[str], index: int) -> bool:
    if index + 1 >= len(lines):
        return False
    return lines[index].strip().startswith("|") and set(split_row(lines[index + 1])) <= {"---", ":---", "---:", ":---:"}


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def strip_code(value: str) -> str:
    return value.strip().strip("`")


def registry_candidates(path: Path) -> set[str]:
    candidates: set[str] = set()
    for table in markdown_tables(path.read_text(encoding="utf-8")):
        for row in table:
            if row.get("Level") == "`blocking-candidate`":
                candidates.add(strip_code(row.get("Check", "")))
    return candidates


def ledger_rows(path: Path) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for table in markdown_tables(path.read_text(encoding="utf-8")):
        if not table or "Accepted samples" not in table[0]:
            continue
        for row in table:
            check = strip_code(row.get("Check", ""))
            if check:
                rows[check] = row
    return rows


def validate(registry_path: Path = DEFAULT_REGISTRY, ledger_path: Path = DEFAULT_LEDGER) -> LedgerResult:
    errors: list[str] = []
    candidates = registry_candidates(registry_path)
    rows = ledger_rows(ledger_path)
    evidence_base = evidence_ref_base(ledger_path)
    for check in sorted(candidates - set(rows)):
        errors.append(f"missing ledger row for blocking-candidate check: {check}")
    for check in sorted(set(rows) - candidates):
        errors.append(f"ledger row is not a blocking-candidate check: {check}")
    parsed_rows = [validate_row(check, row, errors, evidence_base) for check, row in sorted(rows.items())]
    decision_counts = count_by_decision(parsed_rows)
    checks_needing_samples = [row.check for row in parsed_rows if row.remaining_samples > 0]
    upgrade_eligible_checks = [row.check for row in parsed_rows if row.upgrade_eligible]
    upgrade_review_needed_checks = [row.check for row in parsed_rows if row.upgrade_review_needed]
    return LedgerResult(
        registry_path=relative(registry_path),
        ledger_path=relative(ledger_path),
        blocking_candidate_count=len(candidates),
        ledger_row_count=len(rows),
        decision_counts=decision_counts,
        total_remaining_samples=sum(row.remaining_samples for row in parsed_rows),
        checks_needing_samples=checks_needing_samples,
        upgrade_eligible_checks=upgrade_eligible_checks,
        upgrade_review_needed_checks=upgrade_review_needed_checks,
        rows=parsed_rows,
        errors=errors,
    )


def evidence_ref_base(ledger_path: Path) -> Path:
    resolved = ledger_path.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError:
        return ledger_path.parent.resolve()
    return ROOT


def validate_row(check: str, row: dict[str, str], errors: list[str], evidence_base: Path) -> BurnInLedgerRow:
    samples = row.get("Accepted samples", "")
    accepted, target = parse_samples(check, samples, errors)
    evidence_refs = parse_evidence_refs(row.get("Evidence refs", ""))
    if accepted > 0 and not evidence_refs:
        errors.append(f"{check}: accepted samples require Evidence refs")
    validate_evidence_refs(check, evidence_refs, evidence_base, errors)
    decision = row.get("Current decision", "")
    if decision not in DECISIONS:
        errors.append(f"{check}: Current decision must be one of {sorted(DECISIONS)}")
    elif decision in UPGRADE_DECISIONS and accepted < target:
        errors.append(f"{check}: {decision} requires Accepted samples to be {target}/{target}, got {samples}")
    upgrade_review_needed = accepted >= target and decision == "keep-candidate"
    for field in ("False positives", "Repair path", "Cost", "Next evidence"):
        if not row.get(field, "").strip():
            errors.append(f"{check}: {field} must be non-empty")
    if upgrade_review_needed and "upgrade decision" not in row.get("Next evidence", "").lower():
        errors.append(f"{check}: 2/2 keep-candidate rows must route Next evidence to upgrade decision review")
    return BurnInLedgerRow(
        check=check,
        accepted_samples=accepted,
        sample_target=target,
        remaining_samples=max(target - accepted, 0),
        evidence_refs=evidence_refs,
        false_positives=row.get("False positives", ""),
        repair_path=row.get("Repair path", ""),
        cost=row.get("Cost", ""),
        current_decision=decision,
        next_evidence=row.get("Next evidence", ""),
        upgrade_eligible=accepted >= target,
        upgrade_review_needed=upgrade_review_needed,
    )


def parse_samples(check: str, samples: str, errors: list[str]) -> tuple[int, int]:
    sample_match = SAMPLES_RE.match(samples)
    if not sample_match:
        errors.append(f"{check}: Accepted samples must use N/2 format")
        return 0, 2
    accepted = int(sample_match.group("accepted"))
    target = int(sample_match.group("target"))
    if accepted > target:
        errors.append(f"{check}: Accepted samples cannot exceed target: {samples}")
    return accepted, target


def parse_evidence_refs(value: str) -> list[str]:
    normalized = value.strip()
    if not normalized or normalized == "-":
        return []
    return [item.strip() for item in normalized.split(",") if item.strip()]


def validate_evidence_refs(check: str, evidence_refs: list[str], evidence_base: Path, errors: list[str]) -> None:
    evidence_ref_utils.validate_existing_repo_relative_refs(
        evidence_refs,
        evidence_base,
        "Evidence refs",
        check,
        errors,
        allow_selectors=True,
    )


def count_by_decision(rows: list[BurnInLedgerRow]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        if row.current_decision:
            counts[row.current_decision] = counts.get(row.current_decision, 0) + 1
    return dict(sorted(counts.items()))


def render_markdown(result: LedgerResult) -> str:
    lines = [
        "Check burn-in ledger audit:",
        f"- registry: {result.registry_path}",
        f"- ledger: {result.ledger_path}",
        f"- blocking candidates: {result.blocking_candidate_count}",
        f"- ledger rows: {result.ledger_row_count}",
        f"- decision counts: {result.decision_counts}",
        f"- remaining sample slots: {result.total_remaining_samples}",
        f"- checks needing samples: {result.checks_needing_samples}",
        f"- upgrade-eligible checks: {result.upgrade_eligible_checks}",
        f"- upgrade review needed checks: {result.upgrade_review_needed_checks}",
    ]
    if result.rows:
        lines.append("")
        lines.append("| Check | Accepted samples | Remaining | Evidence refs | Decision | Next evidence |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for row in result.rows:
            samples = f"{row.accepted_samples}/{row.sample_target}"
            evidence_refs = ", ".join(row.evidence_refs) if row.evidence_refs else "-"
            lines.append(
                f"| `{row.check}` | {samples} | {row.remaining_samples} | {evidence_refs} | "
                f"{row.current_decision or '-'} | {row.next_evidence or '-'} |"
            )
    if result.errors:
        lines.append("")
        lines.append("Errors:")
        lines.extend(f"- {error}" for error in result.errors)
    else:
        lines.append("")
        lines.append("Errors: none")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    result = validate(Path(args.registry).expanduser(), Path(args.ledger).expanduser())
    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print(render_markdown(result))
    return 1 if result.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
