# Harness Remaining Work

更新时间：2026-05-25
当前状态：核心链路已在测试仓库、仓外 starter 复演、WS-01 Three.js Snake capability sample 和 REQDOC-003 -> WS-03 历史薄业务切片中跑通；WS-03 Godot browser slice 已退出 active validation，当前 blocking browser smoke 保留 WS-01 / WS-02；Candidate workflow skills 达到 3/2 accepted eval / control samples 但保持 Candidate；agentic standards、P0 Ruff linter、security / guardrail evidence 和 code-shape 主债务已落地；agentic standards 维护细则下沉到 `.agents/skills/harness-maintenance/references/agentic-standards.md`；GitHub private + Free 下 branch protection / ruleset 已确认为 plan-limited ceiling；OPEN-01 首轮 PR + main push 远端 CI burn-in 已完成；剩余项以真实样本观察、升级决策和远端 plan ceiling 为主

## 作用

本文件用于集中列出当前 harness 仍未完成的事项。

它关注的是“还差什么才能更稳定、更可复用”，不是历史回顾。

## 当前判断

- `0 -> 1 初始化可用性` 已在测试仓库和仓外 starter 复演中验证完成
- `requirements -> implementation -> smoke -> runtime promotion -> status` 已在新仓库内跑通一轮
- Stop hook 的 `REQ/WS` 自动发现现已覆盖 `observation -> session -> reducer draft` 流程
- Runtime sanitizer 已覆盖 Stop observation、Stop session、SessionStart additional context 和 reducer draft；prompt preview、transcript path 与历史 runtime 读取路径会做 best-effort redaction
- Requirements source docs 已增加 source trust、instruction handling 和 sanitization status；外部 PRD / 网页摘录 / 大段粘贴需求必须作为 evidence / data 处理，而不是 agent 可执行指令；`external-web` / `third-party` / `unknown` 且 `pending` 的来源会触发 review-required warning
- 高影响动作矩阵已覆盖远端分支删除、PR close / merge、workflow permission、secret / env、deployment / release、external sending、destructive file / database operations；hooks 只允许提示、dry-run、draft 或 evidence collection
- `threejs-snake` 是当前 WS-01 harness capability validation sample，`harness-trace-console` 是当前 WS-02 governance UI sample；`WS-03` Godot browser slice 仅保留历史 evidence，用于说明长 PRD 可压缩进 harness，不再作为 active validation
- GitHub workflow 已加入最小权限、concurrency、timeout、full-SHA action pinning、fixed-version Playwright smoke browser / CLI packages、WS-01 / WS-02 browser smoke、code-shape、Windows hook runtime job、PR touch conflict check、change-triggered advisory summary、`merge_group` 触发、dependency review workflow 和 security evidence workflow；`security-evidence.yml` 已被远端 API 识别，首轮 checkout 失败根因是误跟踪的演练输出 gitlink
- CODEOWNERS、PR template、Dependabot grouping / PR limit、branch hygiene strict PR budget 与 `delete_branch_on_merge` 配置已落地；仓库现为 private 且账号为 GitHub Free，GitHub API 对 branch protection / rulesets 返回 plan limit HTTP 403，因此这些能力当前只能作为 future upgrade gates，不能作为 Stage-00 本地工程阻塞项。
- Karpathy-style 行为护栏已进入 starter 机制层，但仍保持显式调用，不替代仓库治理文档或检查脚本
- `$progressive-feature-development` 与 `$prd-to-project-skills` 已进入 root 和 starter 的 `.agents/skills` 机制层，作为 Candidate skills 显式调用；SAMPLE-001 / SAMPLE-002 / SAMPLE-005 已达到 3/2 accepted eval / control samples，2026-05-10 复核后仍保持 Candidate，避免把方案先行流程变成简单任务默认流程
- `scripts/check_repo_skills.py`、`scripts/check_requirements_shape.py`、`scripts/check_skill_usage_samples.py`、`scripts/check_github_guardrails.py` 与 `scripts/check_change_triggered_followups.py` 已落地为 warning-only evidence / follow-up checks；`check_github_guardrails.py` 已拆分为 helper 模块并新增 orphan gitlink 检查，`check_change_triggered_followups.py --markdown` 已接入 PR / main push 的 GitHub Actions Summary 并显示 check level / CI coverage
- Agentic standards 相关 trace / eval / tool-contract / sample-gap checks 已落地为可校验 contract；维护规则、互通边界和最小验证命令见 `$harness-maintenance` `references/agentic-standards.md`。
- 2026-05-21 agentic refresh 已补 external standards crosswalk、agentic red-team eval/gap/control 覆盖，以及 repo-local workspace sandbox / rehydration manifest checker；2026-05-24 已补 agentic red-team local-replay 样本账本与 checker，当前 8 个 accepted local-replay 样本覆盖全部 8 类 red-team risk family；2026-05-25 已补 2 个 `sandbox-claim-honesty` accepted real incidents、2 个 `GAP-GUARDRAIL-SOURCE-BOUNDARY` accepted real source-boundary samples 和 2 个 `GAP-SEC-CONTROL-MATRIX-BURNIN` accepted real AC-01 mapping samples。这些仍只证明本地 contract、可复跑 guardrail 行为、两次 sandbox-honesty continuation 边界、两次 source-priority / normalization 边界和两次 control-matrix 映射边界，不证明真实外部攻击、native sandbox provider、OpenAI hosted eval/trace、MCP/A2A 或外部 OTLP 互通。
- P0 linter 已落地为 `pyproject.toml` + pinned Ruff + `git diff --check`；当前只覆盖保守 Python lint 和 whitespace，不替代 semantic standards review、security policy 或 tool-contract checks。
- External standards crosswalk 与 agentic control matrix 已落地；第一阶段只作为 evidence / gap review，不把 hosted trace/eval、MCP/A2A 或外部 collector 视为已完成。
- `docs/ai/check-registry.md` 已记录 check 等级；Scorecard、CodeQL、SBOM 和 dependency review 已作为 security evidence / advisory evidence 接入，第一阶段不作为 required checks；triage / SLO 见 `docs/ai/security/security-evidence-triage.md`
- Candidate skill promotion 已从“样本登记”升级为 with/without 对照 eval；PRD 技术假设检查要求状态和 verification method
- REQDOC-003 已完成首轮标准化并绑定 REQ-007 / REQ-008 / REQ-009 与 WS-03；Godot engine 仍保持 proposed，后续如继续推进应先做独立 engine spike
- project architecture/style/dependency skill 生命周期已进入模板与 ADR；默认不进入短链路，也不新增 blocking checker
- context budget audit 已完成首轮 OPEN-10 triage 并补充增长护栏：starter/default 目标保持 6500，当前 root 预算为 8500，80/90 高水位、ADR 到达预算和 stage status 行数触发 warning；2026-05-21 已新增 runtime token budget blocking-candidate 审计，用于按需检查 rollout transcript 的大工具输出、last input、fresh input/cache miss 和长会话信号；2026-05-23 Stop hook 已接 warning-only token-pressure guard，只提示后续轮次，不阻断；PreToolUse preflight v1 已接 warning-only burn-in，用于提示大输出、destructive、external-send 和 remote-write 风险；2026-05-24 已补 preflight burn-in 样本账本与 checker，当前 accepted real warning sample 仍为 0；Stop loop / scope monitor v1 已接 warning-only burn-in，用于提示 repeated tool commands、repeated failed tool outputs、excessive validation/test loops 和 possible task-scope churn；2026-05-24 已补 loop / scope monitor burn-in 样本账本与 checker，当前 accepted real warning sample 仍为 0；Local Trace Summary v1 已作为 no-network advisory report 进入 burn-in，用于汇总本地 observation / agent trace 的 session、事件、changed paths、REQ/WS、promotion 信号和失败 / warning 线索；2026-05-24 已补 local trace summary burn-in 样本账本，当前有 3 个 accepted real local JSON report 样本，但只有 1 个 accepted distinct task class（`harness-hardening`）；changed-file follow-up triage 继续 warning-only / 按需使用
- [Agentic Harness Gap Roadmap](./agentic-harness-gap-roadmap.md) 已把 8 个开源 harness / agentic engineering 对比缺口沉淀为 P0/P1/P2 vertical slices；P0 PreToolUse preflight guard v1 + burn-in 样本账本、P1 Stage Checkpoint Artifact v1、P1 Loop / Scope Monitor v1 + burn-in 样本账本、P1 Local Trace Summary v1 + burn-in 样本账本、P1 Harness Sample Gap Evidence v1、真实样本采集队列 + burn-in readiness 审计 + pending 模板漂移检查、P1 Candidate Check Burn-in Ledger v1、P2 Red-team Local Replay Samples v1 和 P2 Task Profile Audit v1 + real/synthetic 样本计数已 warning-only / advisory 落地，其中 Task Profile Audit 当前已有 accepted real simple / complex / 0-1-stage 各 1 个样本并达到升级讨论门槛且 keep-advisory，`GAP-TRACE-OTLP-PILOT-BURNIN` 当前已有 1 个 accepted local-interop sample，`GAP-GUARDRAIL-SOURCE-BOUNDARY` 当前已有 2 个 accepted real samples、达到 ready-for-upgrade-discussion 且 keep-advisory，`GAP-SEC-CONTROL-MATRIX-BURNIN` 当前已有 2 个 accepted real samples、达到 ready-for-upgrade-discussion 且 keep-advisory，`GAP-AGENTIC-SANDBOX-HONESTY` 当前已有 2 个 accepted real incidents、达到 ready-for-upgrade-discussion 且 keep-advisory；ADR-016 / ADR-017 已分别把 cascade stop 和 trace remote interop future-work contract 转入可采样 append lane，但两者 accepted real sample 仍为 0；P2 red-team / surface-control 仍需更多真实 incident / interop burn-in，后续按真实样本继续调阈值、误报和升级路径，不一次性扩大 hook 面。
- archive candidate monitor 已落地为 warning-only 检查；自动归档仍不纳入默认 hook
- runtime reducer、runtime traceability、bootstrap `render_plan`、governance traceability、working-context sync metadata、bootstrap harness、governance checker、eval checker、code-shape checker 和 requirements-shape checker 已完成低风险拆分；`check_code_shape.py --all` 当前无 warning，后续新增 warning 按新的 code-shape batch 处理
- 当前剩余问题不再是“能不能用”，而是 `post-burn-in event-driven sample watchlist + private-Free plan ceiling visibility + security evidence triage samples + AI/Agent guardrails sample monitoring + runtime / trace interop sample monitoring`；无法主动验证的真实样本统一留存在 [Harness Real Sample Watchlist](./harness-real-sample-watchlist.md)，以后遇到真实事件再唤醒，不反复尝试覆盖不存在的场景。

