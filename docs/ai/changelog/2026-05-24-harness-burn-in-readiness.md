# 2026-05-24 Harness Burn-in Readiness

更新时间：2026-05-24
阶段或版本：stage-00 / agentic harness hardening
状态：已确认

## 新增功能

- 新增 `scripts/check_harness_burn_in_readiness.py`，汇总 roadmap sample gaps 的 accepted real、cross-task、profile coverage 和 local-only evidence 计数。
- 新增 `tests/test_harness_burn_in_readiness.py`，覆盖 P0/P1 未就绪、Local Trace Summary 仍需更多样本、Task Profile Audit 仍需更多 profile 覆盖，以及 future/local-only 边界。
- Governance workflow 现在会生成包含 future-work / local-only 的 `/tmp/harness-burn-in-readiness.md` 与 JSON readiness artifact，并把 readiness report 追加到 GitHub step summary。
- `scripts/plan_harness_sample_collection.py` 现在复用 readiness 计数，在采集队列和 capture card 中显示 metric 与 current / upgrade target，避免静态 gap 状态和真实样本计数漂移。
- 新增 `scripts/check_harness_pending_samples.py` 与 `tests/test_harness_pending_samples.py`，跨 JSONL 样本账本汇总 accepted / pending / rejected 计数，并把 pending 槽位与当前 collection queue 对齐。
- 新增 `docs/ai/standards/harness-future-work-contracts.jsonl`、`scripts/check_harness_future_work_contracts.py` 与 `tests/test_harness_future_work_contracts.py`，为 `GAP-TRACE-REMOTE-INTEROP` 和 `GAP-AGENTIC-CASCADE-STOP` 记录 needs-ADR contract 前置条件。
- `--sample-template` 遇到 future-work gaps 时现在生成 `harness-future-work-contract/v1` 前置合同草稿，保持 `sample_collection_allowed=false`，不再生成普通 sample evidence 草稿。
- pending sample slot audit 现在额外区分 actionable sample gaps、actionable without review-ready pending、future-work contract-blocked gaps 和 local-only gaps，避免把 queued-without-pending 或 placeholder pending 误读成已具备可复核样本。
- `check_harness_pending_samples.py --review-cards` 现在会为每个 pending 槽位输出只读复核卡片，包含 ledger line、checker command、readiness、current / target 和边界说明。
- `plan_harness_sample_collection.py` 新增 `--actionable-only --pending-state without-pending` 过滤入口，可直接输出仍缺 pending slot 的可采样 capture cards。
- `plan_harness_sample_collection.py` 现在还支持 `without-review-ready-pending` / `with-review-ready-pending` / `with-placeholder-pending` 等 pending review-state filter；placeholder pending 不再从真实事件采集队列中移除。
- sample collection queue / capture cards 会显示 target checker command，与 intake bundle / pending review cards 使用同一条复核路径。
- sample collection queue / capture cards / JSON report 现在复用 pending slot summary，直接显示 pending slot status、ledger refs 和 review blockers；单 gap capture card 可作为真实事件补字段清单。
- `check_harness_sample_templates.py` 支持同一组 actionable / pending-state filter，可验证“仍缺 pending slot”或“仍缺 review-ready pending”的草稿包是否匹配目标 checker。
- 新增 `scripts/build_harness_sample_intake_bundle.py` 与 `tests/test_harness_sample_intake_bundle.py`，把 actionable without review-ready pending 草稿按目标 artifact 分组展示，并在输出前复用目标 checker 校验；当前草稿数为 17，其中 PreToolUse preflight 和 Loop / Scope Monitor 的 placeholder pending 仍保留在真实采集目标中。
- sample intake bundle 每条 entry 现在携带 pending slot status、sample id 和 ledger refs，让操作员能直接区分无 pending、placeholder pending 和 review-ready pending。
- sample intake bundle 新增 `--summary` 短输出，governance workflow 会生成完整 bundle / JSON report，并把短 summary 写入 GitHub step summary。
- changed-file follow-up 现在会为 harness sample gap surface 同时建议 intake bundle 默认输出、`--summary` 和 `--json`，避免本地复核漏掉 CI summary / machine-readable report。
- sample intake bundle 与 pending review cards 现在共用 target checker command 路由；bundle entry / JSON report 会显示 append 后应跑的复核命令，`--summary` 的 target 表也会展示该命令。
- 专用样本模板现在显式写入对应 `GAP-*` id；pending sample slot audit 继续兼容旧行，但会拒绝专用 ledger 中指向其他 gap 的新显式 `gap_id`。
- pending sample slot audit 现在为 placeholder 行输出 `review_blockers`，并传到 review cards、intake bundle JSON 和 `--summary` 的 Pending Slot Blockers 表。
- pending sample slot audit / review cards 现在支持 `--gap-id <GAP-ID>` 和 `--review-state review-ready`，可从单个 capture card 直接进入 focused review，不必扫描全部 pending 槽位。
- inclusive collection queue / pending audit 现在把 accepted local-only gap 路由到 `no-sample-collection`，保留统计可见性，但不再生成 append lane 或下一步采样命令。

## 修复问题

