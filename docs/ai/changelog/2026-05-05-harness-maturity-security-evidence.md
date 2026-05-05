# 2026-05-05 Harness Maturity Security Evidence

更新时间：2026-05-05
阶段或版本：stage-00
状态：已确认

## 新增功能

- 新增 check registry，记录 harness checks 的 `advisory / review-required / blocking-candidate / blocking` 等级。
- `check_change_triggered_followups.py` 的 text / JSON / markdown 输出新增 check level 与 CI coverage。
- `check_github_guardrails.py` 识别 `security-evidence` workflow，并在远端 branch protection / rulesets 为 `UNKNOWN` 或 `WARN` 时输出 recommended actions。
- 新增 `Security Evidence` workflow，接入 Scorecard、CodeQL 和 SBOM artifact，第一阶段均为 advisory。
- 新增 supply-chain provenance 计划，定义未来 artifact 的 build entrypoint、source revision、digest、SBOM 和 attestation 记录面。

## 修复问题

- 避免把所有 advisory checks 直接升级为 blocking，减少流程税。
- 让 PR summary 能显示建议检查是否已有 CI 覆盖，降低 reviewer 判断成本。
- 明确远端 branch protection / rulesets 不可证明时 OPEN-01 仍应保持阻塞。

## 行为变化

- Scorecard / CodeQL / SBOM 只提供证据，不进入 required checks。
- `security-evidence` workflow 使用 `continue-on-error`，初始 burn-in 不阻断主线。
- `AGENTS.md` 不扩张；新增规则由 check registry、workflow、skill reference、status 和 changelog 承接。

## 破坏性变更

- 无。

## 验证范围

- `python3 -m unittest discover -s tests`
- `python3 -m unittest discover -s tests` from `new_pro_standard`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_repo_skills.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_github_guardrails.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `git diff --check`

## 关联文档

- [Check Registry](../check-registry.md)
- [Supply Chain And Provenance Plan](../security/supply-chain-provenance-plan.md)
- [Harness Remaining Work](../harness-open-items.md)
- [Harness Maintenance Supply Chain Reference](../../../.agents/skills/harness-maintenance/references/supply-chain-security.md)
