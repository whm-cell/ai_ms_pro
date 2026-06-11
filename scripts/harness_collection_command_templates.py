from __future__ import annotations


REAL_SAMPLE_LEDGER_ACTIONS = ("append-new-pending-slot", "fill-existing-placeholder")

CAPTURE_GATE_SUMMARY_LABELS = {
    "replace-placeholder-after-real-event": ("placeholder replacement", "placeholder-replacement"),
    "requires-approved-bounded-incident": ("approved bounded incident", "approved-bounded-incident"),
    "requires-approved-remote-interop": ("remote interop", "remote-interop"),
    "requires-bounded-real-incident": ("bounded real incident", "bounded-real-incident"),
    "requires-cross-task-resume": ("cross-task resume", "cross-task-resume"),
    "requires-distinct-task-class-report": ("distinct task class report", "distinct-task-class-report"),
    "requires-security-workflow-event": ("security workflow event", "security-event"),
    "requires-user-confirmed-high-impact-action": (
        "user confirmed high impact action",
        "user-confirmed-high-impact-action",
    ),
    "requires-workflow-task-event": ("workflow task event", "workflow-task-event"),
}
LEDGER_ACTION_SUMMARY_LABELS = {
    "append-new-pending-slot": ("append new pending slot", "append-new-pending-slot"),
    "fill-existing-placeholder": ("fill existing placeholder", "fill-existing-placeholder"),
}
READINESS_SUMMARY_LABELS = {
    "needs-first-real-sample": ("needs first real sample", "needs-first-real-sample"),
    "needs-more-real-samples": ("needs more real samples", "needs-more-real-samples"),
}

