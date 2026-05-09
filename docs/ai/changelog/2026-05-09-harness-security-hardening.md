# 2026-05-09 Harness Security Hardening

更新时间：2026-05-09
阶段或版本：stage-00
状态：已确认

## 新增功能

- GitHub Actions workflow 的 action 引用改为 full-length commit SHA pinning，并保留原 tag 注释作为升级线索。
- 新增 `SECURITY.md` 和 [Security Evidence Triage](../security/security-evidence-triage.md)，定义 private repo 安全报告、Scorecard / CodeQL / SBOM / dependency review / secret scanning advisory 的 triage、SLO 和升级边界。
- Agent guardrail samples 记录首批 P1 source boundary 与 P2 high-impact action matrix 真实样本。
- Requirements source template 和 checker 增加 external-web / third-party / unknown 且 pending 的 review-required 边界。

## 修复问题

- CI supply-chain 证据不再依赖 mutable action tags。
- Security evidence 不再只有 artifact 产出，还具备 owner、严重度、issue 条件和 blocking 升级规则。
- Private GitHub Free 下 GitHub artifact attestation 不再被误写为当前完成条件。

## 行为变化

- Security evidence 仍保持 advisory / review-required，不伪装为 required gate。
- `pending` 的外部来源只能作为待 review 证据，不能作为直接实现依据。
- 高影响动作仍需要明确人工确认；hooks 和后台任务只允许提示、dry-run、draft 或 evidence collection。

## 破坏性变更

- 无

## 验证范围

- `python -m unittest tests.test_requirements_shape`
- `.codex/hooks/run_with_repo_python.sh scripts/check_requirements_shape.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_github_guardrails.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `git diff --check`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [Harness Remaining Work](../harness-open-items.md)
- [Agent Guardrail Samples](../security/agent-guardrail-samples.md)
- [Security Evidence Triage](../security/security-evidence-triage.md)
- [Supply Chain And Provenance Plan](../security/supply-chain-provenance-plan.md)
