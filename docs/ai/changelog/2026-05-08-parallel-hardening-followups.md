# 2026-05-08 Parallel Hardening Followups

更新时间：2026-05-08
阶段或版本：stage-00
状态：已确认

## 新增功能

- 更新 remote merge gates evidence，记录最新 GitHub Actions PR / main push burn-in 成功证据，同时保持 branch protection / rulesets 为 private Free plan-limited `UNKNOWN`。
- 新增 Agent Guardrail Samples，作为 P1 source boundary 与 P2 high-impact action matrix 的轻量样本记录面。
- 新增 runtime handoff renderer，把 reducer 的 handoff draft 渲染逻辑从 `reduce_runtime_observations.py` 拆出。

## 修复问题

- reducer 不再因渲染逻辑集中在主脚本中触发 code-shape warning。
- AI/Agent guardrails 后续观察有固定记录位置，不再依赖临时对话或 runtime 原文。

## 行为变化

- remote merge gates 继续区分 CI evidence 和 remote enforcement；`UNKNOWN` 不写成 OK。
- guardrail samples 不替代 user confirmation，不存 secret，不粘贴完整 PRD、runtime JSONL、transcript 或完整 diff。
- reducer CLI 行为保持不变，`render_handoff_draft` 仍可从 `reduce_runtime_observations.py` 兼容调用。

## 破坏性变更

- 无

## 验证范围

- `.codex/.venv/bin/python -m unittest discover -s tests`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `.codex/hooks/run_with_repo_python.sh scripts/check_github_guardrails.py`
- `git diff --check`

## 关联文档

- [Remote Merge Gates Evidence](../security/remote-merge-gates.md)
- [Agent Guardrail Samples](../security/agent-guardrail-samples.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
