# 当前工作上下文

更新时间：2026-05-02
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
- Last Synced From: status,handoff,manual
- Last Synced At: 2026-05-02

## 当前主目标

- 维持短默认上下文：`index -> working-context -> current status`，再由 Task Discovery profile 决定是否进入 requirements、handoff、ADR 或 archive
- 收敛 Stage-00 剩余 hardening：远端 CI burn-in、GitHub branch protection / ruleset 确认、required checks 生效验证
- 保持 `new_pro_standard` 作为可迁移机制层；当前 repo 的历史 truth 不复制进 starter
- 将 project architecture/style/dependency skill 生命周期保持为按需模板；简单任务不默认读取，长期规则仍提升到 ADR/status/check
- 使用 `scripts/check_context_budget.py` 量化默认上下文厚度；OPEN-10 首轮 triage 已完成，当前保持 warning-only，不接入 Stop hook

## 当前活跃队列

1. 以 [Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md) 为准，继续推进 OPEN-01
2. 推送后观察 `governance`、`windows-hook-runtime`、`smoke` 与 dependency review 是否在远端稳定通过
3. 按 [GitHub 远端配置确认细节](/Volumes/usd/codes/go_projects/ai_ms_pro/--使用细节/github-remote-configuration.md) 在 branch protection / ruleset 中把 required checks、PR review、CODEOWNERS review、conversation resolved 与禁止直推 `main` 配好并回写 OPEN-01
4. 判断 Stage-00 是否可以在远端 burn-in 后压缩并进入下一阶段，同时保留 OPEN-07 / OPEN-08 / OPEN-09 为 P2 策略项

## 当前风险与阻塞

- governance、Windows hook runtime、repo-native smoke 与 dependency review 已进入 workflow，但尚无远端稳定运行历史，暂时不能把“已接 CI”当成完全收敛
- GitHub branch protection / ruleset 属于远端设置，本地文件只能列出要求，不能证明 required checks 已生效；人工配置清单已整理到 `--使用细节/github-remote-configuration.md`
- reducer 阈值已有多日 observation 样本与判定标准，但长期质量仍需在后续 stage compression 中观察
- runtime session / observation 的 stage drift 目前先以 warning 暴露，尚未升级为 blocking
- starter 现在已能在仓外完成 bootstrap + pre-commit，但 copied placeholder docs 仍需 `--force` 才会立刻换成新项目名，`AGENTS.md` 仍需人工项目化；相关说明已回写 starter README/guide
- hook 配置现在已有共享 renderer、独立 `sync_hooks_config.py`、POSIX Python 入口和 Windows PowerShell 入口；但仓库初始化后若跨 host shell/OS 迁移，仍需重新 bootstrap 或显式同步 `.codex/hooks.json`
- Dependabot 已覆盖 GitHub Actions、pip 与 root npm 入口；npm 只有在仓库出现 npm manifest 后才会产生实际更新 PR
- active surface budget 当前由 `.codex/harness.toml` 配置，仍只是 warning，不是 blocking；本轮语义归档后 active bound handoff 已从 5 个降到 2 个
- archive candidate monitor 已可按需列出候选，但不会接入默认 Stop hook，也不会自动移动文件；归档仍由主 Agent 在 stage compression 时确认
- `$repo-governed-coding` 已进入 starter 机制层，但仍是显式调用能力；若未来把它变成默认 workflow，必须再更新 `AGENTS.md` / `ADR`，避免行为 skill 绕过治理文档
- project skill 生命周期模板已落地，但真实 architecture/style/dependency skill 样本仍少；暂不升级为默认 workflow 或 blocking checker
- context budget audit 首轮 triage 已完成：starter/new-project 目标保持 6500，当前 root Stage-00 预算为 8500，`AGENTS.md`、current status 与 `$repo-governed-coding` description 已压缩；后续若再次持续 warning，再按 [OPEN-10 Context Budget 使用细节](/Volumes/usd/codes/go_projects/ai_ms_pro/--使用细节/context-budget-open-10.md) 重新评估
- macOS/POSIX 与 Windows PowerShell Python 解析已修复为优先 `.codex/.venv` 与 Python 3.11+ 候选；后续仍需观察没有 `.codex/.venv` 的全新宿主是否按预期创建 3.11 venv

## 下一次会话先读

1. [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
2. [Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
3. [Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md)
4. [当前活跃 handoff 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active)：只有 resume/recovery 或相关 profile 需要时再进入
5. [需求文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/index.md)：当任务直接落在 `REQ/WS` 或 traceability 时再进入
6. [ADR 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr)：当需要长期决策背景时再进入

## 最近已固化的决策

- 三层 harness 分工保持不变：runtime 只做本地恢复原料，governance docs 承接共享真相，verification scripts/hooks 做漂移检测。
- `plan/workstream` 是 projection surface；当前状态真相默认集中在 `working-context`、active `handoff`、stage `status` 和 `traceability-matrix`。
- 默认上下文链路收缩为短入口，并由 Task Discovery profile 判断是否扩大读取面；长期决策见 ADR-010、ADR-011。
- active handoff 预算与 archive candidate 阈值由 `.codex/harness.toml` 配置；候选提醒保持 warning-only，归档由主 Agent 语义确认。
- project architecture/style/dependency skill 采用 `Draft -> Candidate Skill -> Stable Skill -> Promote -> Deprecate` 生命周期；长期决策见 ADR-013，模板只按需读取。
- context budget audit 采用手动 warning-only 体检；长期决策见 ADR-014，当前 root Stage-00 budget 为 8500，starter/default 初始目标仍为 6500，不自动 compact、不自动归档。
- `new_pro_standard` 同步机制层，包括 Python 解析、hook sync、code-shape、context surface 配置与 Task Discovery；当前 repo 的历史 truth 不复制进 starter。
- GitHub ownership、supply-chain 与 required-check 策略已固化在 ADR-012；branch protection / ruleset 完成前 OPEN-01 仍保持开放。
- `WS-01` 已补黑盒浏览器 smoke；`WS-02` 已有黑盒 DOM smoke。
- `working-context` 当前 stage 与 traceability matrix 中 REQ/WS/STAGE 的一致性已由 governance checker 阻断；runtime artifact 同类错配先 warning-only。
- OPEN-04、OPEN-05、OPEN-06 已在本轮 hardening 中关闭；剩余默认队列收敛到 OPEN-01 和 P2 策略项。
- 当前剩余 hardening 以 [Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md) 和 stage `status` 为准。

## 更新规则

- 只保留当前阶段仍然有效的信息
- 当阶段切换或主目标变化时优先更新本文件
- 过期信息应进入 `status`、`adr` 或归档，而不是继续堆在本文件里
