# Readiness Capture Gates

日期：2026-05-25

## 新增功能

- 新增 `scripts/harness_sample_capture_gates.py`，把 source type、ledger action 和 capture gate 判定从 planner helper 中抽成共享只读规则。
- 新增 `scripts/harness_burn_in_readiness_cli.py`，把 readiness CLI 参数解析从审计主模块中拆出。
- 新增 `scripts/harness_burn_in_readiness_filters.py`，把 readiness gap-id / capture-gate 过滤和计数从 CLI 主模块中拆出。
- 新增 `scripts/harness_burn_in_readiness_render.py`，让 readiness CLI 主文件保持审计数据组装职责，不把表格渲染继续堆进主模块。
- `scripts/check_harness_burn_in_readiness.py` 现在输出 capture gate counts，并在 text / JSON 的每个 readiness item 中带 `capture_gate` 与 `capture_gate_detail`。
- `scripts/check_harness_burn_in_readiness.py --area <area>` 和 `--priority <priority>` 现在可按 roadmap bucket 聚焦 readiness audit。
- `scripts/check_harness_burn_in_readiness.py --gap-id <GAP-ID>` 现在可按单个 gap 聚焦 readiness audit，例如只看 `GAP-TRACE-REMOTE-INTEROP`。
- `scripts/check_harness_burn_in_readiness.py --capture-gate <gate>` 现在可按真实事件前置条件聚焦 readiness audit，例如只看 `requires-approved-remote-interop`。

## 修复问题

- 防止 readiness audit 只显示 accepted count / upgrade target，却隐藏 planner、intake 和 pending focus 已经显示的真实事件前置条件。
- planner 与 readiness 现在复用同一 capture gate 判定，降低 `requires-approved-remote-interop`、`requires-cross-task-resume`、placeholder replacement 等 lane 漂移风险。

## 行为变化

- readiness markdown 表新增 `Capture gate` 列。
- readiness text / JSON 新增 area / priority filters 与 counts，item 新增 `priority`。
- readiness text 输出新增 active gap filter；空过滤范围会显示 no-match 行。
- readiness JSON 新增 `area_filter`、`priority_filter`、`gap_id_filter`、`capture_gate_filter`、`area_counts`、`priority_counts` 和 `capture_gate_counts`，每个 item 新增 `priority`、`capture_gate` 与 `capture_gate_detail`。
- governance workflow step summary 现在追加 full readiness、trace-interop readiness、P2 readiness 和 remote-interop readiness 聚焦视图。

## 破坏性变更

- 无。Capture gates remain read-only routing metadata; they do not collect samples, accept pending rows, or prove readiness.

## 验证范围

- `.codex/.venv/bin/python -m unittest tests.test_harness_burn_in_readiness tests.test_plan_harness_sample_collection`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --area trace-interop --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --priority P2 --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --gap-id GAP-TRACE-REMOTE-INTEROP --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --capture-gate requires-approved-remote-interop --json`
- `.codex/.venv/bin/python -m unittest tests.test_governance_workflow_sample_outputs`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
