# 当前工作上下文

更新时间：2026-06-15
当前阶段：STAGE-00
当前模式：Codex-first harness engineering

## 作用

本文档只保留当前开发阶段最需要被下一次会话立即继承的增量真相。

它不是长期归档，不替代 `plan`、`status`、`handoff`、`adr`。

## 同步元数据

- Current Stage: STAGE-00
- Active Status Source: 未绑定
- Active Handoff Sources: 未绑定
- Requirement IDs: 未绑定
- Workstream IDs: 未绑定
- Last Synced From: bootstrap
- Last Synced At: 2026-06-15

## 当前主目标

- 为 `New Project Standard` 建立最小可用的共享治理控制面。
- 导入首个真实需求并形成第一个 `workstream`。
- 让第一条垂直切片跑通 `requirements -> implementation -> runtime memory -> handoff/status`。

## 当前活跃队列

1. 初始化 `docs/ai/` 与 `docs/requirements/` 控制面。
2. 导入首个 `REQDOC / REQ / WS`。
3. 实现第一个可验证的垂直切片。
4. 跑通 runtime observation / session / reducer / handoff-status 链路。
5. 默认将共享恢复面保持在 `index -> working-context -> status -> configured active handoff budget`。

## 当前风险与阻塞

- 首个真实场景尚未导入，当前还不能证明 traceability 链路可用。
- 若把旧项目共享真相直接复制过来，会污染新项目控制面。
- 若未先初始化 `index / plan / working-context / traceability-matrix`，`Stop` hook 可能在首轮工作后直接给出治理失败。
- active handoff 默认预算由 `.codex/harness.toml` 控制；被 `status` 吸收后的完成型 handoff 应进入 `archive`，否则默认恢复面会再次膨胀。

## 下一次会话先读

1. [AI 文档入口索引](./index.md)
2. [当前工作上下文](./working-context.md)
3. [需求文档入口索引](../requirements/index.md)
4. [项目计划](./plan.md)
5. [Harness 可迁移清单](./harness-portability-guide.md)
6. [新项目 AGENTS 改写指南](./new-project-agents-rewrite-guide.md)

## 最近已固化的决策

- 项目采用 `Runtime Harness + Governance Harness + Verification Harness` 三层分工。
- `.codex/runtime/` 只保留本地恢复原料，不替代 `docs/ai/` 与 `docs/requirements/` 的共享治理真相。
- 默认共享恢复面保持轻量：`index -> working-context -> status -> configured active handoff budget`。
- `AGENTS.md` 保持轻量 trigger layer；projection、verification、GitHub guardrails 与 skill lifecycle 细则默认由 repo-local skills、references、templates 或 checks 按需承接。
- `scripts/check_change_triggered_followups.py` 是 warning-only follow-up triage，用 changed files 提示可能需要的专项检查和 skill/reference；starter workflow 可把包含 check level / CI coverage 的 markdown 摘要写入 PR / CI summary。
- `docs/ai/check-registry.md` 记录 checks 的等级；Scorecard / CodeQL / SBOM 默认只是单个顺序 `security-evidence` job 里的 artifact evidence，不是 required checks。
- `plan` 与 `workstream` 属于 projection surface，不应重复承载快速变化的当前状态。
- `.agents/skills/repo-governed-coding/` 是可选行为护栏，默认显式调用，不替代 `AGENTS.md`、共享治理文档或检查脚本。
- `.agents/skills/harness-maintenance/` 是可选 harness 维护能力，只在修改 runtime、hooks、reducers、compression、verification、GitHub guardrails 或 code-shape checks 时按需调用。
- `.agents/skills/requirements-traceability-maintenance/` 是可选 requirements 维护能力，只在 PRD 导入、`REQDOC / REQ / WS`、traceability matrix 或技术假设变化时按需调用。
- `.agents/skills/progressive-feature-development/` 与 `.agents/skills/prd-to-project-skills/` 是可选机制层 skills，默认只在非平凡功能或稳定 PRD 模式分类任务中按需调用。
- `.agents/skills/team-pr-conflict-control/` 是可选团队协作机制层 skill，只在多人 / 多 AI 并行开发、PR touch-set overlap、PR template、CODEOWNERS 或 merge queue readiness 时按需调用。
- `.github/pull_request_template.md`、CODEOWNERS、portable workflows、advisory follow-up summary、security evidence workflow 与 `scripts/check_pr_touch_conflicts.py` 是 starter 机制层；PR touch conflict 默认只阻断已确认 high-risk overlap，GitHub API `UNKNOWN` 在 burn-in 阶段保持可见但不阻断。
- `scripts/check_github_guardrails.py` 是薄 CLI；`scripts/github_guardrails/` 承接本地 workflow、remote GitHub、orphan gitlink 与 supply-chain evidence 结构检查。新项目仍必须在 GitHub 远端单独确认 branch protection、rulesets 和 merge queue。
- Python runtime 选择优先 repo-local `.codex/.venv`；首次 bootstrap 可读取父级 `.env` 的 allowlisted Python selector 或 pyenv 版本来创建 venv，但不复制 `.env`、不输出 secret、不替代项目配置管理。

## 更新规则

- 只保留当前阶段仍然有效的增量真相。
- 当 stage 切换、主目标变化或 `status/handoff` 完成压缩后优先更新本文档。
- 过期细节应进入 `status`、`adr` 或 `archive`，而不是继续堆在默认恢复面里。
