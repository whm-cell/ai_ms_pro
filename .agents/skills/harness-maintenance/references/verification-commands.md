# Verification Commands

Use this reference to select checks after harness, governance, requirement, or skill changes.

## Command Selection

- Changed files should be mapped to likely missed follow-ups first: `.codex/hooks/run_with_repo_python.sh scripts/check_change_triggered_followups.py`
- Shared governance truth changed: `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- Staged code or harness code changed: `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --staged`
- Default context, AGENTS, status, ADR, or skill surface grew: `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- Active handoffs reached budget or stage compression is planned: `.codex/hooks/run_with_repo_python.sh scripts/check_archive_candidates.py`
- Repo-local skills changed: `.codex/hooks/run_with_repo_python.sh scripts/check_repo_skills.py`
- PRD, `REQDOC`, `REQ`, `WS`, matrix, or technical assumptions changed: `.codex/hooks/run_with_repo_python.sh scripts/check_requirements_shape.py`
- Candidate skills are being promoted or evaluated: `.codex/hooks/run_with_repo_python.sh scripts/check_skill_usage_samples.py`
- GitHub workflows, CODEOWNERS, Dependabot, dependency review, or remote guardrails changed: `.codex/hooks/run_with_repo_python.sh scripts/check_github_guardrails.py`
- Skill structure changed: `python3 /Users/coolm/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-dir>`

## Windows Equivalent

Use `.codex/hooks/run_with_repo_python.ps1` with the same script path when working from PowerShell.

## Warning Interpretation

- `check_change_triggered_followups.py` is advisory. It suggests checks and references from changed files; it does not prove those commands have already run.
- `check_github_guardrails.py` may report remote `UNKNOWN` when credentials, permissions, or GitHub configuration are unavailable. Do not restate `UNKNOWN` as OK.
- `check_skill_usage_samples.py` may report `0/2` for Candidate skills. That is evidence against always-on promotion, not a failure to hide.
- `check_context_budget.py` and `check_archive_candidates.py` are warning-only unless the project explicitly changes their policy.
- Existing legacy code-shape warnings should be reported, not automatically rewritten outside the requested scope.
