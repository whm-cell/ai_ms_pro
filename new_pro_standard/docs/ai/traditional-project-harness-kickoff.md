# 传统项目接入 Harness 的标准起手式

更新时间：2026-04-19
适用范围：已有代码仓库、已有部分文档或约定，但还没有 Codex-first harness 的项目

## 目标

在不打断现有交付的前提下，把项目接到这套 harness 上。

重点不是一次性补全所有历史，而是：

- 先建立最小控制面
- 先让下一轮真实功能迭代可追踪
- 再逐步把治理强度补上

## 起手原则

- 不追求一次性回填全量历史需求
- 不先给全仓每个模块都建立 `REQ / WS`
- 不把 `plan` 写成当前状态公告栏
- 先让一个真实迭代链路跑通，再扩展

## 第一轮必须完成的事

第一轮接入，建议只完成这 8 件事：

1. 引入 starter 机制层文件
2. 运行 bootstrap，建立最小 `docs/ai` 与 `docs/requirements`
3. 改写 `AGENTS.md`
4. 建立当前项目的 `working-context`
5. 导入一个最重要的原始需求文档为 `REQDOC`
6. 拆出首批 `REQ`
7. 归并成第一个 `WS`
8. 用这个 `WS` 跑一轮真实实现 -> handoff -> governance check

## 标准接入步骤

### Step 0. 盘点现状

先不要改业务代码，先盘点：

- 代码主目录
- 真实启动命令
- 测试命令
- 现有产品文档或需求文档
- 当前版本最重要的一条功能线

产出目标：

- 知道“哪个模块最适合做第一条垂直切片”
- 知道“哪份文档适合作为首个 `REQDOC`”

### Step 1. 唤醒控制面

把 `new_pro_standard` 的内容复制到新仓库根目录后，执行：

```bash
python3 scripts/bootstrap_harness.py --project-name "你的项目名"
git config core.hooksPath .githooks
```

然后确认仓库根已有：

- `AGENTS.md`
- `.codex/`
- `docs/ai/`
- `docs/requirements/`
- `scripts/`

### Step 2. 改写治理骨架

先改这些文件，不要先写业务实现：

- `AGENTS.md`
- `docs/ai/index.md`
- `docs/ai/working-context.md`
- `docs/ai/plan.md`
- `docs/requirements/index.md`
- `.codex/harness.toml`

目标是把旧项目假设清掉，让 AI 读到的是新仓库真相。

### Step 3. 只导入一个真实需求包

不要一次导入十几份旧文档。

第一轮只选一个：

- 当前最重要的功能升级
- 当前最急的版本目标
- 当前最容易形成端到端验证的用户路径

然后建立：

- `REQDOC-001`
- `REQ-001 ~ N`
- `WS-01`
- `traceability-matrix` 映射

### Step 4. 只实现一个垂直切片

第一轮不要铺开多个 workstream。

只做：

- 一个 `WS`
- 一条端到端路径
- 一套最小验证

完成后补：

- `handoff`
- 必要时 `status`
- `traceability-matrix`

### Step 5. 接入日常节奏

当第一条链路已经跑通后，再把这套方式变成默认工作流：

- 新需求先落 `REQDOC / REQ / WS`
- 当前执行状态写 `working-context`
- 子任务完成写 `handoff`
- 阶段结束压 `status`
- 长期决策写 `ADR`

## 第一轮推荐产物

如果你只想知道“第一轮最小要落哪些文件”，建议是这组：

- `AGENTS.md`
- `docs/ai/index.md`
- `docs/ai/working-context.md`
- `docs/ai/plan.md`
- `docs/requirements/index.md`
- `docs/requirements/source/REQDOC-001-*.md`
- `docs/requirements/normalized/REQ-001-*.md`
- `docs/requirements/workstreams/WS-01-*.md`
- `docs/requirements/traceability-matrix.md`
- `docs/ai/handoffs/active/<first-workstream>.md`

## 第一轮不要做的事

- 不要补全所有历史版本 `REQDOC`
- 不要给每个技术任务都建 `WS`
- 不要把 `working-context` 写成长篇项目介绍
- 不要把 `plan` 写成每天变动的进度面板
- 不要让 runtime 文件替代 handoff/status

## 传统项目最适合 harness 的切入点

优先选这些场景做首轮接入：

- 一个明确的 V2 功能
- 一个可端到端验证的页面或接口链路
- 一个已经有现成需求文档的模块
- 一个跨前后端但边界清晰的迭代

不建议首轮就拿这些做切入：

- 全仓重构
- 全量技术债治理
- 大规模目录迁移
- 无明确验收标准的抽象优化

## 可直接给 AI 的首轮接入 Prompt

```text
先不要直接写业务功能。
先把当前传统项目接到这套 harness 上：
1. 盘点代码目录、启动方式、测试方式、现有文档
2. 改写 AGENTS.md、index、working-context、plan、requirements index
3. 选一份最重要的现有需求文档作为 REQDOC-001
4. 拆出首批 REQ，并归并成 WS-01
5. 只实现 WS-01 的第一个垂直切片
6. 完成后补 handoff、traceability，并跑 governance check
```

## 完成判定

传统项目接入 harness 的第一轮，不是看“文档写了多少”，而是看下面这条链路有没有跑通：

`existing docs -> REQDOC -> REQ -> WS -> implementation -> handoff -> governance check`

只要这条链已经跑通一次，后续迭代就可以按同一套路扩大。
