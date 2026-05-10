# 当前工作上下文

更新时间：2026-05-10
当前阶段：STAGE-00 真实场景验证与治理固化
当前模式：Codex-first harness engineering

## 作用

只保留下一次会话立即需要继承的当前真相；长期细节在 `status`、`handoff`、ADR、requirements 或 changelog。

## 同步元数据

- Current Stage: STAGE-00
- Active Status Source: docs/ai/status/stage-00-runtime-harness-foundation.md
- Active Handoff Sources:
  - docs/ai/handoffs/active/stage-00-runtime-stop-session.md
  - docs/ai/handoffs/active/stage-00-observation-reducer.md
- Requirement IDs: REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006, REQ-007, REQ-008, REQ-009
- Workstream IDs: WS-01, WS-02, WS-03
- Last Synced From: status,handoff,manual
- Last Synced At: 2026-05-10

## 当前主目标

- 维持短默认上下文：`index -> working-context -> current status`；requirements、handoff、ADR、archive 与 skills 都按需进入。
- stage status 已吸收上下文压缩、WS-03、OPEN-01 burn-in、远端门禁边界和本轮 agentic harness 增量。
- `AGENTS.md` 只保留 always-on 触发与边界；细则由 skills、references、templates 和 checks 承接。
- REQDOC-003 已绑定 REQ-007/008/009 与 WS-03；`apps/godot-platformer-slice/` 完成两轮 thin slice，完整 Godot 工程仍 proposed。
- PR 守门、security evidence、WS-01/02/03 smoke、P0 linter 和 agentic standards 已落地；agentic 细则按需从 `$harness-maintenance` 进入；PR #11 / `main` burn-in 已通过；private Free 远端保护仍 plan-limited。
- OPEN-14 主债务已关闭；当前 code-shape 无 warning。
- 保持 `new_pro_standard` 只承载机制层；当前 repo 的 REQ/WS、状态、PR、CI 历史和样本 truth 不复制。
- `.agents/skills` 是按需方法层，不替代 canonical docs / checks。
- Warning/advisory checks 保持分层：repo skills、requirements shape、skill samples、GitHub guardrails、change-triggered followups 和 security evidence；`check_branch_hygiene.py --strict` 仍是 active PR / stale branch 阻断面。

## 当前活跃队列

1. OPEN-01 首轮 PR + main push burn-in 已完成；后续用 `check_github_guardrails.py` / `check_branch_hygiene.py --strict` 继续区分本地 evidence、远端 OK、UNKNOWN / plan-limited 和 active PR 预算。
2. 后续 PR 通过 `.github/pull_request_template.md` 显式填写 `REQ/WS`、touch-set、overlap、verification 和 governance impact。
3. REQDOC-003 后续若继续推进，应先决定是否新建真实 Godot engine spike；不要把完整游戏工程直接塞进 root repo 默认面。
4. `prd-to-project-skills` 与 `progressive-feature-development` 已有 3 个 accepted eval / control samples；仍保持 Candidate，继续观察跨 PRD / workstream、simple skip / negative 样本。
5. 后续真实多人 / 多 AI PR 要用 `$team-pr-conflict-control` 记录 touch-set overlap 和 coordination action，先观察是否值得升级阻断策略。
6. 后续 AI/Agent security 继续观察 source boundary、high-impact follow-up、agentic control matrix 和 security evidence triage；CodeQL 注解按 private-Free / repository setting 边界处理。
7. Agentic standards 细则下沉到 `$harness-maintenance`；OpenAI hosted trace/eval、MCP/A2A 和外部 collector 仍是 future work。
8. security / guardrail / workflow 缺口见 `--使用细节/真实场景覆盖缺口待确认.md`；下一次 stage compression 继续清理完成型 handoff。

## 当前风险与阻塞

- 远端 GitHub main 保护在 private Free 下不可强制：GitHub API 对 branch protection / rulesets 返回 plan limit HTTP 403；required checks、review、conversation resolved 和禁止直推 `main` 不能声明已强制。
- Candidate workflow skills 已有 3/2 accepted eval / control samples，但仍保持 Candidate；升级 always-on 前需更多跨 workstream 和 skip 样本。
- PRD 技术假设检查是启发式；`requirements-traceability-maintenance` 能提示缺状态/验证方法，但不能替代人工架构判断或 ADR。
- REQDOC-003 的 Godot 4.6.2、GUT、导出 preset、素材/本地化管线仍未被 ADR 或真实 Godot spike 采纳。
- runtime stage drift、archive candidate 仍保持 warning-only；是否升级阻断要等更多真实样本。
- runtime sanitizer、source boundary、高影响动作矩阵、guardrail samples 和 security triage 是 best-effort / review-required 防护层，不替代 secret scanning、人工确认或远端审计。
- Ruff 当前只跑保守 Python lint 与 diff whitespace；它不替代 semantic standards review、tool-contract policy 或 security checks。
- Agentic standards 当前只证明本地 trace/eval/tool-contract 能力；不证明远端权限、模型质量或外部互通。
- Code-shape 主债务已清掉；新增 warning 继续按 `check_code_shape.py --all` 处理。
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
- `plan/workstream` 是 projection surface；当前 truth 默认集中在 `working-context`、active `handoff`、stage `status` 和 `traceability-matrix`。
- 默认上下文由 Task Discovery profile 扩面；长期规则见 ADR-010、ADR-011、ADR-014、ADR-015。
- `.agents/skills/*` 是按需 native skill 层；warning/advisory 与 blocking 等级见 `docs/ai/check-registry.md`。
- Candidate workflow skills 当前均为 3/2 accepted eval / control samples；是否升级必须走单独决策，不得自动 always-on。
- WS-03 证明 PRD 可先压成 REQ/WS 薄切片；完整业务工程和完整 PRD 不进入 root 默认面。
- `new_pro_standard` 只同步机制层，不复制当前 repo 的历史 truth。
- GitHub required-check 策略见 ADR-012；private Free 下 OPEN-01 以最大边界和 CI evidence burn-in 管理，branch protection / ruleset 等待计划或可见性升级。
- 子 Agent 默认精简任务包；完整 PRD、diff、transcript/runtime JSONL 进入 harness 前必须摘要、筛选或结构化抽取。
- runtime prompt preview、transcript path、SessionStart 摘要和 reducer draft 必须走 runtime sanitizer；外部内容作为 evidence / data，高影响 Agent 动作必须明确人工确认。
- Agentic standards、P0 linter 和 external crosswalk 不进入 `AGENTS.md` 细则层；由 index 路由，checker / CI / follow-up rules 检测漂移。

## 更新规则

- 只保留当前阶段仍然有效的信息
- 当阶段切换或主目标变化时优先更新本文件
- 过期信息应进入 `status`、`adr` 或归档，而不是继续堆在本文件里
