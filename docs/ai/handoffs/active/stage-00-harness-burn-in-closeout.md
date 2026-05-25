# Stage-00 Harness Burn-in Closeout Handoff

更新时间：2026-05-25
阶段：stage-00
任务：harness-burn-in-closeout
状态：待接力

## 需求与工作流标识

- Requirement IDs：未绑定
- Workstream IDs：未绑定
- 说明：本 handoff 是 harness control-plane 收尾，不把 burn-in 工作绑定成游戏需求。WS-01 / WS-03 / WS-04 只作为历史 validation sample 或产品边界背景，精确要求仍以 `docs/requirements/*` 为准。

## 本任务目标

- 将已停止的 2026-05-24 / 2026-05-25 长 session 从 `.codex/runtime/*` 恢复材料提升为 canonical closeout 结论。
- 明确当前不是继续追加 harness 功能或强行制造真实样本，而是做分批 review、校验、提交和 PR 收口。
- 给下一位 Agent 一个可执行的拆分顺序，避免把 hooks、CI、apps、runtime artifacts 和会计文档混成一个不可审查的大变更。

## 已完成内容

- Runtime / Governance / Verification harness 主链路已可用，Stage-00 仍保持进行中但不再缺“能否使用”的证明。
- Warning-only PreToolUse preflight、Stop runtime token pressure、Stop loop / scope monitor、本地 trace summary、Stage checkpoint、sample-gap readiness、pending sample queue、upgrade decision、future-work contract 和 candidate check burn-in ledger 已进入 repo-local 可校验面。
- `GAP-GUARDRAIL-SOURCE-BOUNDARY`、`GAP-SEC-CONTROL-MATRIX-BURNIN`、`GAP-WORKFLOW-TASK-PROFILE-AUDIT`、`GAP-AGENTIC-SANDBOX-HONESTY` 已达到 ready-for-upgrade-discussion，并都有 bounded `keep-advisory` 决策。
- `GAP-TRACE-REMOTE-INTEROP` 与 `GAP-AGENTIC-CASCADE-STOP` 已经由 ADR-017 / ADR-016 批准进入 bounded sampling path，但 accepted real sample 仍为 0。
- WS-03 Godot browser slice 已退出 active validation；当前 repo-native browser capability validation 回到 WS-01 / WS-02 / Three.js smoke 边界。

## 修改文件

- Closeout / accounting docs：`docs/ai/working-context.md`、`docs/ai/index.md`、`docs/ai/status/stage-00-runtime-harness-foundation.md`、`docs/ai/harness-open-items.md`、`docs/ai/check-registry.md`、`docs/ai/changelog/*`
- Runtime hook controls：`.codex/hooks.json`、`.codex/hooks/*.py`、`.codex/harness.toml`、`.agents/skills/harness-maintenance/references/runtime-token-budget.md`
- Burn-in / sample machinery：`docs/ai/agentic-harness-gap-roadmap.md`、`docs/ai/check-burn-in-ledger.md`、`docs/ai/standards/*.jsonl`、`scripts/check_harness_*`、`scripts/*burn_in*`、`tests/test_harness_*`
- CI / verification expansion：`.github/workflows/governance-and-smoke.yml`、`scripts/change_triggered_followup_rules.py`、`scripts/check_code_shape.py`、`scripts/check_requirements_shape.py`
- Validation boundary change：deleted `apps/godot-platformer-slice/*` and `scripts/godot_platformer_slice_smoke.py`; added `apps/threejs-snake/*` and Three.js smoke / contract scripts
- Do not stage actual `.codex/runtime/sessions/*`, `.codex/runtime/observations/*`, or raw tool output artifacts as canonical truth.

## 关键实现决策

- Runtime files are recovery inputs only. Stable conclusions must land in handoff, status, ADR, plan, requirements, changelog, or check outputs before they are treated as shared project memory.
- `2/2 accepted` sample count opens upgrade discussion only. It does not promote advisory checks to blocking without a separate decision.
- Placeholder, template, synthetic, local-only, approved contract, or no-write candidate output is not accepted real evidence.
- Local no-network trace / local interop evidence does not prove remote collector, hosted OpenAI trace/eval, MCP/A2A, external OTLP, native sandbox, or GitHub remote enforcement.
- GitHub private Free branch protection / rulesets remain plan-limited `UNKNOWN`; do not claim required checks, review, conversation resolution, or main push protection are remotely enforced.

## 行为护栏摘要

- Assumptions：当前 session 已停止；下一步目标是 closeout and split, not more feature discovery.
- Scope Boundary：不要继续扩 hooks、CI、sample collectors、apps 或 requirements；不要为了满足样本计数制造 synthetic evidence。
- Success Criteria：新增 canonical handoff；working-context / index 指到 handoff；closeout checks 通过或只剩已知 warnings；分批 review 顺序明确。
- Verification：当前 closeout 可以用 governance / context / code-shape / requirements / sample-readiness / upgrade-decision / future-contract / unittest / ruff / diff-check 组合验证。Three.js browser smoke 可留到 PR closeout 或 CI 跑。

