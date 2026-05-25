# Changelog: Harness Sample Gap Evidence

更新时间：2026-05-24
阶段或版本：stage-00 / stage-01 harness hardening
状态：已确认

## 新增功能

- 新增 `docs/ai/standards/harness-sample-gap-evidence.md` 与 `harness-sample-gap-evidence.jsonl`，作为 roadmap gap 的通用 bounded evidence intake。
- 新增 `scripts/check_harness_sample_gap_evidence.py` 与 `tests/test_harness_sample_gap_evidence.py`，校验 source type、outcome、本地/外部声明边界、OTLP local pilot 约束、evidence refs 和 raw runtime 边界。
- 新增 `scripts/plan_harness_sample_collection.py` 与 `tests/test_plan_harness_sample_collection.py`，把当前 gap evidence 转成下一批真实样本采集队列。
- `plan_harness_sample_collection.py` 支持 `--gap-id <GAP-ID> --capture-card`，用于真实事件发生时展开单个 gap 的采集卡。
- `plan_harness_sample_collection.py` 的队列、capture card 和 JSON report 现在带 target checker command，真实事件采集后可直接进入目标 checker 复核。
- `plan_harness_sample_collection.py` 的队列、capture card 和 JSON report 现在也带 pending slot status、ledger refs 与 review blockers，placeholder pending 不再只作为隐藏过滤条件。
- `plan_harness_sample_collection.py` 支持 `--gap-id <GAP-ID> --sample-template`，只在 stdout 输出 pending JSONL 草稿，辅助真实事件采集后人工补全。
- 新增 `scripts/check_harness_sample_templates.py` 与 `tests/test_harness_sample_templates.py`，把 planner 生成的 pending 模板逐条交给目标 ledger checker，防止 schema / source type 漂移。
- `scripts/change_triggered_followup_rules.py` 与 `scripts/change_triggered_harness_sample_rules.py` 已把模板生成器、模板漂移 checker、collector、collection lane routing、pending queue state、collection config、collection renderer、placeholder replacement gate、pending append gate、outcome review gate、intake renderer 和 follow-up coverage audit 纳入 `harness-sample-gap-evidence` follow-up，后续改这些控制面会提示运行 sample-gap queue / bundle / pending / replacement / append / outcome / coverage 复核。
- 新增 `scripts/check_harness_sample_followup_coverage.py` 与 `tests/test_harness_sample_followup_coverage.py`，确定性审计 sample-gap control-plane docs / scripts / tests 是否都会触发 `harness-sample-gap-evidence` follow-up，并确认 queue、pending、replacement、append、outcome、future-work contract 和 coverage audit 命令仍在建议命令包内。
- `governance-and-smoke` 现在运行 sample follow-up coverage audit，写出 markdown + JSON，并把 coverage audit 追加到 GitHub step summary。
- 新增 `scripts/check_warning_sample_code_alignment.py` 与 `tests/test_warning_sample_code_alignment.py`，校验 PreToolUse / Stop loop hook emitted finding codes、导出常量、样本 checker enums 和 Stop recommendation mapping 是否对齐，防止 warning 输出的 code 无法进入 bounded burn-in 样本。
- `governance-and-smoke` 现在运行 warning sample code alignment check；PreToolUse / loop-scope changed-file follow-up 也会提示运行该 checker。
- 新增 `scripts/check_harness_collection_config.py` 与 `tests/test_harness_collection_config.py`，校验 gap catalog、priority、trigger、target ledger、future-work contract target 和 review command routing 是否对齐。
- 移除 `GAP-AGENTIC-CASCADE-STOP` 在 dedicated sample target map 中的残留 future-work 路由；该 gap 继续走 `harness-future-work-contracts.jsonl`，未获 ADR / contract approval 前不采样。
- 将 `collect_harness_sample_gaps.py` 接入通用 gap evidence ledger，让未专用化 gap 也能显示 ledger count。
- 专用 ledger 的新 pending 模板现在也显式携带 `gap_id`，slot audit 会校验它和 ledger 默认归属一致；既有缺省 `gap_id` 的旧行继续兼容。
- pending slot audit / intake bundle 现在会显示 placeholder 行的 `review_blockers`，说明真实事件采集后还需要补哪些字段才能进入复核。
- pending review cards 支持 `--gap-id <GAP-ID>` 和 `--review-state review-ready` 聚焦单个 gap 或只列可复核 pending 行。
- collection planner 现在支持 `--priority P0|P1|P2|P3` 聚焦采集 lane；template drift checker 和 intake bundle 支持 `--area` / `--priority` / `--pending-state` 聚焦同一批草稿，方便只复核某个 area 或优先级。
- collection planner 和 intake bundle 现在输出 `ledger_action`，区分 `fill-existing-placeholder`、`append-new-pending-slot`、`review-existing-pending-slot`、`inspect-mixed-pending-slots`、`define-contract-precondition` 和 `no-sample-collection`，避免真实事件采集时重复追加已有 placeholder 或把 local-only evidence 误导到 append lane。
- `fill-existing-placeholder` 的 sample template 现在复用已有 pending placeholder 的 sample id，并在 intake bundle 正文标记 replace / do-not-append 写入模式；如果误把替换草稿追加成新行，重复 id checker 会阻止它进入账本。
- 新增 `scripts/check_harness_placeholder_replacement.py` 与 `tests/test_harness_placeholder_replacement.py`，用于在替换 placeholder 行之前只读校验候选 JSON / JSONL：必须匹配已有 pending placeholder id、保持 `outcome=pending`、通过目标 checker，并达到 review-ready；该脚本不写 ledger、不接受样本。
- 新增 `scripts/check_harness_sample_append.py` 与 `tests/test_harness_sample_append.py`，用于在追加新的 pending 样本行之前只读校验候选 JSON / JSONL：gap 必须仍属于 `append-new-pending-slot` lane、sample id 不得重复、保持 `outcome=pending`、通过目标 checker，并达到 review-ready；该脚本不写 ledger、不接受样本。
- 新增 `scripts/check_harness_sample_outcome.py` 与 `tests/test_harness_sample_outcome.py`，用于在 pending 样本行改成 `accepted` 或 `rejected` 前只读校验候选 JSON / JSONL：必须匹配已有 review-ready pending row、保持 schema / gap / source_type 对齐、通过目标 checker，并拒绝直接把 placeholder pending 改成 accepted；该脚本不写 ledger、不接受样本，只报告 `burn_in_counted`。
- replacement / append no-write review 通过时，现在会在 JSON/text report 中返回下一步 `check_harness_sample_outcome.py <candidate-jsonl>`；这保证“替换或追加 pending row”和“把 outcome 改成 accepted / rejected”仍是两个独立复核步骤。
- collection planner、template drift checker 和 intake bundle 现在支持 `--ledger-action <ACTION>` 聚焦同一类账本处理 lane，例如只看需要填充已有 placeholder 的真实事件。
- collection planner 的静态采集优先级、target artifact 和 trigger 文案拆到 `scripts/harness_sample_collection_config.py`，保持主 planner 小一些并继续通过原模块导出既有常量。
- collection planner 的 markdown / JSON / capture-card 渲染拆到 `scripts/harness_sample_collection_render.py`，保持 planner 低于 code-shape 行数阈值，并纳入 sample-gap follow-up 覆盖。
- future-work contract target 现在接入共享 review-command routing，collection planner 的 `define-contract-precondition` capture card 不再显示 `unknown`，而是指向 `scripts/check_harness_future_work_contracts.py`。
- pending slot audit 现在输出 queued / actionable ledger action counts 和 gap lists，让 `check_harness_pending_samples.py --json` 也能直接显示哪些 gap 应填 placeholder、哪些应追加 pending row。
- pending slot audit 现在输出 `next_collection_lane_commands`，把 `fill-existing-placeholder`、`append-new-pending-slot`、`review-existing-pending-slot` 和 future-work `define-contract-precondition` lane 直接映射到下一步 planner / intake / review / contract checker 命令，仍然只做 stdout 路由，不写 ledger。
- local-only accepted gap 现在显示为 `no-sample-collection`，保留在 inclusive queue / pending audit 统计中，但不会产生下一步采样命令或进入 append-new-pending-slot lane。
- `fill-existing-placeholder` 的 next collection lane 和 placeholder review cards 现在会显示 `check_harness_placeholder_replacement.py <candidate-jsonl>`，真实事件补全后可先跑 no-write replacement review，再人工替换 ledger 行。
- sample intake bundle 的 `fill-existing-placeholder` text / summary / JSON 输出现在也显示 `check_harness_placeholder_replacement.py <candidate-jsonl>`，确保真实事件补全后从 bundle 入口也先经过 no-write replacement review。
- sample intake bundle 的 `append-new-pending-slot` text / summary / JSON 输出现在显示 `check_harness_sample_append.py <candidate-jsonl>`，确保新增 pending 行前从 bundle 入口也先经过 no-write append review。
- review-ready pending lane 和 review cards 现在显示 `check_harness_sample_outcome.py <candidate-jsonl>`，确保 pending 行改为 accepted / rejected 前从 pending audit 入口先经过 no-write outcome review。
- sample intake bundle 的 markdown renderer 拆到 `scripts/harness_sample_intake_render.py`，并纳入 change-triggered follow-up 规则，后续改 summary / text 输出会触发 sample-gap queue 与 bundle 复核。
- `governance-and-smoke` 的 sample gap collector 现在写出 markdown 和 JSON report，并把缺口表追加到 GitHub step summary，避免真实样本缺口只留在 job-local `/tmp` 文件中。
- `governance-and-smoke` 的 pending sample slot audit 现在写出 future/local-inclusive markdown、JSON 和 placeholder review cards，并把 lane report 与 placeholder cards 追加到 GitHub step summary，避免 CI 只保留默认 current queue 视图。
- `governance-and-smoke` 的 sample collection planner 现在同时写出 markdown queue、JSON queue，并把当前 collection queue 追加到 GitHub step summary，便于 PR 页面直接看到下一批真实样本采集 lane。
- sample collection planner 的 markdown queue 现在在表格前输出 queued gap、priority、readiness、pending slot status 和 ledger action 汇总，CI summary 可直接看到采集 lane 分布。
- `governance-and-smoke` 的 future-work contract check 现在写出 markdown 和 JSON report，并把 contract precondition report 追加到 GitHub step summary，明确 contract / ADR 未批准前不能采样。

