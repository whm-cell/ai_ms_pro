# 新项目 AGENTS 改写指南

更新时间：2026-04-19
适用范围：把 `new_pro_standard` 引入一个新仓库之后，如何把 starter 版 `AGENTS.md` 改成该项目自己的默认治理规则

## 核心判断

`AGENTS.md` 不是项目简介，也不是当前状态摘要。

它应该回答的是：

- 这个仓库默认如何与 AI 协作
- 哪些文档是主真相
- 哪些规则每次都成立
- 一个任务什么情况下才算完成

所以改写 `AGENTS.md` 的目标不是“写得更长”，而是把 repo 的默认约束写准。

## 哪些内容建议保留

starter 里的这些部分通常可以保留，只需小幅参数化：

- `Document System`
- `Required Workflow`
- `Reading Order`
- `Harness Layers`
- `Python Runtime Rule`
- `Projection Surface Boundary`
- `Verification Layer`
- `Completion Condition`

这些部分描述的是机制层，不是旧项目真相。

## 哪些内容必须改写

新项目至少要改这 6 类信息。

### 1. Purpose

要改成“这个项目在做什么”，而不是继续沿用 starter 的泛化表述。

至少补清：

- 项目目标
- 项目边界
- AI 在这个仓库中的主要职责

### 2. Project Bootstrap Notes

这里要改成新仓库的实际初始化说明。

至少补清：

- 哪些文件在第一次会话前必须先确认
- 哪些文档要先改写
- 哪些目录是业务代码主入口

### 3. Reading Order

如果新项目有自己的真相入口，必须写进阅读顺序。

常见补充：

- 核心架构文档
- API 合同文档
- 业务领域词汇表
- 数据库 schema 或 interface 目录

### 4. Repo-specific Defaults

starter 默认只定义治理骨架，不知道你的项目怎么跑。

这里通常要新增或改写：

- 代码主目录
- 启动命令
- 测试命令
- 生成物目录
- 禁止直接改写的目录
- 需要谨慎处理的外部依赖或环境

### 5. Verification Layer

这里必须变成“这个项目真实可执行的检查方式”。

至少明确：

- 首选治理检查命令
- 项目自己的测试命令
- 哪些场景必须 smoke / integration test

### 6. Completion Condition

不能只保留“治理检查通过”，还要补项目交付门槛。

常见补充：

- 关键测试通过
- API 合同同步
- 数据迁移脚本齐全
- 前端/后端联调通过

## 哪些内容不要写进 AGENTS.md

这些内容应放到别处，不应写进 `AGENTS.md`：

- 当前阶段状态
- 当前 backlog
- 某次会话的临时任务
- 一次性 bug 处理记录
- 已经过期的旧版本需求摘要
- 当前项目特定的 `REQ-XXX` / `WS-XX` 列表

这些应分别进入：

- `working-context`
- `handoff`
- `status`
- `traceability-matrix`

## 推荐改写顺序

1. 先保留 starter 的机制骨架，不要一开始大改结构。
2. 先改 `Purpose` 和 `Project Bootstrap Notes`，把旧项目语义清掉。
3. 再补 `Reading Order` 和 repo-specific defaults。
4. 最后补 `Verification Layer` 与 `Completion Condition`。
5. 改完后立刻跑 `python3 scripts/check_ai_governance.py`。

## 最小改写清单

如果你时间有限，先确保这份最小清单完成：

- `Purpose` 已换成新项目目标
- `Project Bootstrap Notes` 已写明首轮初始化动作
- 阅读顺序已指向新项目真实入口
- 已明确代码主目录和测试命令
- 已明确哪些文档是 primary truth
- 已明确任务完成的最小验证条件

## 推荐补充的 repo-specific 段落

如果是中大型项目，建议在 `AGENTS.md` 额外加 2 到 4 个短段落：

- `## Code Entry Points`
- `## Repo-specific Constraints`
- `## Verification Commands`
- `## Protected Boundaries`

它们比把细节塞进 `working-context` 更稳定。

## 一个够用的 starter 改写结果应该长什么样

下面这组信息如果都能在 `AGENTS.md` 找到，基本就算改到位了：

- 仓库要做什么
- 默认先读哪些真相文件
- 需求和执行文档如何分层
- hooks / scripts / docs 各自负责什么
- 代码改动后至少要补什么文档
- 完成任务前至少跑哪些检查

## 可直接给 AI 的改写指令

```text
不要直接写业务代码。
先把当前仓库的 AGENTS.md 从 starter 版改成项目版：
1. 保留 harness 机制骨架
2. 移除旧项目假设
3. 写清项目目标、代码入口、验证命令、受保护边界
4. 保持 docs/ai 与 docs/requirements 的分层不变
5. 改完后检查 index、working-context、requirements index 是否仍一致
```
