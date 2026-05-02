# 当前工作上下文

更新时间：YYYY-MM-DD
当前阶段：STAGE-00
当前模式：Codex-first harness engineering

## 作用

本文档只保留当前开发阶段最需要被下一次会话立即继承的增量真相。

它不是长期归档，不替代 `plan`、`status`、`handoff`、`adr`。

## 同步元数据

- Current Stage: STAGE-00
- Active Status Source: 未绑定
- Active Handoff Sources: 未绑定
- Requirement IDs: 未绑定
- Workstream IDs: 未绑定
- Last Synced From: bootstrap
- Last Synced At: YYYY-MM-DD

## 当前主目标

- 为 `New Project Standard` 建立最小可用的共享治理控制面。
- 导入首个真实需求并形成第一个 `workstream`。
- 让第一条垂直切片跑通 `requirements -> implementation -> runtime memory -> handoff/status`。

## 当前活跃队列

1. 初始化 `docs/ai/` 与 `docs/requirements/` 控制面。
2. 导入首个 `REQDOC / REQ / WS`。
3. 实现第一个可验证的垂直切片。
4. 跑通 runtime observation / session / reducer / handoff-status 链路。
5. 默认将共享恢复面保持在 `index -> working-context -> status -> configured active handoff budget`。

## 当前风险与阻塞

- 首个真实场景尚未导入，当前还不能证明 traceability 链路可用。
- 若把旧项目共享真相直接复制过来，会污染新项目控制面。
- 若未先初始化 `index / plan / working-context / traceability-matrix`，`Stop` hook 可能在首轮工作后直接给出治理失败。
- active handoff 默认预算由 `.codex/harness.toml` 控制；被 `status` 吸收后的完成型 handoff 应进入 `archive`，否则默认恢复面会再次膨胀。

## 下一次会话先读

1. [AI 文档入口索引](./index.md)
2. [当前工作上下文](./working-context.md)
3. [需求文档入口索引](../requirements/index.md)
4. [项目计划](./plan.md)
5. [Harness 可迁移清单](./harness-portability-guide.md)
6. [新项目 AGENTS 改写指南](./new-project-agents-rewrite-guide.md)

## 最近已固化的决策

- 项目采用 `Runtime Harness + Governance Harness + Verification Harness` 三层分工。
- `.codex/runtime/` 只保留本地恢复原料，不替代 `docs/ai/` 与 `docs/requirements/` 的共享治理真相。
- 默认共享恢复面保持轻量：`index -> working-context -> status -> configured active handoff budget`。
- `plan` 与 `workstream` 属于 projection surface，不应重复承载快速变化的当前状态。
- `.codex/skills/repo-governed-coding/` 是可选行为护栏，默认显式调用，不替代 `AGENTS.md`、共享治理文档或检查脚本。

## 更新规则

- 只保留当前阶段仍然有效的增量真相。
- 当 stage 切换、主目标变化或 `status/handoff` 完成压缩后优先更新本文档。
- 过期细节应进入 `status`、`adr` 或 `archive`，而不是继续堆在默认恢复面里。
