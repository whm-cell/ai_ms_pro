# 轻量版大项目文档治理方案

更新时间：2026-04-15

## 目标

在当前仓库内，用尽量少的结构实现：

- 控制阶段性文档膨胀
- 保留可接力的活跃上下文
- 让 AI 与人类都能快速定位当前有效信息
- 在没有重型管理系统的情况下维持稳定的文档秩序

## 核心闭环

持续治理建议明确为：

`分层 -> 压缩 -> 归档 -> 保留活跃入口`

说明：

- 分层：不同职责的内容进入不同文档层
- 压缩：低层高频记录持续汇总到高层摘要
- 归档：失活文档移出主入口
- 保留活跃入口：用 `index.md` 指向当前有效文档

## 推荐目录

```text
docs/
  requirements/
    index.md
    source/
    normalized/
    workstreams/
    traceability-matrix.md
  ai/
    index.md
    plan.md
    handoffs/
      active/
      archive/
    status/
    changelog/
    adr/
    archive/
```

## 六层模型

在存在大量需求文档的项目里，建议把“需求源层”放在 `docs/requirements/`，而不是混入 `docs/ai/`。

这样可以明确区分：

- `docs/requirements/`：要做什么
- `docs/ai/`：现在做到哪、接下来怎么做

### 1. 规划层

- `plan.md`
- 项目目标、范围、阶段、风险、验收标准

### 2. 阶段状态层

- `status/*.md`
- 阶段目标、完成度、风险、阻塞、下一步

### 3. 任务接力层

- `handoffs/active/*.md`
- 当前任务上下文、修改文件、未完成项、下一步动作

### 4. 版本说明层

- `changelog/*.md`
- 对外变更说明

### 5. 长期决策层

- `adr/*.md`
- 跨阶段仍有效的架构与关键决策

### 6. 历史归档层

- `archive/`
- `handoffs/archive/`

## 模板设计依据

这次模板不是按具体业务域构建，而是按两条线索构建：

- 项目推进线索：计划 -> 执行 -> 汇总 -> 发布 -> 长期决策
- 信息生命周期：短期接力 -> 中期阶段判断 -> 长期稳定记忆

因此它更适合作为 AI 协作骨架，而不是某个具体业务系统的专属模板。

如果项目一开始就有多份需求文档，则应先经历：

`原始需求 -> 标准化需求 -> 工作流 -> 开发阶段`

不要直接让开发执行层去消费未经整理的多份原始需求文档。

## Skill 的正确位置

skill 不应该承担全部治理职责。

更稳的分工是：

- 项目规则：定义何时必须更新文档
- hooks / 自动化：在关键事件触发检查
- skill：按需完成某一类任务
- 验证脚本：检查是否漏更新

也就是说，skill 负责“怎么做”，不单独负责“做不做”。

## 项目中期新增 Skill 时如何协调

当项目进入中期，又新增 2 到 4 个 skill 处理新需求时，真正负责协调的不是 skill 本身，而是治理层。

协调机制应当是：

- `AGENTS.md`：定义稳定规则
- `docs/ai/index.md`：定义当前有效入口
- 文档分层：定义结果应该落到哪里
- `Codex`：在当前任务里选择最小必要 skill 集合

### 关键原则

#### 1. 老 skill 不会“常驻运行”

旧 skill 不应被理解成后台一直运行的组件。

它们的有效部分通常体现在：

- 之前产出的文档
- 已经沉淀的代码或脚本
- 已经固化到 `AGENTS.md` 和模板里的规则

#### 2. 新 skill 不能绕过现有文档层

中期新增 skill 后，仍然必须落入既有文档系统：

- 子任务结果进入 `handoff`
- 阶段结论进入 `status`
- 对外变化进入 `changelog`
- 长期决策进入 `adr`

这能保证新旧 skill 的产物仍在同一个治理平面上。

#### 3. 治理规则比单个 skill 更高优先级

如果新 skill 的工作方式与旧约定冲突，以仓库级规则为准。

也就是说：

- skill 可以替换任务方法
- 但不能私自替换文档治理规则

#### 4. 若新 skill 取代旧做法，必须显式记录

如果某个新 skill 改变了长期工作流，应更新：

- `status`：说明当前阶段怎么变了
- `adr`：若属于长期有效决策，则沉淀为正式决策

必要时还应把旧草稿或旧流程说明移入归档。

## 不同阶段如何落地不同 Skill

### 启动与规划阶段

产物：

- `plan.md`
- 必要时 `adr`

适合：

- 规划类
- 架构类
- 技术选型类 skill

### 功能开发阶段

