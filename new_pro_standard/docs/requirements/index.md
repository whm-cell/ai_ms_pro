# 需求文档入口索引

更新时间：YYYY-MM-DD
当前状态：待导入首个真实验证场景

## 目的

本目录用于管理项目的需求来源、需求标准化结果、工作流拆解和需求追踪关系。

它回答四个问题：

- 原始需求文档有哪些
- 每份需求文档标准化后是什么
- 这些需求被拆成了哪些可执行工作流
- 当前开发阶段正在响应哪些需求

## 建议阅读顺序

1. [需求追踪矩阵](./traceability-matrix.md)
2. [标准化需求目录](./normalized)
3. [工作流目录](./workstreams)
4. [原始需求目录](./source)

## 目录结构

- [source](./source)
- [normalized](./normalized)
- [workstreams](./workstreams)
- [traceability-matrix.md](./traceability-matrix.md)

## 使用规则

- `source/` 只保存原始需求文档或原始需求转录稿
- `normalized/` 将原始需求统一整理成一致结构
- `workstreams/` 将多个需求映射成可开发的业务工作流
- `traceability-matrix.md` 负责串联 `需求 -> 工作流 -> 阶段 -> 实现/测试`
- 当 `docs/ai/` 下的 `handoff`、`status` 或 reducer 草稿已经绑定需求时，应显式写出 `Requirement IDs` / `Workstream IDs`，并与本目录中的追踪关系保持一致

## 当前活跃内容

- 暂无 source 文档
- 暂无 normalized 文档
- 暂无 workstream 文档
- 追踪关系将在 [traceability-matrix.md](./traceability-matrix.md) 中初始化
