# 2026-05-10 Workflow Skill Upgrade Review

更新时间：2026-05-25
状态：复核完成，保持 Candidate

## 结论

`prd-to-project-skills` 与 `progressive-feature-development` 仍保持 Candidate，不升级 Stable / always-on。

## 当前样本快照

| Skill | Accepted | Rejected | 样本摘要 | 判断 |
| --- | ---: | ---: | --- | --- |
| `prd-to-project-skills` | 3 | 0 | SAMPLE-001 WS-01 Three.js validation；SAMPLE-002 WS-02 Trace Console；SAMPLE-005 approved-plan control | 保持 Candidate；继续观察；不升级 Stable |
| `progressive-feature-development` | 3 | 0 | SAMPLE-001 WS-01 Three.js validation；SAMPLE-002 WS-02 Trace Console；SAMPLE-005 approved-plan control | 保持 Candidate；继续观察；不升级 Stable |
| `team-pr-conflict-control` | 0 | 0 | SAMPLE-003 PR burn-in pending；SAMPLE-004 parallel guardrail review pending | 保持 Observed；不计入 accepted team sample |

## 保持 Candidate 的原因

| Skill | 当前决定 | 原因 | 后续证据 |
| --- | --- | --- | --- |
| `prd-to-project-skills` | Keep Candidate | accepted 样本证明需求/工作流方法有用，但仍缺跨模块、跨类型 source 和实际 skill 发布后的维护收益。 | 新增不同 workstream 样本，并记录是否创建、拒绝或调整 candidate skill。 |
| `progressive-feature-development` | Keep Candidate | accepted 样本证明非平凡功能适合 plan gate，也证明已有完整计划时可以跳过重复计划；但简单任务 skip 样本不足。 | 新增简单任务 skip / negative 样本，记录流程税与收益。 |
| `team-pr-conflict-control` | Keep Observed | 尚无真实多人 / 多 AI PR overlap、coordination action 和 merge result 的 accepted 样本。 | 需要真实 PR touch-set overlap、review / coordination action 和最终冲突结果。 |

## 不升级的边界

- 不把 Candidate skill 写入 `AGENTS.md` always-on 规则。
- 不把 accepted sample count 解读成所有任务都必须先跑完整 skill workflow。
- 不把 pending team sample 计入真实多人 PR accepted 样本。
- 不把当前验收状态或最新验证证据写进 skill 本体；它们留在 requirements、status、handoff、ADR、changelog 或 checks。

## 后续样本要求

| 需要的样本 | 必填字段 | 目标落点 |
| --- | --- | --- |
| Real team / multi-AI PR overlap | PR link, base/head, touch-set overlap, high-risk files, coordination action, final merge/conflict result | `docs/ai/skill-usage-samples.md` plus PR body/review link |
| Simple-task skip sample | task summary, why skill was skipped, verification that no coordination risk existed, process-tax outcome | `docs/ai/skill-usage-samples.md` as rejected or accepted skip/control sample |
| Cross-workstream feature sample | requirement/workstream ids, with/without reading surface, implementation output, verification commands | `docs/ai/skill-usage-samples.md` plus detailed eval if needed |

## Verification

- `.codex/hooks/run_with_repo_python.sh scripts/check_skill_usage_samples.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_change_triggered_followups.py --files docs/ai/skill-usage-samples.md docs/ai/skill-evals/2026-05-10-workflow-skill-upgrade-review.md docs/ai/security/agent-guardrail-samples.md docs/ai/security/security-evidence-triage.md`
- `.codex/hooks/run_with_repo_python.sh scripts/check_agent_eval_dataset.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_github_guardrails.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `git diff --check`
