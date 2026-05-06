# GitHub Guardrails Maintenance

Use this reference when changing GitHub workflows, CODEOWNERS, Dependabot, dependency review, branch protection expectations, or remote guardrail checks.

## Repo Rules

- Workflows should keep least-privilege permissions, bounded timeouts, and concurrency cancellation unless a job has a documented reason to differ.
- Harness control-plane paths should stay covered by `.github/CODEOWNERS`.
- Dependency review and Dependabot are the default supply-chain guardrails for this stage.
- Scorecard, CodeQL, and SBOM may run as advisory evidence jobs before being promoted to required checks.
- Branch protection / ruleset configuration must be verified on GitHub before claiming required checks are enforced.
- Expected required checks are `governance`, `windows-hook-runtime`, `smoke`, and dependency review.
- Change-triggered follow-up summaries may be posted to GitHub Actions Summary, but they remain advisory and must not be described as required checks.
- CodeQL remains out of Stage-00 by default until the project enters release / CI maturity or has enough business code to justify it.

## Check

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_github_guardrails.py
```

`UNKNOWN` means the local repo cannot prove the remote state, usually because `gh` is not authenticated or lacks permission. Do not treat `UNKNOWN` as OK.