- 防止 sample gap collector / planner 只能列“下一步采样”，但不能直接回答“是否已经可以讨论升级”的缺口。
- 明确 local-only OTLP pilot、future remote interop 和 accepted local-replay 不等同 accepted real sample。

## 行为变化

- `check-registry` 将 `check_harness_burn_in_readiness.py` 登记为 advisory。
- tool contract registry 记录该脚本为 CI-safe read-only audit。
- change-triggered follow-up 中的 harness sample gap evidence 路由会提示 readiness audit。
- sample collection queue 仍然只是 planning surface；它读取 sample checker report 计算 readiness，但不写入样本、不批准动作、不把 pending template 计入 burn-in。
- sample collection queue 的 pending-state filter 只读取样本账本覆盖情况；它不会把缺 pending slot 或缺 review-ready pending slot 自动写入 ledger。
- planner 中的 pending slot status / refs / blockers 只读现有账本；它们用于定位 placeholder 行还缺哪些真实事件字段，不会自动接受 pending 样本或改变 readiness 计数。
- sample template drift check 的 filtered queue 模式只校验草稿 shape，不把 actionable gaps 计为样本；`without-pending` 仍严格表示没有任何 pending ledger row，`without-review-ready-pending` 用于默认真实采集草稿包并保留 placeholder pending gaps。
- sample intake bundle 是 stdout-only 操作员审阅面；它不写入 ledger、不接受 pending 样本、不批准 future-work sampling，也不把草稿计为 accepted burn-in。
- sample intake bundle 中的 pending slot metadata 只读样本账本；它用于路由真实样本采集，不会把 placeholder row 转成 accepted evidence。
- governance workflow 中的 intake bundle summary 只展示队列、target、pending slot status 和 target review command，不展示 JSONL template body；完整草稿仍保存在 job-local `/tmp/harness-sample-intake-bundle.md`。
- changed-file follow-up 仍是 advisory；它提示应该跑哪些 intake bundle 命令，不代表已经采集或接受任何真实样本。
- pending sample slot audit 只读已写入的 JSONL 样本账本；它显示哪些 queued gaps 已经有 pending 槽位，按 evidence class 拆分 accepted real / synthetic / local-replay / local-only 计数，把 pending 槽位标成 `review-ready` 或 `placeholder`，并单独列出 actionable without pending、actionable without review-ready pending、contract-blocked 和 local-only gaps，不把 pending 槽位当作 accepted burn-in。
- accepted local-only gap 会留在 inclusive queue 的 `no-sample-collection` 统计中；除非 roadmap 状态改变，它不会产生 sample template、intake bundle entry 或 next collection lane command。
- pending review cards 只负责指导复核，不会修改 outcome；卡片会显示 evidence class 和 review state，pending 样本必须经单独人工/主 agent 复核后才能改为 accepted 或 rejected。
- pending review card filters 只改变显示范围；它们不会把 pending 样本标为 review-ready、不会补字段、不会接受或拒绝样本。
- review blockers 只解释 placeholder 行为什么还不能复核；它不会自动补字段、不会接受样本，也不会改变 readiness 计数。
- dedicated ledger 的显式 `gap_id` 只用于路由和错账检查；它不会改变 existing accepted / pending / rejected 计数，也不会把模板或 pending rows 计为 accepted burn-in。
- Local Trace Summary readiness 现在按 accepted distinct task classes 计数；当前 3 个 accepted report 同属 `harness-hardening`，所以进度仍为 1/3，而不是按 report 行数算作 3/3。
- future-work contract audit 会保持 `sample_collection_allowed=false`，直到 ADR / contract approval 明确授权；当前不证明远端互通、级联 agent containment 或真实 incident 覆盖。
- future-work gaps 在 collection planner 中显示为 `contract-blocked`，目标 artifact 是 `docs/ai/standards/harness-future-work-contracts.jsonl`；合同未批准前不进入样本采集账本。

## 破坏性变更

- 无。该脚本只读现有样本账本和 checker report，不生成 evidence、不写 ledger、不升级 blocking。

## 验证范围

- `python3 tests/test_harness_burn_in_readiness.py`
- `python3 tests/test_plan_harness_sample_collection.py`
- `python3 tests/test_harness_pending_samples.py`
- `python3 tests/test_harness_future_work_contracts.py`
- `python3 tests/test_harness_sample_templates.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --gap-id GAP-GUARDRAIL-PREFLIGHT-WARNING --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --gap-id GAP-GUARDRAIL-PREFLIGHT-WARNING --json`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --actionable-only --pending-state without-pending --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --actionable-only --pending-state without-review-ready-pending --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --include-accepted --ledger-action no-sample-collection --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --review-cards`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --gap-id GAP-GUARDRAIL-PREFLIGHT-WARNING --review-cards`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --review-state review-ready --review-cards`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_future_work_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --actionable-only --pending-state without-pending`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --actionable-only --pending-state without-review-ready-pending`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --summary`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --json`
- `python3 tests/test_harness_sample_intake_bundle.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --json`
- `python3 tests/test_governance_workflow_sample_outputs.py`
- `python3 tests/test_change_triggered_followups.py`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Remaining Work](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
