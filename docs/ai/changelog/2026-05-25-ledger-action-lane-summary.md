# 2026-05-25 Ledger Action Lane Summary

## 新增功能

- Governance workflow 现在把 `append-new-pending-slot` 和 `fill-existing-placeholder` 两条 ledger-action lane 展开到 planner capture-card、template drift、intake summary 和 pending capture-focus 四个 summary 面。
- Pending capture focus 对这两条 lane 使用 `--capture-focus-limit 0`，避免默认前 5 个聚焦卡隐藏剩余 append 或 placeholder replacement 目标。

## 修复问题

- 修复只按 capture-gate / readiness 查看 CI summary 时仍需人工从 ledger-action bucket count 反查 append 与 placeholder fill 全量队列的问题。
- 补齐 sample follow-up coverage、change-triggered rules、workflow output tests 和 tool contract registry 对这两条 lane 的覆盖。

## 行为变化

- `append-new-pending-slot` lane 当前显示 13 个仍需真实事件或 bounded review 的缺口。
- `fill-existing-placeholder` lane 当前显示 2 个 pending placeholder 缺口，真实 warning 或 real event 补齐后仍需先跑 `check_harness_placeholder_replacement.py <candidate-jsonl>`。
- 这些视图只读，只进入 CI summary / stdout，不写 ledger、不生成样本、不接受 evidence。

## 破坏性变更

- 无。现有默认 queue、capture-gate、readiness 和 upgrade-decision 视图保持不变。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --ledger-action append-new-pending-slot --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --ledger-action fill-existing-placeholder --capture-card`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --ledger-action append-new-pending-slot`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py --ledger-action fill-existing-placeholder`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --ledger-action append-new-pending-slot --summary`
- `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --ledger-action fill-existing-placeholder --summary`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus --capture-focus-ledger-action append-new-pending-slot --capture-focus-limit 0`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus --capture-focus-ledger-action fill-existing-placeholder --capture-focus-limit 0`

## 关联文档

- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
