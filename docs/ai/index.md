# AI 文档入口索引

更新时间：2026-05-07
当前状态：Stage-00 harness 已可用；REQDOC-003 已登记为 workflow Candidate skills 的首个 accepted eval 样本；context budget 已补 80/90 高水位、ADR 到达预算与 stage status 压缩 warning；远端 main 保护仍受 GitHub plan / public repo 限制阻塞
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
- [Check Registry](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/check-registry.md)：评估某个 check 是否 advisory、review-required、blocking-candidate 或 blocking 时再进入
- [Supply Chain And Provenance Plan](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/security/supply-chain-provenance-plan.md)：修改 Scorecard、CodeQL、SBOM、SLSA 或 release provenance 时再进入
- `$progressive-feature-development`：非平凡功能、跨模块、API / storage / architecture、测试策略变化或显式 plan-first 任务再调用
- `$prd-to-project-skills`：PRD / requirements / workstream / ADR / 实现样本中出现稳定项目开发模式时再调用
- `$requirements-traceability-maintenance`：PRD 导入、`REQDOC / REQ / WS`、traceability-matrix 或技术假设状态变化时再调用
- `$harness-maintenance`：修改 bootstrap、hooks、runtime reducer、session compression、verification command reference、GitHub guardrails、supply-chain evidence 或 code-shape checks 时再调用
- `$team-pr-conflict-control`：多人或多 AI 并行开发、open PR changed-file overlap、PR template、CODEOWNERS 或 merge queue / `merge_group` readiness 任务再调用
- [PRD 长文到 Harness 与 Skill 使用细节](/Volumes/usd/codes/go_projects/ai_ms_pro/--使用细节/PRD长文到Harness与Skill使用细节.md)：导入万字 PRD、拆 REQ/WS、判断是否 skill 化时再查看
- [需求与 Skill 冲突处理细节](/Volumes/usd/codes/go_projects/ai_ms_pro/--使用细节/需求与Skill冲突处理细节.md)：PRD/REQ/WS 与既有 skill 建议冲突时再查看
- [Candidate Skill Usage Samples](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/skill-usage-samples.md)：评估 Candidate skill with/without eval 时再进入
- [Candidate Skill Eval Protocol](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/skill-evals/README.md)：记录详细对照实验材料时再进入
- `scripts/check_repo_skills.py`：确认 `.agents/skills` 是否 Codex discoverable、repo-local only 或 globally installed 时手动运行
- `scripts/check_requirements_shape.py`：导入 PRD / REQ / WS 后检查 traceability、技术假设状态和 verification method 时手动运行
- `scripts/check_skill_usage_samples.py`：检查 Candidate skill 对照实验样本数量时手动运行
- `scripts/check_change_triggered_followups.py`：根据 changed files 提示应补跑的专项检查和应打开的 skill/reference；CI / PR summary 使用 `--markdown` 输出，仍为 advisory
- `scripts/check_github_guardrails.py`：确认本地/远端 GitHub guardrails 状态时手动运行
- `scripts/check_pr_touch_conflicts.py`：PR 上比较当前 changed files 与同 base open PR，阻断高风险文件 overlap
- `scripts/check_context_budget.py`：默认上下文变重、stage compression 前或 skill/rule 膨胀排查时手动运行；会提示 80/90 高水位、ADR 到达预算和 stage status 行数压缩
- [上下文预算 OPEN-10 使用细节](/Volumes/usd/codes/go_projects/ai_ms_pro/--使用细节/上下文预算OPEN-10使用细节.md)：忘记何时重跑 budget triage、是否压缩、是否接 hook 时再查看
- [阶段提交与 PR-CI 操作手册](/Volumes/usd/codes/go_projects/ai_ms_pro/--使用细节/阶段提交与PR-CI操作手册.md)：业务小阶段完成、下班前保存进度、准备 push/PR/CI 时再查看
- [GitHub 私有仓库 Harness 与完整 CI 配置清单](/Volumes/usd/codes/go_projects/ai_ms_pro/--使用细节/GitHub私有仓库Harness与完整CI配置清单.md)：接手公司私有仓库、配置 branch protection / ruleset、required checks、CODEOWNERS、security evidence 与完整 CI 时再查看
- [已归档 handoff 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/archive)：当前 truth surface 不足以回答历史原因时再进入
- [当前 Changelog 目录](./changelog)

当前 active handoff 默认预算由 `.codex/harness.toml` 的 `context_surface.active_handoff_budget` 控制，初始值为 `5`。达到预算时应优先压缩/归档，而不是继续扩展默认入口面。

## 当前阶段锚点

- 当前 stage status：[Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
- 当前 hardening backlog：[Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md)
- 当前 active handoff 精确集合：以 [当前工作上下文](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md) 的 `## 同步元数据` 为准
- 最新 ADR：[ADR-015 Progressive Feature And PRD Skills](./adr/ADR-015-progressive-feature-and-prd-skills.md)
- 最新 changelog：[2026-05-07 Context Budget Growth Guardrails](./changelog/2026-05-07-context-budget-growth-guardrails.md)

## 归档入口

- [handoffs/archive](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/archive)
- [archive](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/archive)

## 维护规则

- 本文件只做稳定路由，不维护完整阶段目录或第二套“下一次会话先读”
- active handoff / ADR 的精确当前集合，优先维护在 `working-context` 同步元数据与对应目录中，而不是在这里重复展开
- 新增或归档 `handoff`、`status`、`changelog`、`adr` 后，更新这里的稳定入口与阶段锚点
- 当 stage `status` 已吸收某个完成型 handoff 且其不再有默认 resume 价值时，将其移入 `handoffs/archive`
- 本地 runtime harness 文件不应加入本索引
