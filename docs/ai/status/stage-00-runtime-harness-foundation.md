# Stage-00 Runtime Harness Foundation Status

更新时间：2026-05-02
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
  - Runtime 链路：`Stop observation -> Stop session -> SessionStart resume context`、runtime staged 阻断、runtime metadata 自动发现、observation reducer 与 handoff-first 提升路径
  - Governance 链路：`REQ/WS` metadata、working-context sync metadata、projection surface boundary、active handoff/status metadata 校验、requirements traceability alignment
  - Verification 链路：repo-local Python runner、cross-platform hook entrypoints、hook sync check、code-shape budget、governance check、WS-01/WS-02 deterministic 与黑盒 smoke
  - Starter 链路：`bootstrap_harness.py`、离线 best-effort venv 初始化、仓外 starter 复演、new project pre-commit 复演、no-old-truth boundary 与 portability guide
  - Context 链路：默认短链路、Task Discovery profiles、context surface budget、archive candidate monitor、project skill lifecycle template、context budget audit
  - GitHub 守门：workflow 最小权限/concurrency/timeout、CODEOWNERS、Dependabot、dependency review、Windows hook runtime job 与 required-check 策略
- 进行中：
  - OPEN-01：远端 CI burn-in、GitHub branch protection / ruleset required checks 确认
  - OPEN-07 / OPEN-08 / OPEN-09：starter 样板、行为 skill 默认化、project skill lifecycle 真实样本观察
- 本轮 OPEN-10 结论：
  - `6500` token budget 保留为 starter / 新项目默认目标
  - 当前 root repo 采用 `8500` 作为 Stage-00 本地预算，因为默认链路仍包含成熟阶段 status 与治理历史
  - `AGENTS.md` 已压缩长细则；current status 已压缩历史完成列表；`$repo-governed-coding` description 已缩短
  - `scripts/check_context_budget.py` 继续手动 warning-only，不接 Stop hook，不自动 compact / archive

## 本阶段关键成果

- 两个真实 workstream 已证明当前 harness 能跑通 `requirements -> implementation -> smoke -> runtime promotion -> status`。
- 默认恢复面已收缩为 `index -> working-context -> stage status -> configured active handoff budget`，archive 只在 recovery/dispute 或当前 truth surface 不足时进入。
- `new_pro_standard` 已同步机制层，包括 Python 解析、hook sync、code shape、context surface、Task Discovery、project skill lifecycle 与 context budget audit；当前 repo 的历史 truth 不复制进 starter。
- `plan/workstream` 已明确为 projection surface，当前状态真相默认回收到 `working-context`、active `handoff`、stage `status` 和 `traceability-matrix`。
- `REQ <-> WS <-> STAGE` 至少已有一层自动校验：`working-context` 当前 stage 与 matrix 不一致会阻断，runtime artifact 先 warning-only。

## 风险与阻塞

- CI workflow 已落地并增强，但尚未积累远端绿色运行历史；branch protection / ruleset 仍需远端配置并人工确认。
- Windows PowerShell runner 已补静态 parity 测试，但本机没有 `pwsh` / `powershell`，仍需要 Windows 宿主真实执行复演。
- reducer 与 runtime artifact 的 stage drift 目前仍 warning-only，是否升级阻断要看后续样本。
- active surface budget、archive candidate monitor、context budget audit 都保持 warning-only；真正压缩/归档仍由主 Agent 语义确认。
- `$repo-governed-coding`、project skill lifecycle 和 context budget audit 已进入 starter，但都不替代 `AGENTS.md`、ADR、requirements 或 verification scripts。
- Starter copied placeholder docs 仍需 `--force` 才会立刻替换成新项目名，`AGENTS.md` 仍需人工项目化。

## 下一阶段重点

- 推动 OPEN-01：远端 workflow green history、required checks、CODEOWNERS review、conversation resolved 与禁止直推 `main` 的远端确认。
- 在下一次 stage compression 时继续审查 archive candidate monitor 输出，确认候选已被 status、backlog 或 ADR 吸收。
- 在后续真实项目中观察 `$repo-governed-coding`、project skill lifecycle 和 context budget audit 是否需要从显式/手动能力升级。
- 继续判断 `WS-01` 与 `WS-02` 是保留为验证样板，还是压缩为更轻的 starter 说明。

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
- [2026-05-02 Context Budget Audit](../changelog/2026-05-02-context-budget-audit.md)
- [OPEN-10 使用细节](../../../--使用细节/context-budget-open-10.md)
