# Stage-00 Runtime Harness Foundation Status

更新时间：2026-05-05
阶段：stage-00
状态：进行中

## 需求与工作流标识

- Requirement IDs：REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006
- Workstream IDs：WS-01, WS-02
- 当前阶段已通过 `WS-01` 与 `WS-02` 完成两个真实场景的 requirements traceability 与实现验证

## 当前阶段目标

- 建立最小可用的 runtime / governance / verification harness 协作链路
- 保持 repo-first 治理边界，并让 session、observation、reducer、traceability metadata 可恢复、可压缩、可验证
- 为后续真实需求导入、阶段化开发和新项目 starter 迁移保留稳定控制面

## 当前完成度

- 已完成：
  - Runtime / Governance：Stop observation/session、metadata 自动发现、reducer handoff-first、REQ/WS/STAGE 校验、projection boundary
  - Verification：repo-local Python runner、hook sync、code shape、governance、WS-01/WS-02 smoke、context budget、archive candidate、change-triggered followups、CI / PR summary、check registry、repo skill / requirements / skill eval / GitHub guardrails checks
  - Starter：bootstrap、离线 best-effort venv、仓外复演、pre-commit 复演、no-old-truth boundary、`.agents/skills` 机制层同步
      - Skills：`repo-governed-coding`、`harness-maintenance`、`requirements-traceability-maintenance`、`progressive-feature-development`、`prd-to-project-skills`、`team-pr-conflict-control` 均在 Codex repo-local 原生路径 `.agents/skills`，并使用 `policy.allow_implicit_invocation: false`
  - Evidence：Candidate skill promotion 从样本登记升级为 with/without eval；PRD 导入检查现在要求技术假设状态和 verification method
  - GitHub：workflow 最小权限/concurrency/timeout、CODEOWNERS、PR template、Dependabot、dependency review、Windows hook runtime job、PR touch conflict checker、change-triggered advisory summary、security evidence workflow、`merge_group` 触发、required-check 策略和可运行远端 guardrails check；`check_github_guardrails.py` 已拆成 helper 模块并新增 orphan gitlink 检查；PR touch conflict 在 burn-in 阶段只阻断已确认 high-risk overlap
- 进行中：
  - OPEN-01：远端 CI burn-in、GitHub branch protection / ruleset required checks 确认
  - OPEN-07 / OPEN-08 / OPEN-09：starter 样板、行为 skill 默认化、project skill lifecycle 与 workflow skill 真实样本观察
  - P2：继续压缩完成型 Stage-00 历史；本轮已把完成型 skill/evidence handoff 移入 archive，active handoff 从 4 降到 2

## 本阶段关键成果

- 两个真实 workstream 已证明当前 harness 能跑通 `requirements -> implementation -> smoke -> runtime promotion -> status`。
- 默认恢复面已收缩为 `index -> working-context -> stage status -> configured active handoff budget`，archive 只在 recovery/dispute 或当前 truth surface 不足时进入。
- `new_pro_standard` 已同步机制层，包括 Python 解析、hook sync、code shape、context surface、Task Discovery、project skill lifecycle、`.agents/skills` 与 context budget audit；当前 repo 的历史 truth 不复制进 starter。
- `plan/workstream` 已明确为 projection surface，当前状态真相默认回收到 `working-context`、active `handoff`、stage `status` 和 `traceability-matrix`。
- `REQ <-> WS <-> STAGE` 至少已有一层自动校验：`working-context` 当前 stage 与 matrix 不一致会阻断，runtime artifact 先 warning-only。
- repo-local skills、requirements shape、Candidate skill eval samples、GitHub guardrails 与 changed-file follow-up triage 已有独立 warning-only checks；PR / main push 会展示 advisory summary 和 check level / CI coverage，避免继续膨胀 governance checker 或 `AGENTS.md`。

## 风险与阻塞

