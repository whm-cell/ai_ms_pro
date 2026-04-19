# 当前工作上下文

更新时间：YYYY-MM-DD
当前阶段：STAGE-00
当前模式：Codex-first harness engineering

## 作用

本文件只保留当前开发阶段最需要被下一次会话立即继承的真相。

它不是长期归档，不替代 `plan`、`status`、`handoff`、`adr`。

## 当前主目标

- 为 `New Project Standard` 建立最小可用的共享治理控制面
- 导入首个真实需求并形成第一个 workstream
- 让第一个垂直切片完成 requirements、implementation 与治理闭环

## 当前活跃队列

1. 初始化 `docs/ai/` 和 `docs/requirements/` 控制面
2. 导入首个 `REQDOC / REQ / WS`
3. 实现第一个可验证的垂直切片
4. 跑通 runtime observation / session / reducer / handoff-status 链路

## 当前风险与阻塞

- 首个真实场景尚未导入，当前还不能证明 traceability 链路可用
- 若把旧项目共享真相直接复制过来，会污染新项目控制面
- 若未先初始化 index / plan / working-context / traceability-matrix，Stop hook 可能在首轮工作后直接给出治理失败

## 当前真实入口

- [项目规则 AGENTS.md](../../AGENTS.md)
- [AI 文档入口索引](./index.md)
- [需求文档入口索引](../requirements/index.md)
- [项目计划](./plan.md)
- [Harness 可迁移清单](./harness-portability-guide.md)
- [新项目 AGENTS 改写指南](./new-project-agents-rewrite-guide.md)
- [传统项目接入 Harness 的标准起手式](./traditional-project-harness-kickoff.md)
- [V2 文档项目的 REQDOC / REQ / WS / STAGE 拆解模板](../requirements/v2-requirements-splitting-template.md)

## 下一次会话先读

1. [AI 文档入口索引](./index.md)
2. [当前工作上下文](./working-context.md)
3. [需求文档入口索引](../requirements/index.md)
4. [项目计划](./plan.md)
5. [Harness 可迁移清单](./harness-portability-guide.md)
6. [新项目 AGENTS 改写指南](./new-project-agents-rewrite-guide.md)

## 最近已固化的决策

- 项目采用 `AGENTS.md + Codex Stop hook + 校验脚本` 的治理方式
- 项目采用 `docs/requirements/` 与 `docs/ai/` 分层管理需求与执行上下文
- `.codex/runtime/` 只保存本地 session/observation 原料，不替代 `docs/ai/` 共享治理文档

## 更新规则

- 只保留当前阶段仍然有效的信息
- 当阶段切换或主目标变化时优先更新本文件
- 过期信息应进入 `status`、`adr` 或归档，而不是继续堆在本文件里
