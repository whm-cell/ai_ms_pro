# 2026-05-08 Private Free GitHub Boundary

更新时间：2026-05-08
阶段或版本：stage-00
状态：已确认

## 新增功能

- Reclassified GitHub branch protection / rulesets for the current private GitHub Free repository as plan-limited future gates instead of local-code gaps.
- Updated `scripts/check_github_guardrails.py` reporting so GitHub API responses that say to upgrade to Pro or make the repository public produce plan-limited recommended actions.

## 修复问题

- Fixed stale OPEN-01 wording that treated private-Free unavailable branch protection / rulesets as a local engineering gap.

## 行为变化

- Remote merge gates now distinguish supported-plan missing configuration from private-Free plan-limited `UNKNOWN`.
- OPEN-01 completion now focuses on local/CI/process evidence under the current plan; required checks, required reviews, branch protection, rulesets, and merge queue remain future upgrade gates.

## 破坏性变更

- 无

## 验证范围

- `.codex/.venv/bin/python -m unittest discover -s tests`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_github_guardrails.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [Remote Merge Gates Evidence](../security/remote-merge-gates.md)
- [Harness Remaining Work](../harness-open-items.md)
