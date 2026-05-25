#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


RUNNER = ".codex/hooks/run_with_repo_python.sh"
CONTRACT_PRECONDITION_REVIEW_COMMAND = f"{RUNNER} scripts/check_harness_future_work_contracts.py"
CONTRACT_DECISION_FIELDS = (
    "auth_model",
    "endpoint_or_authority_scope",
    "redaction_or_boundary_model",
    "cost_or_stop_boundary",
)


@dataclass(frozen=True)
class FutureContractState:
    gap_id: str
    contract_id: str
    status: str
    contract_kind: str
    sample_collection_allowed: bool
    adr_required: bool
    adr_refs: list[str]
    missing_adr_refs: bool
    required_decision_fields: list[str]
    next_action: str
    review_command: str
    sample_collection_boundary: str
    evidence_refs: list[str]


def build_contract_states(
    future_gap_ids: list[str],
    contracts_by_gap: dict[str, dict[str, Any]],
) -> list[FutureContractState]:
    return [contract_state(gap_id, contracts_by_gap.get(gap_id)) for gap_id in future_gap_ids]


def contract_state(gap_id: str, record: dict[str, Any] | None) -> FutureContractState:
    if record is None:
        return FutureContractState(
            gap_id=gap_id,
            contract_id="missing",
            status="missing-contract",
            contract_kind="not-recorded",
            sample_collection_allowed=False,
            adr_required=True,
            adr_refs=[],
            missing_adr_refs=True,
            required_decision_fields=list(CONTRACT_DECISION_FIELDS),
            next_action=contract_next_action("missing-contract", False, True),
            review_command=CONTRACT_PRECONDITION_REVIEW_COMMAND,
            sample_collection_boundary=contract_sample_collection_boundary("missing-contract", False),
            evidence_refs=[],
        )
    adr_refs = text_list(record.get("adr_refs"))
    status = text(record.get("status"))
    sample_allowed = record.get("sample_collection_allowed") is True
    missing_adr_refs = adr_refs == ["none"] or not adr_refs
    return FutureContractState(
        gap_id=gap_id,
        contract_id=text(record.get("id")) or "missing-id",
        status=status,
        contract_kind=text(record.get("contract_kind")),
        sample_collection_allowed=sample_allowed,
        adr_required=record.get("adr_required") is True,
        adr_refs=adr_refs,
        missing_adr_refs=missing_adr_refs,
        required_decision_fields=list(CONTRACT_DECISION_FIELDS),
        next_action=contract_next_action(status, sample_allowed, missing_adr_refs),
        review_command=CONTRACT_PRECONDITION_REVIEW_COMMAND,
        sample_collection_boundary=contract_sample_collection_boundary(status, sample_allowed),
        evidence_refs=text_list(record.get("evidence_refs")),
    )


def contract_next_action(status: str, sample_allowed: bool, missing_adr_refs: bool) -> str:
    if status == "missing-contract":
        return "Add a future-work contract row before planning any sampling."
    if status == "retired":
        return "Keep this gap out of sample collection unless the future-work item is reopened."
    if status == "approved-for-sampling" and sample_allowed:
        return "Use the target sample checker and ledger review gate before collecting evidence."
    if status == "needs-adr" or missing_adr_refs:
        fields = ", ".join(CONTRACT_DECISION_FIELDS)
        return f"Create or approve an ADR/contract covering {fields}, then rerun this checker."
    return "Review this contract before collecting samples; sampling is still blocked."


def contract_sample_collection_boundary(status: str, sample_allowed: bool) -> str:
    if sample_allowed:
        return "Allowed by contract record; sample evidence still needs the target checker."
    if status == "retired":
        return "Retired future-work contract; do not collect samples unless reopened."
    if status == "missing-contract":
        return "Blocked because no future-work contract row exists."
    return "Blocked because sample_collection_allowed=false; do not collect samples until approval."


def text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def text_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]
