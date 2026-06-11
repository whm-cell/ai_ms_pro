# 2026-05-24 Check Burn-in Ledger

更新时间：2026-05-24
阶段或版本：stage-00 / agentic harness hardening
状态：已确认

## 新增功能

- 新增 `docs/ai/check-burn-in-ledger.md`，为 `blocking-candidate` checks 记录 accepted samples、false positives、repair path、cost、current decision 和 next evidence。
- 新增 `scripts/check_burn_in_ledger.py`，校验 `check-registry.md` 中所有 `blocking-candidate` 是否都有 ledger 行。
- 新增 `tests/test_check_burn_in_ledger.py`，覆盖 repo ledger、缺失行、字段格式、决策枚举和 JSON 输出。
- 增加升级决策一致性校验：`ready-for-adr` 与 `promote-to-blocking` 必须已有 `2/2` accepted samples，且 accepted sample count 不能超过目标值。

## 修复问题

- 修复 `agentic-harness-gap-roadmap.md` 中 G8 的优先级漂移：表格和迭代顺序统一为 `P2 Task Profile Audit`。
- 把 G5 从“待做 ledger”推进到 “v1 ledger 已落地，但仍需真实样本 burn-in”。
- 修复 `check_burn_in_ledger.py` 在 macOS 系统 Python 3.9 下运行单测时因 `zip(strict=True)` 不兼容而失败的问题；follow-up 建议中的 plain `python3 tests/test_check_burn_in_ledger.py` 现在可直接通过。

## 行为变化

- `check_burn_in_ledger.py` 登记为 advisory check；它校验证据账本结构和升级决策一致性，不生成 accepted samples，也不授权升级 blocking。
- `check_change_triggered_followups.py` 会在 check registry、burn-in ledger 或 checker 变化时提示对应 follow-up。
- `docs/ai/index.md` 增加 Check Burn-in Ledger 入口和常用检查命令。
- `governance-and-smoke.yml` 接入 `check_burn_in_ledger.py`，并写出 markdown / JSON report 到 job-local `/tmp`，同时把 ledger audit 追加到 GitHub step summary；tool contract 的 `automation_mode` 更新为 `ci`；该检查仍保持 advisory，只校验 coverage / shape / upgrade-decision consistency。

## 破坏性变更

- 无。新 checker 只读 repo 文档，不写文件、不阻断 hook、不改变现有 check 等级。

## 验证范围

- `python3 tests/test_check_burn_in_ledger.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_burn_in_ledger.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_burn_in_ledger.py --json`
- `python3 tests/test_governance_workflow_sample_outputs.py`
- `python3 tests/test_change_triggered_followups.py`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `.codex/.venv/bin/python -m ruff check .codex/hooks scripts tests`
- `git diff --check`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Check Registry](../check-registry.md)
- [Check Burn-in Ledger](../check-burn-in-ledger.md)
- [Harness Remaining Work](../harness-open-items.md)
