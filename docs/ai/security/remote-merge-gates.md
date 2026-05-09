# Remote Merge Gates Evidence

更新时间：2026-05-08
状态：private GitHub Free plan-limited；local/CI guardrail evidence present

## Purpose

记录当前仓库对 GitHub 远端合并门禁的可证明状态，避免把本地 workflow 文件或本地检查误说成远端已强制。

## Plan Constraint

当前仓库已切换为 private，GitHub 账号为 Free。GitHub API 对 `main` branch protection 与 repository rulesets 返回：

- `Upgrade to GitHub Pro or make this repository public to enable this feature. (HTTP 403)`

因此当前缺口不再按“继续本地实现即可关闭”处理，而是记录为 plan-limited ceiling。除非升级 GitHub 计划或把仓库改为 public，否则不能把 branch protection、rulesets、required checks、review gates 或 merge queue 声明为远端强制。

## Current Evidence

| Area | Current Evidence | Status |
| --- | --- | --- |
| Workflows | `governance-and-smoke.yml`, `dependency-review.yml`, `security-evidence.yml` exist and are visible to GitHub API | OK |
| PR process | CODEOWNERS, PR template, PR touch conflict checker, `merge_group` workflow triggers exist | OK |
| Auto branch cleanup | GitHub `delete_branch_on_merge` is enabled | OK |
| Dependabot fan-out | `.github/dependabot.yml` groups updates and limits each ecosystem directory to 1 open PR | OK |
| Branch hygiene | `check_branch_hygiene.py --strict` reports 3/10 total open PRs, 0/3 Codex PRs, 3/4 Dependabot PRs, 0/0 failed open PRs, and 0 stale remote/local branches | OK |
| Local audit | `scripts/check_github_guardrails.py` reports local/remote guardrail status | OK |
| Branch protection | GitHub API returns private-Free plan limit HTTP 403 | PLAN-LIMITED / UNKNOWN |
| Required checks | Cannot be enforced on `main` through branch protection / rulesets under current plan | PLAN-LIMITED |
| Review gates | PR review, CODEOWNERS review, resolved conversations, and direct-push restrictions cannot be proven as remote gates under current plan | PLAN-LIMITED |
| Branch rulesets | GitHub API returns private-Free plan limit HTTP 403 | PLAN-LIMITED / UNKNOWN |

## CI Evidence Burn-in Snapshot

Last audited: 2026-05-08 10:09 Asia/Shanghai.

Read-only commands used:

- `gh repo view --json nameWithOwner,visibility,isPrivate,viewerPermission,deleteBranchOnMerge,defaultBranchRef`
- `gh workflow list --all`
- `gh run list --limit 20 --json databaseId,workflowName,displayTitle,event,status,conclusion,createdAt,updatedAt,headBranch,headSha,url`
- `gh run view <run-id> --json databaseId,workflowName,event,status,conclusion,createdAt,updatedAt,jobs,url`
- `gh api repos/whm-cell/ai_ms_pro/branches/main/protection`
- `gh api repos/whm-cell/ai_ms_pro/rulesets`

Confirmed remote repository state:

- Repository: `whm-cell/ai_ms_pro`
- Visibility: private
- Default branch: `main`
- Current viewer permission: admin
- `delete_branch_on_merge`: enabled

Confirmed workflow visibility:

| Workflow | GitHub API status | Local workflow file | Trigger boundary |
| --- | --- | --- | --- |
| Governance And Smoke | active | `.github/workflows/governance-and-smoke.yml` | `pull_request`, `merge_group`, `push` |
| Dependency Review | active | `.github/workflows/dependency-review.yml` | `pull_request`, `merge_group`; job runs only on `pull_request` |
| Security Evidence | active | `.github/workflows/security-evidence.yml` | `pull_request`, `push`, schedule, manual dispatch |

Latest proven successful PR evidence:

