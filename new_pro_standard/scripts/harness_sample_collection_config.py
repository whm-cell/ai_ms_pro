from __future__ import annotations

PENDING_STATES = (
    "any",
    "with-pending",
    "without-pending",
    "with-review-ready-pending",
    "without-review-ready-pending",
    "with-placeholder-pending",
    "without-placeholder-pending",
)
PRIORITY_LEVELS = ("P0", "P1", "P2", "P3")
LEDGER_ACTIONS = (
    "append-new-pending-slot",
    "define-contract-precondition",
    "fill-existing-placeholder",
    "inspect-mixed-pending-slots",
    "no-sample-collection",
    "review-existing-pending-slot",
    "review-upgrade-decision",
)
CAPTURE_GATES = (
    "contract-precondition-first",
    "no-sample-collection",
    "replace-placeholder-after-real-event",
    "requires-approved-bounded-incident",
    "requires-approved-remote-interop",
    "requires-bounded-real-incident",
    "requires-cross-task-resume",
    "requires-distinct-task-class-report",
    "requires-real-event",
    "requires-security-workflow-event",
    "requires-user-confirmed-high-impact-action",
    "requires-workflow-task-event",
    "upgrade-decision-review",
)
DEDICATED_TARGETS = {
    "GAP-GUARDRAIL-PREFLIGHT-WARNING": "docs/ai/standards/pre-tool-use-preflight-samples.jsonl",
    "GAP-RUNTIME-LOOP-SCOPE-WARNING": "docs/ai/standards/loop-scope-monitor-samples.jsonl",
    "GAP-RUNTIME-STAGE-CHECKPOINT-RESUME": "docs/ai/checkpoints/resume-samples.jsonl",
    "GAP-TRACE-LOCAL-SUMMARY-BURNIN": "docs/ai/standards/local-trace-summary-samples.jsonl",
    "GAP-WORKFLOW-TASK-PROFILE-AUDIT": "docs/ai/standards/task-profile-audit-sample.jsonl",
    "GAP-AGENTIC-TOOL-SQUATTING": "docs/ai/security/agentic-red-team-samples.jsonl",
    "GAP-AGENTIC-MEMORY-POISONING": "docs/ai/security/agentic-red-team-samples.jsonl",
    "GAP-AGENTIC-A2A-HANDOFF": "docs/ai/security/agentic-red-team-samples.jsonl",
    "GAP-AGENTIC-SANDBOX-HONESTY": "docs/ai/security/agentic-red-team-samples.jsonl",
}
FUTURE_WORK_CONTRACT_TARGET = "docs/ai/standards/harness-future-work-contracts.jsonl"
UPGRADE_DECISION_TARGET = "docs/ai/standards/harness-upgrade-decisions.jsonl"
PRIORITIES = {
    "GAP-GUARDRAIL-PREFLIGHT-WARNING": "P0",
    "GAP-RUNTIME-STAGE-CHECKPOINT-RESUME": "P1",
    "GAP-RUNTIME-LOOP-SCOPE-WARNING": "P1",
    "GAP-TRACE-LOCAL-SUMMARY-BURNIN": "P1",
    "GAP-SEC-SCHEDULED-RUN": "P1",
    "GAP-SEC-PR-DEPENDENCY": "P1",
    "GAP-SEC-CONTROL-MATRIX-BURNIN": "P1",
    "GAP-WORKFLOW-TASK-PROFILE-AUDIT": "P2",
    "GAP-AGENTIC-CASCADE-STOP": "P2",
}
TRIGGERS = {
    "GAP-GUARDRAIL-PREFLIGHT-WARNING": "Capture the next real PreToolUse warning before a large-output, destructive, or external action.",
    "GAP-RUNTIME-LOOP-SCOPE-WARNING": "Capture the next real Stop loop/scope warning from a long or repeated-validation session.",
    "GAP-RUNTIME-STAGE-CHECKPOINT-RESUME": "Capture a resume that uses stage-checkpoint/v1 outside the harness-hardening task class.",
    "GAP-SEC-SCHEDULED-RUN": "Capture the next scheduled or manually dispatched security-evidence workflow run.",
    "GAP-SEC-PR-DEPENDENCY": "Capture the next dependency PR, release, CodeQL, SBOM, or dependency-review event.",
    "GAP-GUARDRAIL-CONFIRMATION": "Capture the next high-impact action that requires explicit user confirmation.",
    "GAP-GUARDRAIL-SOURCE-BOUNDARY": "Capture the next PRD, issue, Slack, web, or pasted-source normalization boundary.",
    "GAP-SEC-CONTROL-MATRIX-BURNIN": "Capture the next real security or guardrail sample mapped to an AC control id.",
    "GAP-WORKFLOW-CROSS-WS": "Capture the next cross-workstream task where workflow skills are loaded or skipped.",
    "GAP-WORKFLOW-SIMPLE-SKIP": "Capture the next simple task where Candidate workflow skills are explicitly skipped.",
    "GAP-WORKFLOW-PR-OVERLAP": "Capture the next real PR overlap or multi-agent edit conflict.",
    "GAP-TRACE-OTLP-PILOT-BURNIN": "Capture the next local capture-server OTLP HTTP JSON export run with explicit endpoint and send boundary.",
    "GAP-TRACE-LOCAL-SUMMARY-BURNIN": "Capture the next local trace summary report from a different task class.",
    "GAP-WORKFLOW-TASK-PROFILE-AUDIT": "Review the existing upgrade decision before collecting more task-profile evidence.",
    "GAP-TRACE-REMOTE-INTEROP": (
        "Capture the next explicitly confirmed remote interop probe under ADR-017, including endpoint class, "
        "send decision, redaction state, failure mode, and stop boundary."
    ),
    "GAP-AGENTIC-CASCADE-STOP": (
        "Capture the next bounded local cascade-control incident under ADR-016 without raw transcript, prompt, "
        "secret, external payload, or autonomous retry evidence."
    ),
}
