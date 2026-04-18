# Projection Surface Freshness Handoff

更新时间：2026-04-18
阶段：stage-00
任务：projection-surface-freshness
状态：已完成

## 需求与工作流标识

- Requirement IDs：未绑定
- Workstream IDs：未绑定
- 本任务解决的是 repo 级治理边界，不新增 requirement / workstream canonical mapping

## 本任务目标

- 收紧 `docs/ai/plan.md` 与 `docs/requirements/workstreams/*.md` 的职责边界
- 把“当前状态真相优先放在 primary truth surface”写成 repo 规则，而不是保留在聊天结论里
- 给 governance check 增加最小的 projection freshness 保护，但只检查显式状态字段

## 已完成内容

- 在 `AGENTS.md` 中新增 projection surface boundary 规则，明确 primary truth 与 projection document 的分工
- 新增 [ADR-005 Projection Surface Freshness Boundary](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-005-projection-surface-freshness.md)，把这次边界决策固化为长期规则
- 更新 [docs/ai/plan.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/plan.md)，加入“使用边界”并移除会漂移的当前状态表述
- 更新 [WS-01-threejs-snake-mvp.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/workstreams/WS-01-threejs-snake-mvp.md)，移除自维护完成态，改成“状态来源”链接
- 更新治理脚本，使其能够识别 `plan/workstream` 中显式状态字段，并在这些 projection 文档落后于上游真相时失败
- 更新 `working-context`、stage status 和 `docs/ai/index.md`，把本次治理变化纳入当前控制面

## 修改文件

- [AGENTS.md](/Volumes/usd/codes/go_projects/ai_ms_pro/AGENTS.md)
- [docs/ai/adr/ADR-005-projection-surface-freshness.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-005-projection-surface-freshness.md)
- [docs/ai/plan.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/plan.md)
- [docs/requirements/workstreams/WS-01-threejs-snake-mvp.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/workstreams/WS-01-threejs-snake-mvp.md)
- [docs/ai/working-context.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)
- [docs/ai/status/stage-00-runtime-harness-foundation.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
- [docs/ai/index.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
- [scripts/check_ai_governance.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/check_ai_governance.py)
- [scripts/check_ai_doc_quality.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/check_ai_doc_quality.py)

## 关键实现决策

- 不继续把 `plan/workstream` 当成次级当前状态面，而是把它们收缩回 projection surface
- 不做自由文本级 freshness 判断，只对显式状态字段做校验，避免高误报
- `plan` 与 `workstream` 一律先声明“状态来源”，再保留各自稳定的结构职责
- 这次决策先用文档边界 + 最小脚本规则落地，不额外引入 hook 自动回写

## 当前未完成项

- 尚未给 AI-side metadata 与 `traceability-matrix.md` 做字段级一致性自动校验
- 尚未给多 workstream 场景建立更细粒度的 projection freshness 依赖
- 尚未把治理检查接入 CI

## 已知风险与注意事项

- 当前 freshness 规则只覆盖显式标签，不理解隐含的自然语言状态句子
- 如果后续有人再次把大量当前状态写回 `plan` 或 `workstream`，校验只能覆盖显式字段，仍需遵守文档边界
- 目前 workstream freshness 的 canonical 上游仍以 `traceability-matrix.md` 为主，多 workstream 场景下若需要更精细依赖，后续应另补规则

## 已验证有效的路线

- 先收缩 projection 文档职责，再补最小规则，比直接扩大全面 freshness 图更稳
- 用 ADR 固化 repo 级边界，能让后续治理脚本和文档写法有共同依据
- 把状态真相集中到 `working-context`、`handoff`、`status`、`traceability-matrix`，更符合当前仓库的控制面设计

## 已验证无效的路线

- 继续让 `plan/workstream` 自由写“已完成/未验证/最新 smoke”，但不纳入 freshness 校验
- 试图用 hook 自动回写 projection 文档来掩盖职责边界不清的问题
- 在没有字段约束的前提下做自由文本语义 freshness 检测

## 尚未尝试但建议的路线

- 等第二个真实 workstream 落地后，再决定是否要给 workstream-level freshness 加更细的映射规则
- 若 metadata consistency 成为高频问题，可在此基础上继续补 `REQ/WS` 与 `traceability-matrix` 的字段级校验
- 如果后续 CI 接入治理检查，可把 projection freshness 规则一并纳入 merge 前阻断

## 下一位 Agent 的第一步动作

- 先读 [ADR-005 Projection Surface Freshness Boundary](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-005-projection-surface-freshness.md) 和更新后的 [docs/ai/plan.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/plan.md)，再决定下一步是继续补 metadata consistency 校验，还是推进第二个真实 workstream
