# Local Sync And Cleanup

Cleanup must preserve user work and keep canonical truth in shared docs, not runtime traces.

## Sync Local Main

Use this only when the user asks to sync local `main` after remote `main` moved.

```powershell
git status --short --branch
git fetch origin --prune
git switch main
git reset --hard origin/main
git status --short --branch
```

Only use the hard reset after confirming the target is `main`, the worktree is clean, and the user wants a clean sync. If local `main` has uncommitted work, stop and propose commit, stash, or worktree.

## Sync A Development Branch

For an active development branch:

```powershell
git status --short --branch
git fetch origin --prune
git rebase origin/main
```

Use merge instead of rebase only when the branch history must be preserved or the user asks for merge-based sync.

## Cleanup PR Repair Worktrees

After a PR is merged:

```powershell
git worktree list
git -C <repair-worktree> status --short --branch
git worktree remove <repair-worktree>
```

Do not remove the user's main development worktree. Do not remove a worktree with uncommitted changes without explicit confirmation.

## Runtime Artifacts

`.codex/runtime/**` is local recovery evidence only. Do not use it as a source of requirements, architecture truth, or completion claims.

Allowed cleanup actions:

- Keep runtime outputs untracked.
- Remove transient runtime files only when they are not needed for current recovery.
- Promote durable findings into `docs/ai/*`, `docs/requirements/*`, ADRs, status, handoffs, or deterministic checks.
- Check tracked runtime files with `git ls-files .codex/runtime`.

Do not delete tracked README/templates under `.codex/runtime` unless a harness change explicitly retires them.

## Legacy Prompt Docs

If old prompt docs duplicate this skill, prefer adding a short pointer to this skill rather than maintaining two full procedures. Delete legacy docs only when the user explicitly agrees or the content has been fully absorbed into this skill.
