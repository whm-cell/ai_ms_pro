# 标准化需求：Harness 主真相聚合展示

更新时间：2026-04-18
需求编号：REQ-004
来源文档：REQDOC-002
需求标题：聚合 primary truth surface，形成可直接查看的 Harness 控制台
状态：已完成

## 背景

- 当前仓库已经有 `working-context`、stage `status`、`traceability-matrix` 等 primary truth surface，但阅读入口仍以 Markdown 为主。
- 为了验证第二个真实 workstream，需要一个能直接消费这些 primary truth surface 的 repo-native 应用，而不是再造一份平行状态。

## 目标

- 在浏览器中聚合当前阶段、主目标、活跃队列和 requirements traceability 信息
- 让第二个垂直场景直接以 repo 内主真相文档为数据源运行

## 范围

### 包含

- 读取 `docs/ai/working-context.md`
- 读取 `docs/ai/status/stage-00-runtime-harness-foundation.md`
- 读取 `docs/requirements/traceability-matrix.md`
- 展示当前阶段、摘要卡片、主目标或活跃队列等核心信息

### 不包含

- 在线编辑治理文档
- 服务端存储或多人协作
- 独立于 repo 文档存在的第二套业务数据模型

## 验收条件

- 控制台页面可在静态服务器下成功加载
- 页面能显示当前阶段与 traceability 摘要
- 页面数据来源明确指向 repo 内主真相文档

## 依赖与前置条件

- 依赖 `working-context`、stage `status` 与 `traceability-matrix` 已存在且格式可解析
- 依赖零构建静态应用接入方式继续可用

## 风险与待澄清项

- 若 Markdown 结构后续大幅变化，前端解析逻辑可能需要同步调整
- 若主真相文档出现格式漂移，控制台可能先暴露问题而不是自动修复问题

## 关联工作流

- WS-02：Harness Trace Console

## 关联阶段

- STAGE-00：真实场景验证与治理固化
