# Harness Remaining Work

更新时间：2026-04-30
当前状态：核心链路已在测试仓库和仓外 starter 复演中跑通；CI、hook sync、更深一层的 traceability alignment、runtime metadata 自动发现、首条黑盒 smoke 与可选行为护栏 skill 已落地，剩余项继续以 hardening 为主

## 作用

本文件用于集中列出当前 harness 仍未完成的事项。

它关注的是“还差什么才能更稳定、更可复用”，不是历史回顾。

## 当前判断

- `0 -> 1 初始化可用性` 已在测试仓库和仓外 starter 复演中验证完成
- `requirements -> implementation -> smoke -> runtime promotion -> status` 已在新仓库内跑通一轮
- Stop hook 的 `REQ/WS` 自动发现现已覆盖 `observation -> session -> reducer draft` 流程
- `harness-trace-console` 已新增黑盒 DOM smoke，不再只依赖 `?smoke=1` 下的 namespaced test API
- Karpathy-style 行为护栏已进入 starter 机制层，但仍保持显式调用，不替代仓库治理文档或检查脚本
- archive candidate monitor 已落地为 warning-only 检查；自动归档仍不纳入默认 hook
- 当前剩余问题不再是“能不能用”，而是 `CI burn-in + reducer threshold + blackbox 扩展 + deeper runtime/stage consistency`

## P0 当前最值得做

### OPEN-01 CI burn-in 与 workflow 稳定性观察

- 目标：让新落地的 `governance + hook sync + repo-native smoke` workflow 积累远端稳定运行历史
- 当前缺口：workflow 文件已落地，但还没有足够的远端 green history 来证明它在常规 PR / push 上稳定
- 完成定义：
  - 至少一轮远端 workflow 通过
  - `python3 scripts/sync_hooks_config.py --check` 自动运行
  - `python3 scripts/check_ai_governance.py` 自动运行
  - `python3 scripts/threejs_snake_smoke.py` 与 `python3 scripts/harness_trace_console_smoke.py` 自动运行
  - 失败结果能直接定位到 governance、hook sync 或 smoke 维度

## 本轮已关闭

### OPEN-02 外部独立路径复演

- 结果：已在仓外临时目录完成 `starter copy -> bootstrap --force -> git config core.hooksPath .githooks -> git add -> .githooks/pre-commit`
- 关闭原因：starter 的 `run_with_repo_python.sh` 已修复 macOS `/bin/bash` 3.2 空数组兼容性问题，`check_code_shape.py --staged` 也已把 unborn `HEAD` 的首提交 scaffold 视为 baseline
- 备注：starter copied placeholder docs 若要立刻替换成新项目名，仍需显式 `--force`；`AGENTS.md` 仍由人工项目化，README 与 portability guide 已同步说明

### OPEN-03 Runtime Metadata 自动发现验证

- 结果：Stop runtime observation/session 已支持 changed paths、workstream 模块路径和 traceability matrix 驱动的 `REQ/WS` 自动发现
- 关闭原因：已补 observation、session 以及 reducer draft 三层测试，零配置路径能稳定携带 `Requirement IDs` 与 `Workstream IDs`

## P1 次高优先级

### OPEN-04 Reducer 压缩阈值验证

- 目标：用更真实的 observation 样本评估 reducer 噪音和压缩质量
- 当前缺口：现有样本量小，尚不足以证明长期使用时不会过度泛化或信息不足
- 完成定义：
  - 有多轮 observation 样本
  - reducer 输出可稳定区分 runtime-only 与应提升内容
  - 明确何时压缩到 `status` 或 `ADR`

### OPEN-05 更广的黑盒浏览器回归

- 目标：在已落地的 `harness-trace-console` 黑盒 DOM smoke 之外，再决定是否扩展更多黑盒路径
- 当前缺口：`WS-02` 已不再依赖 namespaced test API，但 `WS-01 / threejs-snake` 仍主要依赖 deterministic smoke
- 完成定义：
  - 至少再补一条核心用户路径或第二个 workstream 的黑盒回归
  - 继续优先使用可见 DOM / 用户交互断言，而不是回退到内部测试 API

### OPEN-06 Traceability / Metadata 一致性自动校验

- 目标：继续把 traceability 校验从当前 primary truth docs 扩展到 runtime / reducer / stage 组合关系
- 当前缺口：AI-side metadata、normalized/workstream 文档以及 matrix -> 文档存在性对齐已接入，但 reducer output、runtime 产物与更细的 `REQ <-> WS <-> STAGE` 组合关系校验仍未自动化
- 完成定义：
  - `handoff / status / reducer output / runtime artifact` 中的 `REQ/WS` 能和 requirements 面对齐
  - `Current Stage` 与 matrix 中的 `STAGE` 关系具备至少一层自动校验
  - mismatch 会被脚本直接拦下或至少报警

## P2 策略性决策

### OPEN-07 Starter 是否保留 Quick Notes 样板

- 目标：决定 `Quick Notes Inbox` 是继续作为 starter 自带样板，还是只保留治理机制层
- 当前缺口：当前测试仓库已经证明样板有价值，但 starter 默认是否应带示例仍未定
- 完成定义：
  - 明确选择“保留样板”或“只保留治理面”
  - 相应更新 starter 文档和迁移说明

### OPEN-08 行为护栏 skill 是否升级为默认 workflow

- 目标：观察 `$repo-governed-coding` 在更多真实任务中的收益，决定它继续显式调用，还是升级为更稳定的 stage / repo 默认策略
- 当前缺口：已进入 starter，但还缺少多任务样本证明它适合作为默认工作流
- 完成定义：
  - 至少几个非平凡实现/审查任务中显式使用该 skill
  - 能证明 assumptions / scope / success criteria / verification plan 对 handoff/status 提炼有实际帮助
  - 若升级为默认，补对应 `status` 或 `ADR`；若不升级，保持显式调用并避免写入 always-on 规则

## 当前不纳入本轮

- 发布 / 部署体系
- 多 workstream 并行治理
- 复杂前端或后端工具链验证
- 自动归档 handoff / changelog 策略；当前只提供 warning-only candidate monitor

## 建议阅读顺序

1. [AI 文档入口索引](./index.md)
2. [当前工作上下文](./working-context.md)
3. [Stage-00 Runtime Harness Foundation Status](./status/stage-00-runtime-harness-foundation.md)
4. [New Repo Rehearsal Handoff](./handoffs/active/stage-00-new-repo-rehearsal.md)
