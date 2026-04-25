# Harness Remaining Work

更新时间：2026-04-25
当前状态：核心链路已在测试仓库跑通，starter 机制层也已与主仓重新对齐并可经 bootstrap 适配当前宿主环境；剩余项以 hardening 为主

## 作用

本文件用于集中列出当前 harness 仍未完成的事项。

它关注的是“还差什么才能更稳定、更可复用”，不是历史回顾。

## 当前判断

- `0 -> 1 初始化可用性` 已在测试仓库验证完成
- `requirements -> implementation -> smoke -> runtime promotion -> status` 已在新仓库内跑通一轮
- 当前剩余问题不再是“能不能用”，而是 `CI + external replay + auto-discovery + cross-host migration hardening`

## P0 当前最值得做

### OPEN-01 CI 接入

- 目标：把 `quick_notes_inbox_smoke.py` 与 `check_ai_governance.py` 纳入持续约束
- 当前缺口：现有验证只在本地人工执行，还没有 merge 前守门
- 完成定义：
  - 有明确的 CI 入口
  - `python3 scripts/check_ai_governance.py` 自动运行
  - `python3 scripts/quick_notes_inbox_smoke.py` 自动运行
  - 失败时能直接阻断回归

### OPEN-02 外部独立路径复演

- 目标：在主仓 `output/` 之外，再复演一次 `new_pro_standard` 的 starter copy 与 bootstrap
- 当前缺口：现有测试仓库仍位于主仓内部路径，尚未完全排除环境共振
- 完成定义：
  - 在外部独立目录中复制 starter
  - 完成 `bootstrap -> git hook -> first REQDOC/REQ/WS -> smoke -> governance check`
  - 结果与当前测试仓库一致

### OPEN-03 Runtime Metadata 自动发现验证

- 目标：验证 runtime hook 在不显式传入 `REQ/WS` 环境变量时，能否稳定带齐 metadata
- 当前缺口：当前 observation/session/reducer 证明的是“显式 metadata 可贯穿”，不是“默认就能自动带齐”
- 完成定义：
  - 至少一轮 observation / session / reducer 不依赖显式环境变量
  - 输出仍能正确关联 `Requirement IDs` 与 `Workstream IDs`

## P1 次高优先级

### OPEN-04 Reducer 压缩阈值验证

- 目标：用更真实的 observation 样本评估 reducer 噪音和压缩质量
- 当前缺口：现有样本量小，尚不足以证明长期使用时不会过度泛化或信息不足
- 完成定义：
  - 有多轮 observation 样本
  - reducer 输出可稳定区分 runtime-only 与应提升内容
  - 明确何时压缩到 `status` 或 `ADR`

### OPEN-05 更黑盒的浏览器回归

- 目标：在现有 deterministic smoke 之外，再补一层不依赖 namespaced API 的浏览器验证
- 当前缺口：现有 smoke 能证明行为稳定，但仍依赖 `?smoke=1` 下的测试接口
- 完成定义：
  - 至少一条核心用户路径可在更黑盒模式下通过
  - 能覆盖表单输入、提交、列表结果等可见行为

### OPEN-06 Traceability / Metadata 一致性自动校验

- 目标：自动检查 AI-side metadata 与 `traceability-matrix.md` 的一致性
- 当前缺口：`working-context` 与 active `handoff/status` 的 `REQ/WS` 字段存在性校验已接入，但 reducer output、runtime 产物与更细的 `REQ <-> WS <-> STAGE` 组合关系校验仍未自动化
- 完成定义：
  - `handoff / status / reducer output` 中的 `REQ/WS` 能和 requirements 面对齐
  - mismatch 会被脚本直接拦下或至少报警

## P2 策略性决策

### OPEN-07 Starter 是否保留 Quick Notes 样板

- 目标：决定 `Quick Notes Inbox` 是继续作为 starter 自带样板，还是只保留治理机制层
- 当前缺口：当前测试仓库已经证明样板有价值，但 starter 默认是否应带示例仍未定
- 完成定义：
  - 明确选择“保留样板”或“只保留治理面”
  - 相应更新 starter 文档和迁移说明

## 当前不纳入本轮

- 发布 / 部署体系
- 多 workstream 并行治理
- 复杂前端或后端工具链验证
- 自动归档 handoff / changelog 策略

## 建议阅读顺序

1. [AI 文档入口索引](./index.md)
2. [当前工作上下文](./working-context.md)
3. [Stage-00 Runtime Harness Foundation Status](./status/stage-00-runtime-harness-foundation.md)
4. [New Repo Rehearsal Handoff](./handoffs/active/stage-00-new-repo-rehearsal.md)
