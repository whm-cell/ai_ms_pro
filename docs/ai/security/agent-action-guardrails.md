# Agent Action Guardrails

更新时间：2026-05-08
状态：P2 high-impact action matrix landed

## Purpose

定义 Agent 可执行或可协助执行的高影响动作边界，避免 destructive、externally visible 或 permission-changing 动作被 hooks、脚本或 Agent 自动推进。

本文件是 policy matrix，不是操作日志。实际执行证据应留在 PR、命令输出、GitHub audit / API evidence、deployment record 或对应 status / handoff 摘要中。

## Global Rules

- 高影响动作必须先取得用户明确确认；确认应包含动作、目标对象和预期结果。
- 用户的泛化授权不等于逐项授权；例如“清理一下”不自动允许删除远端分支、关闭 PR、删库或发外部消息。
- Hooks 和检查器只能做 detection、warning、summary、policy reminder 或 evidence collection；不得自动执行高影响动作。
- 自动化脚本若支持高影响动作，默认必须 dry-run / report-only，并要求显式 flag 或人工确认路径。
- Secret、token、env value 和完整 credential 不写入治理文档、runtime、PR 描述或日志；只能记录 redacted name、scope、owner 和验证结论。
- 外部可见动作完成后必须回读验证，而不是只相信命令 exit code。

## High-Impact Action Matrix

| Action Surface | User Confirmation Required | Allowed Tools / Scripts | Verification Command / Evidence | May Hooks Automate It |
| --- | --- | --- | --- | --- |
| Remote branch deletion | Required for every branch deletion. Do not delete open PR branches directly; close or merge the PR first. | `scripts/check_branch_hygiene.py --strict` for audit; GitHub UI / `gh` / GitHub API only after explicit confirmation. | `git ls-remote --heads origin <branch>` shows absent; PR state is merged / closed when applicable; branch hygiene check reports no stale unmanaged branches. | No deletion. Hooks may report stale branches, active PR budget, failed open PRs, or cleanup candidates. |
| PR close | Required unless the user explicitly asked to close that specific PR. | GitHub app, `gh pr close`, or GitHub UI after confirming PR number, branch, and reason. | PR page / API state is `closed`; branch state is handled separately; PR comment or close reason records why it was closed. | No. Hooks may surface failed PRs, stale PRs, or overlap risk only. |
| PR merge | Required unless the user explicitly asked to merge that specific PR and merge preconditions are satisfied. | GitHub app, `gh pr merge`, or GitHub UI after confirming PR number, merge method, checks, and review state. | PR page / API state is `merged`; expected commit is on target branch; relevant checks and review evidence are attached or summarized. | No. Hooks may run required/advisory checks, summarize status, or flag missing evidence. |
| Workflow permission changes | Required for any `.github/workflows/*` permission increase, token scope expansion, OIDC change, protected path owner change, or remote guardrail setting change. | File edits through normal repo workflow; `scripts/check_github_guardrails.py`; GitHub UI / API for remote settings only after confirmation. | Diff shows least-privilege scope; `scripts/check_github_guardrails.py` output is recorded; remote branch protection / ruleset status is OK or explicitly UNKNOWN / plan-limited. | No permission mutation. Hooks may lint workflow shape, report missing minimal permissions, or summarize UNKNOWN remote gates. |
| Secret or environment changes | Required for create, update, delete, rotate, rename, or scope changes. Secret values must be supplied through the target secret manager, not through chat/docs/logs. | GitHub / cloud / deployment provider secret UI or API after confirmation; repo files may use `.env.example` placeholders only. | Secret name and scope are visible without value; application or CI proves the secret is usable; logs show redacted names only. | No. Hooks may redact, detect possible leaks, run secret scanners, or warn about changed env templates. |
| Deployments and releases | Required for production deployment, public preview publication, release creation, tag push, package publish, artifact signing, rollback, or environment promotion. | Provider UI / CLI, release scripts, `gh release`, package manager publish commands, or deployment workflows after confirming target environment and version. | Deployment URL / release page / tag / package version is visible; smoke or health check passes; rollback plan or rollback evidence is noted for production. | No external publish. Hooks may build artifacts, run smoke tests, produce release notes draft, or report deployment readiness. |
| External messages and sending | Required before sending Slack, email, Teams, issue/PR comments, customer messages, forms, webhooks, or other externally visible communication. Drafting does not require confirmation; sending does. | Slack/Gmail/Teams/GitHub tools, provider UI, webhook clients, or API calls after confirming audience, channel, body, and attachments. | Sent message permalink, message ID, issue/PR comment URL, email sent state, or API response is captured. | No sending. Hooks may draft summaries or warn that a pending external send needs confirmation. |
| Destructive file operations | Required for deleting files outside the requested scope, bulk deletion, force overwrite, history rewrite, permission changes, or generated cleanup that affects tracked files. | `git status`, `git diff`, targeted shell commands, repo cleanup scripts with dry-run first; destructive commands only after confirmation. | `git status --short` and relevant `git diff --stat` match the requested scope; deleted paths are expected; backups or recovery path are known when needed. | No destructive write. Hooks may report generated artifacts, stale files, or scope drift. |
| Destructive database operations | Required for schema drop, table truncate, data deletion, irreversible migration, production write, fixture reset, or destructive local DB command that cannot be trivially recreated. | Migration tools, DB clients, app admin scripts, or Docker compose commands after confirming environment, target, backup, and rollback. | Target environment is confirmed; migration / query result is recorded; backup or rollback evidence exists for non-local data; post-change smoke passes. | No. Hooks may run read-only checks, migration dry-runs, or warn about destructive migration names. |

## Confirmation Format

For high-impact actions, the user confirmation should make the target unambiguous:

```text
Confirm: <action> <target> because <reason>. Expected result: <result>.
```

Examples:

- `Confirm: close PR #12 because it is superseded by PR #15. Expected result: PR #12 closed, branch retained unless separately confirmed.`
- `Confirm: delete remote branch codex/old-spike because PR #8 is merged. Expected result: origin/codex/old-spike no longer exists.`
- `Confirm: deploy preview for commit abc123 to staging. Expected result: staging URL updated and smoke passes.`

## Automation Boundary

Allowed automation:

- detect changed high-impact surfaces;
- suggest review-required follow-ups;
- run read-only audits and smoke checks;
- prepare drafts, plans, summaries, or dry-run output;
- redact sensitive values from runtime and logs.

Disallowed automation:

- delete remote branches;
- close or merge PRs;
- increase workflow or remote repository permissions;
- create, update, delete, or reveal secrets;
- publish releases, packages, deployments, or messages;
- run destructive file or database writes.

## Review-Required Follow-Up

Changes to this document or high-impact action surfaces should trigger a review-required follow-up through `scripts/check_change_triggered_followups.py`.

This follow-up remains advisory: it points reviewers to the matrix and relevant verification commands, but it does not block by itself and does not prove the commands have run.

## Verification

Use the narrowest applicable check set:

```bash
.codex/hooks/run_with_repo_python.sh scripts/check_change_triggered_followups.py --files docs/ai/security/agent-action-guardrails.md
.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py
```

If `scripts/check_change_triggered_followups.py` changed, also run:

```bash
.codex/.venv/bin/python -m unittest tests.test_change_triggered_followups
```
