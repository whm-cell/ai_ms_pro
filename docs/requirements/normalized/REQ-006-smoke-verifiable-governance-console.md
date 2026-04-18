# 标准化需求：可 smoke 的治理证据控制台

更新时间：2026-04-18
需求编号：REQ-006
来源文档：REQDOC-002
需求标题：提供 deterministic smoke 与 runtime promotion 验证入口
状态：已完成

## 背景

- 如果第二个垂直场景只能手工打开页面查看，仍不足以证明 harness 已具备稳定复用性。
- 当前仓库已经在 `WS-01` 上验证了 deterministic browser smoke，但还没有第二个 workstream 样本。
- 用户要求的是“用一个垂直场景验证 harness 是否可用”，因此这次验证必须包含可重复的 smoke 和 runtime promotion 入口。

## 目标

- 为 `WS-02` 提供 deterministic browser smoke
- 为当前工作区生成带 `REQ/WS` metadata 的 runtime observation/session，并能用 reducer 输出 handoff-first 草稿

## 范围

### 包含

- `?smoke=1` 下的 namespaced 测试 API
- repo-level smoke 脚本
- 用显式 `Requirement IDs / Workstream IDs` 运行 runtime hooks 与 reducer

### 不包含

- 自动化 CI 集成
- 无人工语义判断的 canonical 文档自动发布
- 所有 future workstream 的统一 smoke 基座

## 验收条件

- `python3 scripts/harness_trace_console_smoke.py` 可以稳定通过
- runtime observation 和 session 能带上 `REQ-004, REQ-005, REQ-006 / WS-02`
- reducer 能基于当前 observation 生成带同一组 metadata 的 handoff 草稿

## 依赖与前置条件

- 依赖 `REQ-004` 与 `REQ-005` 对应的页面和筛选能力已完成
- 依赖现有 Stop hooks 与 reducer 脚本仍可手工调用

## 风险与待澄清项

- 当前 runtime metadata 仍依赖显式传入或环境变量，不代表所有自动化场景都已零配置
- smoke 主要覆盖 deterministic 交互与数据解析，不等价于视觉回归或 CI 级稳定性

## 关联工作流

- WS-02：Harness Trace Console

## 关联阶段

- STAGE-00：真实场景验证与治理固化