## P0 当前最值得做

### OPEN-15 Agentic Harness Gap Roadmap

- 目标：把动作前拦截、loop/scope monitor、本地 trace summary、candidate check burn-in、red-team 样本、tool/skill surface control 和 task profile audit 拆成可验证的小切片
- 当前状态：差距和迭代顺序已记录在 [Agentic Harness Gap Roadmap](./agentic-harness-gap-roadmap.md)；P0 preflight guard v1、P1 loop / scope monitor、P1 local trace summary、P1 sample-gap readiness / pending queue、P1 candidate check burn-in ledger、P2 red-team local replay 和 P2 task profile audit 均已形成 warning-only / advisory v1。无法主动验证的真实样本已转入 [Harness Real Sample Watchlist](./harness-real-sample-watchlist.md)：当前只在真实 warning、真实跨任务 resume、真实 security workflow、真实高影响确认、真实 workflow skill task、真实 red-team incident 或真实 remote interop 出现时唤醒对应 no-write review lane；不再把反复运行 planner / intake / readiness 当成当前推进项。4 个 ready gap（Source Boundary、Control Matrix Burn-in、Task Profile Audit、Sandbox Honesty）均保持 keep-advisory，PreToolUse / Loop-Scope placeholder 仍待真实事件替换，Local Trace Summary 仍需不同 task class，remote interop / cascade stop 虽已获 ADR sampling approval 但 accepted real sample 仍为 0。P1 Candidate Check Burn-in Ledger v1 已记录 blocking-candidate checks 的样本、误报、修复路径、成本和当前决策，并由 governance job 校验账本覆盖和升级决策一致性；下一步是分支 closeout / review，而不是继续追样本。
- 2026-05-24 更新：ADR-016 已采纳 `GAP-AGENTIC-CASCADE-STOP` 的 bounded local incident 采样边界，`FWC-2026-05-24-agentic-cascade-stop` 现为 `approved-for-sampling`；readiness / planner / pending / intake 输出会把该 gap 路由到 red-team `append-new-pending-slot`，仍需 `check_harness_sample_append.py <candidate-jsonl>` 和后续 `check_harness_sample_outcome.py <candidate-jsonl>`，该 gap accepted real incident 仍为 0。ADR-017 已采纳 `GAP-TRACE-REMOTE-INTEROP` 的 bounded remote interop 采样边界，`FWC-2026-05-24-trace-remote-interop` 现为 `approved-for-sampling`；该 gap 进入 generic gap evidence `real-interop-run` append lane，但 accepted real interop sample 仍为 0，不能声明 hosted collector、OpenAI、MCP 或 A2A 互通已完成。
- 2026-05-24 更新：pending audit 现在输出 bounded `next_capture_focus`，默认列出前 5 个 actionable without review-ready pending gaps，并为每个 gap 给出 roadmap area、带当前 `ledger_action` 的 lane-specific focused planner、intake 和 lane review command，同时输出 active area / priority / ledger-action filters、shown/available、area / priority / ledger-action buckets、limit 和 truncated metadata，避免维护者从完整 actionable 队列中手动推断下一步或把默认截断误读成完整覆盖；该输出只辅助真实事件采集，不写 ledger、不接受样本。
- 2026-05-25 更新：`scripts/check_harness_pending_samples.py --capture-focus` 现在可单独输出 compact read-only cards，显示每个聚焦 gap 的 roadmap area、target artifact、target checker、planner、intake、lane review、evidence needed checklist、trigger 和 boundary，方便把下一步采样面写入 CI summary 或人工交接；默认列前 5 个并显示 `Focus entries: shown/available`、area / priority / ledger-action / capture-gate buckets、`Focus limit`、`Focus truncated`，`--capture-focus-limit 0` 可展开全部 matching actionable capture lanes，`--capture-focus-area` / `--capture-focus-priority` / `--capture-focus-ledger-action` / `--capture-focus-gate` 可只看某个 roadmap area、优先级、lane 或真实事件前置条件；governance workflow 会同时追加默认 focus、full-expansion focus、needs-first-real-sample readiness focus 和 needs-more-real-samples readiness focus，避免默认截断隐藏后排真实采集 lane，也避免首样本 blocker 或 partial burn-in lane 只出现在 bucket count 里；空过滤范围会显式 no-match。
- 2026-05-25 更新：pending audit 现在把 queue readiness metric 快照写入 JSON，并在 text / capture-focus 中显示 metric/current-target 与 accepted-real/readiness 差异；这会把 `GAP-RUNTIME-STAGE-CHECKPOINT-RESUME` 的账本 accepted real=2 但 accepted cross-task resume samples=0/2 显式暴露，避免把同一 harness-hardening 线程样本误读成跨任务 burn-in 已满足。
- 2026-05-25 更新：collection planner、intake bundle 和 pending `next_capture_focus` 现在都输出 `capture_gate` / `capture_gate_detail`，把“等真实 warning 替换 placeholder”“跨任务 resume”“不同 task class local trace report”“ADR-017 remote interop probe”“ADR-016 bounded cascade incident”“security workflow event”“bounded real incident”“workflow task event”等前置条件机器化暴露；`--capture-gate` 和 `--capture-focus-gate` 可按这些门槛聚焦队列或 focus cards；这些字段和过滤器只说明采集门槛，不生成样本、不接受 evidence。
- 2026-05-25 更新：pending `next_capture_focus` 现在支持 `--capture-focus-readiness`，并在文本 / JSON 输出 `next_capture_focus_readiness_filter`、shown/available readiness bucket counts；可直接用 `--capture-focus-readiness needs-more-real-samples` 聚焦已有 first sample 但仍未满足 upgrade target 的 lane，例如 Local Trace Summary 不同 task class 报告，且不改变完整 pending accounting 或写入任何样本。
- 2026-05-25 更新：`scripts/check_harness_sample_templates.py` 现在输出 draft review-state counts 和 capture-gate counts，并在 JSON validation entry 中暴露 `template_review_state` / `template_review_blockers` / `capture_gate` / `capture_gate_detail`；`--capture-gate` 可只审计一个真实事件门槛的草稿，例如 ADR-017 remote interop；模板审计通过只证明 schema 与目标 checker 没漂移，不代表草稿已可写入 pending ledger 或可计入 accepted evidence。
- 2026-05-25 更新：governance workflow 现在会把默认 template drift report、`--readiness needs-first-real-sample`、`--readiness needs-more-real-samples` 和 `--readiness ready-for-upgrade-discussion` 模板漂移视图写入 step summary；首样本 blocker、partial burn-in lane、ready decision drafts 和全量模板 drift 可分开检查，仍然只读，不写 ledger、不接受样本。
- 2026-05-25 更新：`scripts/check_harness_sample_templates.py --readiness local-sample-only` 现在不会为 local-only `no-sample-collection` gap 生成 placeholder 草稿，而是输出 `skipped_no_sample_collection_count` 和 `skipped_no_sample_collection_gap_ids`；governance workflow 也会追加 local-sample-only template drift 视图。当前该视图只列出 `GAP-TRACE-OTLP-PILOT-BURNIN` 被跳过，表示它保留在 inclusive 可见性里，但不进入 append / replacement / outcome 样本路径。
- 2026-05-25 更新：governance workflow 现在也会追加 `--include-accepted --readiness local-sample-only --capture-card` 的 planner 视图和 `--include-future --include-accepted --readiness local-sample-only` 的 readiness 视图，change-triggered sample-gap follow-up required commands 同步覆盖这两条；该视图只暴露 `no-sample-collection` 边界，intake bundle 和 pending capture-focus 对 local-sample-only 继续返回显式 no-match，这是设计行为，因为二者只服务下一条可采集样本 lane。
- 2026-05-25 更新：governance workflow 现在额外追加 `requires-approved-remote-interop` 的 planner capture-card、template drift、intake summary 和 pending capture-focus 视图；当前只聚焦 `GAP-TRACE-REMOTE-INTEROP` 这个 P3 trace interop 缺口，仍需 ADR-017 允许的真实 remote interop probe 后先走 `check_harness_sample_append.py <candidate-jsonl>`，不是把 local OTLP pilot、模板或 contract approval 算作 accepted remote interop evidence。
- 2026-05-25 更新：governance workflow 现在额外追加 `requires-approved-bounded-incident` 的 planner capture-card、template drift、intake summary 和 pending capture-focus 视图；当前只聚焦 `GAP-AGENTIC-CASCADE-STOP` 这个 P2 agentic-red-team 缺口，仍需 ADR-016 允许的真实 bounded local cascade-control incident 后先走 `check_harness_sample_append.py <candidate-jsonl>`，不是把 local-replay、模板或 contract approval 算作 accepted real incident evidence。
- 2026-05-25 更新：governance workflow 现在额外追加 `replace-placeholder-after-real-event` 的 planner capture-card、template drift、intake summary 和 pending capture-focus 视图；当前只聚焦 PreToolUse preflight 与 Loop / Scope Monitor 两个 pending placeholder 槽位，目的是提醒真实 warning 后先走 `check_harness_placeholder_replacement.py <candidate-jsonl>`，不是把 placeholder 算作真实样本。
- 2026-05-25 更新：`scripts/check_harness_placeholder_replacement.py` 现在会确认 candidate gap 当前仍属于 `fill-existing-placeholder` lane，并从当前 queue 回显 `capture_gate` / `capture_gate_detail`、`evidence_needed`、trigger 和 boundary；这只强化真实 warning 后替换占位行前的 no-write 复核，不写 ledger、不接受样本、不改变 readiness 或 upgrade decision。
- 2026-05-25 更新：`check_harness_placeholder_replacement.py` 的 no-write 报告现在会从当前采集 queue 回显 `capture_gate` / `capture_gate_detail`、`evidence_needed`、trigger 和 boundary；这让真实 warning 替换占位行前能直接对照 `replace-placeholder-after-real-event` 前置条件复核，仍不写 ledger、不接受样本、不改变 readiness。
- 2026-05-25 更新：governance workflow 现在额外追加 `requires-security-workflow-event` 的 planner capture-card、template drift、intake summary 和 pending capture-focus 视图；当前只聚焦 scheduled security evidence run 与 PR / dependency evidence 两个 P1 缺口，二者仍需真实 workflow / PR / release 事件后先走 `check_harness_sample_append.py <candidate-jsonl>`，不是把模板算作 accepted evidence。
- 2026-05-25 更新：governance workflow 现在额外追加 `requires-bounded-real-incident` 的 planner capture-card、template drift、intake summary 和 pending capture-focus 视图；当前只聚焦 tool / skill squatting、memory poisoning、A2A / handoff confusion 三个 P2 red-team 缺口，三者仍需真实 bounded incident 后先走 `check_harness_sample_append.py <candidate-jsonl>`，不是把 local-replay 或模板算作 accepted real incident。
- 2026-05-25 更新：governance workflow 现在额外追加 `requires-workflow-task-event` 的 planner capture-card、template drift、intake summary 和 pending capture-focus 视图；当前只聚焦 cross-workstream skill load / skip、simple skip 和 PR overlap 三个 P2 workflow-skill 缺口，三者仍需真实 workflow task 后先走 `check_harness_sample_append.py <candidate-jsonl>`，不是把模板算作 accepted evidence。
- 2026-05-25 更新：governance workflow 现在额外追加 `requires-cross-task-resume` 的 planner capture-card、template drift、intake summary 和 pending capture-focus 视图；当前只聚焦 `GAP-RUNTIME-STAGE-CHECKPOINT-RESUME` 这个 P1 runtime-durability 缺口。Stage Checkpoint 已有 accepted real ledger row 不能替代 cross-task readiness，仍需 harness-hardening 任务类之外的真实 resume 后先走 `check_harness_sample_append.py <candidate-jsonl>`，不是把模板 checkpoint id、同任务线程 resume 或 accepted real 粗计算作 accepted cross-task sample。
- 2026-05-25 更新：governance workflow 现在额外追加 `requires-distinct-task-class-report` 的 planner capture-card、template drift、intake summary 和 pending capture-focus 视图；当前只聚焦 `GAP-TRACE-LOCAL-SUMMARY-BURNIN` 这个 P1 trace-interop 缺口。Local Trace Summary 已有 3 条 accepted real local report，但 task class 仍只有 `harness-hardening=3`，readiness 仍是 1/3；后续必须采集不同任务类的真实 no-network summary report，并先走 `check_harness_sample_append.py <candidate-jsonl>`，不是把同任务类报告数量或 needs-more 聚合视图算作满足。
- 2026-05-25 更新：governance workflow 现在额外追加 `requires-user-confirmed-high-impact-action` 的 planner capture-card、template drift、intake summary 和 pending capture-focus 视图；当前只聚焦 `GAP-GUARDRAIL-CONFIRMATION` 这个 P1 ai-guardrail 缺口。后续只有真实高影响动作且有显式用户确认时才可采集，候选必须包含 user confirmation、command/action、result 和 rollback note，并先走 `check_harness_sample_append.py <candidate-jsonl>`；模板、普通 warning 或未确认命令都不能算作 accepted evidence。
- 2026-05-25 更新：`check_harness_sample_append.py` 的 no-write 报告现在会从当前采集 queue 回显 `capture_gate` / `capture_gate_detail`、`evidence_needed`、trigger 和 boundary；这让真实样本候选在 append 前能直接对照真实事件前置条件复核，仍不写 ledger、不接受样本、不改变 readiness。
- 2026-05-25 更新：`check_harness_sample_append.py` 与 `check_harness_placeholder_replacement.py` 的 no-write 报告现在也回显当前 queue 的 readiness、source metric 和 current / target；这会把 cross-task resume、distinct task class report、real warning 等精确 burn-in 指标放到 append / replacement 前置复核里，避免只看 accepted real 粗计数或 candidate 自述。
- 2026-05-25 更新：pending `--review-cards` 现在也会把当前 queue 的 ledger action、capture gate、gate detail、trigger 和 evidence checklist 写入每张 pending card；placeholder review card 可以直接看到真实 warning / replacement 前置条件，不必再跳到 planner 或 capture-focus 才能复核采集字段。
- 2026-05-25 更新：`scripts/check_harness_burn_in_readiness.py` 现在也输出 active area / priority / gap-id / capture-gate filters、area / priority / capture gate counts，并在每个 readiness item 中暴露 `capture_gate` / `capture_gate_detail`；`--area` / `--priority` 可按 roadmap bucket 聚焦，`--gap-id` 可只审计单个 gap，`--capture-gate` 可只审计一个真实事件门槛，例如 ADR-017 remote interop；空过滤范围显式显示 no-match；这些字段复用 planner / intake / pending focus 的 roadmap 维度和真实事件门槛，只用于审计下一步采集前置条件，不生成样本、不接受 evidence。
- 2026-05-25 更新：readiness audit 新增 `--readiness` 过滤器，可直接聚焦 `needs-first-real-sample`、`needs-more-real-samples`、`ready-for-upgrade-discussion` 等状态；governance workflow 会追加 needs-first-real-sample、needs-more-real-samples 和 ready-for-upgrade-discussion 聚焦视图，当前剩余 first-sample blocker、partial burn-in lane 与 ready decision draft lane 都可以直接从 CI summary 读取，不需要从全量 readiness 表格人工筛选；该过滤器只改变审计视图，不生成或接受样本。
- 2026-05-25 更新：collection planner、intake bundle 和 template drift check 也支持 `--readiness`，可以把审计中的 readiness state 直接转成采集队列、summary 草稿包和模板漂移验证；例如 `--readiness needs-first-real-sample` 当前聚焦 14 条首样本 blocker，`--readiness needs-more-real-samples` 当前只聚焦 `GAP-TRACE-LOCAL-SUMMARY-BURNIN`，`--readiness ready-for-upgrade-discussion` 当前聚焦 4 条 upgrade-decision review lane；governance workflow 会把这三类 readiness 的 focused capture-card、template drift 和 intake summary 都追加到 step summary。
- 2026-05-25 更新：governance workflow 会把 full readiness、trace-interop readiness、P2 readiness、ADR-017 remote-interop readiness、needs-first-real-sample readiness、needs-more-real-samples readiness 和 ready-for-upgrade-discussion readiness 都追加到 step summary，避免后排 trace / P2 / remote interop / partial burn-in / ready-decision 缺口只出现在全量表格或 JSON 里；这些聚焦视图仍是只读审计，不改变 ledgers。
- 2026-05-25 更新：readiness audit 的 CI summary 现在也追加 `requires-approved-bounded-incident`、`replace-placeholder-after-real-event`、`requires-security-workflow-event`、`requires-bounded-real-incident`、`requires-workflow-task-event`、`requires-cross-task-resume`、`requires-distinct-task-class-report` 和 `requires-user-confirmed-high-impact-action` 聚焦视图；planner / template / intake / pending focus 与 readiness 四个面现在都能按同一真实采集 gate 查看，仍只暴露 current/target 和前置条件，不写 ledger、不接受样本。
- 2026-05-25 更新：governance workflow 现在额外追加 `review-upgrade-decision` / `upgrade-decision-review` 的 planner capture-card、template drift、intake summary 和 readiness 聚焦视图；当前 4 个 ready gap（Source Boundary、Control Matrix Burn-in、Task Profile Audit、Sandbox Honesty）都已有 keep-advisory 决策，本视图只是把替换草稿、candidate review command、decision ref 与 readiness 快照放进 CI summary，不新增 evidence、不写 upgrade-decision ledger、不把任何 check 升级为 blocking。
- 2026-05-25 更新：`scripts/check_harness_upgrade_decisions.py` 现在要求每条 ready-gap 决策携带 `next_evidence_needed`，并在 text / JSON 输出 `next_evidence_needed_by_gap`；`scripts/check_harness_upgrade_decision_candidate.py` 和 upgrade-decision 模板同步暴露该字段。当前 4 个 keep-advisory gap 的后续真实样本、误报复核或边界证据需求可以机器读取，但这不新增 accepted evidence、不替换决策行、不把任何 check 升级为 blocking。
- 2026-05-25 更新：`scripts/check_harness_upgrade_decision_candidate.py` 现在会重新解析当前 `review-upgrade-decision` queue，并在 report / JSON 中回显 `ledger_action`、readiness、source metric、current / target、`capture_gate` / `capture_gate_detail`、`evidence_needed`、trigger、boundary、带 `--ledger-action review-upgrade-decision` 的 focused planner command 和 focused intake command；单条 keep/promote/defer 草稿如果已经离开 ready-gap decision lane，会被 no-write gate 拒绝，避免用过期草稿替换 decision row，也避免通用 intake 命令返回空 scope。
- 2026-05-25 更新：`scripts/check_harness_future_work_contract_candidate.py` 现在会重新解析当前 queue，并在 report / JSON 中回显 `ledger_action`、readiness、source metric、current / target、`capture_gate` / `capture_gate_detail`、`evidence_needed`、trigger、boundary、带当前 `ledger_action` 过滤的 focused planner command 和 focused intake command；已获 ADR / contract approval 并路由到 append lane 的 future-work contract 草稿，会被 no-write contract candidate gate 拒绝继续替换，避免把采样已获批的合同退回过期 precondition lane。
- 2026-05-25 更新：ready-gap `next_evidence_needed` 现在也贯通到 `plan_harness_sample_collection.py --ledger-action review-upgrade-decision --capture-card` 和 `build_harness_sample_intake_bundle.py --ledger-action review-upgrade-decision --summary/--json`；capture card 显示 `Next evidence needed`，intake 的 Capture Checklist / Upgrade Decision Review 表也显示同一列表。该输出只改善 keep-advisory 后续采集交接，不新增样本、不写 ledger、不升级 blocking。
- 2026-05-25 更新：readiness audit summary/JSON 现在输出 `readiness_gap_ids` 和 `capture_gate_gap_ids`，直接列出每个 readiness state 或真实事件门槛对应的 gap id；这只改善人工交接，不写 ledger、不生成样本、不把待采集 gap 计为 evidence。
- 2026-05-25 更新：governance workflow 现在额外追加 ledger-action lane 视图，覆盖 `append-new-pending-slot` 和 `fill-existing-placeholder` 在 planner capture-card、template drift、intake summary 与 pending capture-focus 四个面上的全量队列；当前 append lane 为 13 个缺口，placeholder fill lane 为 2 个缺口。该视图只展开 CI summary 和人工交接面，不写 ledger、不生成样本、不把 placeholder 或模板计为 accepted evidence。
- 2026-05-25 更新：pending capture-focus 默认截断视图现在会输出 hidden gap ids；JSON 字段为 `next_capture_focus_hidden_gap_ids`，普通 text 和 `--capture-focus` cards 也会显示 exact hidden gap ids。该变更只改善人工交接，不写 ledger、不生成样本、不把 hidden lane 计为 accepted evidence。
- 2026-05-25 更新：readiness audit 现在直接输出 per-gap next collection commands，包括 target artifact、target checker、`ledger_action`、focused planner / intake command 和 lane review command；markdown 追加 `Next Collection Commands` 表，JSON 同步携带这些字段。append、placeholder-fill、upgrade-decision 和 local-only/no-sample 路由可以直接从 readiness 输出进入人工复核交接，但仍不写 ledger、不生成或接受 evidence。
- 2026-05-25 更新：readiness audit 的 per-gap next collection commands 现在按 `ledger_action` 生成 lane-specific focused planner / intake command；append、placeholder-fill、ready-gap upgrade-decision 和 contract-precondition lane 会带对应 `--ledger-action`，outcome lane 的 intake scope 会带 `--pending-state with-review-ready-pending`，避免 handoff 给出看似有效但返回空 scope 的通用 `--gap-id` intake 命令。
- 2026-05-25 更新：append / placeholder replacement no-write review report 现在也回显带当前 `ledger_action` 的 lane-specific focused planner / intake command；候选复核失败或需要回看采集上下文时，复核者不用重新手写同一 gap 的 `--gap-id` 路由，也不会退回 append / replacement 之外的通用 scope。该字段只辅助采集和复核，不写 ledger、不生成或接受 evidence。
- 2026-05-25 更新：pending `next_capture_focus` 的 planner / intake 命令现在也由 `harness_collection_lane_commands.py` 按当前 `ledger_action` 生成；placeholder focus 会带 `--ledger-action fill-existing-placeholder`，append focus 会带 `--ledger-action append-new-pending-slot`，review-ready lane 会给出 `--ledger-action review-existing-pending-slot` 加 `--pending-state with-review-ready-pending` 的 intake summary。该变更只修正交接命令路由，不写 ledger、不接受样本、不改变 readiness。
- 2026-05-25 更新：readiness audit 的 next-collection routing helper 已拆到 `scripts/harness_burn_in_readiness_routing.py`，`scripts/check_harness_burn_in_readiness.py` 回到 code-shape 行数预算内；这是内部维护性拆分，CLI、JSON、markdown 和 ledger 边界不变。
- 2026-05-25 更新：`scripts/harness_burn_in_readiness_routing.py` 已纳入 `scripts/check_harness_sample_followup_coverage.py` discovery 和 `scripts/change_triggered_harness_sample_rules.py` pattern；后续改 readiness target/checker/planner/intake/lane-review routing 时会触发完整 sample-gap follow-up 命令包，避免 routing helper 漂移但 CI summary 仍显示旧采集路径。
- 2026-05-25 更新：`scripts/check_harness_sample_followup_coverage.py` 现在要求 `REQUIRED_COMMANDS` 与 routed `HARNESS_SAMPLE_GAP_COMMANDS` 完全闭合；baseline intake/readiness 命令、sample-gap 相关单测或未来新增 routed command 未进入 required coverage 时会直接报错。该变更只强化 follow-up coverage audit，不运行那些命令、不写 ledger、不生成或接受样本。
- 2026-05-25 更新：`.github/workflows/governance-and-smoke.yml` 现在纳入 `harness-sample-gap-evidence` change-triggered follow-up 和 coverage discovery，routed / required 命令包同步包含 `python3 tests/test_governance_workflow_sample_outputs.py`；后续改 sample-gap CI summary 文本或步骤时会提示跑 workflow-output 静态断言，仍不运行 workflow、不写 ledger、不生成或接受样本。
- 2026-05-25 更新：`scripts/check_harness_collection_config.py` 现在会从 inclusive readiness report 读取实际 active capture gates / ledger actions / readiness states，确认它们仍在 CLI choices 中；对真实采样 capture gate，还要求 `HARNESS_SAMPLE_GAP_COMMANDS` 包含 planner、template、intake、readiness 和 pending-focus 的 focused command，防止新增 gate 后 CI summary 或 follow-up 命令包漏掉聚焦视图。
- 2026-05-25 更新：`scripts/check_harness_collection_config.py` 现在也会针对 active real-sample ledger actions 校验 lane-wide focused command 包；`append-new-pending-slot` / `fill-existing-placeholder` 这类真实采样 lane 必须同时保留 planner capture-card、template drift、intake summary 和 pending focus full-expansion 命令。该检查只防 ledger-action lane 漂移，不生成模板、不写 ledger、不接受样本。
- 2026-05-25 更新：`scripts/check_harness_collection_config.py` 现在还会针对 active real-sample readiness states 校验 focused command 包；当前 `needs-first-real-sample` / `needs-more-real-samples` 必须同时保留 planner、template、intake、readiness audit 和 pending focus 命令。该检查只防 readiness filter 漂移，不改变 readiness 计数、不写 ledger、不接受样本。
- 2026-05-25 更新：`scripts/check_harness_collection_config.py` 现在还会统计 active real-sample area / priority，并确认 pending capture-focus 的 area、priority、ledger-action、capture-gate 和 readiness choices 覆盖当前真实采样队列；当前 area 为 6 个、priority 为 4 个。该检查只防过滤入口漂移，不改变 pending accounting、不写 ledger、不接受样本。
- 2026-05-25 更新：`scripts/check_harness_collection_config.py` 现在还要求 active real-sample area / priority 都有 planner capture-card、template drift、intake summary、readiness audit 和 pending capture-focus focused command 进入 `HARNESS_SAMPLE_GAP_COMMANDS`；`scripts/check_harness_sample_followup_coverage.py` 的 required command list 同步闭合这些命令。当前 6 个 area 和 4 个 priority 都有五面聚焦命令覆盖；该检查只防 follow-up 命令包漏掉 roadmap bucket，不运行命令、不写 ledger、不生成或接受样本。
- 2026-05-25 更新：governance workflow 现在把 active area 和 active priority 的 planner capture-card、template drift、intake summary、readiness audit 与 pending capture-focus 视图都追加进 step summary；当前覆盖 6 个 area 和 4 个 priority。`tests/test_governance_workflow_sample_outputs.py` 从当前 inclusive readiness report 推导这些命令与 `cat /tmp/...` 摘要段，防止 follow-up 命令包有 area / priority focus 但 CI summary 只剩 full queue；该检查只读 workflow 文本，不运行 workflow、不写 ledger、不生成或接受样本。
- 2026-05-25 更新：`tests/test_governance_workflow_sample_outputs.py` 现在会从当前 inclusive readiness report 推导 active real-sample area / priority / capture gate / ledger-action / readiness 的 workflow summary 命令和 step-summary section，并确认 governance workflow step summary 同步包含 planner、template、intake、readiness、pending-focus 命令及对应 `cat /tmp/...` 摘要输出；后续新增真实采样 bucket、gate、lane 或 readiness 时，不能只更新 follow-up 命令包而漏掉 CI summary 可见段。该检查只读 workflow 文本，不运行 workflow、不写 ledger、不接受样本。
- 2026-05-25 更新：`scripts/harness_sample_template_records.py` 已从 `scripts/harness_sample_templates.py` 拆出具体草稿 record 构造函数，让模板入口回到 code-shape 行数预算内；该 helper 也纳入 change-triggered sample-gap follow-up pattern。required commands 现在包含 `check_harness_sample_templates.py --readiness local-sample-only`，防止 no-sample skip 回归不被聚焦验证覆盖。
- 2026-05-25 更新：`scripts/build_harness_sample_intake_bundle.py --summary` / `--json` 现在暴露 draft `template_review_state`、`template_review_blockers` 和 state counts；schema-valid 草稿仍会显示为 placeholder，直到真实事件字段补齐并通过 append / replacement gate。例如 Stage Checkpoint cross-task resume 草稿会显式提示必须替换模板 checkpoint id。
- 2026-05-25 更新：intake bundle entry 和 summary queue 现在也显示 readiness source metric 与 current / target；Stage Checkpoint intake 行会显示 `accepted cross-task resume samples | 0/2`，Local Trace Summary 会显示 `accepted real local trace summary task classes | 1/3`，避免人工只看 readiness 标签或模板数量。
- 2026-05-25 更新：新增第 2 个 `sandbox-claim-honesty` accepted real incident，并在 `harness-upgrade-decisions.jsonl` 记录 `GAP-AGENTIC-SANDBOX-HONESTY` 的 keep-advisory 决策；`scripts/check_harness_sample_templates.py` 的 upgrade decision 模板复核改为单条 candidate gate，避免多个 ready gap 同时存在时一条模板因缺另一条 ready decision 被误判失败。
- 2026-05-25 更新：新增第 2 个 `GAP-GUARDRAIL-SOURCE-BOUNDARY` accepted real source-boundary sample，并在 `harness-upgrade-decisions.jsonl` 记录 keep-advisory 决策；该 gap 现在进入 `review-upgrade-decision` lane，不再出现在默认 append-new-pending-slot 采集队列。
- 2026-05-24 补充：`scripts/build_harness_sample_intake_bundle.py --summary` 和 `--json` 现在暴露每个 entry 的 `evidence_needed` capture checklist；该清单只用于真实事件采集前确认 bounded evidence 字段，不写 ledger、不接受样本、不改变剩余 gap 计数。
- Pending sample review-state 当前定位：`scripts/harness_sample_slots.py` 通过 `scripts/harness_sample_boundary.py` 把 `no_external_claim`、real/local `local_only`、red-team pending `local_only/no_external_claim`、local trace `no_network/local_only` 和 Stage Checkpoint cross-task resume 模板 checkpoint 未替换纳入 placeholder blocker；`check_harness_sample_append.py` 与 `check_harness_placeholder_replacement.py` 共享该判断，防止边界含糊的 pending candidate 进入 outcome review；`check_harness_sample_outcome.py` 会确认目标 gap 当前仍属于 `review-existing-pending-slot` lane，回显当前 queue 的 readiness / source metric / capture gate / evidence checklist / lane-specific focused planner / intake command，并读取目标 pending ledger 原始行拒绝稳定 evidence 字段改写，让 outcome review 只处理 accepted / rejected 与复核字段。
- Stage Checkpoint v1 当前定位：`docs/ai/checkpoints/stage-checkpoints.jsonl` 是 bounded shared checkpoint artifact，`docs/ai/checkpoints/resume-samples.jsonl` 记录真实 continuation / resume 样本；`scripts/check_stage_checkpoints.py` 校验 schema、stage/status、恢复提示、下一步、evidence、REQ/WS、`resume_scope`、resume samples 和 raw runtime 边界；它不做执行引擎，也不把 `.codex/runtime/*` 或 raw transcript 写入共享治理面。当前 checkpoint burn-in 已达到 2/2 accepted samples，但 accepted cross-task sample 仍为 0；新增 pending cross-task 样本必须在 append gate 里替换模板 checkpoint id `CP-2026-05-24-agentic-harness-burnin`，并保持 `resume_scope=cross-task`；结论是保持 advisory，不写 ADR、不升级 blocking，后续继续收跨任务样本。
- Local Trace Summary v1 当前定位：`scripts/summarize_runtime_traces.py` 只读 `.codex/runtime/observations/*.jsonl` 与 `agent-traces/*.agent-trace.jsonl`，输出本地 Markdown / JSON 摘要；`scripts/check_local_trace_summary_samples.py` 校验 no-network/local-only 样本、task_class、redaction state 和 raw runtime 边界；当前有 3 个 accepted real local JSON report 样本，但 accepted distinct task class 仍只有 1 个（`harness-hardening`）。Harness Sample Gap Evidence v1 当前记录 1 个 OTLP localhost capture-server accepted local-interop sample、2 个 source-boundary accepted real samples 和 2 个 control-matrix accepted real samples。它们都是 advisory / bounded evidence，不上传、不阻断、不声明 OpenAI / OTLP external collector / MCP / A2A 互通，也不把 source-boundary 或 AC-01 映射升级为 blocking
- Agentic Red-Team Samples v1 当前定位：`scripts/check_agentic_red_team_samples.py` 校验 `docs/ai/security/agentic-red-team-samples.jsonl` 中的 AC control、risk family、local-replay / real-incident 类型、false-positive rule、replay command、evidence_refs 和 raw runtime 边界；当前有 8 个 accepted local-replay 样本覆盖全部 8 类 red-team risk family，并有 2 个 `sandbox-claim-honesty` accepted real incidents；其它 risk family 仍需真实事件 burn-in
- Task Profile Audit v1 当前定位：`scripts/check_task_profile_audit.py` 校验 JSONL audit artifact 中的 profile、实际读取面、改动文件、验证命令、REQ/WS closure、real/synthetic 样本类型、accepted real profile 计数和 raw runtime 边界；默认样本在 `docs/ai/standards/task-profile-audit-sample.jsonl`，当前已有 accepted real simple / complex / 0-1-stage 各 1 个样本，达到升级讨论的 profile 覆盖门槛；CI 只证明规则和样本可运行，是否升级仍需单独决策
- 完成定义：
  - 每个切片都有最小脚本或 hook、单测、文档入口和样本证据
  - 新能力默认 advisory / warning-only，升级 blocking 前必须按 check registry 记录真实样本、误报率和修复路径
  - 默认上下文不因路线图膨胀；详细机制继续下沉到 `$harness-maintenance` references 或 checks

