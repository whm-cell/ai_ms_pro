# 2026-05-09 CI Burn-in Evidence

更新时间：2026-05-09
阶段或版本：stage-00
状态：已确认

## 新增功能

- 新增 OPEN-01 首轮远端 burn-in 证据记录，覆盖 PR #11 checks、merge commit `c1f170faa701885882a0ed7a2105c1054fe956ea` 和 `main` push workflows。

## 修复问题

- 关闭 OPEN-01 仍缺首轮远端 PR + main push CI evidence 的记录缺口。
- 将 CodeQL `Code scanning is not enabled for this repository` 上传注解登记到 security triage，避免把 advisory evidence 误解为 required gate 失败。

## 行为变化

- `docs/ai/harness-open-items.md` 现在把 OPEN-01 首轮 burn-in 标为已完成，并把后续工作改为 scheduled / 后续 PR 样本观察。
- `docs/ai/security/security-evidence-triage.md` 记录 `Security Evidence` run 25599034597 的 CodeQL code-scanning 注解，当前不要求开 issue、人工 hold 或 blocking 升级。
- `docs/ai/security/remote-merge-gates.md` 更新到 PR #11 与 merge commit `c1f170f` 的最新证据。

## 破坏性变更

- 无

## 后续观察

- 继续积累 scheduled / 后续 PR security evidence 样本，确认 CodeQL code-scanning 注解是否持续出现。
- 若仓库升级 GitHub plan、改 public 或启用 code scanning，再重新评估 CodeQL 上传状态是否进入 blocking 候选。
- branch protection、rulesets、required reviews 和 required checks 继续作为 future upgrade gates，不在 private GitHub Free 下声明已远端强制。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_github_guardrails.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_branch_hygiene.py --strict`
- `git diff --check`

## 关联文档

- [Harness Remaining Work](../harness-open-items.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [Remote Merge Gates Evidence](../security/remote-merge-gates.md)
- [Security Evidence Triage](../security/security-evidence-triage.md)
- [Supply Chain And Provenance Plan](../security/supply-chain-provenance-plan.md)