## 修复问题

- 修复部分 security / guardrail / workflow / trace gap 只能显示 `not tracked by a sample checker yet`、无法登记 bounded evidence count 的缺口。

## 行为变化

- `GAP-TRACE-OTLP-PILOT-BURNIN` 当前有 1 个 accepted local-interop sample，并在 collector 中标记为 `accepted-local-sample`。
- collector 会继续显示 accepted real/local 计数；本地样本不会被计为真实远端互通或 security / guardrail 真实样本。
- collection planner 默认只列尚未完成的可采集项；`--include-future --include-accepted` 才显示 future work 和已有 local sample。

## 边界

- 该检查保持 advisory，不自动生成证据、不升级 blocking。
- OTLP local pilot 只证明 localhost capture-server 路径；不证明 hosted collector、OpenAI tracing、MCP、A2A、native sandbox 或外部 OTLP 互通。

## 破坏性变更

- 无。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_gap_evidence.py`
- `python3 tests/test_harness_sample_gap_evidence.py`
- `.codex/hooks/run_with_repo_python.sh scripts/collect_harness_sample_gaps.py`
- `.codex/hooks/run_with_repo_python.sh scripts/collect_harness_sample_gaps.py --json`
- `python3 tests/test_harness_sample_gaps.py`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --gap-id GAP-GUARDRAIL-PREFLIGHT-WARNING --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --priority P0 --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --ledger-action fill-existing-placeholder --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --include-accepted --ledger-action no-sample-collection --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --gap-id GAP-GUARDRAIL-PREFLIGHT-WARNING --sample-template`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_placeholder_replacement.py <candidate-jsonl>`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_append.py <candidate-jsonl>`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_outcome.py <candidate-jsonl>`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --include-future --ledger-action define-contract-precondition --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --json`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --gap-id GAP-GUARDRAIL-PREFLIGHT-WARNING --json`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --gap-id GAP-GUARDRAIL-PREFLIGHT-WARNING --sample-template`
- `python3 tests/test_plan_harness_sample_collection.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --area workflow-skills --priority P2 --actionable-only --pending-state without-review-ready-pending`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --ledger-action fill-existing-placeholder`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --area ai-guardrail --priority P0 --summary`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --ledger-action fill-existing-placeholder --summary`
- `python3 tests/test_harness_placeholder_replacement.py`
- `python3 tests/test_harness_sample_append.py`
- `python3 tests/test_harness_sample_outcome.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --include-future --include-accepted`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --include-future --include-accepted --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --review-state placeholder --review-cards`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --gap-id GAP-GUARDRAIL-PREFLIGHT-WARNING --review-cards`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --review-state review-ready --review-cards`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_future_work_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_future_work_contracts.py --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_collection_config.py`
- `python3 tests/test_harness_collection_config.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_warning_sample_code_alignment.py`
- `python3 tests/test_warning_sample_code_alignment.py`
- `python3 tests/test_harness_sample_templates.py`
- `python3 tests/test_harness_pending_samples.py`
- `python3 tests/test_harness_sample_followup_coverage.py`
- `python3 tests/test_governance_workflow_sample_outputs.py`
- `python3 tests/test_change_triggered_followups.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Sample Gap Evidence](../standards/harness-sample-gap-evidence.md)