FOCUSED_CAPTURE_GATE_COMMAND_TEMPLATES: tuple[str, ...] = (
    ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
    "--capture-gate {capture_gate} --capture-card",
    ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --capture-gate {capture_gate}",
    ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
    "--capture-gate {capture_gate} --summary",
    ".codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py "
    "--include-future --include-accepted --capture-gate {capture_gate} --json",
    ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
    "--capture-focus --capture-focus-gate {capture_gate}",
)
FOCUSED_REAL_LEDGER_ACTION_COMMAND_TEMPLATES: tuple[str, ...] = (
    ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
    "--ledger-action {ledger_action} --capture-card",
    ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py "
    "--ledger-action {ledger_action}",
    ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
    "--ledger-action {ledger_action} --summary",
    ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
    "--capture-focus --capture-focus-ledger-action {ledger_action} --capture-focus-limit 0",
)
FOCUSED_REAL_READINESS_COMMAND_TEMPLATES: tuple[str, ...] = (
    ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
    "--readiness {readiness} --capture-card",
    ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --readiness {readiness}",
    ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
    "--readiness {readiness} --summary",
    ".codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py "
    "--include-future --include-accepted --readiness {readiness} --json",
    ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
    "--capture-focus --capture-focus-readiness {readiness}",
)
FOCUSED_REAL_AREA_COMMAND_TEMPLATES: tuple[str, ...] = (
    ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
    "--area {area} --capture-card",
    ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --area {area}",
    ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
    "--area {area} --summary",
    ".codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py "
    "--include-future --include-accepted --area {area} --json",
    ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
    "--capture-focus --capture-focus-area {area}",
)
FOCUSED_REAL_PRIORITY_COMMAND_TEMPLATES: tuple[str, ...] = (
    ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
    "--priority {priority} --capture-card",
    ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --priority {priority}",
    ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
    "--priority {priority} --summary",
    ".codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py "
    "--include-future --include-accepted --priority {priority} --json",
    ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
    "--capture-focus --capture-focus-priority {priority}",
)
WORKFLOW_CAPTURE_GATE_COMMAND_TEMPLATES: tuple[str, ...] = (
    "python3 scripts/plan_harness_sample_collection.py --capture-gate {capture_gate} --capture-card",
    "python3 scripts/check_harness_sample_templates.py --capture-gate {capture_gate}",
    "python3 scripts/build_harness_sample_intake_bundle.py --capture-gate {capture_gate} --summary",
    "python3 scripts/check_harness_burn_in_readiness.py --include-future --include-accepted "
    "--capture-gate {capture_gate}",
    "python3 scripts/check_harness_pending_samples.py --capture-focus --capture-focus-gate {capture_gate} "
    "--capture-focus-limit 0",
)
WORKFLOW_REAL_LEDGER_ACTION_COMMAND_TEMPLATES: tuple[str, ...] = (
    "python3 scripts/plan_harness_sample_collection.py --ledger-action {ledger_action} --capture-card",
    "python3 scripts/check_harness_sample_templates.py --ledger-action {ledger_action}",
    "python3 scripts/build_harness_sample_intake_bundle.py --ledger-action {ledger_action} --summary",
    "python3 scripts/check_harness_pending_samples.py --capture-focus "
    "--capture-focus-ledger-action {ledger_action} --capture-focus-limit 0",
)
WORKFLOW_REAL_READINESS_COMMAND_TEMPLATES: tuple[str, ...] = (
    "python3 scripts/plan_harness_sample_collection.py --readiness {readiness} --capture-card",
    "python3 scripts/check_harness_sample_templates.py --readiness {readiness}",
    "python3 scripts/build_harness_sample_intake_bundle.py --readiness {readiness} --summary",
    "python3 scripts/check_harness_burn_in_readiness.py --include-future --include-accepted "
    "--readiness {readiness}",
    "python3 scripts/check_harness_pending_samples.py --capture-focus --capture-focus-readiness {readiness} "
    "--capture-focus-limit 0",
)
WORKFLOW_REAL_AREA_COMMAND_TEMPLATES: tuple[str, ...] = (
    "python3 scripts/plan_harness_sample_collection.py --area {area} --capture-card",
    "python3 scripts/check_harness_sample_templates.py --area {area}",
    "python3 scripts/build_harness_sample_intake_bundle.py --area {area} --summary",
    "python3 scripts/check_harness_burn_in_readiness.py --include-future --include-accepted "
    "--area {area}",
    "python3 scripts/check_harness_pending_samples.py --capture-focus --capture-focus-area {area} "
    "--capture-focus-limit 0",
)
WORKFLOW_REAL_PRIORITY_COMMAND_TEMPLATES: tuple[str, ...] = (
    "python3 scripts/plan_harness_sample_collection.py --priority {priority} --capture-card",
    "python3 scripts/check_harness_sample_templates.py --priority {priority}",
    "python3 scripts/build_harness_sample_intake_bundle.py --priority {priority} --summary",
    "python3 scripts/check_harness_burn_in_readiness.py --include-future --include-accepted "
    "--priority {priority}",
    "python3 scripts/check_harness_pending_samples.py --capture-focus --capture-focus-priority {priority} "
    "--capture-focus-limit 0",
)
WORKFLOW_CAPTURE_GATE_SECTION_TEMPLATES: tuple[tuple[str, str], ...] = (
    ("### Harness sample collection queue ({label})", "cat /tmp/harness-sample-collection-{slug}.md"),
    ("### Harness burn-in readiness ({label})", "cat /tmp/harness-burn-in-readiness-{slug}.md"),
    ("### Harness sample template drift ({label})", "cat /tmp/harness-sample-templates-{slug}.md"),
    ("### Harness sample intake bundle ({label})", "cat /tmp/harness-sample-intake-{slug}.md"),
    ("### Harness pending next capture focus ({label})", "cat /tmp/harness-pending-capture-focus-{slug}.md"),
)
WORKFLOW_LEDGER_ACTION_SECTION_TEMPLATES: tuple[tuple[str, str], ...] = (
    ("### Harness sample collection queue ({label})", "cat /tmp/harness-sample-collection-{slug}.md"),
    ("### Harness sample template drift ({label})", "cat /tmp/harness-sample-templates-{slug}.md"),
    ("### Harness sample intake bundle ({label})", "cat /tmp/harness-sample-intake-{slug}.md"),
    ("### Harness pending next capture focus ({label})", "cat /tmp/harness-pending-capture-focus-{slug}.md"),
)
WORKFLOW_READINESS_SECTION_TEMPLATES: tuple[tuple[str, str], ...] = (
    ("### Harness sample collection queue ({label})", "cat /tmp/harness-sample-collection-{slug}.md"),
    ("### Harness burn-in readiness ({label})", "cat /tmp/harness-burn-in-readiness-{slug}.md"),
    ("### Harness sample template drift ({label})", "cat /tmp/harness-sample-templates-{slug}.md"),
    ("### Harness sample intake bundle ({label})", "cat /tmp/harness-sample-intake-{slug}.md"),
    ("### Harness pending next capture focus ({label})", "cat /tmp/harness-pending-capture-focus-{slug}.md"),
)
WORKFLOW_PENDING_FOCUS_SECTION_TEMPLATES: tuple[tuple[str, str], ...] = (
    ("### Harness pending next capture focus ({label})", "cat /tmp/harness-pending-capture-focus-{slug}.md"),
)
WORKFLOW_AREA_PRIORITY_SECTION_TEMPLATES: tuple[tuple[str, str], ...] = (
    ("### Harness sample collection queue ({label})", "cat /tmp/harness-sample-collection-{slug}.md"),
    ("### Harness burn-in readiness ({label})", "cat /tmp/harness-burn-in-readiness-{slug}.md"),
    ("### Harness sample template drift ({label})", "cat /tmp/harness-sample-templates-{slug}.md"),
    ("### Harness sample intake bundle ({label})", "cat /tmp/harness-sample-intake-{slug}.md"),
    ("### Harness pending next capture focus ({label})", "cat /tmp/harness-pending-capture-focus-{slug}.md"),
)
