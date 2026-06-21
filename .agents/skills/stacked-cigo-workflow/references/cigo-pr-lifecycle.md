# CIGO PR Lifecycle

This repo uses a fast local gate plus asynchronous PR verification model.

## Submit A PR

1. Inspect the working tree and intended touch set.
2. Create or use a `codex/` feature branch; do not push `main`.
3. Stage only intentional files. Exclude `.codex/runtime/**` unless a tracked README/template is intentionally changed.
4. Run local fast gates selected by `docs/ai/verification-minimums.md`.
5. Commit and push the feature branch.
6. Open a draft PR unless the user explicitly requests ready-for-review.
7. Let GitHub Actions run longer portable smoke, Windows, or security evidence checks.

Typical fast checks for staged mixed changes:

```powershell
git diff --cached --check
powershell -NoProfile -ExecutionPolicy Bypass -File .codex/hooks/run_with_repo_python.ps1 scripts/check_code_shape.py --staged
```

Use the POSIX `.codex/hooks/run_with_repo_python.sh` wrapper when working outside PowerShell. Broaden only for the changed surface.

## Monitor PR Checks

Report status only unless the user asks for repair. Distinguish:

- local fast gates
- PR smoke
- governance/security evidence
- live-provider checks skipped by design
- remote required-check / branch-protection state that is `UNKNOWN`

PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .codex/hooks/run_with_repo_python.ps1 scripts/report_pr_checks.py <PR>
```

POSIX:

```bash
.codex/hooks/run_with_repo_python.sh scripts/report_pr_checks.py <PR>
```

If checks fail, name the failing workflow/job and summarize the key log lines.

## Repair Failed Checks

When current local work may continue, use an isolated repair worktree.

PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .codex/hooks/run_with_repo_python.ps1 scripts/start_pr_repair_worktree.py <PR>
```

POSIX:

```bash
.codex/hooks/run_with_repo_python.sh scripts/start_pr_repair_worktree.py <PR>
```

Then work only inside the printed repair worktree:

1. Inspect failure logs.
2. Make the smallest fix.
3. Run relevant fast gates.
4. Commit inside the repair worktree.
5. Push with the exact command printed by the helper, usually `git push origin HEAD:<head-branch>`.

Do not stage or modify unrelated work in the user's current worktree.

## Merge To Main

Before merging:

1. Confirm PR is open.
2. Mark ready if it is still draft and the user asked to merge.
3. Confirm expected head SHA has not moved when metadata is available.
4. Confirm checks are green, or get explicit user confirmation for any known exception.
5. Merge to `main`.
6. Confirm `merged=true` and remote `main` moved.

Do not auto-sync the user's local development branch after merge. Ask or wait for a sync request.

## Boundary

Current repository GitHub branch protection / required checks / no-direct-push enforcement may still be remote `UNKNOWN`. This workflow is an operator guardrail and local evidence boundary, not proof that GitHub enforces every rule remotely.
