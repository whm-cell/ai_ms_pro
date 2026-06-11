from __future__ import annotations


def ledger_action_for_status(readiness: str, source_type_needed: str, pending_slot_status: str) -> str:
    if readiness == "ready-for-upgrade-discussion":
        return "review-upgrade-decision"
    if source_type_needed == "contract-blocked":
        return "define-contract-precondition"
    if source_type_needed == "local-only":
        return "no-sample-collection"
    if pending_slot_status == "review-ready":
        return "review-existing-pending-slot"
    if pending_slot_status == "placeholder":
        return "fill-existing-placeholder"
    if pending_slot_status == "mixed":
        return "inspect-mixed-pending-slots"
    return "append-new-pending-slot"


def source_type_for_gap(gap: object, readiness: str) -> str:
    gap_id = getattr(gap, "id", "")
    gap_status = getattr(gap, "status", "")
    if readiness == "ready-for-upgrade-discussion":
        return "upgrade-decision"
    if gap_status == "future-work" and readiness == "needs-contract-or-adr-first":
        return "contract-blocked"
    if gap_status == "accepted-local-sample":
        return "local-only"
    if gap_id == "GAP-GUARDRAIL-PREFLIGHT-WARNING":
        return "real-tool-call"
    if gap_id == "GAP-RUNTIME-LOOP-SCOPE-WARNING":
        return "real-session"
    if gap_id == "GAP-TRACE-LOCAL-SUMMARY-BURNIN":
        return "real-local-report"
    if gap_id == "GAP-WORKFLOW-TASK-PROFILE-AUDIT":
        return "real-task"
    if gap_id == "GAP-TRACE-REMOTE-INTEROP":
        return "real-interop-run"
    if gap_id.startswith("GAP-AGENTIC-"):
        return "real-incident"
    if gap_id == "GAP-RUNTIME-STAGE-CHECKPOINT-RESUME":
        return "cross-task-resume"
    return "real-sample"


def capture_gate_for_gap(
    gap: object,
    readiness: str,
    ledger_action: str,
    source_type_needed: str,
) -> tuple[str, str]:
    gap_id = getattr(gap, "id", "")
    gap_area = getattr(gap, "area", "")
    if readiness == "ready-for-upgrade-discussion":
        return (
            "upgrade-decision-review",
            "Review a bounded keep/promote/defer decision; do not append sample evidence.",
        )
    if source_type_needed == "contract-blocked":
        return (
            "contract-precondition-first",
            "Define the future-work contract and ADR coverage before any sample collection is routed.",
        )
    if source_type_needed == "local-only":
        return (
            "no-sample-collection",
            "Local-only evidence is already bounded; do not collect another sample unless the roadmap status changes.",
        )
    if ledger_action == "fill-existing-placeholder":
        return (
            "replace-placeholder-after-real-event",
            "Wait for the matching real event, replace the placeholder row, then run the replacement review gate.",
        )
    if gap_id == "GAP-RUNTIME-STAGE-CHECKPOINT-RESUME":
        return (
            "requires-cross-task-resume",
            "Only a resume outside the harness-hardening task class satisfies this readiness metric.",
        )
    if gap_id == "GAP-TRACE-LOCAL-SUMMARY-BURNIN":
        return (
            "requires-distinct-task-class-report",
            "Only a local trace summary from a distinct task class satisfies this readiness metric.",
        )
    if gap_id == "GAP-TRACE-REMOTE-INTEROP":
        return (
            "requires-approved-remote-interop",
            "Only an explicitly confirmed ADR-017 remote interop probe qualifies; local-only or inferred interop does not.",
        )
    if gap_id == "GAP-AGENTIC-CASCADE-STOP":
        return (
            "requires-approved-bounded-incident",
            "Only an ADR-016 bounded local cascade-control incident qualifies; do not include raw prompts, transcripts, secrets, or external payloads.",
        )
    if gap_id == "GAP-GUARDRAIL-CONFIRMATION":
        return (
            "requires-user-confirmed-high-impact-action",
            "Only a real high-impact action with explicit user confirmation qualifies.",
        )
    if gap_area == "security-evidence":
        return (
            "requires-security-workflow-event",
            "Only a real PR, release, dependency, scheduled security, CodeQL, SBOM, or dependency-review event qualifies.",
        )
    if gap_area == "workflow-skills":
        return (
            "requires-workflow-task-event",
            "Only a real workflow task matching the trigger qualifies.",
        )
    if gap_area == "agentic-red-team":
        return (
            "requires-bounded-real-incident",
            "Only a bounded real incident summary qualifies; do not include raw prompts, transcripts, secrets, or external payloads.",
        )
    return (
        "requires-real-event",
        "Only a real event matching the trigger and evidence checklist qualifies.",
    )
