# AI 文档入口索引

更新时间：2026-05-13
当前阶段：STAGE-01 游戏 MVP 开发
当前判断：harness 可用；context budget 已升级为 strict gate；WS-04 Pixel Freeze Platformer repo-native MVP 已完成 smoke 验证；Godot 工程、正式素材、音频、移动端和发布流水线仍是后续独立范围。

## 入口说明

本文件只做稳定路由。默认阅读链路保持短：`AGENTS.md -> working-context -> current status`。
requirements、handoff、ADR、archive、skills、PRD 原文、runtime JSONL 和完整 diff 都按任务需要再进入。

## 默认短链路

1. [项目规则 AGENTS.md](/Volumes/usd/codes/go_projects/ai_ms_pro/AGENTS.md)
2. [当前工作上下文](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)
3. [Stage-01 Game MVP Development Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-01-game-mvp-development.md)

## 按需入口

- [需求入口](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/index.md)：PRD、REQ、WS、traceability 或 0-1 workstream 任务再进入。
- [Traceability Matrix](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/traceability-matrix.md)：核对 `REQDOC -> REQ -> WS -> STAGE -> 验收`。
- [项目计划](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/plan.md)：阶段目标、范围或验收框架不清时再进入。
- [Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)：harness foundation、WS-01/02/03、OPEN-01 和 agentic standards 历史基线。
- [Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md)：查看 OPEN 项和完成定义。
- [Active Handoffs](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active)：resume、recovery 或相关 profile 需要时再进入。
- [ADR 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr)：长期决策背景需要时再进入。
- [Check Registry](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/check-registry.md)：确认 check 等级和 CI 覆盖。
- [Supply Chain And Provenance Plan](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/security/supply-chain-provenance-plan.md)：security evidence。
- [Security Evidence Triage](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/security/security-evidence-triage.md)：Scorecard、CodeQL、SBOM、dependency review 和 secret scanning advisory 的 triage / SLO。
- [Agentic Control Matrix](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/security/agentic-control-matrix.md)：agentic security control 映射。
- [Remote Merge Gates Evidence](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/security/remote-merge-gates.md)：private Free plan limit、CI evidence 和 future gates。
- [Agent Harness Security](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/security/agent-harness-security.md)：runtime redaction、source boundary、action matrix 和 samples 入口。
- Agentic standards：[Trace](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/standards/agent-trace-schema.md)、[Evals](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/evals/README.md)、[Tool Contracts](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/tool-contracts/README.md)、[External Crosswalk](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/standards/agentic-harness-crosswalk.md)；维护细则见 `$harness-maintenance`。
- [Candidate Skill Usage Samples](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/skill-usage-samples.md)：评估 Candidate skill 证据时再进入。
- [Candidate Skill Eval Protocol](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/skill-evals/README.md)：写详细 eval 或升级复核时再进入。

## 按需 Skills

- `$harness-maintenance`：bootstrap、hooks、runtime reducer、session compression、GitHub guardrails、supply-chain evidence 或 code-shape。
- `$requirements-traceability-maintenance`：PRD 导入、`REQDOC / REQ / WS`、traceability-matrix 或技术假设状态变化。
- `$progressive-feature-development`：非平凡功能、跨模块变更、测试策略变化或显式 plan-first 任务。
- `$prd-to-project-skills`：从 PRD / workstream / 实现样本中判断是否沉淀稳定项目 skill。
- `$team-pr-conflict-control`：多人或多 AI 并行 PR、touch-set overlap、CODEOWNERS、merge queue / `merge_group` readiness。

## 常用检查

- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/.venv/bin/python -m ruff check .codex/hooks scripts tests`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `git diff --check`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_skill_catalog.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_requirements_shape.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_agent_eval_dataset.py`
- Agentic standards：按 `$harness-maintenance` `references/agentic-standards.md` 选择 trace / eval / tool-contract checks。
- 其他按 changed-file follow-up 或 [verification commands](/Volumes/usd/codes/go_projects/ai_ms_pro/.agents/skills/harness-maintenance/references/verification-commands.md) 选择。

## 当前锚点

- 当前 status：[Stage-01 Game MVP Development Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-01-game-mvp-development.md)
- 当前 hardening backlog：[Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md)
- 当前 active handoff 精确集合：以 [working-context](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md) 的同步元数据为准。
- 最新 ADR：[ADR-015 Progressive Feature And PRD Skills](./adr/ADR-015-progressive-feature-and-prd-skills.md)
- 最新 changelog：[2026-05-12 Context Budget Strict Gate](./changelog/2026-05-12-context-budget-strict-gate.md)

## 维护规则

- 本文件不展开完整阶段目录，也不维护第二套“下一次会话先读”。
- 新增或归档 `handoff`、`status`、`changelog`、`adr` 后，只更新稳定入口和当前锚点。
- 本地 runtime harness 文件不加入本索引；需要时通过 reducer、handoff 或 status 摘要进入共享 truth。
