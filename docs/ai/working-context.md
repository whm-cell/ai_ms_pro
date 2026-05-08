# 当前工作上下文

更新时间：2026-05-08
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
- Requirement IDs: REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006, REQ-007, REQ-008, REQ-009
- Workstream IDs: WS-01, WS-02, WS-03
- Last Synced From: status,manual,handoff
- Last Synced At: 2026-05-08

## 当前主目标

- 维持短默认上下文：`index -> working-context -> current status`；requirements、handoff、ADR、archive 与 skills 都按需进入。
- 本轮 stage status 已吸收上下文压缩、WS-03 combo/rank 薄切片、SAMPLE-002 和远端门禁证据化结论。
- `AGENTS.md` 已压缩为 always-on 触发与边界层；projection、verification、GitHub、skill lifecycle 细则继续由 skills、references、templates 和 checks 承接。
- REQDOC-003 已完成首轮标准化，绑定 REQ-007 / REQ-008 / REQ-009 与 WS-03；`apps/godot-platformer-slice/` 已完成首轮玩法闭环和第二轮 combo/rank 薄切片，完整 Godot 工程仍是 proposed / 待确认。
- 收敛 Stage-00 剩余 hardening：repo 内 PR 守门已补 PR template、touch conflict checker、branch hygiene strict PR 预算与 `merge_group` workflow 触发；远端 GitHub branch protection 当前返回 404，branch rulesets 为空，仍未证明强制门禁。
- 保持 `new_pro_standard` 只承载机制层；当前 repo 的 REQ/WS、状态、PR、CI 历史和样本 truth 不复制。
- 已将 skills 迁到 Codex repo-local 原生路径 `.agents/skills`；`harness-maintenance` 下沉 runtime / hook / compression / verification / GitHub / code-shape 细则，`requirements-traceability-maintenance` 下沉 PRD/REQ/WS/技术假设维护流程，`team-pr-conflict-control` 下沉多人 / 多 AI PR touch-set 冲突控制，Candidate workflow skills 继续显式触发。
- 使用 warning-only evidence / follow-up checks：`check_repo_skills.py`、`check_requirements_shape.py`、`check_skill_usage_samples.py`、`check_github_guardrails.py`、`check_change_triggered_followups.py`；`check_branch_hygiene.py --strict` 已升级为 active PR / stale branch 阻断面；其中 change-triggered follow-up 已可在 CI / PR summary 展示，Scorecard / CodeQL / SBOM 先作为 security evidence 运行，GitHub guardrails 已拆成 helper 模块并检查 orphan gitlink。

## 当前活跃队列

1. 继续推进 OPEN-01：远端 workflow green history、required checks、branch protection / ruleset 与 security analysis 确认；当前 branch protection 404、rulesets 为空，`security-evidence.yml` 已被远端识别。
2. 用 `scripts/check_github_guardrails.py` 辅助区分本地已具备、远端 OK、远端 UNKNOWN，不再只靠人工记忆。
3. 用 `scripts/check_branch_hygiene.py --strict` 控制 active PR 数量预算：total 10、Codex 3、Dependabot 4、failed open 0；PR CI 传入 `--current-pr`，避免把当前 PR 自身正在运行或刚失败的 checks 作为“其他失败 open PR”自阻断；open PR 分支通过 merge/close 处理，不直接删除。
4. 后续 PR 通过 `.github/pull_request_template.md` 显式填写 `REQ/WS`、touch-set、overlap、verification 和 governance impact。
5. REQDOC-003 后续若继续推进，应先决定是否新建真实 Godot engine spike；不要把完整游戏工程直接塞进 root repo 默认面。
6. `prd-to-project-skills` 与 `progressive-feature-development` 已有 SAMPLE-001 / SAMPLE-002 两个 accepted eval；下一步是单独评估是否保持 Candidate、升级 stable，或继续观察简单任务流程税。
7. 后续真实多人 / 多 AI PR 要用 `$team-pr-conflict-control` 记录 touch-set overlap 和 coordination action，先观察是否值得升级更多阻断策略。
8. 下一次 stage compression 继续清理完成型 handoff，避免 Stage-00 历史进入长期默认面。

## 当前风险与阻塞

- 远端 GitHub main 保护仍未生效：`check_github_guardrails.py` 当前显示 branch protection 404、branch rulesets 为空；required checks、review、conversation resolved 和禁止直推 `main` 不能声明已强制。
- Candidate workflow skills 已达到 2/2 accepted eval 前置证据；不得自动升级 always-on，仍需评估简单任务流程税和后续样本。
- PRD 技术假设检查是启发式；`requirements-traceability-maintenance` 能提示缺状态/验证方法，但不能替代人工架构判断或 ADR。
- REQDOC-003 的 Godot 4.6.2、GUT、导出 preset、素材/本地化管线仍未被 ADR 或真实 Godot spike 采纳。
- runtime stage drift、archive candidate 仍保持 warning-only；是否升级阻断要等更多真实样本。
- context budget 已收紧为 80/90 高水位、ADR 到达预算、stage status 行数 warning；本轮已执行 stage compression，并开始把旧 ADR 移入 archive。
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
- 默认上下文由 Task Discovery profile 扩面；长期规则见 ADR-010、ADR-011、ADR-014、ADR-015。
- `.agents/skills/*` 是按需 native skill 层，不替代 requirements、status、ADR、checks 或 `AGENTS.md`。
- Change-triggered follow-up、GitHub guardrails、requirements shape、skill samples 与 security evidence 都是 warning/advisory 证据层；阻断等级见 `docs/ai/check-registry.md`。
- Candidate workflow skills 当前均为 2/2 accepted samples；是否升级必须走单独决策，不得自动 always-on。
- WS-03 证明 PRD 可先压成 REQ/WS 薄切片；完整业务工程和完整 PRD 不进入 root 默认面。
- `new_pro_standard` 只同步机制层，不复制当前 repo 的历史 truth。
- GitHub required-check 策略见 ADR-012；branch protection / ruleset 完成前 OPEN-01 仍开放。
- 子 Agent 默认精简任务包；完整 PRD、diff、transcript/runtime JSONL 进入 harness 前必须摘要、筛选或结构化抽取。

## 更新规则

- 只保留当前阶段仍然有效的信息
- 当阶段切换或主目标变化时优先更新本文件
- 过期信息应进入 `status`、`adr` 或归档，而不是继续堆在本文件里
