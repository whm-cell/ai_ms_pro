# 当前工作上下文

更新时间：2026-05-25
当前阶段：STAGE-01 游戏 MVP 开发
当前模式：Codex-first harness + repo-native game slice

## 作用

只保留下一次会话立即需要继承的当前真相；长期细节在 `status`、`handoff`、ADR、requirements 或 changelog。

## 同步元数据

- Current Stage: STAGE-01
- Active Status Source: docs/ai/status/stage-01-game-mvp-development.md
- Active Handoff Sources:
  - docs/ai/handoffs/active/stage-00-harness-burn-in-closeout.md
- Requirement IDs: REQ-010, REQ-011, REQ-012, REQ-013
- Workstream IDs: WS-04
- Last Synced From: status,handoff,manual
- Last Synced At: 2026-05-25

## 当前主目标

- STAGE-01 当前主线是 REQDOC-003 / `prd_game.md` 的 repo-native 游戏 MVP，不把完整 PRD 长期放进默认上下文。
- WS-04 已完成 `apps/pixel-freeze-platformer/` 三关 MVP：移动/跳跃、冻结攻击、投掷连锁、清场出口、评级、HUD、暂停/重开、localStorage 进度和中英本地化种子。
- `scripts/pixel_freeze_platformer_smoke.py` 覆盖 load -> validate content -> controls -> clear level -> next level -> campaign complete -> locale/reset。
- 本轮 harness capability validation 回到 `apps/threejs-snake/`：`scripts/threejs_snake_smoke.py` 验证 deterministic smoke API，`scripts/threejs_snake_blackbox_smoke.py` 验证真实 DOM / keyboard 路径。
- REQDOC-003 已绑定 REQ-007/008/009 与 WS-03，也已扩展绑定 REQ-010/011/012/013 与 WS-04；完整 Godot 工程仍是 proposed / 后续 engine spike。
- WS-03 Godot browser slice 已从 active worktree / CI 移除，只保留历史 evidence；后续如重启 Godot 必须新建 engine spike / ADR / smoke。
- `AGENTS.md` 只保留 always-on 触发与边界；细则由 skills、references、templates 和 checks 承接。
- `.agents/skills` 是按需方法层，不替代 canonical docs / checks。

## 当前活跃队列

1. 当前优先任务是 stopped harness-burn-in session closeout：先按 `stage-00-harness-burn-in-closeout.md` 拆分 review / stage / commit，不继续扩大 hooks、CI、apps 或 sample collectors。
2. 未来真实样本采集已下沉到 `docs/ai/harness-real-sample-watchlist.md`；保持 event-driven，只有遇到真实 PreToolUse warning、Stop warning、跨任务 resume、security workflow、remote interop、red-team incident 或 workflow skill 任务时再唤醒。
3. 不为了补齐 readiness 数字制造 synthetic evidence，也不要反复运行 planner / intake / readiness 去追不存在的场景；`.codex/runtime/*` placeholders 不是 canonical truth。
4. 若继续推进游戏产品化，先决定是否启动 Godot engine spike，并用 ADR 明确 Godot 版本、目录结构、导出和 smoke 策略；不要复用已退出 active validation 的 WS-03 browser slice 作为当前证据。
5. 若继续浏览器 MVP，Boss、更多关卡、触控输入、正式资源管线或 CI 接入应拆新 REQ/WS，不直接扩大 WS-04。
6. 后续 PR 通过 `.github/pull_request_template.md` 显式填写 `REQ/WS`、touch-set、overlap、verification 和 governance impact。
7. 后续真实多人 / 多 AI PR 要用 `$team-pr-conflict-control` 记录 touch-set overlap 和 coordination action。

## 当前风险与阻塞

