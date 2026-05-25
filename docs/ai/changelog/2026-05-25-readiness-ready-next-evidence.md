# Readiness Ready Next Evidence

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- `scripts/check_harness_burn_in_readiness.py` 现在把 ready gap 的 upgrade-decision `next_evidence_needed` 带入 readiness item。
- Readiness text / markdown 输出新增 `ready next evidence needed by gap` 摘要和 `Ready Gap Next Evidence` 表。
- Readiness JSON 输出新增 top-level `ready_next_evidence_needed_by_gap`，并在对应 item 内输出 `next_evidence_needed`。
- `scripts/plan_harness_sample_collection.py` 与 sample template helper 复用 readiness item 的 `next_evidence_needed`，ready-gap decision draft 不再只依赖硬编码 fallback。

## 修复问题

- 修复 ready gap 已有 `keep-advisory` 决策时，readiness 报告只能看到 decision status / ref，不能直接看到后续还要采集哪些真实样本、误报或边界证据的问题。

## 行为变化

- 该变更只补齐控制面可见性；不写 ledger、不生成样本、不接受 pending row、不升级 blocking。

## 破坏性变更

- 无。

## 验证范围

- `.codex/.venv/bin/ruff check scripts/harness_upgrade_decision_status.py scripts/harness_burn_in_readiness_types.py scripts/check_harness_burn_in_readiness.py scripts/harness_burn_in_readiness_render.py scripts/harness_sample_collection_items.py scripts/plan_harness_sample_collection.py scripts/harness_sample_template_records.py tests/test_harness_burn_in_readiness.py tests/test_plan_harness_sample_collection.py tests/test_harness_sample_intake_bundle.py tests/test_tool_contracts.py`
- `python3 tests/test_harness_burn_in_readiness.py`
- `python3 tests/test_plan_harness_sample_collection.py`
- `python3 tests/test_harness_sample_intake_bundle.py`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --readiness ready-for-upgrade-discussion`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --readiness ready-for-upgrade-discussion --json`
- `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --gap-id GAP-WORKFLOW-TASK-PROFILE-AUDIT --json`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --all`
- `.codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py`

## 关联文档

- [AI 文档入口索引](../index.md)
- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
