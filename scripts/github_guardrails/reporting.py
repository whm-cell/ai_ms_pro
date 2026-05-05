from __future__ import annotations

from .model import Check


def recommended_actions(checks: list[Check]) -> list[str]:
    actions: list[str] = []
    for check in checks:
        if check.name == "branch protection" and check.status == "UNKNOWN":
            actions.append(
                "Remote branch protection could not be proven. Configure GitHub branch protection or rulesets when the plan/repo visibility allows it."
            )
        elif check.name == "branch protection" and check.status == "WARN":
            actions.append(
                "Update branch protection to require PR review, CODEOWNERS review, conversation resolution, and expected required checks."
            )
        elif check.name == "branch rulesets" and check.status == "UNKNOWN":
            actions.append(
                "Remote branch rulesets could not be proven. Keep OPEN-01 blocked instead of claiming main is protected."
            )
        elif check.name == "branch rulesets" and check.status == "WARN":
            actions.append(
                "Update branch rulesets so required checks include governance, windows-hook-runtime, smoke, and dependency-review."
            )
    return actions


def emit_text(checks: list[Check]) -> None:
    print("GitHub guardrails check:")
    for check in checks:
        print(f"[{check.status}] {check.name}: {check.detail}")
    counts = {status: sum(1 for check in checks if check.status == status) for status in ("OK", "WARN", "UNKNOWN")}
    print(f"Summary: OK={counts['OK']} WARN={counts['WARN']} UNKNOWN={counts['UNKNOWN']}")
    actions = recommended_actions(checks)
    if actions:
        print("Recommended actions:")
        for action in actions:
            print(f"- {action}")
