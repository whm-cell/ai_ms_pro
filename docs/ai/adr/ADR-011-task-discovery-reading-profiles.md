# Task Discovery Reading Profiles

更新时间：2026-04-30
编号：ADR-011
标题：按任务复杂度选择上下文读取面
状态：已采纳

## 背景

- Context surface 配置化能防止默认入口继续变厚，但复杂任务和 0-1 阶段推进仍需要读到足够的 requirements、handoff、ADR 和历史约束。
- 不能要求用户每次手动说明“这是简单任务还是复杂任务”；分类应由 Agent 默认完成，并允许用户显式覆盖。
- 需要避免从“简单任务过载”摆到“复杂任务漏读”的另一端。

## 决策

- 在 `AGENTS.md` 增加 Task Discovery Protocol，作为 always-on 稳定规则。
- Codex 在 substantial work 前先按任务复杂度选择读取 profile，并简短说明判断。
- 默认 profile 分为 simple、medium、complex、0-1 stage、recovery/dispute。
- 用户显式指令优先级最高，但这些短语只是可选覆盖控制，不是每轮必填后缀；示例包括 `按简单任务处理`、`按复杂任务处理`、`这是 0-1 阶段任务`、`不要读 archive`、`需要深挖历史`。
- `new_pro_standard` 同步同一协议，让新项目继承“自动分类 + 用户可覆盖”的默认行为。

## 备选方案

- 方案 A：要求用户每次手动标注任务复杂度。
- 方案 B：所有任务都默认读完整历史。
- 方案 C：所有任务都只读短链路，复杂任务由失败后补读。

## 决策理由

- 手动标注会增加用户负担，且用户的一句话常常已经包含足够的分类线索。
- 全量读历史会重新制造厚上下文污染。
- 只读短链路会让复杂任务漏掉 requirements、traceability、ADR 或归档原因。
- 读取 profile 可以把“默认小上下文”和“复杂任务足够上下文”合并成一个可执行规则。

## 影响

- 简单任务默认仍走短链路。
- 复杂任务、治理规则变化、traceability 变化和 0-1 阶段推进会自动扩大读取面。
- Archive 仍不是默认入口，只在 recovery/dispute 或当前 truth surface 不足时进入。
- 该规则是稳定行为协议，不携带当前阶段候选列表或历史细节。

## 关联文档

- [项目规则 AGENTS.md](../../AGENTS.md)
- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [ADR-010 Context Surface Layering](./ADR-010-context-surface-layering.md)
