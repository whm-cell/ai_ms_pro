# 当前工作上下文

更新时间：2026-05-04
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
- Last Synced At: 2026-05-04

## 当前主目标

- 维持短默认上下文：`index -> working-context -> current status`；requirements、handoff、ADR、archive 与 skills 都按需进入。
- 收敛 Stage-00 剩余 hardening：远端 CI burn-in、GitHub branch protection / ruleset、required checks 与 security analysis 确认。
- 保持 `new_pro_standard` 只承载机制层；当前 repo 的 REQ/WS、状态、PR、CI 历史和样本 truth 不复制。
- 已将 skills 迁到 Codex repo-local 原生路径 `.agents/skills`；Candidate skills 继续显式触发，简单任务不走方案先行流程。
- 使用四个 warning-only evidence checks：`check_repo_skills.py`、`check_requirements_shape.py`、`check_skill_usage_samples.py`、`check_github_guardrails.py`。

## 当前活跃队列

1. 继续推进 OPEN-01：远端 workflow green history、required checks、branch protection / ruleset 与 security analysis 确认。
2. 用 `scripts/check_github_guardrails.py` 辅助区分本地已具备、远端 OK、远端 UNKNOWN，不再只靠人工记忆。
3. 后续真实 PRD / 非平凡功能任务要登记 with/without eval；`prd-to-project-skills` 与 `progressive-feature-development` 仍是 0/2。
4. 下一次 stage compression 继续清理完成型 handoff，避免 Stage-00 历史进入长期默认面。

## 当前风险与阻塞

- 远端 GitHub 设置仍可能是 UNKNOWN；本地脚本不能替代 GitHub branch protection / ruleset 的真实配置。
- Candidate skill eval 仍无 accepted 样本；不得为了升级 always-on 伪造样本或把简单任务拖入完整流程。
- PRD 技术假设检查是启发式；它能提示缺状态/验证方法，但不能替代人工架构判断。
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
- `.agents/skills/*` 是 repo-local native skill 层；`AGENTS.md` 只保留轻触发，Candidate skills 不替代 requirements / status / ADR。
- Candidate skill 升级必须有 with/without eval；当前两个 workflow skills 均为 0/2 accepted samples。
- `new_pro_standard` 同步机制层，不复制当前 repo 的历史 truth。
- GitHub ownership、supply-chain 与 required-check 策略已固化在 ADR-012；branch protection / ruleset 完成前 OPEN-01 仍保持开放。

## 更新规则

- 只保留当前阶段仍然有效的信息
- 当阶段切换或主目标变化时优先更新本文件
- 过期信息应进入 `status`、`adr` 或归档，而不是继续堆在本文件里
