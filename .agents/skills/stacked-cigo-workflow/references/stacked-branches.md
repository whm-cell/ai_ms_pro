# Stacked Branches

Use stacked branches when a new requirement depends on code from an unmerged PR.

## Shape

```text
main
  \
   A  current PR branch, waiting for CI/repair/merge
    \
     B  follow-up branch that depends on A
```

## Start B From A

If the current worktree is clean and does not need to keep servicing A:

```powershell
git status --short --branch
git switch -c codex/<new-task>
```

If A may still need checks or repairs, prefer a separate worktree:

```powershell
git worktree add ..\<repo>-<new-task> -b codex/<new-task> codex/<parent-pr-branch>
```

Open B's PR against A while A is still unmerged. This keeps review diffs scoped to B.

## After A Merges

In B's worktree:

```powershell
git fetch origin --prune
git switch codex/<new-task>
git rebase origin/main
git diff --stat origin/main...HEAD
```

Then retarget B's PR base to `main`. Confirm the diff no longer contains A-only changes.

If conflicts occur:

1. Stop and list conflict files.
2. Resolve by preserving B's business intent on top of `main`.
3. Run fast gates.
4. Continue the rebase only after the conflict resolution is understood.

## When Not To Stack

Do not stack when the follow-up does not require A's code. Branch from `origin/main` instead.

If only one or two commits from A are needed, branch from `origin/main` and cherry-pick those commits.

## References

- GitHub Stacked PRs overview: https://github.github.com/gh-stack/introduction/overview/
- GitHub gh-stack: https://github.github.com/gh-stack/
- gh-stack skill/library: https://mcpservers.org/agent-skills/github/gh-stack
- Graphite stacked diffs guide: https://graphite.com/guides/stacked-diffs
