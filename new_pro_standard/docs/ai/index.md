# AI 文档入口索引

更新时间：YYYY-MM-DD
当前状态：待导入首个真实场景
当前阶段：STAGE-00

## 入口说明

本文档是 `docs/ai/` 的稳定路由层，面向 AI 与人类执行者。

这里只保留共享治理控制面的默认入口，不在这里重复展开完整阶段目录。

`.codex/runtime/` 下的 session 与 observation 文件属于本地 runtime harness，不纳入默认共享阅读面，也不作为项目共享真相。

## 默认短链路

1. [项目规则 AGENTS.md](../../AGENTS.md)
2. [当前工作上下文](./working-context.md)

任务进入哪个更深入口，由 `AGENTS.md` 的 Task Discovery Protocol 判断。简单任务默认停在短链路；requirements、plan、handoff、ADR 与 archive 都是按需入口。

用户通常不需要手动标注任务类型。`按简单任务处理`、`按复杂任务处理`、`这是 0-1 阶段任务`、`不要读 archive`、`需要深挖历史` 只是可选覆盖指令，用来纠正或收窄 Agent 的默认判断。

## 按需深入入口

- [需求文档入口索引](../requirements/index.md)：需求驱动、traceability 或 0-1 stage 任务再进入
- [项目计划](./plan.md)：阶段目标、范围与验收框架需要确认时再进入
- [Harness 可迁移清单](./harness-portability-guide.md)
- [Check Registry](./check-registry.md)：评估某个 check 是否 advisory、review-required、blocking-candidate 或 blocking 时再进入
- [Harness Real Sample Watchlist](./harness-real-sample-watchlist.md)：记录只能等真实事件发生后再采集的样本缺口；不要把 starter 模板计数当成项目事实
- [Harness Sample Gap Evidence Template](./templates/harness-sample-gap-evidence-record.md)：真实样本 candidate JSONL 形状；模板不是 accepted evidence
- [Supply Chain And Provenance Plan](./security/supply-chain-provenance-plan.md)：修改 Scorecard、CodeQL、SBOM、SLSA 或 release provenance 时再进入
- [Candidate Skill Usage Samples](./skill-usage-samples.md)：记录真实 with/without eval 样本时再进入
- [新项目 AGENTS 改写指南](./new-project-agents-rewrite-guide.md)
- [传统项目接入 Harness 的标准起手式](./traditional-project-harness-kickoff.md)
- [Project Skill Lifecycle Template](./templates/project-skill-lifecycle.md)：创建或调整 architecture/style/dependency skill 时再进入
- [Candidate Skill Eval Protocol](./skill-evals/README.md)：评估 Candidate skill with/without 样本时再进入
- `$progressive-feature-development`：非平凡功能、跨模块、API / storage / architecture、测试策略变化或显式 plan-first 任务再调用
- `$prd-to-project-skills`：PRD / requirements / workstream / ADR / 实现样本中出现稳定项目开发模式时再调用
- `$requirements-traceability-maintenance`：PRD 导入、`REQDOC / REQ / WS`、traceability-matrix 或技术假设状态变化时再调用
- `$harness-maintenance`：修改 bootstrap、hooks、runtime reducer、session compression、verification command reference、GitHub guardrails、supply-chain evidence 或 code-shape checks 时再调用
- `$team-pr-conflict-control`：多人或多 AI 并行开发、open PR changed-file overlap、PR template、CODEOWNERS 或 merge queue / `merge_group` readiness 任务再调用
- `scripts/check_repo_skills.py`：确认 `.agents/skills` 是否 Codex discoverable、repo-local only 或 globally installed 时手动运行
- `scripts/check_requirements_shape.py`：导入 PRD / REQ / WS 后检查 traceability、技术假设状态和 verification method 时手动运行
- `scripts/extract_requirement_source.py`：大型或 instruction-like raw PRD/source 先进入 `docs/requirements/source-raw/quarantine/`，并生成 bounded sanitized excerpt / REQDOC draft
- `scripts/check_skill_catalog.py`：第三方 `.codex/skills`、catalog/lock、vendor/proxy metadata 或 skill/tool output scan policy 变化时手动运行；`--check-output <file>` 可扫描 bounded 输出
- `scripts/check_skill_usage_samples.py`：检查 Candidate skill 对照实验样本数量时手动运行
- `scripts/collect_harness_sample_gaps.py`：列出 starter-safe generic `GAP-*` 真实样本观察目录；新项目可沿用或替换为项目 gap id
- `scripts/plan_harness_sample_collection.py`：从观察目录生成采集计划或 pending candidate 模板；不写 ledger、不接受 evidence
- `scripts/check_harness_sample_gap_evidence.py`：校验空账本或 candidate JSONL；拒绝 synthetic accepted evidence、raw runtime、旧项目 ledger 迁移
- `scripts/check_change_triggered_followups.py`：根据 changed files 提示应补跑的专项检查和应打开的 skill/reference；CI / PR summary 可使用 `--markdown` 输出 check level / CI coverage，仍为 advisory
- `scripts/check_agent_eval_dataset.py`：校验 `docs/ai/evals/agent-harness-evals.jsonl` 的 starter-safe eval 数据集
- `scripts/run_agent_eval_dataset.py --dry-run`：列出 eval case 的本地检查，不调用模型 API 或外部服务
- `scripts/check_agent_trace_schema.py` / `scripts/export_agent_trace.py` / `scripts/check_tool_contracts.py`：维护本地 trace schema、adapter sample 和 tool-contract registry 时运行
- `scripts/check_mock_data_boundary.py` / `scripts/check_data_activation.py`：维护 mock/fixture 边界或切换 `smoke | shadow-real | real` 数据激活模式时运行
- `scripts/check_reuse_retirement.py`：新增大文件、平行 checker/helper/adapter 或旧 mock/smoke/legacy 路径可能退场时运行；默认只给 review-required 候选，不自动删除代码
- `scripts/check_github_guardrails.py`：确认本地/远端 GitHub guardrails 状态时手动运行
- `scripts/check_branch_hygiene.py --strict`：控制 active PR 数量预算、failed open PR 和 stale branch，CI / PR summary 也会运行
- `scripts/check_pr_touch_conflicts.py`：PR 上比较当前 changed files 与同 base open PR，阻断高风险文件 overlap
- `scripts/check_context_budget.py`：默认上下文变重、stage compression 前或 skill/rule/source 膨胀排查时手动运行；会提示 80/90 高水位、ADR 到达预算、stage status 行数、skill catalog、raw source 和 static task packet 预算
- [handoffs/active](./handoffs/active)
- [status](./status)
- [changelog](./changelog)
- [adr](./adr)
- 默认 active handoff 预算由 `.codex/harness.toml` 的 `context_surface.active_handoff_budget` 控制，初始值为 `5`。达到预算时优先压缩到 `status` 或归档，而不是继续扩张默认恢复面。

## 当前阶段占位

- 暂无阶段 `status`
- 暂无活跃 `handoff`
- 暂无阶段 `changelog`
- 暂无正式 `adr`

## 活跃目录

- [handoffs/active](./handoffs/active)
- [status](./status)
- [changelog](./changelog)
- [adr](./adr)

## 归档入口

- [handoffs/archive](./handoffs/archive)
- [archive](./archive)

## 维护规则

- 本文件只做稳定路由，不维护第二套“当前阶段总表”或“下一次会话先读”的完整展开版。
- 新增或归档 `handoff`、`status`、`changelog`、`adr` 后，更新这里的稳定入口与占位状态。
- 当某个完成型 `handoff` 已被 `status` 或 `adr` 吸收且不再有默认恢复价值时，将其移入 `handoffs/archive`。
- 本地 runtime harness 文件不应加入本索引。
