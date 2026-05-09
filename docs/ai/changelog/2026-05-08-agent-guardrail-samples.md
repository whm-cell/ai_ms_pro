# 2026-05-08 Agent Guardrail Samples

更新时间：2026-05-08
阶段或版本：stage-00
状态：已确认

## 新增功能

- 新增 [Agent Guardrail Samples](../security/agent-guardrail-samples.md)，作为 P1 source boundary 与 P2 high-impact action matrix 的轻量样本记录面。
- 样本模板覆盖触发规则、source / action 摘要、处理结果、误报 / 漏报、reviewer 负担、证据链接和 blocking 升级信号。

## 修复问题

- 补齐 P1 / P2 guardrails 后续观察位置，避免把真实样本散落在 runtime、PRD 原文、完整 transcript 或临时对话中。

## 行为变化

- 后续评估是否把 advisory / review-required 升级为 blocking 时，应先检查样本记录是否已经提供足够真实证据。
- 样本记录不替代 user confirmation，不存 secret，也不粘贴完整 PRD、runtime JSONL、transcript 或完整 diff。

## 破坏性变更

- 无

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `git diff --check`

## 关联文档

- [Agent Harness Security](../security/agent-harness-security.md)
- [Agent Action Guardrails](../security/agent-action-guardrails.md)
- [AI 文档入口索引](../index.md)
