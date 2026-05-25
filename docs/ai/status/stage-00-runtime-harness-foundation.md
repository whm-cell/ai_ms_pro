# Stage-00 Runtime Harness Foundation Status

更新时间：2026-05-25
阶段：stage-00
状态：进行中

## 需求与工作流标识

- Requirement IDs：REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006, REQ-007, REQ-008, REQ-009
- Workstream IDs：WS-01, WS-02, WS-03
- 当前阶段已通过 WS-01、WS-02 和历史 WS-03 完成 requirements traceability 与实现验证；当前 active browser smoke 收敛为 WS-01 / WS-02，WS-03 Godot browser slice 不再作为 active validation。

## 当前阶段目标

- 建立可恢复、可压缩、可验证的 runtime / governance / verification harness。
- 用真实业务薄切片验证 PRD 能通过 REQ/WS 进入 harness，而不是把完整 PRD 长期放进默认上下文。
- 把 GitHub private Free 最大边界、AI/Agent security guardrails、context budget、skill eval 和 code-shape 债务做成可复查证据。

## 当前完成度

- Runtime / Governance / Verification 主链路已可用，并已扩展到 P0 linter、agentic standards 和 code-shape 主债务拆分。
- WS-01、WS-02 具备 repo-native 实现和 CI browser smoke；WS-03 Godot browser slice 保留为历史 evidence，不再进入 active validation；REQDOC-003 不引入完整 Godot 工程。
- `new_pro_standard` 只同步机制层；当前 repo 的 REQ/WS、PR、CI、status、样本和历史 truth 不复制。
- GitHub 侧已具备最小权限 workflow、SHA pinning、固定 Playwright、CODEOWNERS、PR template、Dependabot、dependency review、security evidence、PR conflict / branch hygiene 和 `merge_group`；private Free 下 branch protection / rulesets 仍是 future gates。
- 2026-05-24 / 2026-05-25 harness burn-in 已进入 closeout / split：当前缺口不再是“能不能用”，而是分批 review、future real-event sample monitoring 和 advisory / blocking 升级决策。

## 本阶段关键成果

- 已跑通 `requirements -> implementation -> smoke -> runtime promotion -> status`；当前 CI blocking smoke 覆盖 WS-01 / WS-02，WS-03 作为历史 burn-in evidence 保留。
- PR #11 与合并后的 `main` push 已完成首轮 CI burn-in，覆盖 governance、Windows hook runtime、smoke、dependency review、Scorecard、CodeQL artifact 和 SBOM artifact。
- Candidate workflow skills 已有 3 个 accepted eval / control samples；本轮复核后仍保持 Candidate。
- AI/Agent security 与 agentic standards 已从说明提升为可校验 evidence / contract；维护细则已下沉到 `$harness-maintenance` references。

## 风险与阻塞

- OPEN-01 已调整为 private GitHub Free 最大边界：GitHub API 对 branch protection / rulesets 返回 plan limit HTTP 403；远端 required checks、review、conversation resolved 和禁止直推 `main` 不能声明已强制，但也不再作为本地代码缺口追打。
- dependency review、Scorecard、CodeQL、SBOM 和 secret scanning advisory 当前仍以 advisory / artifact evidence 为主；private Free 下不作为 required gate。
- runtime stage drift、archive candidate、context budget、source boundary 和 change-triggered followups 继续 warning / review-required；高影响动作矩阵不允许 hooks 自动执行 destructive、externally visible 或 permission-changing 动作。
- Agentic standards 只证明本地 trace / eval / tool-contract 能力；不等于模型质量评测、远端权限审计、OpenAI hosted trace/eval、MCP/A2A 或外部 collector 互通；Ruff 不替代 semantic review。
- Code-shape 主债务已清掉：`check_ai_governance.py`、`bootstrap_harness.py` 与 `check_agent_eval_dataset.py` 均已拆到阈值内。
- REQDOC-003 的 Godot 4.6.2、GUT、导出 preset、素材、本地化和发布管线仍是 proposed / 待确认；root repo 只保留 harness 研究所需的薄业务样本。

## 本轮收敛

- 上下文已 stage compression，旧 ADR 开始移入 archive；后续继续避免默认面膨胀。
- WS-03 连击计分与评级反馈作为历史薄切片 evidence 保留；当前不再由 CI active smoke 运行。
- Candidate workflow skills 达到 3/2 accepted eval / control samples；本轮单独复核后保持 Candidate。
- Agentic standards、P0 linter、external crosswalk 与 code-shape 拆分已同步到 checks / registry / index；细则从默认上下文迁入 `$harness-maintenance` reference。
- Stage Checkpoint、PreToolUse preflight、Loop / Scope Monitor、Local Trace Summary、Harness Sample Gap Evidence、Candidate Check Burn-in Ledger、future-work contract 和 upgrade-decision gates 已形成 warning-only / advisory closeout 面。
- 4 个 ready-for-upgrade-discussion gap（Source Boundary、Control Matrix Burn-in、Task Profile Audit、Sandbox Honesty）均保持 `keep-advisory`；PreToolUse real warning、Loop / Scope real warning、cross-task resume、distinct task class trace、remote interop 和 cascade stop 仍需未来真实样本。
- Stopped long session 的 canonical 入口是 [Stage-00 Harness Burn-in Closeout Handoff](../handoffs/active/stage-00-harness-burn-in-closeout.md)；`.codex/runtime/*` 只保留为本地恢复材料，不替代 status / handoff / ADR。

## 下一阶段重点

- 先按 closeout handoff 拆分 dirty worktree：closeout docs、runtime hook controls、sample ledger machinery、CI expansion、validation boundary switch、ADR/security boundaries 分批 review / commit。
- OPEN-01 首轮远端 burn-in 已完成；下一步积累 scheduled / 后续 PR 样本。
- 观察 AI/Agent guardrails、agentic control matrix 与 security evidence 真实样本，再决定是否升级 advisory / review-required 层。
- 继续观察 WS-01 / WS-02 browser smoke 在后续 CI 中的 burn-in 结果，失败时区分 Playwright 版本、浏览器安装和应用切片回归；WS-03 后续若恢复必须走新的 Godot engine spike / ADR / smoke 决策。
- 继续观察 Candidate workflow skills 的跨 workstream 样本和简单任务 skip / negative 样本。
- 观察 agentic standards 的真实维护成本，再决定是否发展外部 OpenTelemetry/OpenAI exporter、MCP-like tool policy 或更强语义检查。
- 继续压缩 Stage-00 历史：完成型 handoff 归档、status 保持摘要、ADR 旧决策归档或 supersede。
- 继续关注 code-shape 新增 warning。

## 验收判断

- Stage-00 已证明 harness 能跑通 `requirements -> implementation -> smoke -> runtime promotion -> status`。
- 当前尚未完全进入下一阶段，因为 Godot engine spike、长期 skill/PR 样本、后续 CI 样本和 AI/Agent guardrails 真实样本仍需确认；远端强制门禁在 private Free 下已归类为 plan-limited ceiling。
- 剩余风险主要是远端 enforcement 不可用时的人审纪律、长期上下文增长和维护性债务，不是本地 harness 能否使用。

## 关联文档

- [Harness Remaining Work](../harness-open-items.md)
- [AI 文档入口索引](../index.md)
- [当前工作上下文](../working-context.md)
- [Agent Harness Security](../security/agent-harness-security.md)
- [Agentic Control Matrix](../security/agentic-control-matrix.md)
- [Agent Trace Standard](../standards/agent-trace-schema.md)
- [Agent Harness Evals](../evals/README.md)
- [Tool Contracts](../tool-contracts/README.md)
