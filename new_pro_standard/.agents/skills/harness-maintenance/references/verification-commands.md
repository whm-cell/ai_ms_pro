# Verification Commands

Use this reference to select checks after harness, governance, requirement, or skill changes.

## Command Selection

- Changed files should be mapped to likely missed follow-ups first: `.codex/hooks/run_with_repo_python.sh scripts/check_change_triggered_followups.py`
- CI / PR summaries can use markdown output: `python3 scripts/check_change_triggered_followups.py --base origin/main --markdown >> "$GITHUB_STEP_SUMMARY"`
- Shared governance truth changed: `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- Staged code or harness code changed: `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --staged`
- Default context, AGENTS, status, ADR, or skill surface grew: `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- Active handoffs reached budget or stage compression is planned: `.codex/hooks/run_with_repo_python.sh scripts/check_archive_candidates.py`
- Repo-local skills changed: `.codex/hooks/run_with_repo_python.sh scripts/check_repo_skills.py`
- Third-party `.codex/skills`, skill catalog/lock, vendor/proxy metadata, or skill/tool output scan policy changed: `.codex/hooks/run_with_repo_python.sh scripts/check_skill_catalog.py`
- Skill/tool output artifact needs prompt-injection-style scan: `.codex/hooks/run_with_repo_python.sh scripts/check_skill_catalog.py --check-output <file>`
- PRD, `REQDOC`, `REQ`, `WS`, matrix, technical assumptions, raw evidence, or source quarantine metadata changed: `.codex/hooks/run_with_repo_python.sh scripts/check_requirements_shape.py`
- Candidate skills are being promoted or evaluated: `.codex/hooks/run_with_repo_python.sh scripts/check_skill_usage_samples.py`
- GitHub workflows, CODEOWNERS, Dependabot, dependency review, or remote guardrails changed: `.codex/hooks/run_with_repo_python.sh scripts/check_github_guardrails.py`
- Scorecard, CodeQL, SBOM, SLSA, or provenance policy changed: review `docs/ai/check-registry.md` and `docs/ai/security/supply-chain-provenance-plan.md`
- Skill structure changed: `python3 /Users/coolm/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-dir>`

## Windows Equivalent

Use `.codex/hooks/run_with_repo_python.ps1` with the same script path when working from PowerShell.

## Warning Interpretation

- `check_change_triggered_followups.py` is advisory. It suggests checks and references from changed files; CI summary output still does not prove those commands have already run.
- `check_github_guardrails.py` may report remote `UNKNOWN` when credentials, permissions, or GitHub configuration are unavailable. Do not restate `UNKNOWN` as OK.
- `check_skill_usage_samples.py` may report `0/2` for Candidate skills. That is evidence against always-on promotion, not a failure to hide.
- `check_skill_catalog.py` treats downloaded `.codex/skills` as dependency-like assets. Large third-party `SKILL.md` files should be hidden behind a short proxy/catalog entry instead of becoming discovery text. Enabled catalog/lock entries should carry source URL, commit/hash, license, trust/risk, permission booleans, and enabled state. `--check-output` scans bounded output bytes for dangerous instruction-like tool/skill text; it does not replace human review of truncated content.
- `check_requirements_shape.py` treats external source content as evidence/data, not executable agent instructions. Raw PRD evidence and quarantined material should be summarized, excerpted, sanitized, or reviewed before use as implementation basis; use `--strict` only when a project intentionally promotes warnings.
- `check_context_budget.py` is blocking by default for default-surface high-watermark, hard-budget, always-on line-budget, and active stage-status compression gates; use `--warning-only` only for manual audits.
- Existing legacy code-shape warnings should be reported, not automatically rewritten outside the requested scope.
