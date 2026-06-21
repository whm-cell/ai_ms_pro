# 当前工作上下文

更新时间：2026-06-21
当前阶段：STAGE-00 Runtime Harness Foundation
当前模式：Codex-first harness + bounded runtime capability

## 作用

只保留下一次会话立即需要继承的当前真相；长期细节在 `status`、`handoff`、ADR、requirements 或 changelog。

## 同步元数据

- Current Stage: STAGE-00
- Active Status Source: docs/ai/status/stage-00-runtime-harness-foundation.md
- Active Handoff Sources: docs/ai/handoffs/active/stage-00-harness-burn-in-closeout.md
- Requirement IDs: REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006
- Workstream IDs: WS-01, WS-02
- Last Synced From: status,handoff,manual
- Last Synced At: 2026-06-21
- Last Sync Detail: Synced after borrowed harness controls added default-off quality supervisor protocol, manual async verification runner, default context line-density gate, and generalized runtime artifact staging boundary.

## 当前主目标

- Stage-00 从 harness closeout 转向 capability 增量建设，但三层边界不变：runtime 本地恢复、governance 共享真相、verification 漂移检测。
- 当前新增能力只限 local-first durability、bounded observability/eval、loop triage、coding/config/mock-data/data-activation/reuse-retirement/enterprise review-required standards 和 advisory guardrails。
- 2026-06-17 已固化 optimization defaults、run metrics、Real Data Activation Gate、Reuse And Retirement Gate 与 starter Python runtime 选择；均只增加审计/初始化信号，不新增外部发送、native sandbox、hosted eval/trace、MCP/A2A、真实 CI agent workflow、生产数据集成或自动删代码能力。
- 2026-06-20 主分支推送 CI follow-up 已固化：PR branch hygiene 仍 strict，main push branch hygiene 只写 advisory summary，避免无关远端分支清理阻断主分支发布；Windows Python resolution 单测使用版本探针 mock，不依赖 POSIX fake executable。
- 2026-06-20 commit / push 流程已拆分：本地 commit 只跑 fast gates，PR checks 失败用独立 repair worktree，合并 `main` 和同步本地开发分支保持独立确认；新增 PR checks 只读报告和 PR repair worktree helper，均为 advisory 操作辅助。
- 2026-06-21 从 `demo_txt_t_proto` 吸收 bounded harness controls：`quality_supervisor` 默认关闭并由 review-required checker 审计；`start_async_verification.py` 仅写本地 runtime 恢复材料；context budget 增加默认面 line-density gate；governance 泛化拦截 staged generated `.codex/runtime` artifacts。
- 2026-06-06 至 06-16 的 bounded vnext、external decisions、Prototype Design Brief、productization/config/coding-browser/loop/mock-data/enterprise standards 均保持 review-required / advisory 边界。
- Active validation 仍只有 WS-01 Three.js Snake 与 WS-02 Harness Trace Console。
- 2026-06-15 `new_pro_standard` 已同步公共 harness 机制，并保持 starter-safe 边界：不复制本 repo 的 REQ/WS、accepted samples、runtime artifacts 或 demo apps。

## 当前活跃队列

1. 收敛 canonical change surface，避免 `.codex/runtime/*` 被跟踪或当成共享 truth。
2. 压缩 context / ADR 预算，保持默认阅读链路短。
3. 只用真实 bounded evidence 补 cross-task resume、remote interop、高影响动作和 guardrail 样本；不能用 schema sample 或 local-only artifact 补数。
4. 独立处理 legacy code-shape 大文件，不扩大 harness 产品边界。

## 当前风险与阻塞

- GitHub private Free 下 main 保护 / ruleset 仍是 remote `UNKNOWN`。
- Agentic security / trace / sandbox / sample-gap / loop triage 只证明本地 bounded contract；不证明 hosted trace、native sandbox、MCP/A2A、scheduler 或外部 collector。
- `GAP-TRACE-OTLP-PILOT-BURNIN` 只有 1 个 accepted local-interop sample；`verified_remote=0`。
- `GAP-RUNTIME-STAGE-CHECKPOINT-RESUME` 尚无 accepted cross-task resume sample；不能用 harness-hardening 任务补数。
- CI agent contract 与 local execution policy wrapper 都是 advisory / assistive，不创建真实 CI agent workflow，也不证明 native sandbox。
- Planner / executor / reviewer 与 bounded loop triage 目前都只是 sample / triage shape，不证明 scheduler runtime、A2A、hosted trace 或 red-team evidence。
- External harness decisions 只证明 source-backed operator choices；不证明 remote trace、hosted eval、native sandbox、MCP/A2A 或 CI agent runtime。
- `GAP-GUARDRAIL-CONFIRMATION` 已有 1 个 accepted real sample，仍是 `needs-more-real-samples`；`GAP-GUARDRAIL-PREFLIGHT-WARNING` 已有 2 个 accepted real warning samples（含 1 个 false positive）并记录 `keep-advisory`，不得升级 blocking。
- 高影响动作、PreToolUse warning、runtime drift、security triage 和 runtime token pressure 仍是 warning / review-required；PreToolUse 只支持后续 tuning 讨论，不支持阻断。