产物：

- `handoff`
- 阶段末 `status`

适合：

- 实现类
- 调试类
- 测试补齐类 skill

### 联调与发布阶段

产物：

- `status`
- `changelog`

适合：

- 验证类
- 发布说明类
- 联调类 skill

## Codex 环境下的最佳适配

对于当前项目，最佳适配应以 Codex 自身的机制为主，而不是以 Claude 风格机制为主。

Codex 下更合适的治理落点是：

1. 项目级 `AGENTS.md`
2. `docs/ai/index.md` 作为活跃入口
3. `plan / handoff / status / changelog / adr` 作为持久记忆层
4. 按需使用 skill，而不是让 skill 长期常驻
5. 用脚本或 CI 做验证层

其中，真正应当“始终生效”的是：

- `AGENTS.md`
- `docs/ai/index.md`
- 文档分层规则
- 验证规则

而不是多个 skill 持续运行。

## 官方最佳实践总结

### OpenAI 方向

结合 OpenAI 的 Codex、Agents、Cookbook 与安全实践，稳定性主要来自四层：

1. 持久项目指令
例如 `AGENTS.md`，存放代码中不能直接推断的项目约束。

2. 活的计划文档
长任务不依赖聊天记忆，而是持续更新计划和当前状态。

3. 结构化输出与 guardrails
不要只靠自由文本更新文档，应先产出结构化状态，再写入模板。

4. evals / graders
复杂 agent 工作流要靠评估和验证，而不只是提示词。

### Anthropic 方向

结合 Claude Code 的官方文档，最稳的做法是：

1. 用 `CLAUDE.md` 承载每次会话都要知道的项目规则
2. 用 `.claude/rules/` 按路径或主题拆分规则
3. 用 hooks 在 `Stop`、`SubagentStop`、`PostToolUse`、`FileChanged` 等事件上触发文档检查
4. 用 subagent 和 skill 处理具体任务，但不让它们单独承担治理

### 对当前仓库的结论

虽然 Anthropic 的 hooks 和规则体系很强，但你当前环境是 Codex。

因此对于本项目，优先级应是：

1. 用 `AGENTS.md` 固化长期规则
2. 用 `docs/ai/index.md` 做活跃入口
3. 用文档模板做结构化记忆
4. 用脚本和 CI 做验证层
5. 再按需引入业务 skill

也就是说，Claude 风格内容可以作为参考，但不应成为当前仓库的主治理实现。

## 对“skill 调用幻觉”的根本解决方式

如果某一阶段引入新的业务 skill，确实可能出现：

- 模型更关注业务实现
- 没有实时更新 handoff / status / index
- 模板信息逐渐失真

根本解决方式不是继续叠加更多 skill，而是把文档维护提升为工作流完成条件：

1. 在项目级规则中明确何时必须更新文档
2. 用事件钩子在关键时点触发检查
3. 用结构化字段表达阶段状态
4. 用脚本或 CI 校验文档是否同步

## 第二层兜底：Git Pre-commit

当前仓库已补充版本化 Git hook：

- `.githooks/pre-commit`

它运行：

- `python3 scripts/check_ai_docs.py`

这个 hook 的定位是第二层兜底：

- 第一层：Codex `Stop` hook
- 第二层：Git `pre-commit`
- 第三层：后续可接入 CI

这样即使某次 Codex 会话没有触发或没有正确执行收尾，提交时仍会再次检查。

## 验证层应该从什么时候开始

### 结论

验证层应该从项目一开始就存在，但不应该一开始就做重。

正确做法不是：

- 一开始完全没有验证
- 或者一开始就上完整 CI 与复杂检查

而是：

- Day 0 就有最小验证
- 随项目复杂度增加逐步加强

### 第 0 阶段：初始化阶段

这时就应该有最小验证。

最小验证包括：

- 每次有实质性改动后，检查是否影响 `docs/ai/`
- 新增文档后，检查 `index.md` 是否仍然正确

这时不一定需要脚本，但必须有规则。

### 第 1 阶段：项目刚开始开发但规模还小

这时建议补一个轻量脚本。

目标不是阻塞开发，而是给出提示，例如：

- 代码改了但 `docs/ai/` 没动
- 新建了 `status` 但索引没更新

这个阶段的验证应以“提醒”为主。

### 第 2 阶段：进入多阶段、多任务、多会话开发

这时验证层就不该只是提醒，而应更强。

建议检查：

- 活跃 `handoff` 是否指向当前阶段
- 已完成阶段是否产出 `status`
- `index.md` 是否引用最新活跃文档
- 应归档的 `handoff` 是否还停留在活跃区

