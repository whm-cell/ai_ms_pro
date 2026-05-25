# 2026-05-24 Agentic Cascade Stop Contract Approval

## 新增功能

- 新增 ADR-016，定义 `GAP-AGENTIC-CASCADE-STOP` 的 bounded local real-incident 采样边界。
- `FWC-2026-05-24-agentic-cascade-stop` 现在可进入 `approved-for-sampling`，并引用已采纳 ADR 覆盖 authority、scope、redaction 和 stop / cost 边界。
- collection planner、pending report 和 intake bundle 现在可把已批准采样的 future-work gap 路由到 dedicated sample ledger。

## 修复问题

- 避免 `GAP-AGENTIC-CASCADE-STOP` 在合同已批准后仍被报告为 `define-contract-precondition` / contract-blocked。
- 避免 collection config 一刀切拒绝所有 future-work dedicated sample targets；未批准的 future-work gap 仍必须走 future contract target。

## 行为变化

- `GAP-AGENTIC-CASCADE-STOP` 现在进入 red-team `append-new-pending-slot` lane，目标账本是 `docs/ai/security/agentic-red-team-samples.jsonl`。
- `GAP-TRACE-REMOTE-INTEROP` 仍是唯一 contract-blocked future-work gap。
- actionable sample gap 数从 16 变为 17；future contract 状态为 approved 1 个、blocked 1 个。

## 破坏性变更

- 无。该变更只开放 bounded pending-sample routing，不写 ledger、不接受样本、不升级 blocking。

## 验证范围

- `python3 tests/test_harness_future_work_contracts.py`
- `python3 tests/test_harness_burn_in_readiness.py`
- `python3 tests/test_plan_harness_sample_collection.py`
- `python3 tests/test_harness_pending_samples.py`
- `python3 tests/test_harness_sample_intake_bundle.py`
- `python3 tests/test_harness_collection_config.py`
- `python3 tests/test_harness_sample_templates.py`
- `python3 tests/test_harness_future_work_contract_candidate.py`
- `python3 tests/test_tool_contracts.py`

## 关联文档

- `docs/ai/adr/ADR-016-agentic-cascade-stop-boundary.md`
- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
- `.agents/skills/harness-maintenance/references/verification-commands.md`
