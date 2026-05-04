# Progressive Feature And PRD Skills

更新时间：2026-05-04
编号：ADR-015
标题：渐进式功能发现与 PRD-to-Skill 按需工作流
状态：已采纳

## 背景

- 直接把“分析框架 -> 选择 skills -> 技术方案 -> 代码生成 -> 代码优化”写成默认流程，会让简单任务背负流程税。
- PRD、normalized requirements 和 workstream 中确实会出现可复用的项目开发模式，但把 PRD 当前状态直接写进 skill 会制造隐藏且易过期的 truth。
- 当前 harness 已经有 `docs/requirements`、`docs/ai`、runtime 和 verification 分层；新流程必须复用这些层，而不是复制 ECC 的 `.claude/PRPs`、commands 或 hooks。
- ADR-013 已采纳项目 skill 生命周期，但还缺少“功能开发前的渐进式发现”和“PRD 内容何时 skill 化”的具体按需入口。

## 决策

- 新增 `.agents/skills/progressive-feature-development/`，作为非平凡功能开发的按需技术方案 gate。
- 新增 `.agents/skills/prd-to-project-skills/`，用于把 PRD / requirement / workstream / ADR / 实现样本中的稳定方法提炼为候选项目 skill。
- `AGENTS.md` 只记录触发规则和治理边界，不展开完整开发流水线。
- 两个 skill 默认显式调用，不进入简单任务默认短链路，不新增 blocking checker。
- 将两个 skill 同步进 `new_pro_standard` 作为机制层，不复制当前 repo 的 REQ/WS、状态、CI、PR 或历史结论。
- 两个 skill 的结果必须回写 requirements、handoff、status、ADR、changelog、checks 或 candidate skill；skill 不拥有 canonical truth。

## 备选方案

- 方案 A：把完整方案先行流程直接写进 `AGENTS.md`。
- 方案 B：整包复制 ECC 的 PRP commands、hooks 和 `.claude/PRPs` 目录。
- 方案 C：只依靠 `repo-governed-coding`，不新增 feature / PRD skill。

## 决策理由

- 方案 A 会扩大默认上下文，并让简单任务付出不必要的流程成本。
- 方案 B 会形成第二套控制面，和当前 `docs/requirements` / `docs/ai` / verification harness 重叠。
- 方案 C 能约束实现阶段，但不能解决“技术方案先行”和“PRD 稳定模式 skill 化”的发现问题。
- 两个独立 skill 可以保持职责清晰：一个服务功能开发前的渐进式发现，一个服务 PRD-to-skill 的知识分类。

## 影响

- 非平凡功能、跨模块、API / storage / architecture、测试策略变更或显式 plan-first 请求，应按需调用 `$progressive-feature-development`。
- PRD、requirements、workstream、ADR 或重复实现样本中出现稳定开发模式时，应按需调用 `$prd-to-project-skills`。
- 简单任务继续使用默认短链路，不强制加载两个新 skill。
- Starter 获得同样机制，但新项目仍需根据自身事实决定是否保留、修改、提升或废弃这些 skill。

## 关联文档

- [Progressive Feature Development Skill](../../../.agents/skills/progressive-feature-development/SKILL.md)
- [PRD To Project Skills](../../../.agents/skills/prd-to-project-skills/SKILL.md)
- [Project Skill Lifecycle Template](../templates/project-skill-lifecycle.md)
- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [Harness Remaining Work](../harness-open-items.md)
