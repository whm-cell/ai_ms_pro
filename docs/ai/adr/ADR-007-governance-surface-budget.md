# Governance Surface Budget

更新时间：2026-04-22
编号：ADR-007
标题：收紧默认治理面并给 active handoff 设预算
状态：已采纳

## 背景

- `docs/ai/index.md`、`working-context.md` 与 stage `status` 之间已经出现重复的目录型信息，默认恢复路径越来越像三份阶段总表。
- active `handoff` 数量已经超过“下一位 Agent 默认应读”的合理规模，虽然 stage `status` 已存在，但完成型 handoff 仍长期停留在 active。
- 当前治理检查已经能校验 freshness 与 metadata 一致性，但还不能提醒“默认治理面是否过胖”。
- 需要在不破坏三层 harness 边界的前提下，降低默认上下文体积，并让这件事具备可持续的自约束能力。

## 决策

- `docs/ai/index.md` 定位为稳定路由层，只保留默认阅读顺序、当前控制面入口和少量关键 ADR，不再展开完整阶段目录。
- `docs/ai/working-context.md` 定位为“同步元数据 + 增量真相 + 下一次会话先读”，不再维护第二套全量入口清单或阶段级决策总表。
- stage `status` 继续承担阶段压缩结论，但 `## 关联文档` 只保留稳定路由入口与当前仍活跃的文档集合，不再重复展开完整已吸收清单。
- 完成型 handoff 一旦已被 stage `status` 或 ADR 吸收，且不再存在默认 resume 价值，就移入 `docs/ai/handoffs/archive/`。
- 新增默认 active handoff 预算：`5`。`scripts/check_ai_governance.py` 对“active handoff 总量”与“working-context 绑定的 active handoff 数量”超预算给出 warning。
- 本轮预算先作为 warning，而不是 blocking；是否升级为阻断，取决于后续误报率与阶段复杂度。

## 备选方案

- 方案 A：继续保留当前多入口并行展开的目录结构，只通过人工克制控制体积
- 方案 B：把所有当前状态进一步压进 `working-context`，弱化 `status` 与 `handoff`
- 方案 C：让 hook 或 reducer 自动决定 handoff 的归档与入口更新

## 决策理由

- 方案 A 没有自维持机制，随着 workstream 增长会反复回到“入口文档越来越胖”的状态。
- 方案 B 会让 `working-context` 继续过载，违背已经确立的 projection / primary truth 边界。
- 方案 C 需要自动化去判断“是否还值得默认阅读”，语义风险高，也容易在多 session / 多 agent 场景下误判。
- “轻量路由 + 增量真相 + 阶段压缩 + 归档 + 预算 warning” 与现有三层 harness、handoff 压缩链和字段级校验机制兼容，改动最小。
- 把预算做成 checker warning，可以在不增加 always-on prompt 负担的前提下，给未来任务一个可重复的收敛信号。

## 影响

- `docs/ai/index.md` 与 `working-context.md` 会显著变短，默认恢复面更接近“下一位 Agent 真正需要先读的东西”。
- 部分已被 stage `status` / ADR 吸收的 handoff 将转入 `docs/ai/handoffs/archive/`；archive 承担历史可追溯性，active 只承担默认接力性。
- `scripts/check_ai_governance.py` 会新增 active surface budget warning，帮助后续任务及时压缩/归档，而不是等入口文档膨胀后再人工清理。
- 该决策暂不进入 `AGENTS.md`，避免把仓库治理面的每一次收缩策略都变成 always-on prompt 负担；长期稳定后再评估是否升级为默认仓库规则。

## 关联文档

- [项目计划](../plan.md)
- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
