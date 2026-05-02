# Project Skill Lifecycle

更新时间：2026-05-02
编号：ADR-013
标题：项目架构、样式与依赖 skill 生命周期
状态：已采纳

## 背景

- Task Discovery 与 context surface 配置已经让默认恢复链路保持较小，但项目架构、样式和依赖约束仍可能在 0-1 阶段快速变化。
- 如果把这些约束全部放进 `AGENTS.md`，简单任务会继续背负厚上下文；如果只散落在 status、handoff 或 ADR 中，后续任务又需要反复翻找。
- Skill 可以作为按需加载的项目执行指南，但不能替代仓库治理文档、requirements 或 verification scripts。
- Runtime session `019ddc1d-c60a-76f0-8cb3-17637251c3fb` 中关于 context surface、Task Discovery 和 archive candidate 的结论已被 ADR-010、ADR-011、stage status 与 changelog 吸收；本 ADR 补齐其中尚未固化的项目 skill 生命周期决策，因此不另建 active handoff。

## 决策

- 新增 `docs/ai/templates/project-skill-lifecycle.md`，作为 architecture / style / dependency skill 的按需生命周期模板。
- 生命周期采用 `Draft -> Candidate Skill -> Stable Skill -> Promote -> Deprecate`。
- 项目专属 skill 只在相关任务中按需加载，不进入默认短链路。
- Skill 必须提供 escape hatch：当新需求、性能证据、依赖生态或架构方向与当前 skill 冲突时，允许偏离，但长期变化必须提升到 ADR、status、handoff 或 requirements。
- 第一版不新增 blocking checker；通过现有 governance check 验证文档路由与 ADR/status 同步。若后续出现 skill 滥用或冲突，再考虑 warning-only 检查。
- `new_pro_standard` 同步该模板作为机制层，不复制当前 repo 的项目 truth。

## 备选方案

- 方案 A：把项目架构、样式和依赖规则直接写入 `AGENTS.md`。
- 方案 B：不引入 skill 生命周期，只依赖 status、handoff 和 ADR。
- 方案 C：新增 blocking checker，强制所有项目 skill 带生命周期字段。

## 决策理由

- `AGENTS.md` 适合稳定 always-on 规则，不适合承载早期会变化的项目细节。
- 纯文档层能保存共享真相，但不能降低每次任务的执行上下文成本。
- Skill 生命周期模板可以让项目规则先轻量试用，再按证据升级为 skill、ADR、AGENTS 或 check。
- Blocking checker 目前收益不足；项目 skill 使用样本还不够多，先保持模板与 ADR 约束更稳妥。

## 影响

- 简单任务仍默认停留在短链路，不读取 project skill lifecycle 模板。
- 0-1 阶段、架构/样式/依赖变更、创建或调整项目 skill 时，应按需读取生命周期模板。
- 项目 skill 的结论必须回写共享治理层；skill 只负责执行指导，不拥有 canonical truth。
- Starter 获得可迁移模板，但新项目仍需根据自身架构和业务事实决定是否创建具体 skill。

## 关联文档

- [Project Skill Lifecycle Template](../templates/project-skill-lifecycle.md)
- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Stage-00 Runtime Harness Foundation Status](../status/stage-00-runtime-harness-foundation.md)
- [Harness Remaining Work](../harness-open-items.md)
- [ADR-010 Context Surface Layering](./ADR-010-context-surface-layering.md)
- [ADR-011 Task Discovery Reading Profiles](./ADR-011-task-discovery-reading-profiles.md)