## 下一次会话先读

1. [AI 文档入口索引](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/index.md)
2. [Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
3. [Stage-00 Harness Burn-in Closeout Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-harness-burn-in-closeout.md)
4. [需求追踪矩阵](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/traceability-matrix.md)

仅在真实样本事件或 sample-gap 审计时，再读 [Harness Real Sample Watchlist](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-real-sample-watchlist.md)。

## 最近已固化的决策

- Runtime files、full diff、transcript、source evidence 和 subagent output 都是 bounded/on-demand 输入；稳定结论必须提升到 docs / checks / ADR。
- Sample-gap 机制只记录真实 evidence 与 upgrade decisions；synthetic evidence 不得补 accepted real sample。
- Capability summary 是 artifact-backed local summary，只支持后续决策，不自动升级 blocking、remote 或 hosted capability claim。
- Task outcome eval command validation treats repo-local `.codex/.venv/bin/python` as optional; CI must still validate referenced repo scripts/tests.
- External harness decisions are source-backed and default-permitted only for local/no-effect improvements; external effects still need explicit per-run confirmation.
- Harness optimization defaults keep STAGE-00 evidence-first: local model/cost/latency and `run_metrics` are metadata; sandbox / CI agent / hosted eval / MCP-A2A stay comparison-only or task-shape gated unless separately approved.
- Prototype Design Brief validation is a disabled-by-default design projection gate; only enabled projects or slices get brief and artifact child checks in `check_ai_governance.py`.
- Evidence-based coding standards are review-required only; candidate Ruff / JS lint rules need real samples before any blocking upgrade.
- Productization/config/mock-data/data-activation/reuse-retirement/coding-browser/loop triage standards are review-required or advisory only; they improve routing and visibility, not runtime capability claims, production data quality, auto deletion, or dead-code proof.
- Starter bootstrap now supports parent `.env` allowlisted selectors and pyenv version fallback before PATH / launcher fallback; this is a local harness setup convenience, not a dependency or secret-management system.
- Enterprise Code Boundary skill is Candidate only; logging/redaction, error contract, and runtime side effect boundaries are review-required standards until real samples justify checkers or blocking-candidate promotion.
- Code-shape covers mixed stacks at file level; Python keeps AST budgets.
- `.codex/hooks.json` and WS-01 / WS-02 smoke scripts now use portable launchers; Windows resolves `.cmd/.exe/.bat`, macOS / Linux keep POSIX/plain `npx`, and smoke execution remains argv-only `shell=False`.
- Main-push branch hygiene is advisory-only; PR branch hygiene remains strict. Unmanaged remote branches still need owner review, but this does not prove branch protection or ruleset health.
- Commit / push workflow helpers are local/advisory only: `scripts/report_pr_checks.py` is read-only, `scripts/start_pr_repair_worktree.py` isolates PR repair in a sibling worktree, and neither proves remote enforcement or PR check success.
- `$stacked-cigo-workflow` is the repo-local skill entry for CIGO-style PR lifecycle, stacked follow-up branches, isolated PR repair worktrees, safe `main` sync, and runtime cleanup; it keeps the same local/advisory boundaries as the commit / push helpers.
- Quality supervisor protocol remains disabled by default; enabling it must preserve hooks-cannot-spawn-subagents and main-agent canonical-write boundaries.
- Async verification status/log artifacts are local recovery evidence only; a run is not a pass claim until `status.json` says `passed` and the log has been inspected.
- 2026-06-01 至 2026-06-06 已完成 capability bootstrap、tightening、state/evidence/aggregate 与 vnext advisory slices；边界仍是 local-first。

## 更新规则

- 只保留当前阶段仍有效的信息。
- 阶段切换或主目标变化时优先更新本文件。
- 过期细节进入 `status`、`adr`、`changelog` 或 archive，不继续堆在本文件。