| Workflow | Run | Event | Head | Proven jobs / steps | Conclusion |
| --- | --- | --- | --- | --- | --- |
| Governance And Smoke | [25532589524](https://github.com/whm-cell/ai_ms_pro/actions/runs/25532589524) | `pull_request` | `dependabot/github_actions/github-actions-runtime-0fa9a95d58` at `bfe8d7b57892f592a901fb0cd2a668c20cba66c9` | `governance`, `windows-hook-runtime`, `smoke`; hook sync, advisory summary, branch hygiene summary, PR touch conflict check, unit tests, AI governance, code-shape, Windows Python / hook runner tests, four browser smoke checks | success |
| Dependency Review | [25532589508](https://github.com/whm-cell/ai_ms_pro/actions/runs/25532589508) | `pull_request` | same head | `dependency-review` job and Dependency Review step | success |
| Security Evidence | [25532589506](https://github.com/whm-cell/ai_ms_pro/actions/runs/25532589506) | `pull_request` | same head | Scorecard, CodeQL initialize/analyze/upload, SBOM generate/upload | success |

Latest proven successful `main` push evidence:

| Workflow | Run | Event | Head | Proven jobs / steps | Conclusion |
| --- | --- | --- | --- | --- | --- |
| Governance And Smoke | [25532557241](https://github.com/whm-cell/ai_ms_pro/actions/runs/25532557241) | `push` | `main` at `9ef8c0dac2c838b23b816ed7ba3c1e8a2ceff427` | `governance`, `windows-hook-runtime`, `smoke`; main advisory summary, main branch hygiene summary, unit tests, AI governance, code-shape, Windows Python / hook runner tests, four browser smoke checks | success |
| Security Evidence | [25532557228](https://github.com/whm-cell/ai_ms_pro/actions/runs/25532557228) | `push` | same head | security evidence workflow completed | success |

Observed non-gate evidence:

- `Dependabot Updates` is active. Recent dynamic update runs include successes and one `npm_and_yarn in /.` failure. This does not prove or disprove branch protection because Dependabot update runs are not the merge gate surface for `main`.
- Older Governance And Smoke PR runs on `codex/stage-00-harness-guardrails-ci` had failures before the later successful run. Treat this as burn-in history, not as current required-check enforcement.

Still not proven:

- No remote required-check enforcement is proven for `governance`, `windows-hook-runtime`, `smoke`, dependency review, or security evidence.
- No remote review gate, CODEOWNERS review gate, resolved-conversation gate, direct-push restriction, or merge queue requirement is proven.
- Branch protection and branch rulesets still return private-Free plan limit HTTP 403; this remains `UNKNOWN`, not OK.

## Current Maximum Boundary

Under private GitHub Free, the repository should maximize the surfaces that remain available:

- Run local and CI checks as evidence gates: `governance`, `windows-hook-runtime`, `smoke`, `dependency-review`, branch hygiene, and PR touch conflict checks.
- Keep PR template, CODEOWNERS, Dependabot grouping, branch hygiene budget, and touch-set conflict checks as process / review evidence, not remote-enforced policy.
- Keep `scripts/check_github_guardrails.py` reporting plan-limited `UNKNOWN` for branch protection and rulesets; never rewrite those as OK.
- Keep Scorecard, CodeQL, SBOM, and dependency review security outputs as advisory / artifact evidence unless the repository plan supports blocking gates.
- Treat branch protection / rulesets / required reviews / required checks / merge queue as future upgrade targets that activate only after upgrading GitHub plan or making the repository public.

## Future Upgrade Gates

If the repository plan or visibility later supports remote enforcement, branch protection or rulesets should require:

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
- For private GitHub Free, treat the branch protection / rulesets 403 as plan-limited, not as a local engineering blocker.
- Do not claim remote required checks, review gates, conversation resolution, direct-push restrictions, or merge queue are enforced until `scripts/check_github_guardrails.py` or an administrator-provided screenshot / export proves the remote settings under a supported plan.
- If the repository is upgraded or made public, re-run guardrails and revisit `Future Upgrade Gates`.
- Do not delete open PR branches directly. Merge or close the PR first, then rely on `delete_branch_on_merge` or `check_branch_hygiene.py`.
- CI blocks when active PR budgets are exceeded, other failed open PRs exist, or stale/unmanaged branches are detected; PR runs pass `--current-pr` so the branch hygiene gate does not self-block on the current PR's own check rollup. Explicit cleanup still requires `scripts/check_branch_hygiene.py --close-failed-dependabot-prs` or a human PR close action.

## Verification

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_github_guardrails.py
.codex/hooks/run_with_repo_python.sh scripts/check_branch_hygiene.py --strict
.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py
git diff --check
```
