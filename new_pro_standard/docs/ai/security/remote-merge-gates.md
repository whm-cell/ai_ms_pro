# Remote Merge Gates Evidence

更新时间：2026-05-09
状态：private GitHub Free plan-limited；首轮 PR + main push CI burn-in 已通过；当前无升级 GitHub plan 计划

## Purpose

记录当前仓库对 GitHub 远端合并门禁的可证明状态，避免把本地 workflow 文件或本地检查误说成远端已强制。

## Plan Constraint

当前仓库已切换为 private，GitHub 账号为 Free。GitHub API 对 `main` branch protection 与 repository rulesets 返回：

- `Upgrade to GitHub Pro or make this repository public to enable this feature. (HTTP 403)`

因此当前缺口不再按“继续本地实现即可关闭”处理，而是记录为 plan-limited ceiling。当前没有升级 GitHub plan 或把仓库改为 public 的计划，所以本仓库只把 GitHub 作为 CI / PR / security artifact evidence 面；不能把 branch protection、rulesets、required checks、review gates 或 merge queue 声明为远端强制。

## Current Evidence

| Area | Current Evidence | Status |
| --- | --- | --- |
| Workflows | `governance-and-smoke.yml`, `dependency-review.yml`, `security-evidence.yml` exist and are visible to GitHub API | OK |
| PR process | CODEOWNERS, PR template, PR touch conflict checker, `merge_group` workflow triggers exist | OK |
| Auto branch cleanup | GitHub `delete_branch_on_merge` is enabled | OK |
| Dependabot fan-out | `.github/dependabot.yml` groups updates and limits each ecosystem directory to 1 open PR | OK |
| Branch hygiene | `check_branch_hygiene.py --strict` reports 2/10 total open PRs, 0/3 Codex PRs, 2/4 Dependabot PRs, 0/0 failed open PRs, and 0 stale remote/local branches after PR #11 was merged and the local stale branch was deleted | OK |
| Local audit | `scripts/check_github_guardrails.py` reports local/remote guardrail status | OK |
| Branch protection | GitHub API returns private-Free plan limit HTTP 403 | PLAN-LIMITED / UNKNOWN |
| Required checks | Cannot be enforced on `main` through branch protection / rulesets under current plan | PLAN-LIMITED |
| Review gates | PR review, CODEOWNERS review, resolved conversations, and direct-push restrictions cannot be proven as remote gates under current plan | PLAN-LIMITED |
| Branch rulesets | GitHub API returns private-Free plan limit HTTP 403 | PLAN-LIMITED / UNKNOWN |

## CI Evidence Burn-in Snapshot

Last audited: 2026-05-09 18:55 Asia/Shanghai.

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
| Governance And Smoke | [25598728368](https://github.com/whm-cell/ai_ms_pro/actions/runs/25598728368) | `pull_request` | `codex/harness-ci-burn-in` at `9b23fd522586bd77126d58ab12c2c3494112cf51` | `governance`, `windows-hook-runtime`, `smoke`; hook sync, advisory summary, branch hygiene summary, PR touch conflict check, unit tests, AI governance, code-shape, Windows Python / hook runner tests, WS-01 / WS-02 browser smoke | success |
| Dependency Review | [25598728367](https://github.com/whm-cell/ai_ms_pro/actions/runs/25598728367) | `pull_request` | same head | `dependency-review` job and Dependency Review step | success |
| Security Evidence | [25598728374](https://github.com/whm-cell/ai_ms_pro/actions/runs/25598728374) | `pull_request` | same head | Scorecard, CodeQL artifact, SBOM artifact | success |

Latest proven successful `main` push evidence:

| Workflow | Run | Event | Head | Proven jobs / steps | Conclusion |
| --- | --- | --- | --- | --- | --- |
| Governance And Smoke | [25599034611](https://github.com/whm-cell/ai_ms_pro/actions/runs/25599034611) | `push` | `main` at `c1f170faa701885882a0ed7a2105c1054fe956ea` | `governance`, `windows-hook-runtime`, `smoke`; main advisory summary, main branch hygiene summary, unit tests, AI governance, code-shape, Windows Python / hook runner tests, WS-01 / WS-02 browser smoke | success |
| Security Evidence | [25599034597](https://github.com/whm-cell/ai_ms_pro/actions/runs/25599034597) | `push` | same head | Scorecard, CodeQL analysis, `codeql-results` artifact, SBOM generation, `sbom-cyclonedx` artifact | success |

Observed non-gate evidence:

- `Dependabot Updates` is active. Recent dynamic update runs include successes and one `npm_and_yarn in /.` failure. This does not prove or disprove branch protection because Dependabot update runs are not the merge gate surface for `main`.
- Older Governance And Smoke PR runs on `codex/stage-00-harness-guardrails-ci` had failures before the later successful run. Treat this as burn-in history, not as current required-check enforcement.
- `Security Evidence` run [25599034597](https://github.com/whm-cell/ai_ms_pro/actions/runs/25599034597) succeeded, but CodeQL emitted `Code scanning is not enabled for this repository` annotations while uploading to GitHub code scanning / database endpoints. Treat this as advisory platform-setting evidence under the current private-Free boundary, not as a required-gate failure.

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

当前没有升级 GitHub plan 的计划。本节只保留为未来条件变化时的参考；不要把它当成当前路线图或实现目标。

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