### 第 3 阶段：准备合并、发版、团队协作

这时验证层应进入 CI 或至少进入标准检查流程。

因为到了这个阶段，文档漂移的成本已经高于补检查的成本。

## 如果一开始不提供验证层，会发生什么

会出现三个直接后果：

1. 早期文档结构看起来存在，但没有执行力
2. 文档更新完全依赖会话中的临时记忆
3. 到中期才开始补验证时，往往已经有一批失真的文档需要回补

所以不建议完全没有验证层起步。

## 如果一开始就提供验证层，会不会妨碍后续变更

不会，只要验证层本身也是分阶段演进的。

关键是：

- 一开始验证的是“基础约束”
- 后续验证规则随项目成熟逐步扩展

不要把一开始的验证写死成大量细节，而应写成可增长的最小骨架。

## 项目变更时，验证层怎么跟着变

推荐把验证规则分成两类：

### 1. 稳定规则

这些规则很少变化：

- 活跃文档必须能从 `index.md` 找到
- 阶段成果应被压缩进更高层文档
- 归档文档不应继续占据主入口

### 2. 项目特定规则

这些规则会随着阶段变化调整：

- 当前阶段需要哪些文档
- 哪些目录变更必须配套 handoff
- 哪些模块变化必须写 ADR

也就是说，验证层并不是一次性写完，而是：

- 核心不变
- 细则迭代

这和测试体系是一样的。

## 对当前项目的建议时间线

### 现在立刻应做的

- 保留 `AGENTS.md`
- 保留 `index.md`
- 保留模板
- 采用手工验证规则

### 下一步应做的

- 增加一个最小校验脚本
- 校验 `index.md` 链接和活跃文档指向

### 项目进入真实开发后应做的

- 把校验脚本接入常用命令或 CI
- 随项目阶段补充更细的验证条件

## 推荐的最稳组合

对当前项目，建议采用：

1. `index.md` 作为总入口
2. `plan / handoff / status / changelog / adr` 作为文档分层
3. `session-handoff / status-report / changelog-automation` 作为按需 skill
4. 后续补一个项目级规则文件
5. 再补最小的 hook 或校验脚本

## 当前仓库的最小验证脚本

当前仓库已增加：

- `python3 scripts/check_ai_docs.py`
- `.codex/hooks.json`
- `.codex/hooks/stop_ai_docs_check.py`

它当前负责：

- 检查 `index.md` 是否引用核心文档
- 检查活跃 `handoff` / `status` / `changelog` / `adr` 是否已在 `index.md` 中出现
- 检查 `index.md` 中的本地路径链接是否存在

它当前不负责自动改文档，只负责发现漂移。

这是刻意设计的，因为“验证”和“修改”最好分开。

## 这个脚本应当由谁调用

短期：

- 由 Codex 按 `AGENTS.md` 规则主动调用
- 并由 repo-local `Stop` hook 自动兜底

中期：

- 由固定收尾流程调用，例如提交前、阶段结束前、发版前

长期：

- 由 CI 或统一检查流程调用，而不是依赖模型记忆

## 如果只让大模型自己决定要不要调用，会不会忘

会。

如果完全依赖模型在复杂上下文中“自己想起来”，那它确实可能漏掉。

所以稳健做法不是“希望模型记得”，而是：

- 在 `AGENTS.md` 中写成显式规则
- 在固定流程中绑定脚本
- 最终在 CI 中强制执行

也就是说，当前阶段可以先让 Codex 主动调用，但目标状态应是“流程绑定”，而不是“记忆绑定”。

## Codex 化后的结构变化

从“以 skill 为中心的提醒式治理”切换到“Codex 执行行为 + 验证层”后，以下结构仍然保留：

- `docs/ai/index.md`
- `plan / handoff / status / changelog / adr`
- 按需使用的 skill

真正发生变化的是治理重心：

- 从“希望 skill 或模型记得更新文档”
- 变成“由 `AGENTS.md` + `Stop hook` + 验证脚本`共同约束`”

因此，不再适用的通常不是文档分层本身，而是那些脱离当前入口体系的旧草稿、重复稿或过渡目录。

## 官方来源

- OpenAI Codex 文档：[Codex](https://developers.openai.com/codex/cloud)
- OpenAI GPT-5 Troubleshooting Guide：[Troubleshooting Guide](https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_troubleshooting_guide)
- Claude Code Common Workflows：[Common workflows](https://code.claude.com/docs/en/common-workflows)
- Claude Code Custom Subagents：[Create custom subagents](https://code.claude.com/docs/en/sub-agents)
