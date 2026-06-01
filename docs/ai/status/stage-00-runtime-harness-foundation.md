# Stage-00 Runtime Harness Foundation Status

更新时间：2026-06-01
阶段：stage-00
状态：进行中

## 需求与工作流标识

- Requirement IDs：REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006
- Workstream IDs：WS-01, WS-02
- 当前阶段的 active validation 只保留 WS-01 Three.js Snake 与 WS-02 Harness Trace Console。

## 当前阶段目标

- 建立可恢复、可压缩、可验证的 runtime / governance / verification harness。
- 用真实业务薄切片验证 requirements 能通过 REQ/WS 进入 harness，而不是把完整来源材料长期放进默认上下文。
- 把 GitHub private Free 最大边界、AI/Agent security guardrails、context budget、skill eval 和 code-shape 债务做成可复查证据。
- 在保持三层 harness 边界不变的前提下，把阶段心态从 closeout 转向 capability 增量建设：runtime durability、bounded observability / interop、task-quality eval。

## 当前完成度

- Runtime / Governance / Verification 主链路已可用，并已扩展到 P0 linter、agentic standards 和 code-shape 主债务拆分。
- Code-shape checker 与 `new_pro_standard` starter template 已覆盖 Rust `.rs` 文件 scope；新增 Rust 大文件按 `rust_file` 阈值进入同一检查路径。
- WS-01、WS-02 具备 repo-native 实现和 browser smoke；WS-01 已补 pause/resume 与 reset-best 作为真实业务小切片，它们仍是当前 active capability / governance UI validation sample。
- `new_pro_standard` 已同步 starter-safe 机制层与关键 harness 能力：runtime warning hooks、sanitizer、traceability / local trace producer、context-budget pre-commit、Ruff / whitespace gate、空样本账本和 no-write sample evidence checker；当前 repo 的 REQ/WS、PR、CI 历史、真实 accepted samples、runtime artifacts 和 demo apps 不复制。
- GitHub 侧已具备最小权限 workflow、SHA pinning、固定 Playwright、CODEOWNERS、PR template、Dependabot、dependency review、security evidence、PR conflict / branch hygiene 和 `merge_group`；private Free 下 branch protection / rulesets 仍是 future gates。
- 2026-05-24 / 2026-05-25 harness burn-in 已进入 closeout / split：当前缺口不再是“能不能用”，而是分批 review、future real-event sample monitoring 和 advisory / blocking 升级决策。

## 本阶段关键成果

- 已跑通 `requirements -> implementation -> smoke -> runtime promotion -> status`；当前 CI blocking smoke 只应覆盖 WS-01 / WS-02。
- WS-01 pause/resume 与 reset-best 已作为 `GAP-WORKFLOW-SIMPLE-SKIP` 的 accepted real workflow-task 样本进入 gap evidence ledger；该 gap 达到 2/2 后已记录 keep-advisory 决策，仍不升级 workflow skill 默认策略。
- PR #11 与合并后的 `main` push 已完成首轮 CI burn-in，覆盖 governance、Windows hook runtime、smoke、dependency review、Scorecard、CodeQL artifact 和 SBOM artifact。
- Candidate workflow skills 已有 accepted eval / control samples；本轮 WS-01 简单任务 skip 样本达到 2/2 后仍保持 Candidate。
- AI/Agent security 与 agentic standards 已从说明提升为可校验 evidence / contract；维护细则已下沉到 `$harness-maintenance` references。

## 风险与阻塞

- OPEN-01 已调整为 private GitHub Free 最大边界：GitHub API 对 branch protection / rulesets 返回 plan limit HTTP 403；远端 required checks、review、conversation resolved 和禁止直推 `main` 不能声明已强制，但也不再作为本地代码缺口追打。
- dependency review、Scorecard、CodeQL、SBOM 和 secret scanning advisory 当前仍以 advisory / artifact evidence 为主；private Free 下不作为 required gate。
- runtime stage drift、archive candidate、context budget、source boundary 和 change-triggered followups 继续 warning / review-required；高影响动作矩阵不允许 hooks 自动执行 destructive、externally visible 或 permission-changing 动作。
- Agentic standards 只证明本地 trace / eval / tool-contract 能力；不等于模型质量评测、远端权限审计、OpenAI hosted trace/eval、MCP/A2A 或外部 collector 互通；Ruff 不替代 semantic review。
- Code-shape 主债务已清掉：`check_ai_governance.py`、`bootstrap_harness.py` 与 `check_agent_eval_dataset.py` 均已拆到阈值内。

