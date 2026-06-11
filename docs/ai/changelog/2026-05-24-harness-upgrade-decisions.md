# 2026-05-24 Harness Upgrade Decisions

更新时间：2026-05-24
阶段或版本：stage-00 / stage-01 harness hardening
状态：已确认

## 新增功能

- 新增 `docs/ai/standards/harness-upgrade-decisions.jsonl`，记录达到 `ready-for-upgrade-discussion` 的 roadmap gap 是否保持 advisory、进入 ADR 或准备升级。
- 新增 `scripts/check_harness_upgrade_decisions.py` 与 `tests/test_harness_upgrade_decisions.py`，校验 ready gap 是否都有决策、决策快照是否仍匹配当前 readiness 计数、以及是否误引用 raw runtime material。
- `governance-and-smoke` 现在写出 harness upgrade decision markdown / JSON report，并追加到 GitHub step summary。

## 修复问题

- 修复 Task Profile Audit 达到升级讨论门槛后缺少确定性决策记录的问题；当前决策为 `keep-advisory`。

## 行为变化

- `GAP-WORKFLOW-TASK-PROFILE-AUDIT` 仍是 advisory；ready-for-upgrade 只表示样本足以讨论，不表示自动升级 blocking。
- 后续新增 ready gap 时，必须补一条 bounded upgrade decision snapshot，否则 `check_harness_upgrade_decisions.py` 会报错。

## 破坏性变更

- 无。该变更只增加升级决策审计，不改变 check 等级、不写 ADR、不生成或接受样本。

## 验证范围

- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_upgrade_decisions.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_upgrade_decisions.py --json`
- `python3 tests/test_harness_upgrade_decisions.py`
- `python3 tests/test_change_triggered_followups.py`
- `python3 tests/test_governance_workflow_sample_outputs.py`
