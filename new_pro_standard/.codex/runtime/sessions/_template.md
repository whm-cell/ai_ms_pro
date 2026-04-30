# Runtime Session 模板

更新时间：YYYY-MM-DD
Agent：main | subagent
Session 类型：new | resume | pause-before-exit
分支或线程：branch-name | thread-id

## 需求与工作流标识

- Requirement IDs：未绑定
- Workstream IDs：未绑定
- 若已绑定，应与 `docs/requirements/traceability-matrix.md` 保持一致

## 当前目标

- 用一句话说明本次 session 试图推进什么

## 会话范围与触发背景

- 说明这次 session 从哪个任务、阶段或阻塞点进入

## 行为护栏快照

- Assumptions：列出本次实现前明确采用的假设；若存在会改变方案的歧义，写入 `当前 Open Loops`
- Scope Boundary：说明本次只改什么、不顺手改什么
- Success Criteria：写出可验证的完成条件
- Verification Plan：列出收尾前应运行的检查、测试或 smoke

## 已做动作

- 记录本次 session 已执行的关键动作、命令或检查

## 触碰文件

- 列出本次 session 实际读取或修改的重要文件

## 已验证有效的路线

- 记录已被本次 session 证实可继续沿用的方案

## 已验证无效的路线

- 记录本次 session 已证伪或应避免重复尝试的方案

## 当前 Open Loops

- 记录当前仍未闭合的问题、假设或待确认项

## 需提升到共享治理层的内容

- 记录应被下一位 Agent 默认继承的结论
- 这些内容应被提升到 `handoff`、`status`、`adr`、`plan` 或需求文档，而不是长期停留在本文件

## 下次 Resume 提示

- 用几条最短的提示说明下次应先读什么、先做什么

## 是否需要提升为 Handoff

- 是 | 否
- 原因：
- 若为“是”，至少同步：任务目标、已完成内容、修改文件、关键实现决策、有效路线、无效路线、候选路线、未完成项、风险、下一步动作