## 本轮收敛

- 上下文已 stage compression，旧 ADR 开始移入 archive；后续继续避免默认面膨胀。
- Candidate workflow skills 保持 Candidate；升级 always-on 需要更多跨场景样本和单独决策。
- Agentic standards、P0 linter、external crosswalk 与 code-shape 拆分已同步到 checks / registry / index；细则从默认上下文迁入 `$harness-maintenance` reference。
- Agent-run provenance 已按 local-first 边界落地：`agent-run-provenance/v1` 记录 authority、REQ/WS、changed files、tool contracts、validation evidence 和 claim boundaries，不依赖 GitHub plan 升级或 cloud agent task。
- Next Best Work Review 已作为 advisory 机制接入 governance checklist、status 模板和 handoff 草稿，用于完成需求或 checkpoint 后判断计划中的下一项是否仍适合当前阶段；当前不升级为 blocking gate。
- Stage Checkpoint、PreToolUse preflight、Loop / Scope Monitor、Local Trace Summary、Harness Sample Gap Evidence、Candidate Check Burn-in Ledger、future-work contract 和 upgrade-decision gates 已形成 warning-only / advisory closeout 面。
- 5 个 ready-for-upgrade-discussion gap（Source Boundary、Control Matrix Burn-in、Task Profile Audit、Sandbox Honesty、Workflow Simple Skip）均保持 `keep-advisory`；PreToolUse real warning、Loop / Scope real warning、cross-task resume、distinct task class trace、remote interop 和 cascade stop 仍需未来真实样本。
- Bounded tool-output capture 已保留 raw artifact、summary、metadata 与 exit code 行为，并补齐 subprocess stdout pipe 释放，避免全量 unittest 出现未关闭文件 `ResourceWarning`。
- Stopped long session 的 canonical 入口是 [Stage-00 Harness Burn-in Closeout Handoff](../handoffs/active/stage-00-harness-burn-in-closeout.md)；`.codex/runtime/*` 只保留为本地恢复材料，不替代 status / handoff / ADR。
- 本轮新增 capability bootstrap：Stop hook 会并行写入 `runtime-execution-snapshot/v1`；新增 bounded remote interop report、task outcome eval dataset/runner 和 capability summary，不改变 local-first / no-overclaim 边界。

## 下一阶段重点

- 后续优先处理 runtime durability、bounded remote interop 和 task outcome eval 的独立小切片；提交前按 changed-file follow-up、governance 和 context-budget gate 验证，不再把 sample-gap 扩张当主建设面。
- OPEN-01 首轮远端 burn-in 已完成；下一步积累 scheduled / 后续 PR 样本。
- GitHub 继续只作为 CI / PR / security artifact evidence 面；当前没有升级 GitHub plan 或把 Copilot cloud agent task 作为一等 harness surface 的计划。
- 观察 AI/Agent guardrails、agentic control matrix 与 security evidence 真实样本，再决定是否升级 advisory / review-required 层。
- 继续观察 WS-01 / WS-02 browser smoke 在后续 CI 中的 burn-in 结果，失败时区分 Playwright 版本、浏览器安装和应用切片回归。
- 继续观察 Candidate workflow skills 的跨 workstream 样本和 negative 样本；`GAP-WORKFLOW-SIMPLE-SKIP` 已达到 2/2 但 keep-advisory，不主动制造 synthetic evidence。
- 观察 execution snapshot 的 resume 收益、remote interop report 的真实 probe 成本、task outcome eval 的稳定性，再决定是否进一步发展 execution engine、外部 OpenTelemetry/OpenAI exporter、MCP-like tool policy 或更强语义检查。
- 继续压缩 Stage-00 历史：完成型 handoff 归档、status 保持摘要、ADR 旧决策归档或 supersede。
- 继续关注 code-shape 新增 warning。

## 下一步选择判断

- Planned next work：继续处理独立、可验证的 Stage-00 harness 维护小切片。
- Decision：continue
- Reason：Next Best Work Review 本轮只补 advisory 机制和提示面，不改变当前 stage goal、REQ/WS 范围或 blocking policy。
- User confirmation required：no

## 验收判断

- Stage-00 已证明 harness 能跑通 `requirements -> implementation -> smoke -> runtime promotion -> status`。
- 当前尚未完全进入下一阶段，因为长期 skill/PR 样本、后续 CI 样本和 AI/Agent guardrails 真实样本仍需确认；远端强制门禁在 private Free 下已归类为 plan-limited ceiling。
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
