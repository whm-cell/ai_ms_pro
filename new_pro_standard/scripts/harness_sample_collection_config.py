from __future__ import annotations


SAMPLE_LEDGER = "docs/ai/standards/harness-sample-gap-evidence.jsonl"
WATCHLIST_DOC = "docs/ai/harness-real-sample-watchlist.md"
TEMPLATE_DOC = "docs/ai/templates/harness-sample-gap-evidence-record.md"
REVIEW_COMMAND = (
    ".codex/hooks/run_with_repo_python.sh "
    "scripts/check_harness_sample_gap_evidence.py --samples <candidate-jsonl>"
)

PRIORITIES = {
    "GAP-STARTER-HIGH-IMPACT-ACTION": "P0",
    "GAP-STARTER-PRETOOL-WARNING": "P0",
    "GAP-STARTER-STOP-WARNING": "P1",
    "GAP-STARTER-CROSS-TASK-RESUME": "P1",
    "GAP-STARTER-SECURITY-EVIDENCE": "P1",
    "GAP-STARTER-WORKFLOW-SKILL": "P2",
    "GAP-STARTER-PR-OVERLAP": "P2",
    "GAP-STARTER-REMOTE-INTEROP": "P3",
}

SOURCE_TYPES = {
    "GAP-STARTER-HIGH-IMPACT-ACTION": "real-user-action",
    "GAP-STARTER-PRETOOL-WARNING": "real-user-action",
    "GAP-STARTER-STOP-WARNING": "real-workflow-run",
    "GAP-STARTER-CROSS-TASK-RESUME": "real-workflow-task",
    "GAP-STARTER-SECURITY-EVIDENCE": "real-security-event",
    "GAP-STARTER-WORKFLOW-SKILL": "real-workflow-task",
    "GAP-STARTER-PR-OVERLAP": "real-workflow-task",
    "GAP-STARTER-REMOTE-INTEROP": "real-interop-run",
}

CAPTURE_GATES = {
    "GAP-STARTER-HIGH-IMPACT-ACTION": "requires-explicit-user-confirmation",
    "GAP-STARTER-PRETOOL-WARNING": "requires-real-warning",
    "GAP-STARTER-STOP-WARNING": "requires-real-stop-warning",
    "GAP-STARTER-CROSS-TASK-RESUME": "requires-cross-task-resume",
    "GAP-STARTER-SECURITY-EVIDENCE": "requires-real-security-event",
    "GAP-STARTER-WORKFLOW-SKILL": "requires-real-workflow-task",
    "GAP-STARTER-PR-OVERLAP": "requires-real-pr-overlap",
    "GAP-STARTER-REMOTE-INTEROP": "requires-project-adr-or-contract",
}
