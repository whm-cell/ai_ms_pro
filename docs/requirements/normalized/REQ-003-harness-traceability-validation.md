# 标准化需求：用真实任务验证 Harness Traceability

更新时间：2026-04-16
需求编号：REQ-003
来源文档：REQDOC-001
需求标题：在真实任务中验证 requirements 与 harness 的追踪闭环
状态：已完成

## 背景

- 当前仓库已经建立了 runtime/governance/verification 三层 harness，但缺少真实业务场景验证。
- 仅靠模板和脚本不能证明 requirements、workstream、runtime memory 和共享治理文档之间的链路是可用的。

## 目标

- 用 Three.js 贪吃蛇场景验证 `REQDOC -> REQ -> WS -> STAGE -> implementation -> handoff/status` 的闭环
- 确保 requirement/workstream metadata 能在 handoff、status、session 和 reducer 中正确出现

## 范围

### 包含

- requirements 文档落地
- traceability matrix 映射
- handoff/status/working-context/index 的同步更新
- runtime session / observation / reducer 在真实任务上的一次验证

### 不包含

- 完整自动化 CI 校验
- 全量 requirement/workstream 一致性检查器
- 多场景业务验证

## 验收条件

- 至少存在一份原始需求、一组标准化需求和一个 workstream
- traceability matrix 能把该场景映射到当前阶段和实现结果
- 实现完成后，相关 handoff/status 能带上对应 metadata
- governance check 能在该真实场景下继续通过

## 依赖与前置条件

- 依赖 `REQ-001` 和 `REQ-002` 的真实代码落地
- 依赖现有 runtime hooks、reducer 与文档模板

## 风险与待澄清项

- 若当前场景落得过轻，可能无法充分验证 traceability 链路
- 若文档和实现不同步，容易出现 requirements 侧已经有 ID 但 AI 侧没有正确引用的漂移

## 关联工作流

- WS-01：Three.js Snake MVP

## 关联阶段

- STAGE-00：Harness 验证与垂直切片接入
