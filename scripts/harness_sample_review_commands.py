from __future__ import annotations


REVIEW_COMMANDS_BY_LEDGER = {
    "docs/ai/standards/pre-tool-use-preflight-samples.jsonl": (
        ".codex/hooks/run_with_repo_python.sh scripts/check_pre_tool_use_preflight_samples.py"
    ),
    "docs/ai/standards/loop-scope-monitor-samples.jsonl": (
        ".codex/hooks/run_with_repo_python.sh scripts/check_loop_scope_monitor_samples.py"
    ),
    "docs/ai/checkpoints/resume-samples.jsonl": ".codex/hooks/run_with_repo_python.sh scripts/check_stage_checkpoints.py",
    "docs/ai/standards/local-trace-summary-samples.jsonl": (
        ".codex/hooks/run_with_repo_python.sh scripts/check_local_trace_summary_samples.py"
    ),
    "docs/ai/standards/task-profile-audit-sample.jsonl": (
        ".codex/hooks/run_with_repo_python.sh scripts/check_task_profile_audit.py"
    ),
    "docs/ai/security/agentic-red-team-samples.jsonl": (
        ".codex/hooks/run_with_repo_python.sh scripts/check_agentic_red_team_samples.py"
    ),
    "docs/ai/standards/harness-sample-gap-evidence.jsonl": (
        ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_gap_evidence.py"
    ),
    "docs/ai/standards/harness-future-work-contracts.jsonl": (
        ".codex/hooks/run_with_repo_python.sh scripts/check_harness_future_work_contracts.py"
    ),
    "docs/ai/standards/harness-upgrade-decisions.jsonl": (
        ".codex/hooks/run_with_repo_python.sh scripts/check_harness_upgrade_decisions.py"
    ),
}

PLACEHOLDER_REPLACEMENT_REVIEW_COMMAND = (
    ".codex/hooks/run_with_repo_python.sh scripts/check_harness_placeholder_replacement.py <candidate-jsonl>"
)

PENDING_APPEND_REVIEW_COMMAND = (
    ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_append.py <candidate-jsonl>"
)

SAMPLE_OUTCOME_REVIEW_COMMAND = (
    ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_outcome.py <candidate-jsonl>"
)

FUTURE_WORK_CONTRACT_CANDIDATE_REVIEW_COMMAND = (
    ".codex/hooks/run_with_repo_python.sh scripts/check_harness_future_work_contract_candidate.py <candidate-jsonl>"
)

UPGRADE_DECISION_CANDIDATE_REVIEW_COMMAND = (
    ".codex/hooks/run_with_repo_python.sh scripts/check_harness_upgrade_decision_candidate.py <candidate-jsonl>"
)


def review_command_for(ledger_path: str) -> str:
    return REVIEW_COMMANDS_BY_LEDGER.get(ledger_path, "unknown")
