# Governance Surface Slimming Handoff

更新时间：2026-04-22
阶段：stage-00
任务：governance-surface-slimming
状态：已完成

## 需求与工作流标识

- Requirement IDs：未绑定
- Workstream IDs：未绑定
- 本任务处理的是 repo 级治理面减重与默认阅读面压缩，不新增 requirements canonical mapping

## 本任务目标

- 收紧 `index / working-context / status` 的默认入口职责，减少目录型重复投影
- 把已被 stage `status` 或 ADR 吸收的完成型 handoff 移出 active，恢复 handoff 的默认接力边界
- 给治理检查增加 active handoff 预算 warning，让默认治理面在后续任务中也能持续保持轻量

## 已完成内容

- 重写 [docs/ai/index.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)，使其收缩为稳定路由层，不再重复展开完整阶段目录
- 重写 [docs/ai/working-context.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)，保留同步元数据、增量真相和小规模默认阅读路径，去掉第二套全量入口清单
- 更新 [docs/ai/status/stage-00-runtime-harness-foundation.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)，补入治理面瘦身结果，并收紧 `## 关联文档` 的重复目录展开
- 新增 [ADR-007 Governance Surface Budget](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-007-governance-surface-budget.md)，把“轻量路由 + 小规模 active handoff + archive + budget warning”的机制固化为长期决策
- 更新 [scripts/check_ai_governance.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/check_ai_governance.py)，新增 active handoff 总量与 `working-context` 绑定 handoff 数量的预算 warning
- 将已被 stage `status` / ADR 吸收且不再具备默认 resume 价值的完成型 handoff 归档到 `docs/ai/handoffs/archive/`

## 修改文件

- [docs/ai/index.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
- [docs/ai/working-context.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)
- [docs/ai/status/stage-00-runtime-harness-foundation.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
- [docs/ai/adr/ADR-007-governance-surface-budget.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr/ADR-007-governance-surface-budget.md)
- [scripts/check_ai_governance.py](/Volumes/usd/codes/go_projects/ai_ms_pro/scripts/check_ai_governance.py)
- [docs/ai/handoffs/archive/stage-00-threejs-snake-mvp.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/archive/stage-00-threejs-snake-mvp.md)
- [docs/ai/handoffs/archive/stage-00-harness-trace-console.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/archive/stage-00-harness-trace-console.md)
- [docs/ai/handoffs/archive/stage-00-requirement-workstream-metadata.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/archive/stage-00-requirement-workstream-metadata.md)
- [docs/ai/handoffs/archive/stage-00-projection-surface-freshness.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/archive/stage-00-projection-surface-freshness.md)
- [docs/ai/handoffs/archive/stage-00-working-context-sync-metadata.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/archive/stage-00-working-context-sync-metadata.md)
- [docs/ai/handoffs/archive/stage-00-repo-governed-coding-skill.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/archive/stage-00-repo-governed-coding-skill.md)
- [docs/ai/handoffs/archive/stage-00-traceability-metadata-consistency-check.md](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/archive/stage-00-traceability-metadata-consistency-check.md)

## 关键实现决策

- 不通过 hook 或 reducer 自动归档 handoff；是否还值得默认阅读，仍保留给主 Agent 在语义节点判断
- 预算只作用于默认治理面，不作用于 archive；archive 继续承担审计性与历史可追溯性
- `index` 只做稳定路由，`working-context` 只做增量真相，stage `status` 只做阶段压缩；三者不再互相抄整套目录
- 预算先做 warning，不直接阻断，避免在阶段边界尚未稳定时引入过强误报

## 已验证有效的路线

- 通过 archive 回收已被 stage `status` / ADR 吸收的 handoff，能明显缩小默认恢复面，同时不损失历史可追溯性
- 用 checker 约束 active handoff 预算，比只靠人工提醒更可持续
- 把瘦身规则固化为 ADR，而不是继续写在自由文本里，能降低后续任务回弹概率

## 已验证无效的路线

- 同时在 `index`、`working-context` 和 stage `status` 中维护完整阶段目录，会让默认上下文持续膨胀
- 继续让完成型 handoff 长期停留在 active，会削弱 `status` 的压缩价值
- 让 runtime 自动化去决定 archive 与入口更新，会越过 repo-first 治理的语义边界

## 尚未尝试但建议的路线

- 若后续 active handoff 仍频繁超过预算，可评估把 warning 升级为可配置 blocking
- 若多 stage 并行成为常态，可把预算从固定阈值改成 stage-aware 或 repo-configurable
- 若后续需要更强 discoverability，可在 archive 层补按阶段或主题的汇总索引，而不是重新把内容推回 active

## 当前未完成项

- active handoff 预算当前仍是 warning，尚未形成阻断式约束
- 尚未为 archive 建立更细的阶段级汇总页
- 尚未统计不同任务类型下“5 个 active handoff”是否是最佳阈值

## 已知风险与注意事项

- 预算过小会影响 resume 体验，预算过大又会失去减重效果；当前阈值仍需真实任务继续验证
- archive 仍依赖 `index / working-context / status` 提供稳定路由，若路由退化，discoverability 也会下降
- 这次瘦身只处理默认治理面，不等于减少了 repo 里的历史文档总量

## 下一位 Agent 的第一步动作

- 新增 active handoff 前，先判断对应内容是否已经被当前 stage `status` 或 ADR 吸收；若已吸收，优先归档而不是继续扩张默认治理面

## 建议同步更新

- 已同步 `working-context`
- 已同步 `stage status`
- 已同步 `ADR-007`
- 检查 [AI 文档入口索引](../../index.md)
