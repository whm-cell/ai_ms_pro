# 当前工作上下文

更新时间：2026-05-05
当前阶段：STAGE-00 真实场景验证与治理固化
当前模式：Codex-first harness engineering

## 作用

本文件只保留当前开发阶段最需要被下一次会话立即继承的真相。

它不是长期归档，不替代 `plan`、`status`、`handoff`、`adr`。

## 同步元数据

- Current Stage: STAGE-00
- Active Status Source: docs/ai/status/stage-00-runtime-harness-foundation.md
- Active Handoff Sources:
  - docs/ai/handoffs/active/stage-00-runtime-stop-session.md
  - docs/ai/handoffs/active/stage-00-observation-reducer.md
- Requirement IDs: REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006
- Workstream IDs: WS-01, WS-02
- Last Synced From: status,manual,handoff
- Last Synced At: 2026-05-05

## 当前主目标

- 维持短默认上下文：`index -> working-context -> current status`；requirements、handoff、ADR、archive 与 skills 都按需进入。
- `AGENTS.md` 已压缩为 always-on 触发与边界层；projection、verification、GitHub、skill lifecycle 细则继续由 skills、references、templates 和 checks 承接。
- 收敛 Stage-00 剩余 hardening：repo 内 PR 守门已补 PR template、touch conflict checker 与 `merge_group` workflow 触发；远端 GitHub branch protection / ruleset 仍需套餐或仓库可见性支持。
- 保持 `new_pro_standard` 只承载机制层；当前 repo 的 REQ/WS、状态、PR、CI 历史和样本 truth 不复制。
- 已将 skills 迁到 Codex repo-local 原生路径 `.agents/skills`；`harness-maintenance` 下沉 runtime / hook / compression / verification / GitHub / code-shape 细则，`requirements-traceability-maintenance` 下沉 PRD/REQ/WS/技术假设维护流程，`team-pr-conflict-control` 下沉多人 / 多 AI PR touch-set 冲突控制，Candidate workflow skills 继续显式触发。
- 使用 warning-only evidence / follow-up checks：`check_repo_skills.py`、`check_requirements_shape.py`、`check_skill_usage_samples.py`、`check_github_guardrails.py`、`check_change_triggered_followups.py`；其中 change-triggered follow-up 已可在 CI / PR summary 展示，Scorecard / CodeQL / SBOM 先作为 security evidence 运行，GitHub guardrails 已拆成 helper 模块并检查 orphan gitlink。

## 当前活跃队列

1. 继续推进 OPEN-01：远端 workflow green history、required checks、branch protection / ruleset 与 security analysis 确认；`security-evidence.yml` 已被远端识别，首轮 checkout orphan gitlink 问题已定位并修复。
2. 用 `scripts/check_github_guardrails.py` 辅助区分本地已具备、远端 OK、远端 UNKNOWN，不再只靠人工记忆。
3. 后续 PR 通过 `.github/pull_request_template.md` 显式填写 `REQ/WS`、touch-set、overlap、verification 和 governance impact。
4. 后续真实 PRD / 非平凡功能任务要登记 with/without eval；`prd-to-project-skills` 与 `progressive-feature-development` 仍是 0/2。
5. 后续真实多人 / 多 AI PR 要用 `$team-pr-conflict-control` 记录 touch-set overlap 和 coordination action，先观察是否值得升级更多阻断策略。
6. 下一次 stage compression 继续清理完成型 handoff，避免 Stage-00 历史进入长期默认面。

## 当前风险与阻塞

- 远端 GitHub main 保护仍是 UNKNOWN；`gh api` 读取 branch protection / rulesets 返回 HTTP 403，需要 GitHub Pro、Team/Enterprise 对应能力或将仓库公开后才能证明该远端强制力。
- Candidate skill eval 仍无 accepted 样本；不得为了升级 always-on 伪造样本或把简单任务拖入完整流程。
- PRD 技术假设检查是启发式；`requirements-traceability-maintenance` 能提示缺状态/验证方法，但不能替代人工架构判断或 ADR。
- runtime stage drift、archive candidate、context budget 都保持 warning-only；是否升级阻断要等更多真实样本。
- starter 仍需新项目人工改写 `AGENTS.md` 和初始 REQ/WS；bootstrap 只初始化机制，不决定业务 truth。
- macOS/POSIX 与 Windows Python 解析已修复，但全新宿主仍需 bootstrap / hook sync 复验。

## 下一次会话先读

1. [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
2. [Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
3. [Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md)
4. [当前活跃 handoff 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active)：只有 resume/recovery 或相关 profile 需要时再进入

## 最近已固化的决策

- 三层 harness 分工不变：runtime 是本地恢复原料，governance docs 是共享真相，verification scripts/hooks 做漂移检测。
- `plan/workstream` 是 projection surface；当前状态真相默认集中在 `working-context`、active `handoff`、stage `status` 和 `traceability-matrix`。
- 默认上下文由 Task Discovery profile 扩面；长期决策见 ADR-010、ADR-011、ADR-014。
- `.agents/skills/*` 是 repo-local native skill 层；`AGENTS.md` 只保留轻触发和不可下沉真相边界，requirements traceability skill 与 Candidate skills 都不替代 requirements / status / ADR。
- 本轮 `AGENTS.md` 默认面压缩不改变能力边界；可下沉细节仍可追溯到 `$repo-governed-coding`、`$harness-maintenance`、`$team-pr-conflict-control`、requirements traceability skill、project-skill-lifecycle template 或检查脚本。
- `scripts/check_change_triggered_followups.py` 用 changed files 提示可能遗漏的专项检查和 skill/reference，降低按需 skill 漏触发概率；当前 workflow 会把 PR / main push 的 markdown 摘要写入 GitHub Actions Summary，并显示 check level / CI coverage，但仍不证明命令已经执行。
- `scripts/check_github_guardrails.py` 现在是薄 CLI 入口，核心逻辑拆到 `scripts/github_guardrails/` 并同步 starter；它能检查 security evidence workflow、远端 workflow 可见性、branch protection / rulesets UNKNOWN 和 orphan gitlink。
- `docs/ai/check-registry.md` 记录 checks 的 `advisory / review-required / blocking-candidate / blocking` 等级；Scorecard / CodeQL / SBOM 暂为 advisory evidence，不进入 required checks。
- Stage status 已同步记录 change-triggered follow-up checker；该 checker 继续保持 warning-only，不替代主 Agent 的语义判断。
- Candidate skill 升级必须有 with/without eval；当前两个 workflow skills 均为 0/2 accepted samples。
- `new_pro_standard` 同步机制层，不复制当前 repo 的历史 truth。
- GitHub ownership、supply-chain 与 required-check 策略已固化在 ADR-012；branch protection / ruleset 完成前 OPEN-01 仍保持开放。
- 多人 / 多 AI 开发的 PR touch-set 冲突控制已进入 `.agents/skills/team-pr-conflict-control/`；repo 内已有 `scripts/check_pr_touch_conflicts.py` 和 PR workflow gate，当前只阻断已确认 high-risk overlap，GitHub API `UNKNOWN` 在 burn-in 阶段保持可见但不阻断。

## 更新规则

- 只保留当前阶段仍然有效的信息
- 当阶段切换或主目标变化时优先更新本文件
- 过期信息应进入 `status`、`adr` 或归档，而不是继续堆在本文件里
