# Area Priority Full Collection Surface

更新时间：2026-05-25
阶段或版本：stage-00
状态：已确认

## 新增功能

- Extended active real-sample area / priority coverage from readiness + pending focus to the full read-only collection surface: planner capture-card, sample template drift, intake summary, readiness audit, and pending capture-focus.
- Added area / priority planner, template, and intake commands to the changed-file follow-up package and required command closure audit.
- Added governance workflow summary sections for every active real-sample area and priority across planner, template, and intake outputs; readiness and pending focus sections remain covered.
- Updated collection config, workflow-output tests, tool contracts, check registry, open items, and roadmap notes so the five-surface area / priority contract is documented and drift-checked.

## 修复问题

- Prevents active roadmap area / priority buckets from being visible in readiness or pending focus while planner, template, or intake step-summary views silently lag.
- Prevents future sample-gap handoffs from falling back to a full queue when a focused area / priority collection surface should already be present.

## 行为变化

- This is visibility and routing coverage only.
- It does not write ledgers, generate samples, accept pending evidence, approve future-work sampling, or change burn-in readiness state.

## 破坏性变更

- 无.

## 验证范围

- `python3 tests/test_harness_collection_config.py`
- `python3 tests/test_harness_sample_followup_coverage.py`
- `python3 tests/test_governance_workflow_sample_outputs.py`
- `python3 tests/test_tool_contracts.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_collection_config.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py`
- `.codex/hooks/run_with_repo_python.sh scripts/check_tool_contracts.py`

## 关联文档

- [Agentic Harness Gap Roadmap](../agentic-harness-gap-roadmap.md)
- [Harness Remaining Work](../harness-open-items.md)
- [Check Registry](../check-registry.md)
- [Tool Contracts](../tool-contracts/README.md)