- CI workflow 已落地并进入 PR #1 burn-in；远端失败已暴露并修复 PR merge diff、Windows Python resolution test、dependency review unsupported、security evidence checkout orphan gitlink、PR touch conflict unknown fail-closed 五类问题，PR branch push 也已收敛为只触发 PR checks，避免重复 push/pull_request CI。
- dependency review 当前在 workflow 中保持 advisory，因为 GitHub 远端报告仓库尚未启用 dependency graph / Advanced Security；Scorecard / CodeQL / SBOM 也先作为单个顺序 `security-evidence` job 产出 artifacts，不进入 required checks。CodeQL 在 private repo 未启用 code scanning 前只生成 SARIF artifact，不上传到 Code Scanning。branch protection / ruleset 与 security analysis 仍需通过 `scripts/check_github_guardrails.py` 和人工配置确认。2026-05-05 已尝试读取 main branch protection / rulesets，但 GitHub 返回 HTTP 403，需要 GitHub Pro 或 public repo。
- reducer 与 runtime artifact 的 stage drift 目前仍 warning-only，是否升级阻断要看后续样本。
- active surface budget、archive candidate monitor、context budget audit 都保持 warning-only；真正压缩/归档仍由主 Agent 语义确认。
- `.agents/skills`、project skill lifecycle 和 context budget audit 不替代 `AGENTS.md`、ADR、requirements 或 verification scripts；`harness-maintenance` 只下沉 runtime / hook / compression / verification / GitHub / code-shape 细则，`requirements-traceability-maintenance` 只下沉 PRD/REQ/WS/技术假设维护方法。
- `scripts/check_change_triggered_followups.py` 只提示 changed files 对应的可能漏跑检查、等级、CI 覆盖状态和应读 reference；CI summary 只提高可见性，不证明命令已执行，也不升级为 blocking policy。
- `$team-pr-conflict-control` 只下沉多人 / 多 AI PR touch-set 冲突控制方法；repo 内已新增 `scripts/check_pr_touch_conflicts.py`、PR template 和 `merge_group` workflow 触发，但远端 merge queue / branch protection 仍未被证明启用。
- `$progressive-feature-development` 与 `$prd-to-project-skills` 仍为 0/2 accepted with/without eval samples；样本不足是当前事实，不应升级为 always-on。
- `security-evidence.yml` 已能被 GitHub API 识别；Scorecard 首轮失败根因是仓库误跟踪 `output/harness_rehearsal_20260419_100339` 为无 `.gitmodules` 映射的 gitlink，不是 Scorecard 规则失败。
- Starter copied placeholder docs 仍需 `--force` 才会立刻替换成新项目名，`AGENTS.md` 仍需人工项目化。

## 下一阶段重点

- 推动 OPEN-01：远端 workflow green history、required checks、CODEOWNERS review、conversation resolved 与禁止直推 `main` 的远端确认。
- 在下一次 stage compression 时继续审查 archive candidate monitor 输出，确认候选已被 status、backlog 或 ADR 吸收。
- 在后续真实项目中观察 `$repo-governed-coding`、`$progressive-feature-development`、`$prd-to-project-skills`、project skill lifecycle 和 context budget audit 是否需要从显式/手动能力升级。
- 对真实 PRD 导入和非平凡功能任务运行 evidence checks，并把 with/without eval 登记到 `docs/ai/skill-usage-samples.md`。
- 在后续多人协作 PR 中验证 `$team-pr-conflict-control` 与 `scripts/check_pr_touch_conflicts.py` 是否足以降低 touch-set 冲突；若样本证明有效，再考虑进一步收紧 merge queue enforcement。
- 继续压缩完成型 Stage-00 历史，判断 `WS-01` / `WS-02` 是保留为验证样板，还是压缩为更轻的 starter 说明。

## 验收判断

- Stage-00 的 runtime harness foundation 已在两个真实 workstream 上验证可用。
- 当前尚未完全进入下一阶段，因为 CI burn-in、GitHub branch protection / ruleset required checks 和 Windows 真实复演仍需确认。
- 剩余问题主要是远端守门与长期样本观察，不是本地 harness 能否使用。

## 关联文档

- [项目计划](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/plan.md)
- [Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md)
- [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
- [当前工作上下文](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)
- [当前活跃 handoff 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active)
- [已归档 handoff 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/archive)
- [ADR 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr)
- [ADR-010 Context Surface Layering](../adr/ADR-010-context-surface-layering.md)
- [ADR-011 Task Discovery Reading Profiles](../adr/ADR-011-task-discovery-reading-profiles.md)
- [ADR-012 GitHub Harness Gatekeeping](../adr/ADR-012-github-harness-gatekeeping.md)
- [ADR-013 Project Skill Lifecycle](../adr/ADR-013-project-skill-lifecycle.md)
- [ADR-014 Context Budget Audit](../adr/ADR-014-context-budget-audit.md)
- [ADR-015 Progressive Feature And PRD Skills](../adr/ADR-015-progressive-feature-and-prd-skills.md)
- [2026-05-02 Context Budget Audit](../changelog/2026-05-02-context-budget-audit.md)
- [2026-05-04 Progressive Feature And PRD Skills](../changelog/2026-05-04-progressive-feature-and-prd-skills.md)
- [2026-05-04 Harness Evidence Checks](../changelog/2026-05-04-harness-evidence-checks.md)
- [2026-05-04 Harness Maintenance Skill Downshift](../changelog/2026-05-04-harness-maintenance-skill-downshift.md)
- [2026-05-04 Traceability And Governance Skill Downshift](../changelog/2026-05-04-traceability-and-governance-skill-downshift.md)
- [2026-05-05 PR Branch Guardrails](../changelog/2026-05-05-pr-branch-guardrails.md)
- [2026-05-05 Change Triggered Followups](../changelog/2026-05-05-change-triggered-followups.md)
- [2026-05-05 Advisory Followups CI Summary](../changelog/2026-05-05-advisory-followups-ci-summary.md)
- [2026-05-05 Harness Maturity Security Evidence](../changelog/2026-05-05-harness-maturity-security-evidence.md)
- [Candidate Skill Usage Samples](../skill-usage-samples.md)
- [OPEN-10 使用细节](../../../--使用细节/上下文预算OPEN-10使用细节.md)
