# AI 文档入口索引

更新时间：2026-05-02
当前状态：Stage-00 已补齐 hook sync、governance + smoke workflow、更深一层的 traceability alignment、runtime metadata 自动发现、WS-01/WS-02 黑盒 smoke、Karpathy-style 行为护栏 starter 化、跨平台 Python 解析优先级、archive candidate monitor、context surface 配置化、task discovery reading profiles、GitHub ownership/supply-chain 守门、完成型 handoff 语义归档、项目 skill 生命周期模板与 context budget audit
当前阶段：STAGE-00 真实场景验证与治理固化

## 入口说明

本文件是 `docs/ai/` 的稳定路由层，面向 AI 与人类执行者。

本索引只覆盖 repo 内共享真相。

`.codex/runtime/` 下的 session 与 observation 文件属于本地 runtime harness，不纳入这里的默认阅读顺序，也不作为项目主真相。

使用规则：

1. 开启新一轮工作时，先读本文件
2. 只保留稳定入口，不在这里重复展开完整阶段目录
3. 当前精确的 active status / handoff 绑定以 `working-context.md` 的同步元数据为准，阶段压缩结论以 `status` 为准

## 默认短链路

1. [项目规则 AGENTS.md](/Volumes/usd/codes/go_projects/ai_ms_pro/AGENTS.md)
2. [当前工作上下文](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)
3. [Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)

任务进入哪个更深入口，由 `AGENTS.md` 的 Task Discovery Protocol 判断。简单任务默认停在短链路；requirements、plan、handoff、ADR 与 archive 都是按需入口。

用户通常不需要手动标注任务类型。`按简单任务处理`、`按复杂任务处理`、`这是 0-1 阶段任务`、`不要读 archive`、`需要深挖历史` 只是可选覆盖指令，用来纠正或收窄 Agent 的默认判断。

## 按需深入入口

- [需求文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/index.md)：需求驱动、traceability 或 0-1 stage 任务再进入
- [项目计划](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/plan.md)：阶段目标、范围与验收框架需要确认时再进入
- [Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md)
- [当前活跃 handoff 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active)：resume、recovery 或相关 profile 需要时再进入
- [ADR 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr)：长期决策背景需要时再进入
- [Project Skill Lifecycle Template](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/templates/project-skill-lifecycle.md)：创建或调整 architecture/style/dependency skill 时再进入
- `scripts/check_context_budget.py`：默认上下文变重、stage compression 前或 skill/rule 膨胀排查时手动运行
- [OPEN-10 Context Budget 使用细节](/Volumes/usd/codes/go_projects/ai_ms_pro/--使用细节/context-budget-open-10.md)：忘记何时重跑 budget triage、是否压缩、是否接 hook 时再查看
- [阶段性提交 / PR CI 操作手册](/Volumes/usd/codes/go_projects/ai_ms_pro/--使用细节/stage-commit-pr-ci-manual.md)：业务小阶段完成、下班前保存进度、准备 push/PR/CI 时再查看
- [已归档 handoff 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/archive)：当前 truth surface 不足以回答历史原因时再进入
- [当前 Changelog 目录](./changelog)

当前 active handoff 默认预算由 `.codex/harness.toml` 的 `context_surface.active_handoff_budget` 控制，初始值为 `5`。达到预算时应优先压缩/归档，而不是继续扩展默认入口面。

## 当前阶段锚点

- 当前 stage status：[Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
- 当前 hardening backlog：[Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md)
- 当前 active handoff 精确集合：以 [当前工作上下文](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md) 的 `## 同步元数据` 为准
- 最新 ADR：[ADR-014 Context Budget Audit](./adr/ADR-014-context-budget-audit.md)
- 最新 changelog：[2026-05-02 Context Budget Audit](./changelog/2026-05-02-context-budget-audit.md)

## 归档入口

- [handoffs/archive](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/archive)
- [archive](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/archive)

## 维护规则

- 本文件只做稳定路由，不维护完整阶段目录或第二套“下一次会话先读”
- active handoff / ADR 的精确当前集合，优先维护在 `working-context` 同步元数据与对应目录中，而不是在这里重复展开
- 新增或归档 `handoff`、`status`、`changelog`、`adr` 后，更新这里的稳定入口与阶段锚点
- 当 stage `status` 已吸收某个完成型 handoff 且其不再有默认 resume 价值时，将其移入 `handoffs/archive`
- 本地 runtime harness 文件不应加入本索引
