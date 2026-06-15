from __future__ import annotations

from change_triggered_rule_builder import rule


ENTERPRISE_CODE_BOUNDARY_RULES: tuple[dict[str, object], ...] = (
    rule(
        "enterprise-code-boundaries",
        "review-required",
        "manual review via enterprise code boundary skill; no checker or blocking promotion in v1",
        (
            ".agents/skills/enterprise-code-boundary-maintenance/**",
            "docs/ai/standards/logging-redaction-boundary.md",
            "docs/ai/standards/error-contract-boundary.md",
            "docs/ai/standards/runtime-side-effect-boundary.md",
            "scripts/change_triggered_enterprise_boundary_rules.py",
            "app/api/**",
            "app/**/route.*",
            "lib/**/*logger*",
            "lib/**/*Logger*",
            "lib/**/*error*",
            "lib/**/*Error*",
            "lib/**/*provider*",
            "lib/**/*Provider*",
            "lib/**/*client*",
            "lib/**/*Client*",
            "lib/**/*adapter*",
            "lib/**/*Adapter*",
            "lib/**/*repository*",
            "lib/**/*Repository*",
            "lib/**/*queue*",
            "lib/**/*Queue*",
            "services/**/*client*",
            "services/**/*Client*",
            "services/**/*adapter*",
            "services/**/*Adapter*",
            "services/**/*repository*",
            "services/**/*Repository*",
            "services/**/*queue*",
            "services/**/*Queue*",
        ),
        (
            ".codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py",
            ".codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py",
            ".codex/hooks/run_with_repo_python.sh scripts/check_repo_skills.py",
        ),
        (
            ".agents/skills/enterprise-code-boundary-maintenance/SKILL.md",
            "docs/ai/standards/logging-redaction-boundary.md",
            "docs/ai/standards/error-contract-boundary.md",
            "docs/ai/standards/runtime-side-effect-boundary.md",
        ),
        "Enterprise logging, error, runtime side-effect, provider, adapter, client, repository, queue, or API boundary may have changed.",
    ),
)
