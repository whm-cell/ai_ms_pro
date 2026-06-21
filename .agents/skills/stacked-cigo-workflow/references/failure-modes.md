# Failure Modes

## Child PR Contains Parent Diff

Symptoms:

- B's PR shows all of A plus B.
- Review is noisy after A already merged.

Fix:

```powershell
git fetch origin --prune
git switch codex/<child>
git rebase origin/main
git diff --stat origin/main...HEAD
```

Retarget the PR base to `main` after A merges.

## Parent PR Fails While Child Work Has Started

Do not repair A from B. Use the CIGO repair worktree flow for A, then rebase B after A's fixed PR merges.

## Local Worktree Is Dirty During Sync

Do not switch branches, reset, or overwrite. Offer:

- commit current work
- stash current work
- create a new worktree

Use the option that keeps PR repair and new feature work separate.

## Runtime Files Keep Appearing

Check whether they are ignored:

```powershell
git status --short .codex/runtime
git ls-files .codex/runtime
```

If runtime files are untracked, keep them out of commits. If a tracked runtime file is stale, promote useful facts to canonical docs first, then remove it in a harness-maintenance task.

## API Or GitHub Access Is Limited

Treat unknown PR/check status as unknown, not green. Do not merge based on a stale local assumption.

## Reset Risk

Never run `git reset --hard` against a computed or ambiguous branch. It is acceptable only for an explicitly requested clean local sync after verifying the target branch and worktree state.
