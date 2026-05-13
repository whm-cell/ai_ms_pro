# 当前工作上下文

更新时间：2026-05-13
当前阶段：STAGE-01 游戏 MVP 开发
当前模式：Codex-first harness + repo-native game slice

## 作用

只保留下一次会话立即需要继承的当前真相；长期细节在 `status`、`handoff`、ADR、requirements 或 changelog。

## 同步元数据

- Current Stage: STAGE-01
- Active Status Source: docs/ai/status/stage-01-game-mvp-development.md
- Active Handoff Sources:
  - docs/ai/handoffs/active/stage-00-runtime-stop-session.md
  - docs/ai/handoffs/active/stage-00-observation-reducer.md
  - docs/ai/handoffs/active/stage-01-pixel-freeze-platformer-mvp.md
- Requirement IDs: REQ-010, REQ-011, REQ-012, REQ-013
- Workstream IDs: WS-04
- Last Synced From: status,handoff,manual
- Last Synced At: 2026-05-13

## 当前主目标

- STAGE-01 当前主线是 REQDOC-003 / `prd_game.md` 的 repo-native 游戏 MVP，不把完整 PRD 长期放进默认上下文。
- WS-04 已完成 `apps/pixel-freeze-platformer/` 三关 MVP：移动/跳跃、冻结攻击、投掷连锁、清场出口、评级、HUD、暂停/重开、localStorage 进度和中英本地化种子。
- `scripts/pixel_freeze_platformer_smoke.py` 覆盖 load -> validate content -> controls -> clear level -> next level -> campaign complete -> locale/reset。
- REQDOC-003 已绑定 REQ-007/008/009 与 WS-03，也已扩展绑定 REQ-010/011/012/013 与 WS-04；完整 Godot 工程仍是 proposed / 后续 engine spike。
- `AGENTS.md` 只保留 always-on 触发与边界；细则由 skills、references、templates 和 checks 承接。
- `.agents/skills` 是按需方法层，不替代 canonical docs / checks。

## 当前活跃队列

1. 若继续推进游戏产品化，先决定是否启动 Godot engine spike，并用 ADR 明确 Godot 版本、目录结构、导出和 smoke 策略。
2. 若继续浏览器 MVP，Boss、更多关卡、触控输入、正式资源管线或 CI 接入应拆新 REQ/WS，不直接扩大 WS-04。
3. 后续 PR 通过 `.github/pull_request_template.md` 显式填写 `REQ/WS`、touch-set、overlap、verification 和 governance impact。
4. 后续真实多人 / 多 AI PR 要用 `$team-pr-conflict-control` 记录 touch-set overlap 和 coordination action。
5. security / guardrail / workflow 缺口见 `--使用细节/真实场景覆盖缺口待确认.md`；下一次 stage compression 继续清理完成型 handoff。

## 当前风险与阻塞

- WS-04 完成的是浏览器 MVP，不证明 Godot engine、GUT、导出模板、移动端、正式素材或商业发布能力。
- 当前本机没有可用 `godot` / `godot4` 命令；真实 Godot 工程仍需后续 spike。
- `pytest` 当前不可用；requirements shape 单测需走 `unittest` 或先安装测试依赖。
- `scripts/check_requirements_shape.py` 仍有既有 code-shape warning：文件行数超过 350。
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
- 第三方 `.codex/skills` 现按 dependency-like 资产处理；使用 `scripts/check_skill_catalog.py` 检查 proxy/catalog/lock 元数据，也可用 `--check-output <file>` 对 skill/tool 输出做 bounded instruction-like scan，避免 raw `SKILL.md` 或工具输出直接扩张 discovery context。
- raw PRD/source evidence 现由 `scripts/extract_requirement_source.py` 先进入 `docs/requirements/source-raw/quarantine/` 并生成 bounded sanitized excerpt / REQDOC draft；source-boundary hardening 继续检查危险指令样式、大 source 和 quarantine/raw-evidence 状态。
- context budget 已拆分 default surface、skill catalog、raw source 和 static task packet；`check_context_budget.py` 会把 `.codex/skills.catalog.json`、`docs/requirements/source/` 与 `docs/requirements/source-raw/` 纳入预算。
- macOS/POSIX 与 Windows Python 解析已修复，但全新宿主仍需 bootstrap / hook sync 复验。

## 下一次会话先读

1. [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
2. [Stage-01 Game MVP Development Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-01-game-mvp-development.md)
3. [Stage-01 Pixel Freeze Platformer MVP Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-01-pixel-freeze-platformer-mvp.md)
4. [需求追踪矩阵](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/traceability-matrix.md)

## 最近已固化的决策

- 三层 harness 分工不变：runtime 是本地恢复原料，governance docs 是共享真相，verification scripts/hooks 做漂移检测。
- `plan/workstream` 是 projection surface；当前 truth 默认集中在 `working-context`、active `handoff`、stage `status` 和 `traceability-matrix`。
- WS-04 已采纳 browser MVP 作为当前游戏开发完成面；Godot 仍需独立 spike/ADR 后才能成为 accepted architecture。
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
