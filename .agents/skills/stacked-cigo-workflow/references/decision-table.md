# Decision Table

Use this table before creating, syncing, repairing, or retargeting branches.

| Situation | Action | PR base | Notes |
| --- | --- | --- | --- |
| New work does not need an unmerged PR | Create `codex/<task>` from `origin/main` | `main` | Fetch first. Keep the diff independent. |
| New work needs branch A that is not merged | Create branch B from A, preferably in a new worktree | A | This is a stacked branch. Do not mix B work into A. |
| Branch A is in PR/CI and may need repairs | Keep repair work isolated from B | A | If A checks fail, repair A in a PR repair worktree. |
| Branch A merged to `main`; branch B still open | Rebase B onto `origin/main`, then retarget B to `main` | `main` | Confirm B's diff only contains B work before pushing or updating the PR. |
| Branch B does not need all of A | Start B from `origin/main`, then cherry-pick the needed commits | `main` | Prefer this when only a narrow commit is needed. |
| Current worktree has unstaged or untracked work | Do not switch/reset casually | unchanged | Commit, stash, or create a new worktree first. |
| User asks to sync local `main` after a PR merge | Fetch, switch to `main`, then fast-forward or reset only after confirming clean state | n/a | Use `reset --hard origin/main` only for an explicit clean sync. |

Minimum preflight:

```powershell
git status --short --branch
git fetch origin --prune
```

Use `git worktree list` before adding or removing worktrees.
