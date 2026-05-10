# 2026-05-10 Workflow Skill Upgrade Review

更新时间：2026-05-10
状态：decision draft

## Purpose

整理 `prd-to-project-skills`、`progressive-feature-development` 与 `team-pr-conflict-control` 的当前样本证据和升级建议。

本文件不是 canonical current-state truth；它只解释本轮为什么不把 Candidate workflow skills 升级为 Stable，也不把 team-pr validation / pending 样本计入 accepted。

## Evidence Summary

| Skill | Accepted | Pending | Evidence base | Current recommendation |
| --- | ---: | ---: | --- | --- |
| `prd-to-project-skills` | 3 | 0 | SAMPLE-001 REQDOC-003 first slice；SAMPLE-002 WS-03 combo/rank second slice；SAMPLE-005 approved-plan control | 保持 Candidate；继续观察；不升级 Stable |
| `progressive-feature-development` | 3 | 0 | SAMPLE-001 REQDOC-003 first slice；SAMPLE-002 WS-03 combo/rank second slice；SAMPLE-005 approved-plan control | 保持 Candidate；继续观察；不升级 Stable |
| `team-pr-conflict-control` | 0 | 2 | SAMPLE-003 PR #11 burn-in pending；SAMPLE-004 Worker D parallel governance review pending | 保持 observed/on-demand；不升级 blocking 或 always-on |

## Workflow Skill Decision

| Skill | Decision | Reason | Upgrade trigger to revisit |
| --- | --- | --- | --- |
| `prd-to-project-skills` | Keep Candidate | 两个 accepted 样本来自同一 PRD/workstream，SAMPLE-005 只证明“无 PRD / 不 skillize”控制边界；尚未证明跨 PRD 复用或实际 skill 发布后的维护收益。 | 新增非 WS-03 PRD / workstream 样本，并记录是否创建、拒绝或调整 candidate skill。 |
| `progressive-feature-development` | Keep Candidate | 两个正样本证明非平凡功能切片 plan gate 有效，SAMPLE-005 证明已有完整计划时可避免重复计划税；仍缺真正简单任务 skip 样本。 | 新增不同模块的非平凡功能样本，再新增一个简单任务 skip/negative sample，证明逃生口有效。 |

## Team PR Conflict Decision

`team-pr-conflict-control` 仍是 `0/2 accepted`，原因如下：

- `SAMPLE-001-team-pr-conflict-control-validation.md` 是结构、discoverability 和离线矩阵验证，不是真实多人 PR。
- `SAMPLE-003 harness-ci-burn-in-pr` 有 PR #11 和远端 CI 证据，但缺真实多人 / 多 AI same-file 或 high-risk overlap、review coordination、merge sequencing 和最终冲突结果。
- `SAMPLE-004 worker-d-parallel-guardrail-sample-review` 是当前多 worker 文档整理边界样本，还没有 PR metadata 或远端 overlap 结果。

这些样本可以证明 skill 的按需使用边界和审计字段，但不能证明它已经减少了真实 PR 冲突返工。因此不升级 always-on、不升级 blocking，也不把 pending 改写成 accepted。

## Next Evidence Needed

| Evidence needed | Minimum auditable fields | Where to record |
| --- | --- | --- |
| Real team / multi-AI PR overlap | PR link, base/head, touch-set overlap, high-risk files, coordination action, final merge/conflict result | `docs/ai/skill-usage-samples.md` plus PR body/review link |
| Simple-task skip sample | task summary, why skill was skipped, verification that no coordination risk existed, process-tax outcome | `docs/ai/skill-usage-samples.md` as rejected or accepted skip/control sample |
| Cross-workstream workflow sample | REQ/WS, baseline_without_skill, run_with_skill, delta, verification, doc promotion | `docs/ai/skill-evals/SAMPLE-XXX-*.md` |

SAMPLE-005 是 accepted control sample，但不替代上述三类后续证据。

## Verification Plan

- `.codex/hooks/run_with_repo_python.sh scripts/check_skill_usage_samples.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_change_triggered_followups.py --files docs/ai/skill-usage-samples.md docs/ai/skill-evals/2026-05-10-workflow-skill-upgrade-review.md docs/ai/security/agent-guardrail-samples.md docs/ai/security/security-evidence-triage.md`
- `.codex/hooks/run_with_repo_python.sh scripts/check_agent_eval_dataset.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `git diff --check`
