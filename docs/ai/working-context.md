# 当前工作上下文

更新时间：2026-04-25
当前阶段：STAGE-00 真实场景验证与治理固化
当前模式：Codex-first harness engineering

## 作用

本文件只保留当前开发阶段最需要被下一次会话立即继承的真相。

它不是长期归档，不替代 `plan`、`status`、`handoff`、`adr`。

## 同步元数据

- Current Stage: STAGE-00
- Active Status Source: docs/ai/status/stage-00-runtime-harness-foundation.md
- Active Handoff Sources:
  - docs/ai/handoffs/active/stage-00-governance-surface-slimming.md
  - docs/ai/handoffs/active/stage-00-runtime-stop-session.md
  - docs/ai/handoffs/active/stage-00-observation-reducer.md
  - docs/ai/handoffs/active/stage-00-harness-portability-template.md
  - docs/ai/handoffs/active/stage-00-new-repo-rehearsal.md
- Requirement IDs: REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006
- Workstream IDs: WS-01, WS-02
- Last Synced From: status,handoff,manual
- Last Synced At: 2026-04-25

## 当前主目标

- 判断 Stage-00 是否已经完成“可用性验证”，并把剩余 hardening 缺口收敛成小规模 backlog
- 保持 `docs/ai/` 与 `docs/requirements/` 的默认控制面轻量、稳定、可恢复
- 确认 `new_pro_standard` 现在已经可以按“starter copy -> bootstrap -> 首个 REQDOC / REQ / WS”路径直接用于新项目起手
- 继续把 runtime、reducer 与 traceability 的一致性校验推进到更真实的样本上

## 当前活跃队列

1. 以 [Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md) 为准，继续推进 OPEN-01、OPEN-02、OPEN-03、OPEN-04、OPEN-06
2. 判断 Stage-00 是否可以在完成本轮 hardening 后压缩并进入下一阶段
3. 用真实 observation 验证 runtime metadata 自动发现与 reducer 压缩阈值
4. 继续观察 active handoff 预算 warning 是否足够收紧默认恢复面，必要时再调阈值或升级级别

## 当前风险与阻塞

- governance check 与 smoke 仍未进入 CI，merge 前守门尚未闭环
- runtime observation/session 依赖 best-effort payload，`REQ/WS` 自动带齐仍未在零配置路径上验证
- reducer 已可用，但尚未在更长期 observation 数据上证明压缩质量
- `WS-01` 与 `WS-02` 的 smoke 仍偏 deterministic；更黑盒的浏览器回归和长期稳定性验证尚未补齐
- starter portability 已在 `output/` 内演练成功，但仓库外部独立路径复演仍未完成
- starter 已补齐 Windows hook entrypoints、code-shape 与 metadata 校验能力，bootstrap 也会按当前宿主环境刷新 `.codex/hooks.json`；若仓库初始化后迁移到另一种 host shell，仍需重新 bootstrap 或只调整 hook 入口配置
- active surface budget 当前只是 warning，不是 blocking；若后续 handoff 再次堆积，仍需要主 Agent 主动压缩/归档

## 下一次会话先读

1. [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
2. [Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
3. [Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md)
4. [当前活跃 handoff 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active)
5. [需求文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/index.md)：当任务直接落在 `REQ/WS` 或 traceability 时再进入
6. [ADR 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr)：当需要长期决策背景时再进入

## 最近已固化的决策

- 项目继续采用 `Runtime Harness + Governance Harness + Verification Harness` 的三层分工，runtime 只保留本地恢复原料
- `plan/workstream` 继续作为 projection surface；当前状态真相默认集中在 `working-context`、`handoff`、`status`、`traceability-matrix`
- `working-context` 继续只保留轻结构化同步元数据和下一步增量真相，不升级为第二份阶段状态总表
- `Stop -> observation/session -> SessionStart additionalContext -> reducer draft` 的最小 runtime promotion 链路已成立，但 reducer 仍维持 handoff-first
- `WS-01` 与 `WS-02` 已验证当前 harness 能支撑两个真实 repo-native workstream
- 默认治理面已收缩为 `index -> working-context -> stage status -> <=5 active handoff`；已被 stage `status` / ADR 吸收的完成型 handoff 进入 archive
- `new_pro_standard` 已同步 Windows hook entrypoints、repo-local Python runnable probe、坏 venv 自愈、staged code-shape pre-commit 与 active handoff/status traceability metadata 校验；新仓 bootstrap 还会按当前宿主环境刷新 `.codex/hooks.json`，默认生成轻量路由型 `index` 与增量真相型 `working-context`
- `index` 与 `working-context` 已进一步去重：精确 active handoff 集合由同步元数据维护，默认恢复入口不再重复展开同一组文档清单
- 2026-04-24: `ghtt_crawler` 中已验证的 Windows hook entry、runnable Python resolution、repo-local venv self-heal 与 staged code-shape budget 已反哺进当前 harness，并在 ADR-008 固化。

## 更新规则

- 只保留当前阶段仍然有效的信息
- 当阶段切换或主目标变化时优先更新本文件
- 过期信息应进入 `status`、`adr` 或归档，而不是继续堆在本文件里
