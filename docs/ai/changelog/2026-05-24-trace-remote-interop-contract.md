# 2026-05-24 Trace Remote Interop Contract Approval

## 新增功能

- 新增 ADR-017，定义 `GAP-TRACE-REMOTE-INTEROP` 的 bounded remote interop 采样边界。
- `FWC-2026-05-24-trace-remote-interop` 现在可进入 `approved-for-sampling`，并引用已采纳 ADR 覆盖 auth、endpoint、redaction 和 cost / stop 边界。
- `check_harness_sample_gap_evidence.py` 新增 `real-interop-run` source type，用于复核 remote interop pending sample 的 bounded endpoint/status/export 字段。

## 修复问题

- 避免 `GAP-TRACE-REMOTE-INTEROP` 在合同已批准后仍被报告为 `define-contract-precondition` / contract-blocked。
- 避免 planner、pending report 和 intake bundle 把 remote interop 继续路由到 future-work contract replacement lane。

## 行为变化

- `GAP-TRACE-REMOTE-INTEROP` 现在进入 generic sample-gap `append-new-pending-slot` lane，目标账本是 `docs/ai/standards/harness-sample-gap-evidence.jsonl`。
- remote interop pending draft 的 `source_type` 为 `real-interop-run`，并通过 `check_harness_sample_append.py <candidate-jsonl>` 和 `check_harness_sample_outcome.py <candidate-jsonl>` 分两步复核。
- future-work contract 状态现在为 approved 2 个、blocked 0 个；remote interop accepted real sample 仍为 0。

## 破坏性变更

- 无。该变更只开放 bounded pending-sample routing，不写 ledger、不接受样本、不升级 blocking、不声明外部 collector、OpenAI hosted trace、MCP 或 A2A 互通已完成。

## 验证范围

- `python3 tests/test_harness_future_work_contracts.py`
- `python3 tests/test_harness_burn_in_readiness.py`
- `python3 tests/test_plan_harness_sample_collection.py`
- `python3 tests/test_harness_pending_samples.py`
- `python3 tests/test_harness_sample_intake_bundle.py`
- `python3 tests/test_harness_collection_config.py`
- `python3 tests/test_harness_sample_templates.py`
- `python3 tests/test_harness_future_work_contract_candidate.py`
- `python3 tests/test_harness_sample_gap_evidence.py`
- `python3 tests/test_harness_sample_append.py`
- `python3 tests/test_tool_contracts.py`

## 关联文档

- `docs/ai/adr/ADR-017-trace-remote-interop-boundary.md`
- `docs/ai/agentic-harness-gap-roadmap.md`
- `docs/ai/harness-open-items.md`
- `docs/ai/check-registry.md`
- `docs/ai/tool-contracts/README.md`
- `docs/ai/tool-contracts/contracts.json`
- `.agents/skills/harness-maintenance/references/verification-commands.md`
