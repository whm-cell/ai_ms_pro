# 中型项目阶段性文档与 Skill 选型发现总结

更新时间：2026-04-15

## 目标

本文档汇总本项目关于“常规 AI 编程与 subagent 并行开发后，如何稳定生成阶段性文档”的发现。

关注点包括：

- 如何避免多轮会话后上下文丢失
- 如何让主 agent 与 subagent 顺利接力
- 如何避免阶段文档膨胀
- 如何让 AI 稳定找到当前有效入口

## 关键结论

- 中型项目最核心的不是单一文档 skill，而是 `handoff + status + changelog` 的组合
- 文档爆炸是真实风险，尤其在多阶段、多 subagent、多轮会话场景下
- 持续治理的核心不是单纯多写文档，而是 `分层 -> 压缩 -> 归档 -> 保留活跃入口`
- 不应依赖 AI 自觉维护索引和模板，最好通过项目规则、事件钩子或验证脚本固化
- 当前项目在没有 Jira、Confluence、统一知识库和成熟检索系统的前提下，保留一个轻量 `index.md` 是合理做法

## 三类核心 Skill

### `session-handoff`

作用：

- 固化子任务或阶段结束时的真实状态
- 记录改了哪些文件、做了哪些决定、下一步从哪里继续

适用：

- subagent 任务完成后
- 阶段中断前
- 主 agent 向下一轮 AI 交接时

### `status-report`

作用：

- 把多个 handoff 压缩为阶段视图
- 记录完成度、风险、阻塞、下一阶段重点

适用：

- 每阶段结束
- 每个里程碑回顾

### `changelog-automation`

作用：

- 生成阶段或版本级变更说明
- 面向测试、产品、联调、归档

适用：

- 阶段收尾
- 发版前

## 目录与分层建议

建议目录：

```text
docs/
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

分层说明：

- `plan`：长期项目边界
- `handoff`：短期接力上下文
- `status`：阶段压缩结果
- `changelog`：对外变更说明
- `adr`：长期决策
- `archive`：退出活跃阶段的历史资料

## 为什么要有 `index.md`

`index.md` 的职责不是做全量目录树，而是给 AI 和人类提供一个稳定入口。

它至少应回答：

- 当前处于哪个阶段
- 当前先看哪几份文档
- 最新有效的 `handoff` / `status` / `changelog` 是什么
- 归档入口在哪里

## 风险判断

如果出现以下情况，说明治理开始失效：

- `index.md` 不再指向最新文档
- 活跃 `handoff` 增长但没有阶段 `status`
- 同一结论在多个文档中重复且相互冲突
- AI 每次都需要重新扫描大量历史文档才能开工

## 推荐组合

### 最小方案

- `session-handoff`

### 稳定方案

- `session-handoff`
- `status-report`

### 完整方案

- `session-handoff`
- `status-report`
- `changelog-automation`

## 实施原则

- 文档更新应成为完成条件的一部分，而不是顺手动作
- 技能负责“怎么做”，规则负责“何时必须做”
- 低层文档必须持续压缩到高层文档
- 历史文档必须退出活跃入口