- WS-04 只证明浏览器 MVP；Godot engine/GUT/export、移动端、正式素材、音频和发布流水线仍需独立 spike/ADR。
- WS-03 Godot browser slice 已退出 active validation；当前测试能力样例是 WS-01 Three.js Snake。
- 当前本机没有 `godot` / `godot4`；`pytest` 也不可用，requirements shape 单测走 `unittest` 或先装依赖。
- GitHub private Free 下 main 保护 / ruleset 仍是 remote `UNKNOWN`；不得声明 required checks、review 或禁直推已强制。
- Candidate workflow skills 虽有 3/2 accepted eval/control samples，仍保持 Candidate；升级 always-on 需要更多 cross-workstream / skip 样本和单独决策。
- Agentic security / trace / sandbox / sample-gap 控制面只证明本地 bounded contract；不证明 secret scanning、远端审计、native sandbox、OpenAI sandbox、MCP/A2A、外部 OTLP 或 hosted trace 互通。
- `GAP-TRACE-OTLP-PILOT-BURNIN` 只有 1 个 accepted local-interop sample；真实远端 collector / hosted trace 仍未完成。
- `GAP-GUARDRAIL-SOURCE-BOUNDARY` 与 `GAP-SEC-CONTROL-MATRIX-BURNIN` 均已有 2 个 accepted real samples 并记录 keep-advisory 升级决策；runtime stage drift、高影响动作、guardrail samples、security triage 和 runtime token pressure 仍是 warning/review-required；是否升级阻断必须等更多样本和单独决策。
- Code-shape 主债务已清掉；context budget 已拆分 default surface、skill catalog、raw source 和 static task packet，继续用对应 checker 守住默认面。
- starter/bootstrap 只初始化机制，不决定业务 truth；新项目仍需人工改写 `AGENTS.md` 和初始 REQ/WS。

## 下一次会话先读

1. [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
2. [Stage-01 Game MVP Development Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-01-game-mvp-development.md)
3. [Stage-00 Harness Burn-in Closeout Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-harness-burn-in-closeout.md)
4. [需求追踪矩阵](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/traceability-matrix.md)

仅在遇到真实样本事件或要做 sample-gap 审计时，再读 [Harness Real Sample Watchlist](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-real-sample-watchlist.md)。

## 最近已固化的决策

- 三层 harness 分工不变：runtime 是本地恢复原料，governance docs 是共享真相，verification scripts/hooks 做漂移检测。
- `plan/workstream` 是 projection surface；当前 truth 默认集中在 `working-context`、active `handoff`、stage `status` 和 `traceability-matrix`。
- WS-04 browser MVP 是当前游戏完成面；Godot 仍需独立 spike/ADR 后才能成为 accepted architecture。
- 默认上下文由 Task Discovery profile 扩面；长期规则见 ADR-010、ADR-011、ADR-014、ADR-015。
- `.agents/skills/*` 是按需 native skill 层；warning/advisory/blocking 等级见 `docs/ai/check-registry.md`。
- 子 Agent 和 source evidence 默认走 bounded summary；完整 PRD、diff、transcript/runtime JSONL 不进入 root 默认面。
- Agentic standards、P0 linter 和 external crosswalk 不进入 `AGENTS.md` 细则层；由 index 路由，checker / CI / follow-up rules 检测漂移。
- 2026-05-24 Harness Sample Gap Evidence v1 接入通用 gap evidence ledger、collector、collection queue、pending audit 和 no-write review gates。
- 2026-05-25 Harness Sample Gap Evidence v1 记录 2 个 source-boundary accepted real samples 和 2 个 control-matrix accepted real samples，用于证明 goal context / summary / memory / repo docs 的 source normalization 边界、goal objective / instruction priority 边界，以及 AC-01 映射不应被提前升级为 blocking。
- 2026-05-25 ready-for-upgrade-discussion gaps 先进入 `review-upgrade-decision` lane；Task Profile Audit、Sandbox Honesty、Source Boundary 与 Control Matrix Burn-in 复用 `harness-upgrade-decisions.jsonl` 的 keep-advisory 决策，不再被默认 planner 当成 append-new-pending-slot。
- 2026-05-24 readiness audit 已直接显示 ready-gap upgrade decision status / ref / missing-decision list；严格 keep/promote/defer 校验仍由 `check_harness_upgrade_decisions.py` 执行。
- 2026-05-25 stopped burn-in session 的下一步是 closeout / split；canonical 入口是 `docs/ai/handoffs/active/stage-00-harness-burn-in-closeout.md`，不是 `.codex/runtime/*`。
- 2026-05-25 真实样本缺口改为 watchlist 管理：无法主动验证的样本只在 `docs/ai/harness-real-sample-watchlist.md` 保留触发条件和 no-write review route，未来遇到真实事件再唤醒。

## 更新规则

- 只保留当前阶段仍然有效的信息
- 当阶段切换或主目标变化时优先更新本文件
- 过期信息应进入 `status`、`adr` 或归档，而不是继续堆在本文件里
