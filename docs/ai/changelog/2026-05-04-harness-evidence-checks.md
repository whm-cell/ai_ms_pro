# 2026-05-04 Harness Evidence Checks

更新时间：2026-05-04
阶段或版本：stage-00
状态：已确认

## 新增功能

- Added `scripts/check_repo_skills.py` to list repo-local skills, validate `SKILL.md` structure, and compare with `$CODEX_HOME/skills`.
- Added `scripts/check_requirements_shape.py` to check `REQDOC -> REQ -> WS -> traceability-matrix` coverage and flag unqualified technical-assumption lines.
- Added `scripts/check_skill_usage_samples.py` to report whether Candidate skills have enough accepted with/without eval samples.
- Added `scripts/check_github_guardrails.py` to report local and remote GitHub guardrails as `OK`, `WARN`, or `UNKNOWN`.
- Added `docs/ai/skill-usage-samples.md` as the evidence registry for Candidate skill promotion decisions.
- Added `docs/ai/skill-evals/README.md` as the detailed Candidate skill eval protocol.

## 修复问题

- Prevented repo-local skills from being confused with globally installed Codex skills.
- Moved repo skills to Codex repo-local native `.agents/skills` and checked `policy.allow_implicit_invocation`.
- Added a requirements-chain check so PRD technical assumptions need explicit status and verification method before they can be treated as adopted architecture facts.
- Made Candidate skill promotion evidence comparative instead of relying on subjective memory.

## 行为变化

- Repo-local skills are now explicitly reported as Codex-discoverable, `repo-local only`, or `globally installed`.
- PRD / requirements imports can now be checked before implementation to catch missing traceability bindings and unverified technical assumptions.
- Candidate workflow skills remain explicit and evidence-gated; missing eval samples are warnings, not blockers.
- Completed skill/evidence handoffs were moved from active to archive to reduce default Stage-00 surface.

## 破坏性变更

- 无

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_repo_skills.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_requirements_shape.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_skill_usage_samples.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_github_guardrails.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`

## 关联文档

- [Candidate Skill Usage Samples](../skill-usage-samples.md)
- [PRD 长文到 Harness + Skill 使用细节](../../../--使用细节/prd-to-skill-harness-usage.md)
- [AI 文档入口索引](../index.md)
- [Harness Remaining Work](../harness-open-items.md)
