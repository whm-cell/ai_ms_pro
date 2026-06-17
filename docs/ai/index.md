# AI 文档入口索引

更新时间：2026-06-17
当前阶段：STAGE-00 Runtime Harness Foundation
当前判断：harness 可用；stage-00 转向 bounded 增量；context budget 是 strict gate；active validation 仍只认 WS-01 / WS-02；外部能力、标准、prototype、code-shape、config、mock-data、run metrics 和 enterprise boundary claim 均按结构化 evidence / boundary 处理。

## 入口说明

本文件只做稳定路由。默认阅读链路保持短：`AGENTS.md -> working-context -> current status`。
requirements、handoff、ADR、archive、skills、runtime JSONL 和完整 diff 都按任务需要再进入。

## 默认短链路

1. [项目规则 AGENTS.md](/Volumes/usd/codes/go_projects/ai_ms_pro/AGENTS.md)
2. [当前工作上下文](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/working-context.md)
3. [Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)

## 按需入口

- Requirements / scope：[需求入口](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/index.md)、[Traceability Matrix](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/requirements/traceability-matrix.md)、[项目计划](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/plan.md)、[Harness Remaining Work](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-open-items.md)。
- Resume / decisions：[Harness Real Sample Watchlist](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/harness-real-sample-watchlist.md)、[Stage Checkpoints](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/checkpoints/README.md)、[Active Handoffs](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active)、[ADR 目录](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/adr)。
- Checks / burn-in：[Registry](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/check-registry.md)、[Burn-in Ledger](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/check-burn-in-ledger.md)。
- Security / agentic：[Supply Chain](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/security/supply-chain-provenance-plan.md)、[Security Evidence Triage](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/security/security-evidence-triage.md)、[Agentic Control Matrix](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/security/agentic-control-matrix.md)、[Remote Merge Gates](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/security/remote-merge-gates.md)、[Agent Harness Security](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/security/agent-harness-security.md)。
- Standards / skills：[standards](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/standards)、[optimization defaults](./standards/harness-optimization-decision-defaults.md)、[bounded loop triage](./standards/bounded-loop-triage.md)、[config](./standards/config-contract-boundary.md)、[mock data](./standards/mock-data-boundary.md)、[logging](./standards/logging-redaction-boundary.md)、[error](./standards/error-contract-boundary.md)、[side effect](./standards/runtime-side-effect-boundary.md)、[productization](./standards/agent-productization-readiness.md)、[coding](./standards/evidence-based-coding-standards.md)、[coding/browser harness selection](./standards/coding-agent-browser-harness-selection.md)、[capability model](./harness-capability-model.md)、[evals](./evals/README.md)、[tool contracts](./tool-contracts/README.md)、[skill samples](./skill-usage-samples.md)；更多标准从 `standards/` 目录按需进入。

## 按需 Skills

- `$harness-maintenance`：bootstrap、hooks、runtime reducer、session compression、GitHub guardrails、supply-chain evidence 或 code-shape。
- `$requirements-traceability-maintenance`：REQDOC / REQ / WS、traceability-matrix 或技术假设状态变化。
- `$progressive-feature-development`：非平凡功能、跨模块变更、测试策略变化或显式 plan-first 任务。
- `$prd-to-project-skills`：从 workstream / 实现样本中判断是否沉淀稳定项目 skill。
- `$repo-governed-coding`：非平凡实现、review、refactor 或涉及魔法值、复杂度、重复、命名、公共抽象边界的代码质量任务。
- `$enterprise-code-boundary-maintenance`：logging/redaction、error contract、runtime side effect、config 或企业编码边界 guardrails。
- `$team-pr-conflict-control`：多人或多 AI 并行 PR、touch-set overlap、CODEOWNERS、merge queue / `merge_group` readiness。

## 常用检查

- Core：`check_ai_governance.py`、`ruff check .codex/hooks scripts tests`、`check_code_shape.py --all`（Python/TS/JS/CSS/SQL/Rust/shell/PowerShell）、`git diff --check`、`check_context_budget.py`。
- Game/static：`check_threejs_snake_contract.py`，其他 smoke 按当前 workstream/status 选择。
- Harness/sample/security/prototype/config/mock-data/enterprise：按 changed-file follow-up、[check registry](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/check-registry.md) 或 [verification commands](/Volumes/usd/codes/go_projects/ai_ms_pro/.agents/skills/harness-maintenance/references/verification-commands.md) 选择，不把完整命令矩阵放在默认索引。

## 当前锚点

- 当前 status：[Stage-00 Runtime Harness Foundation Status](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/status/stage-00-runtime-harness-foundation.md)
- 当前 burn-in closeout：[Stage-00 Harness Burn-in Closeout Handoff](/Volumes/usd/codes/go_projects/ai_ms_pro/docs/ai/handoffs/active/stage-00-harness-burn-in-closeout.md)
- 最新 ADR：[ADR-017 Trace Remote Interop Boundary](./adr/ADR-017-trace-remote-interop-boundary.md)
- 最新 changelog：[Harness Optimization Decision Defaults](./changelog/2026-06-17-harness-optimization-decision-defaults.md)

## 维护规则

- 本文件不展开完整阶段目录，也不维护第二套“下一次会话先读”。
- 新增或归档 `handoff`、`status`、`changelog`、`adr` 后，只更新稳定入口和当前锚点。
- 本地 runtime harness 文件不加入本索引；需要时通过 reducer、handoff 或 status 摘要进入共享 truth。
