# GitHub Guardrails Maintenance

Use this reference when changing GitHub workflows, CODEOWNERS, Dependabot, dependency review, branch protection expectations, or remote guardrail checks.

## Repo Rules

- Workflows should keep least-privilege permissions, bounded timeouts, and concurrency cancellation unless a job has a documented reason to differ.
- Harness control-plane paths should stay covered by `.github/CODEOWNERS`.
- Dependency review and Dependabot are the default supply-chain guardrails for this stage.
- Scorecard, CodeQL, and SBOM may run as advisory evidence jobs before being promoted to required checks.
- Branch protection / ruleset configuration must be verified on GitHub before claiming required checks are enforced.
- For private repositories on GitHub Free, branch protection and rulesets may return a plan-limit HTTP 403. Treat that as a plan-limited ceiling, not a local-code gap.
- Expected future required checks are `governance`, `windows-hook-runtime`, `smoke`, and dependency review.
- Change-triggered follow-up summaries may be posted to GitHub Actions Summary, but they remain advisory and must not be described as required checks.
- CodeQL remains out of Stage-00 by default until the project enters release / CI maturity or has enough business code to justify it.

## Check

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_github_guardrails.py
```

`UNKNOWN` means the local repo cannot prove or use the remote state, usually because `gh` is not authenticated, lacks permission, or the current GitHub plan/visibility does not support the feature. Do not treat `UNKNOWN` as OK; if the detail is plan-limited, keep the local/CI evidence boundary and document the future upgrade gate.
