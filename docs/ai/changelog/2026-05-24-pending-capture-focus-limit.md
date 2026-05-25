# 2026-05-24 Pending Capture Focus Limit

## 新增功能

- `scripts/check_harness_pending_samples.py --capture-focus` 新增 `--capture-focus-limit`。
- 默认仍输出前 5 个 bounded next-capture cards；`--capture-focus-limit 0` 会展开全部 matching actionable capture lanes。
- capture-focus card 现在显示 `Focus entries: shown/available`、`Focus limit` 和 `Focus truncated`，便于 CI summary 或人工交接确认当前输出是否只是默认截断。
- capture-focus card 现在显示 shown / available 的 priority bucket 和 ledger-action bucket，便于默认只看前 5 个时判断后排是否还有 P2 / P3 或 append lane。
- capture-focus card 现在显示每个 gap 的 `Evidence needed` checklist，避免采集者必须先打开 intake bundle 才知道 bounded evidence 字段。
- capture-focus card 现在显示 roadmap area，并支持 `--capture-focus-area`；shown / available bucket 也同步包含 area 计数。
- `--capture-focus-priority` 和 `--capture-focus-ledger-action` 可只渲染某个优先级或 lane 的 next-capture cards；这些过滤只作用于 `next_capture_focus`，不改变完整 pending accounting 或 queue totals。
- JSON 报告新增 `next_capture_focus_area_filter`、`next_capture_focus_priority_filter`、`next_capture_focus_ledger_action_filter`、`next_capture_focus_count`、`next_capture_focus_available_count`、`next_capture_focus_limit`、`next_capture_focus_truncated` 以及 shown / available area / priority / ledger-action count 字段；每个 `next_capture_focus` entry 也带 `area` 和 `evidence_needed`。
- Governance workflow 的 pending sample audit step 现在会把 `--capture-focus` cards 单独追加到 GitHub step summary。
- Sample follow-up coverage 和 change-triggered harness sample rules 现在要求 `--capture-focus --capture-focus-limit 0`、`--capture-focus --capture-focus-area agentic-red-team`、`--capture-focus --capture-focus-priority P2` 和 `--capture-focus --capture-focus-ledger-action fill-existing-placeholder`，防止 full-expansion 与聚焦过滤路径漂移。

## 修复问题

- 避免维护者只能看到默认前 5 个 capture-focus 项时，漏看后排的 approved future-work、security、workflow 或 red-team append lanes。
- 避免为了看到完整 actionable sample lanes 而手动扫描完整 pending JSON。
- 避免维护者为了找 P2/P3 或 placeholder-fill lane 而展开完整 focus cards 后再人工筛选。
- 避免维护者看见聚焦 card 后还要跳到 intake summary 才知道具体要收哪些 bounded evidence 字段。
- 避免维护者想处理某个 roadmap area（例如 agentic-red-team）时只能靠完整列表人工筛选。

## 行为变化

- `PendingSampleReport.next_capture_focus` 现在可由调用方传入 `capture_focus_limit` 控制；默认值保持 5。
- `PendingSampleReport.next_capture_focus` 现在可由调用方传入 area / priority / ledger-action filter；filter 元数据会随 JSON 输出。
- `PendingSampleReport.next_capture_focus[*].evidence_needed` 现在直接复用 collection planner 的 bounded capture checklist。
- `PendingSampleReport.next_capture_focus[*].area` 现在直接复用 collection planner 的 roadmap area。
- `PendingSampleReport` 同时暴露 focus 的展示数量、可用数量、bucket 分布、配置上限和截断状态；默认上限不再需要由调用方靠列表长度猜测。
- `capture_focus_limit=0` 只改变只读输出范围，不改变 collection queue、pending slot、ledger action 或 sample outcome。
- `capture_focus_priorities` 和 `capture_focus_ledger_actions` 只改变只读 focus selection，不改变 collection queue、pending slot、ledger action 或 sample outcome。
- CI summary 现在会显示默认截断状态，避免维护者只看到 full lane report 或 placeholder review cards 时漏掉下一步 capture 入口。
- 以后修改 pending sample control plane 时，默认 cards、full-expansion cards、area 过滤 cards、priority 过滤 cards 和 ledger-action 过滤 cards 都会出现在建议回归命令中。

## 破坏性变更

- 无。默认输出数量保持 5；该变更不写 ledger、不接受样本、不生成真实 evidence、不升级 blocking。

## 验证范围

- `python3 tests/test_harness_pending_samples.py`
- `python3 tests/test_tool_contracts.py`
- `python3 tests/test_governance_workflow_sample_outputs.py`
- `python3 tests/test_harness_sample_followup_coverage.py`
- `python3 tests/test_change_triggered_followups.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus --capture-focus-limit 0`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus --capture-focus-area agentic-red-team`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus --capture-focus-priority P2`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus --capture-focus-ledger-action fill-existing-placeholder`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
- `.agents/skills/harness-maintenance/references/verification-commands.md`
