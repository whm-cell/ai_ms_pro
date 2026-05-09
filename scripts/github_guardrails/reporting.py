from __future__ import annotations

from .model import Check


PLAN_LIMIT_MARKERS = (
    "Upgrade to GitHub Pro or make this repository public",
    "upgrade to github pro or make this repository public",
)


def is_plan_limited(detail: str) -> bool:
    return any(marker in detail for marker in PLAN_LIMIT_MARKERS)


def recommended_actions(checks: list[Check]) -> list[str]:
    actions: list[str] = []
    for check in checks:
        if check.name == "branch protection" and check.status == "UNKNOWN":
            if is_plan_limited(check.detail):
                actions.append(
                    "Private GitHub Free plan limit detected for branch protection. Treat remote enforcement as plan-limited, keep local/CI evidence gates, and enable branch protection only after upgrading the plan or making the repository public."
                )
            else:
                actions.append(
                    "Remote branch protection could not be proven. Configure GitHub branch protection or rulesets when the plan/repo visibility allows it."
                )
        elif check.name == "branch protection" and check.status == "WARN":
            actions.append(
                "Update branch protection to require PR review, CODEOWNERS review, conversation resolution, and expected required checks."
            )
        elif check.name == "branch rulesets" and check.status == "UNKNOWN":
            if is_plan_limited(check.detail):
                actions.append(
                    "Private GitHub Free plan limit detected for branch rulesets. Keep required-check rulesets as a future upgrade path; do not treat this as a local-code gap."
                )
            else:
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
