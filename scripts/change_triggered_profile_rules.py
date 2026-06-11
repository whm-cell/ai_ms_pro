from __future__ import annotations


PROFILE_AND_UPGRADE_RULES: tuple[dict[str, object], ...] = (
    {
        "name": "task-profile-audit",
        "level": "advisory",
        "ci_coverage": "governance job validates the sample artifact; real task audits remain manual / burn-in",
        "patterns": (
            "docs/ai/standards/task-profile-audit*",
            "docs/ai/agentic-harness-gap-roadmap.md",
            "scripts/change_triggered_profile_rules.py",
            "scripts/check_task_profile_audit.py",
            "scripts/evidence_ref_utils.py",
            "tests/test_task_profile_audit.py",
        ),
        "commands": (
            ".codex/hooks/run_with_repo_python.sh scripts/check_task_profile_audit.py",
            "python3 tests/test_task_profile_audit.py",
        ),
        "references": ("docs/ai/standards/task-profile-audit.md",),
        "reason": "Task profile audit evidence or scoped-governance reading profile rules changed.",
    },
    {
        "name": "harness-upgrade-decisions",
        "level": "advisory",
        "ci_coverage": "governance job validates decisions for ready-for-upgrade gaps",
        "patterns": (
            "docs/ai/standards/harness-upgrade-decisions.jsonl",
            "docs/ai/agentic-harness-gap-roadmap.md",
            "scripts/change_triggered_profile_rules.py",
            "scripts/check_harness_upgrade_decisions.py",
            "scripts/evidence_ref_utils.py",
            "tests/test_harness_upgrade_decisions.py",
        ),
        "commands": (
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_upgrade_decisions.py",
            "python3 tests/test_harness_upgrade_decisions.py",
        ),
        "references": ("docs/ai/standards/harness-upgrade-decisions.jsonl",),
        "reason": "Harness gap upgrade readiness decision evidence changed.",
    },
    {
        "name": "next-best-work-review",
        "level": "advisory",
        "ci_coverage": "governance job emits warning-only review gaps",
        "patterns": (
            ".agents/skills/repo-governed-coding/references/governance-checklist.md",
            "docs/ai/templates/next-best-work-review.md",
            "docs/ai/status/_template.md",
            "scripts/ai_governance_next_best_work.py",
            "scripts/runtime_handoff_renderer.py",
            "scripts/change_triggered_profile_rules.py",
            "tests/test_next_best_work_review.py",
            "tests/test_runtime_reducer_metadata.py",
        ),
        "commands": (
            "python3 tests/test_next_best_work_review.py",
            "python3 tests/test_runtime_reducer_metadata.py",
            ".codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py",
        ),
        "references": (
            ".agents/skills/repo-governed-coding/references/governance-checklist.md",
            "docs/ai/templates/next-best-work-review.md",
        ),
        "reason": "Next-work review policy, template, renderer, or warning behavior changed.",
    },
)