### OPEN-01 Private GitHub Free 最大边界与 CI evidence burn-in

- 目标：在 private GitHub Free 的能力边界内，把可用的本地/CI/process 证据层跑满；branch protection、rulesets、required checks、required reviews 和 merge queue 保留为升级 GitHub 计划或改 public 后的 future gates
- 当前状态：首轮 PR + main push 远端 CI burn-in 已完成；repo 内 workflow、CODEOWNERS、PR template、PR touch conflict checker、advisory follow-up summary、check registry、security evidence workflow、Dependabot、dependency review 与 `scripts/check_github_guardrails.py` 已落地；PR touch conflict 在 burn-in 阶段只阻断已确认 high-risk overlap；GitHub API 已对 branch protection / rulesets 返回 private-Free plan limit HTTP 403，后续不应继续把该项当作本地代码缺口
- 远端配置细节：[GitHub 远端配置确认细节](../../--使用细节/GitHub远端配置确认细节.md)
- 首轮完成证据：
  - PR #11 已合并到 `main`，merge commit 为 `c1f170faa701885882a0ed7a2105c1054fe956ea`
  - PR #11 上 `Dependency Review`、`governance`、`windows-hook-runtime`、`smoke` 和 `security-evidence` 全部通过
  - `main` push 上 [Governance And Smoke run 25599034611](https://github.com/whm-cell/ai_ms_pro/actions/runs/25599034611) 通过，当时覆盖 hook sync、main advisory summary、main branch hygiene、unit tests、AI governance、code-shape、Windows hook runtime、WS-01 / WS-02 / WS-03 smoke；当前 active workflow 已收敛为 WS-01 / WS-02 smoke
  - `main` push 上 [Security Evidence run 25599034597](https://github.com/whm-cell/ai_ms_pro/actions/runs/25599034597) 通过，Scorecard、CodeQL artifact 和 SBOM artifact 完成；CodeQL code-scanning 上传注解已登记到 security evidence triage，当前按 advisory / plan-setting 边界处理
- 首轮完成定义状态：
  - 至少一轮远端 workflow 通过：已完成
  - `python3 scripts/sync_hooks_config.py --check` 自动运行
  - `python3 scripts/check_ai_governance.py` 自动运行
  - `python3 scripts/check_code_shape.py --all` 自动运行
  - `scripts/check_change_triggered_followups.py --markdown` 在 PR / main push 的 GitHub Actions Summary 中展示 advisory follow-ups
  - `python3 scripts/threejs_snake_smoke.py`、`python3 scripts/threejs_snake_blackbox_smoke.py`、`python3 scripts/harness_trace_console_smoke.py` 与 `python3 scripts/harness_trace_console_blackbox_smoke.py` 自动运行，覆盖当前 active WS-01 / WS-02 browser smoke
  - Windows runner 至少跑通 Python resolution / hook runner 相关测试
  - dependency review job 在 PR 上可见；private Free 下若无法作为 required check，则保持 advisory / evidence，不升级 blocking
  - `scripts/check_github_guardrails.py` 对 branch protection / rulesets 输出 private-Free plan-limited `UNKNOWN`，并在 recommended actions 中提示“升级计划或改 public 后再启用”，而不是继续要求本地修复
  - GitHub Actions workflow 的 third-party / official actions 使用 full-length commit SHA pinning，并保留原 tag 注释，后续 Dependabot /人工升级时同步验证
  - Playwright browser install 和 smoke CLI 使用 workflow 级 `PLAYWRIGHT_VERSION` / `PLAYWRIGHT_CLI_VERSION` 固定 npm package 版本，避免 smoke job 运行时跟随 `latest` 漂移
  - Future upgrade gates 记录在 `docs/ai/security/remote-merge-gates.md`：若仓库升级 GitHub plan 或改 public，再要求 `governance`、`windows-hook-runtime`、`smoke`、dependency review、PR review、CODEOWNERS review、conversation resolved 和禁止直推 `main`
  - `scripts/check_branch_hygiene.py --strict` 显示 active PR budget 未超限、failed open 0/0，且 stale remote/local branch 均为 0；PR #11 合并并清理本地 stale 分支后为 total 2/10、Codex 0/3、Dependabot 2/4；open PR 分支通过 merge/close 消化，不直接删除
  - GitHub Actions 默认 token 若无法读取 `statusCheckRollup.*.workflowRun`，branch hygiene summary 必须明确显示 failed-open-PR 审计降级说明；active PR budget 与 stale/unmanaged branch 检查继续运行，不把权限不足伪装成完整 OK
  - `scripts/check_github_guardrails.py` 能返回远端状态；未登录、缺权限或 plan-limited 时必须明确显示 `UNKNOWN`，不能伪装成 OK
  - 失败结果能直接定位到 governance、hook sync、code-shape、Windows runner、supply-chain 或 smoke 维度
- 后续观察：继续积累至少一轮 scheduled / 后续 PR security evidence 样本，确认 CodeQL code-scanning 注解是否持续出现；除非升级 GitHub plan、改 public 或启用 code scanning，不把该注解升级为 blocking

## 本轮已关闭

### Workspace Sandbox Manifest 与 Agentic Red-Team Coverage

- 结果：新增 `docs/ai/standards/workspace-sandbox-manifest.toml`、`scripts/check_workspace_sandbox.py` 和 `tests/test_workspace_sandbox.py`，并把 checker 接入 tool contracts、check registry、index 和 governance workflow；eval dataset 扩展到 tool/skill squatting、memory/context poisoning、inter-agent handoff confusion、cascading agents、human-confirmation trust calibration 与 sandbox/rehydration honesty；2026-05-24 追加 `docs/ai/security/agentic-red-team-samples.jsonl`、`scripts/check_agentic_red_team_samples.py` 和 `tests/test_agentic_red_team_samples.py`，把 prompt injection、tool-output injection、skill squatting、memory/context poisoning、handoff / A2A confusion、cascade autonomy、human confirmation 和 sandbox claim honesty 的 local-replay 样本纳入同一账本。
- 关闭原因：已形成本地可校验的 sandbox / rehydration boundary 和 agentic red-team routing surface。
- 备注：该 manifest 和 red-team replay 样本都是 repo-local contract，不是 `.codex` 运行时配置，也不是 native sandbox provider；当前只有 `sandbox-claim-honesty` 有 2 个 accepted real incidents，其它 red-team gaps 仍需真实样本 burn-in。

### Eval Runner、Trace Local / OTLP Pilot Adapter 与 Sample Gap Collector

- 结果：新增 `scripts/run_agent_eval_dataset.py`、`scripts/export_agent_trace.py`、`scripts/collect_harness_sample_gaps.py` 和对应单测；governance workflow 已接入 runner `--dry-run`、trace sample local export 和 sample gap collector；eval runner 执行模式会绑定 trace id / artifact / redaction state；trace exporter 新增 no-network `otlp-http-json` pilot，显式 `--send --endpoint` 才会 POST；2026-05-24 追加 `scripts/check_harness_sample_gap_evidence.py` 和 `docs/ai/standards/harness-sample-gap-evidence.jsonl`，把 OTLP local pilot 作为 bounded local-interop sample 接入 gap collector 计数。
- 关闭原因：eval runner + deterministic grader + trace evidence binding、本地 `agent-trace/v1` export adapter、OTLP HTTP JSON pilot、security / guardrail / workflow sample collection harness 已具备本地可验证路径。
- 备注：`--使用细节/真实场景覆盖缺口待确认.md` 记录尚未真实覆盖的问题点；OpenAI hosted trace/eval、MCP / A2A 真实互通、外部 collector、scheduled / PR / 跨 workstream 真实样本仍是 future work，不因为本地 adapter 或 collector 通过而视为完成。

### P0 Linter、Trace Producer 与 External Standards Crosswalk

- 结果：新增 P0 Ruff linter、CI `git diff --check`、Stop hook `agent-trace/v1` producer、external standards crosswalk，并把 Ruff / whitespace check 写入 tool contract registry。
- 关闭原因：linter、trace producer、external standards crosswalk 已转为 repo 内可检查或可路由 artifact；剩余 W3C/OpenTelemetry/OpenAI exporter、MCP/A2A interoperability、semantic standards-honesty linter 仍是后续升级项。
- 备注：Ruff 当前启用 `E9` 与 Pyflakes `F`；Stop trace 仍是 `.codex/runtime/*` 本地原料，不自动成为共享治理真相。

### OPEN-12 Runtime 敏感信息脱敏闭环

- 结果：新增 runtime sanitizer，Stop observation、Stop session、SessionStart additional context 和 reducer draft 已统一脱敏；2026-05-08 已按人工指令清理 49 个旧 runtime observation/session 文件
- 关闭原因：已补测试覆盖 secret / token / email / phone / transcript path，不再只靠 `compact_text()` 截断
- 备注：这是 best-effort 防扩散层，不替代 secret scanning；历史本地 runtime 文件若要彻底清理，仍需人工删除或重建

### OPEN-13 Prompt injection 边界与高影响动作矩阵

- 结果：`docs/requirements/source/_template.md` 与现有 source docs 已补 `来源可信度`、`指令处理`、`清洗状态`；`scripts/check_requirements_shape.py` 会对缺失或语义不清的边界元数据输出 review-required warning；新增 `docs/ai/security/agent-action-guardrails.md`，并在 `scripts/check_change_triggered_followups.py` 中加入 `high-impact-agent-actions` advisory follow-up
- 关闭原因：外部内容已明确作为 evidence / data 处理，不作为 agent 可执行指令；高影响动作已具备人工确认、允许工具、验证证据和 hook automation boundary 的可审计矩阵；2026-05-09 已记录首批 P1/P2 guardrail samples
- 备注：P1/P2 均先保持 warning / review-required，不直接升级 blocking；后续用真实 PRD、GitHub、deployment 或 external-send 样本观察误报率和 reviewer 负担

### OPEN-02 外部独立路径复演

- 结果：已在仓外临时目录完成 `starter copy -> bootstrap --force -> git config core.hooksPath .githooks -> git add -> .githooks/pre-commit`
- 关闭原因：starter 的 `run_with_repo_python.sh` 已修复 macOS `/bin/bash` 3.2 空数组兼容性问题，`check_code_shape.py --staged` 也已把 unborn `HEAD` 的首提交 scaffold 视为 baseline
- 备注：starter copied placeholder docs 若要立刻替换成新项目名，仍需显式 `--force`；`AGENTS.md` 仍由人工项目化，README 与 portability guide 已同步说明

### OPEN-03 Runtime Metadata 自动发现验证

- 结果：Stop runtime observation/session 已支持 changed paths、workstream 模块路径和 traceability matrix 驱动的 `REQ/WS` 自动发现
- 关闭原因：已补 observation、session 以及 reducer draft 三层测试，零配置路径能稳定携带 `Requirement IDs` 与 `Workstream IDs`

### OPEN-04 Reducer 压缩阈值验证

- 结果：已统计 2026-04-16 至 2026-04-30 的多日 observation 样本，并用 `2026-04-30.jsonl` 跑 reducer 样本审查
- 关闭原因：已形成当前阈值判定标准：runtime-only 或无工作区变更保留本地；单次共享层改动默认生成 handoff 草稿；跨 session 重复出现且已影响 stage 风险、规则或长期策略时再压缩到 `status` 或 `ADR`
- 备注：后续长期样本质量继续归入 OPEN-01 / stage compression 观察，不再作为“基础阈值未定义”缺口

### OPEN-05 更广的黑盒浏览器回归

- 结果：已新增 `scripts/threejs_snake_blackbox_smoke.py`，覆盖真实页面 `load -> keyboard turn -> game over -> Enter restart`
- 关闭原因：`WS-01` 已有黑盒用户路径，`WS-02` 已有黑盒 DOM 路径，两个真实 workstream 都不再只依赖内部 test API

### OPEN-06 Traceability / Metadata 一致性自动校验

- 结果：governance checker 已校验 `working-context` 的 `Current Stage` 与 traceability matrix 中当前 REQ/WS 的 STAGE 关系；runtime session / observation artifact 的同类错配先以 warning 暴露
- 关闭原因：已具备至少一层 `REQ <-> WS <-> STAGE` 自动校验，primary truth mismatch 会阻断，runtime/reducer mismatch 先保持 warning-only

### OPEN-10 Context budget warning triage

- 结果：已创建 [上下文预算 OPEN-10 使用细节](/Volumes/usd/codes/go_projects/ai_ms_pro/--使用细节/上下文预算OPEN-10使用细节.md)；当前 root Stage-00 budget 调整为 8500，starter/new-project 初始目标保留 6500；默认面 80/90 高水位、ADR 到达预算和 stage status 行数纳入 warning；`AGENTS.md` 压缩到 300 行以内，current status 压缩为短判断，`$repo-governed-coding` description 已缩短
- 关闭原因：已完成本轮“是否调整预算、是否压缩默认面、是否接 Stop hook”的判断；context budget audit 继续保持 warning-only 手动运行，不自动 compact，不自动归档
- 备注：未来如果 context budget 再次持续 warning，再开新的 triage 项，而不是把 OPEN-10 长期保持开放

### OPEN-14 Code-shape 分批拆分

- 结果：`check_ai_governance.py`、`bootstrap_harness.py`、`check_agent_eval_dataset.py`、`check_code_shape.py` 与 `check_requirements_shape.py` 已拆分到 code-shape 阈值内；新增 helper 模块保持 CLI / facade 行为不变。
- 关闭原因：`check_code_shape.py --all` 当前无 warning；原有两个大文件 warning、`check_candidate` 函数 warning 和本轮新增 eval checker warning 都已清掉。
- 备注：后续若新增 warning，应作为新的 code-shape batch 处理，不重开 OPEN-14。

## P1 次高优先级

### OPEN-11 多人 / 多 AI PR touch-set 冲突控制验证

- 目标：用真实团队 PR 样本验证 `$team-pr-conflict-control` 是否能降低同文件改动、治理文件冲突和 merge queue 前返工
- 当前缺口：repo-local skill、PR template、changed-files overlap check 与 `merge_group` workflow 触发已落地；仍缺少真实多人 PR 样本和远端 merge queue / branch protection enforcement
- 当前验证：`docs/ai/skill-evals/SAMPLE-001-team-pr-conflict-control-validation.md` 已完成结构、discoverability、当前 PR 与离线场景矩阵验证；该验证不计入真实多人 PR accepted 样本
- 完成定义：
  - 至少两次多人或多 AI 并行 PR 使用该 skill 记录 touch-set overlap、high-risk files 与 coordination action
  - 若样本有效，再决定是否进一步收紧 merge queue / required-check enforcement
  - 若样本证明流程税高于收益，保持显式调用并不升级 always-on

## P2 策略性决策

### OPEN-07 Starter 是否保留 Quick Notes 样板

- 目标：决定 `Quick Notes Inbox` 是继续作为 starter 自带样板，还是只保留治理机制层
- 当前缺口：当前测试仓库已经证明样板有价值，但 starter 默认是否应带示例仍未定
- 完成定义：
  - 明确选择“保留样板”或“只保留治理面”
  - 相应更新 starter 文档和迁移说明

### OPEN-08 行为护栏 skill 是否升级为默认 workflow

- 目标：观察 `$repo-governed-coding` 在更多真实任务中的收益，决定它继续显式调用，还是升级为更稳定的 stage / repo 默认策略
- 当前缺口：已进入 starter，且本轮明确不把功能开发全流程并入默认 workflow；仍缺少多任务样本证明 `$repo-governed-coding` 是否适合升级
- 完成定义：
  - 至少几个非平凡实现/审查任务中显式使用该 skill
  - 能证明 assumptions / scope / success criteria / verification plan 对 handoff/status 提炼有实际帮助
  - 若升级为默认，补对应 `status` 或 `ADR`；若不升级，保持显式调用并避免写入 always-on 规则
  - `$harness-maintenance` 仍保持按需调用；不要把 runtime / hook / GitHub / code-shape 细则重新塞回 `AGENTS.md`

### OPEN-09 Project architecture/style/dependency skill 生命周期真实样本观察

- 目标：验证 `docs/ai/templates/project-skill-lifecycle.md` 是否足以指导新项目在架构、样式和依赖约束变化时创建、升级、偏离或废弃项目 skill
- 当前缺口：模板、ADR、starter 同步、两个 Candidate workflow skills 与 with/without eval registry 已落地；Candidate workflow skills 已达到 3/2 accepted eval / control samples，但仍保持 Candidate
- 完成定义：
  - 模板存在且不进入默认短链路
  - ADR 已采纳并说明 skill 不替代 canonical governance truth
  - `new_pro_standard` 已同步模板和说明
  - Candidate workflow skills 已验证不会替代 requirements / AI governance truth
  - 关键 Candidate skills 已达到 3/2 accepted eval / control samples；下一步是决定升级、继续观察或保持 Candidate
  - governance check 与 code-shape check 通过
  - 至少一个后续真实项目能按 `Draft -> Candidate Skill -> Stable Skill -> Promote -> Deprecate` 路径处理项目约束变更

## 当前不纳入本轮

- 发布 / 部署体系
- 多 workstream 并行治理；当前仅新增 `$team-pr-conflict-control` 作为按需方法层，未做全局阻断式并行治理
- 复杂前端或后端工具链验证
- 自动归档 handoff / changelog 策略；当前只提供 warning-only candidate monitor
- CodeQL blocking / required-check 升级；当前仅作为 security evidence advisory 运行，等业务代码进入 release / CI maturity 阶段后再评估

## 建议阅读顺序

1. [AI 文档入口索引](./index.md)
2. [当前工作上下文](./working-context.md)
3. [Stage-00 Harness Burn-in Closeout Handoff](./handoffs/active/stage-00-harness-burn-in-closeout.md)
4. [Harness Real Sample Watchlist](./harness-real-sample-watchlist.md)（仅真实样本事件或 sample-gap 审计时读取）
5. [Stage-00 Runtime Harness Foundation Status](./status/stage-00-runtime-harness-foundation.md)