## 当前证据状态

- Burn-in readiness：4 个 ready-for-upgrade-discussion gap 已有 keep-advisory 决策；其余主要是 future real-event sample lane。
- Pending sample audit：仍有 2 个 placeholder pending rows，分别是 `GAP-GUARDRAIL-PREFLIGHT-WARNING` 和 `GAP-RUNTIME-LOOP-SCOPE-WARNING`，accepted real warning sample 都是 0。
- Stage Checkpoint：same-task accepted samples 已满足，但 cross-task resume accepted samples 仍是 0。
- Local Trace Summary：已有 3 个 accepted real local reports，但 distinct task class 仍是 1/3。
- Remote interop / cascade stop：ADR 已允许采样，accepted real sample 仍是 0。
- Candidate checks：`check_code_shape.py` 与 `check_tool_contracts.py` 达到 2/2 后仍保持 keep-candidate，需要更多非 harness / high-impact tool 样本再复核。
- 无法主动验证的真实样本已转入 `docs/ai/harness-real-sample-watchlist.md`；后续只在真实事件发生时唤醒，不再反复运行 coverage / planner / intake 试图覆盖。

## 已验证有效的路线

- 用 `check_harness_burn_in_readiness.py`、`check_harness_pending_samples.py`、`check_harness_upgrade_decisions.py`、`check_harness_future_work_contracts.py` 作为 sample / readiness / decision 的权威 closeout 口径。
- 用 no-write append / replacement / outcome / upgrade-decision candidate gates 审核未来真实事件样本，先复核再改 JSONL。
- 第一批只提交 closeout / accounting docs，后续再分别审 runtime hook controls、sample ledger machinery、CI expansion、validation boundary switch、ADR/security boundaries。

## 已验证无效的路线

- 继续让同一个长 session 追完所有真实样本；这些样本依赖未来真实事件，应进入 watchlist，不应成为当前 closeout blocker。
- 把 `.codex/runtime/sessions/*` 的 placeholders、changed-path 推断或 REQ/WS 自动猜测直接当 canonical provenance。
- 把 local-only / no-network / synthetic / template evidence 当成远端互通、hosted trace、native sandbox 或 blocking promotion。
- 把 WS-03 Godot browser slice 当成当前 active validation。

## 尚未尝试但建议的路线

- 按以下顺序拆分 review / commit：
  1. closeout / accounting docs only
  2. runtime token / loop / preflight hook controls
  3. burn-in / sample ledger machinery
  4. CI / verification surface expansion
  5. WS-03 removal / WS-01 Three.js validation boundary
  6. ADR / security / remote interop boundaries
- 先决定是否压缩 Stage-00 status 和 active handoff，再归档完成型 handoff，避免 default context 继续增长。
- 在 PR closeout 或 CI 中补跑 browser-level Three.js smoke；本地 static contract 已足够支撑 doc closeout。

## 当前未完成项

- 分支 dirty worktree 很大，仍需按上面 6 批 review / stage / commit；不要一次性合并。
- `docs/ai/status/stage-00-runtime-harness-foundation.md` 仍需要保持摘要化，避免把 5/24-5/25 全量 changelog 堆回默认面。
- Context budget 接近 warning line，ADR count 已超过预算，需要后续归档 / supersede / 压缩。
- AI governance 仍会提示 runtime session / observation 带旧 STAGE-00 / WS-01 / WS-03 metadata；这是 runtime recovery warning，不是当前 stage truth。
- 未来真实样本 lane 仍未完成，但已留存在 `docs/ai/harness-real-sample-watchlist.md`：real preflight warning、real loop/scope warning、cross-task resume、distinct task class local trace、remote interop、cascade stop、安全工作流、真实高影响动作确认。

## 已知风险与注意事项

- `.github/workflows/governance-and-smoke.yml` 变更面大，必须单独 review。
- `.codex/config.toml` 有一行移除，需要确认是否和 hook behavior 同批。
- `docs/requirements/index.md` 日期早于 2026-05-25 docs，需要确认是否只是未触发要求更新。
- `--使用细节/新项目初始化约束提示词.md` 是 companion guidance，不应混入第一批 closeout unless explicitly required.
- Do not stage actual runtime recovery artifacts; repository history should carry canonical summaries and placeholders only.

## 下一位 Agent 的第一步动作

- 先读 `docs/ai/index.md -> docs/ai/working-context.md -> this handoff -> docs/ai/harness-open-items.md`，然后从 closeout / accounting docs only 批次开始 review and stage。

## 建议同步更新

- 更新 `docs/ai/working-context.md` 的 Active Handoff Sources 和当前活跃队列。
- 更新 `docs/ai/index.md` 当前锚点，明确本 handoff 是 stopped burn-in session 的 canonical closeout 入口。
- 对 `docs/ai/status/stage-00-runtime-harness-foundation.md` 做摘要同步，不粘贴完整 runtime transcript 或全量 changelog。
