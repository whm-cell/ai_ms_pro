# Remote Merge Gates Evidence

更新时间：2026-05-08
状态：remote enforcement not proven；local guardrail evidence present

## Purpose

记录当前仓库对 GitHub 远端合并门禁的可证明状态，避免把本地 workflow 文件或本地检查误说成远端已强制。

## Current Evidence

| Area | Current Evidence | Status |
| --- | --- | --- |
| Workflows | `governance-and-smoke.yml`, `dependency-review.yml`, `security-evidence.yml` exist and are visible to GitHub API | OK |
| PR process | CODEOWNERS, PR template, PR touch conflict checker, `merge_group` workflow triggers exist | OK |
| Auto branch cleanup | GitHub `delete_branch_on_merge` is enabled | OK |
| Dependabot fan-out | `.github/dependabot.yml` groups updates and limits each ecosystem directory to 1 open PR | OK |
| Branch hygiene | `check_branch_hygiene.py --strict` reports 3/10 total open PRs, 1/3 Codex PRs, 2/4 Dependabot PRs, 0/0 failed open PRs, and 0 stale remote/local branches | OK |
| Local audit | `scripts/check_github_guardrails.py` reports local/remote guardrail status | OK |
| Branch protection | `check_github_guardrails.py` reports main branch protection 404 | NOT CONFIGURED / UNKNOWN |
| Required checks | Cannot prove `governance`, `windows-hook-runtime`, `smoke`, dependency review are required on `main` | UNKNOWN |
| Review gates | Cannot prove review, CODEOWNERS review, resolved conversations, or direct-push restrictions are enforced | UNKNOWN |
| Branch rulesets | `check_github_guardrails.py` returns no branch rulesets | WARN |

## Required Remote Gates

Remote branch protection or ruleset should require:

- `governance`
- `windows-hook-runtime`
- `smoke`
- dependency review job
- PR review and CODEOWNERS review for protected paths
- resolved conversations before merge
- no direct pushes to `main`
- merge queue / `merge_group` readiness when the repository plan supports it

## Operating Rule

- Treat `UNKNOWN` as “not proven,” not as OK.
- Do not mark OPEN-01 closed until `scripts/check_github_guardrails.py` or an administrator-provided screenshot / export proves the remote settings.
- If branch protection remains 404 or branch rulesets remain empty, the next action is remote repository settings by an administrator, not another local code change.
- Do not delete open PR branches directly. Merge or close the PR first, then rely on `delete_branch_on_merge` or `check_branch_hygiene.py`.
- CI blocks when active PR budgets are exceeded, failed open PRs exist, or stale/unmanaged branches are detected; explicit cleanup still requires `scripts/check_branch_hygiene.py --close-failed-dependabot-prs` or a human PR close action.

## Verification

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_github_guardrails.py
.codex/hooks/run_with_repo_python.sh scripts/check_branch_hygiene.py --strict
```
