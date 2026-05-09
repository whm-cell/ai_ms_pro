# 2026-05-08 Agent Harness P1/P2 Guardrails

更新时间：2026-05-08
阶段或版本：stage-00
状态：已确认

## 新增功能

- 新增 source boundary metadata：requirements source template 与现有 source docs 均声明 `来源可信度`、`指令处理`、`清洗状态`。
- 新增 `docs/ai/security/agent-action-guardrails.md`，覆盖 destructive、externally visible 和 permission-changing Agent 动作的人工确认、允许工具、验证证据和 hook automation 边界。
- `scripts/check_change_triggered_followups.py` 新增 `high-impact-agent-actions` review-required advisory follow-up。

## 修复问题

- 外部 PRD、网页摘录和大段粘贴需求不再只靠流程纪律区分；source docs 现在必须把内容标成 evidence / data，而不是 Agent 可执行指令。
- 高影响动作不再散落在口头规则中；hooks 和脚本只能提示、dry-run、draft 或收集证据，不能自动执行删除、合并、发送、发布、改权限或破坏性写操作。

## 行为变化

- `check_requirements_shape.py` 会对 source docs 缺失或语义不清的边界元数据输出 review-required warning；默认不阻断，`--strict` 仍会把 warning 提升为失败。
- 变更 GitHub workflow、CODEOWNERS、Dependabot、GitHub guardrails、PR touch conflict 或 action guardrails 时，会提示检查高影响动作边界。

## 破坏性变更

- 无

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_requirements_shape tests.test_change_triggered_followups`
- `.codex/hooks/run_with_repo_python.sh scripts/check_requirements_shape.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_change_triggered_followups.py --files docs/ai/security/agent-action-guardrails.md`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`

## 关联文档

- [Agent Harness Security](../security/agent-harness-security.md)
- [Agent Action Guardrails](../security/agent-action-guardrails.md)
- [Harness Remaining Work](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
