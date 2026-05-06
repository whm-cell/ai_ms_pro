# Team PR Conflict Control Checklist

Use this reference when a team, multiple AIs, or multiple open PRs may touch the same repo surface.

## Inputs

- Current branch and intended base branch.
- Current changed files or planned touch set.
- Open PR changed files for the same base branch.
- Known `REQ/WS` mapping, or `未绑定`.
- High-risk path policy for the repo.

## Suggested Commands

Local touch set:

```bash
git diff --name-only --diff-filter=ACMR origin/main...HEAD
```

Open PR list:

```bash
gh pr list --state open --json number,title,url,headRefName,baseRefName
```

Files for one PR:

```bash
gh pr view <number> --json files,baseRefName,url,title
```

If GitHub API calls fail, mark the overlap result as `UNKNOWN` and do not claim the branch is collision-safe.

## High-Risk Paths

Treat these overlaps as requiring explicit coordination before merge:

- `AGENTS.md`
- `.agents/skills/**`
- `.codex/hooks.json`
- `.codex/harness.toml`
- `.github/workflows/**`
- `.github/CODEOWNERS`
- `.github/dependabot.yml`
- `scripts/check_*.py`
- `scripts/sync_hooks_config.py`
- `scripts/bootstrap_harness.py`
- `docs/requirements/traceability-matrix.md`
- `docs/requirements/source/**`
- `docs/requirements/normalized/**`
- `docs/requirements/workstreams/**`
- `docs/ai/status/**`
- `docs/ai/adr/**`
- lockfiles, schema files, migrations, auth/session boundaries, shared routing, generated API clients, or deployment manifests in product repos.

## Decision Rules

- Same high-risk file in another open PR: block until the owners sequence or split the work.
- Same ordinary file in another open PR: coordinate and document the expected merge order.
- Same domain but different files: warn, request owner review, and check integration tests.
- No visible overlap but GitHub state is unavailable: proceed only if the user accepts the `UNKNOWN` risk.
- Merge queue enabled but required workflows lack `merge_group`: do not claim queued merges are protected.

## Output Template

```text
Collaboration Mode:
Current Touch Set:
Open PR Overlap Result:
High-Risk Files:
Required Coordination Action:
PR Template Coverage:
CODEOWNERS / Merge Queue Readiness:
Governance Writeback Decision:
```
