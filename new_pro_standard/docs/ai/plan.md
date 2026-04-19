# 项目计划

更新时间：YYYY-MM-DD
文档定位：阶段规划与范围控制视图

## 使用边界

- 本文件只承载阶段目标、范围、模块划分和阶段验收口径。
- 当前完成度、最新验证结论和执行证据以 `working-context`、`status`、`handoff` 与 `docs/requirements/traceability-matrix.md` 为准。
- 若阶段目标或范围变化，更新本文件；若只是完成度或验证结果变化，优先更新主真相文档。

## 项目目标

- 为 `New Project Standard` 建立最小可用的 Codex-first harness 控制面
- 导入首个真实需求场景并形成第一个垂直切片
- 跑通 `requirements -> implementation -> runtime memory -> handoff/status` 的最小闭环

## 范围定义

### 当前范围

- 初始化 `docs/ai/` 与 `docs/requirements/` 控制面
- 导入首个真实 `REQDOC / REQ / WS`
- 落地第一个可验证的垂直场景

### 暂不纳入范围

- 多 workstream 并行治理
- CI 强校验接入
- 完整发布或部署体系

## 业务线索与模块划分

### 核心业务线索

- 首个真实需求导入与 traceability
- 第一个垂直切片实现与验证
- runtime observation / reducer / handoff / status 压缩验证

### 模块划分

- `docs/requirements/`：原始需求、标准化需求、工作流和追踪矩阵
- `docs/ai/`：执行计划、handoff、status、ADR 和 working context
- `apps/`：垂直切片实现
- `.codex/runtime/`：session、observation 和 reducer 原料

## 阶段规划

### 第 0 阶段：初始化与首个垂直切片

- 目标：建立控制面、导入首个真实场景并完成最小闭环
- 验收：至少一个真实 workstream 能稳定走通 requirements -> implementation -> handoff/status

### 第 1 阶段：治理收紧

- 目标：补更强的一致性校验与阶段压缩规则
- 验收：metadata、traceability 与主真相面的同步规则稳定

### 第 2 阶段：多场景复用

- 目标：把已验证的 harness 复用到更多真实切片
- 验收：不止一个 workstream 能稳定复用同一套治理链路

## 技术与架构决策

- runtime / governance / verification 三层 harness 已采纳
- requirements traceability 采用 `REQDOC -> REQ -> WS -> STAGE` 结构
- 首个垂直场景优先验证 harness 与可用性，而不是先追求完整工程化

## 风险与约束

- 若首个场景过轻，可能不足以验证真实 traceability 链路
- 若共享文档与实现不同步，容易出现 canonical mapping 漂移
- 初始阶段的自动化能力应保持轻量，不依赖过强的 hook 语义判断

## 文档治理约定

- 子任务完成后生成 `handoff`
- 阶段结束后生成 `status`
- 准备联调、合并或发版前生成 `changelog`
- 长期有效决策写入 `adr`
- 阶段文档更新后检查 [AI 文档入口索引](./index.md)
