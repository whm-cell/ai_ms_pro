# Enterprise Code Boundary Skill

日期：2026-06-14

## 新增功能

- 新增 repo-local Candidate skill：`$enterprise-code-boundary-maintenance`。
- 新增三份 review-required 企业编码边界标准：
  - Logging / Redaction Boundary
  - Error Contract Boundary
  - Runtime Side Effect Boundary
- 将 Config Contract Boundary 作为已落地样本接入该 skill 的路由。

## 行为变化

- `AGENTS.md`、`docs/ai/index.md` 和 `docs/ai/working-context.md` 现在能把企业编码边界任务路由到该 skill。
- `check_change_triggered_followups.py` 新增 `enterprise-code-boundaries` review-required follow-up，只提示人工复核和现有治理检查。
- Enterprise boundary follow-up patterns 独立到 `change_triggered_enterprise_boundary_rules.py`，避免主规则文件继续膨胀。

## 修复问题

- 修正 repo-local skill metadata，显式声明 `policy.allow_implicit_invocation: false`。

## 破坏性变更

- 无。

## 验证范围

- 本次不新增 logging / error / side-effect checker。
- 本次不升级 blocking，不声明 SIEM/DLP、生产 observability、全局错误码平台、service mesh 或远端 side-effect 审计完成。

```bash
python3 /Users/coolm/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/enterprise-code-boundary-maintenance
.codex/hooks/run_with_repo_python.sh scripts/check_repo_skills.py
.codex/hooks/run_with_repo_python.sh scripts/check_skill_catalog.py
python3 tests/test_change_triggered_followups.py
.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py
.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py
```
