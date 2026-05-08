from __future__ import annotations


EXPECTED_WORKFLOWS = {
    ".github/workflows/governance-and-smoke.yml": {
        "jobs": {"governance", "windows-hook-runtime", "smoke"},
        "permissions": {"contents": "read"},
        "triggers": {"pull_request", "merge_group"},
        "tokens": {"check_branch_hygiene.py --markdown --strict", "check_pr_touch_conflicts.py"},
    },
    ".github/workflows/dependency-review.yml": {
        "jobs": {"dependency-review"},
        "permissions": {"contents": "read", "pull-requests": "read"},
        "triggers": {"pull_request", "merge_group"},
    },
    ".github/workflows/security-evidence.yml": {
        "jobs": {"security-evidence"},
        "permissions": {"contents": "read", "security-events": "write"},
        "triggers": {"pull_request", "push", "schedule", "workflow_dispatch"},
        "tokens": {"Run OpenSSF Scorecard", "Perform CodeQL Analysis", "Generate SBOM"},
    },
}
EXPECTED_REQUIRED_CHECKS = {"governance", "windows-hook-runtime", "smoke", "dependency-review"}
CONTROL_PLANE_PATHS = (
    "AGENTS.md",
    ".agents/**",
    ".codex/**",
    ".github/CODEOWNERS",
    ".github/pull_request_template.md",
    ".github/workflows/**",
    "docs/ai/**",
    "docs/requirements/**",
    "scripts/check_*",
)
