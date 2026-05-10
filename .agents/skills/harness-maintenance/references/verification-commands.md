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
- PRD, `REQDOC`, `REQ`, `WS`, matrix, or technical assumptions changed: `.codex/hooks/run_with_repo_python.sh scripts/check_requirements_shape.py`
- Candidate skills are being promoted or evaluated: `.codex/hooks/run_with_repo_python.sh scripts/check_skill_usage_samples.py`
- Agent trace schema or trace samples changed: `.codex/hooks/run_with_repo_python.sh scripts/check_agent_trace_schema.py`
- Agent trace local / OTLP pilot export adapter changed: `.codex/hooks/run_with_repo_python.sh scripts/export_agent_trace.py --input docs/ai/standards/agent-trace-sample.jsonl` and `.codex/hooks/run_with_repo_python.sh scripts/export_agent_trace.py --input docs/ai/standards/agent-trace-sample.jsonl --format otlp-http-json`
- Agent eval dataset changed: `.codex/hooks/run_with_repo_python.sh scripts/check_agent_eval_dataset.py`
- Agent eval runner changed: `.codex/hooks/run_with_repo_python.sh scripts/run_agent_eval_dataset.py --dry-run`; execute selected local checks and trace evidence binding explicitly with `--id <eval-id>` when needed
- Tool contract registry changed: `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- Security / guardrail / workflow sample gaps changed: `.codex/hooks/run_with_repo_python.sh scripts/collect_harness_sample_gaps.py`
- Python linter config, dependency, or CI entrypoint changed: `.codex/.venv/bin/python -m ruff check .codex/hooks scripts tests` and `git diff --check`
- GitHub workflows, CODEOWNERS, Dependabot, dependency review, or remote guardrails changed: `.codex/hooks/run_with_repo_python.sh scripts/check_github_guardrails.py`
- Scorecard, CodeQL, SBOM, SLSA, or provenance policy changed: review `docs/ai/check-registry.md` and `docs/ai/security/supply-chain-provenance-plan.md`
- Skill structure changed: `python3 /Users/coolm/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-dir>`

## Windows Equivalent

Use `.codex/hooks/run_with_repo_python.ps1` with the same script path when working from PowerShell.

## Warning Interpretation

- `check_change_triggered_followups.py` is advisory. It suggests checks and references from changed files; CI summary output still does not prove those commands have already run.
- `check_github_guardrails.py` may report remote `UNKNOWN` when credentials, permissions, or GitHub configuration are unavailable. Do not restate `UNKNOWN` as OK.
- `check_skill_usage_samples.py` may report `0/2` for Candidate skills. That is evidence against always-on promotion, not a failure to hide.
- `run_agent_eval_dataset.py --dry-run` only proves eval routing and grading wiring. A real eval run requires explicitly selecting and executing eval items; trace evidence is read only in execute mode.
- `export_agent_trace.py` defaults to local / no-network export. `--format otlp-http-json` without `--send` is still no-network; external export requires explicit `--send --endpoint` and does not prove OpenAI, MCP, or A2A remote interoperability.
- `collect_harness_sample_gaps.py` lists missing real-scenario evidence. It does not create security, guardrail, or workflow proof by itself.
- `check_context_budget.py` and `check_archive_candidates.py` are warning-only unless the project explicitly changes their policy.
- Existing legacy code-shape warnings should be reported, not automatically rewritten outside the requested scope.
